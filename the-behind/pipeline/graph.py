"""Graph store for The Behind 01 recursive milestone pipeline.

The graph lives in a single JSON file. Every mutation is checkpointed
(saved atomically) immediately, so a long run can be paused, inspected,
and resumed at any point without losing work.

Structure of graph.json:
{
  "version": 1,
  "config":   { ... snapshot of the run configuration ... },
  "run_state": {
      "profile": "full" | "smoke",
      "started_at": iso, "updated_at": iso,
      "expansions_done": int,
      "raw_candidates_seen": int,
      "rejected": [ {"parent_id", "name", "reason", "at"} ... ]   # feeds {already_rejected}
  },
  "nodes": { node_id: {
      "id", "name", "aliases": [], "year": int|null, "domain", "type",
      "definition", "bottleneck",
      "status": "provisional" | "verified",
      "depth": int,
      "expanded": bool,
      "priority": float,          # admission score; frontier is best-first
      "sources": [ {"title","url"} ],
      "verification": null | {"outcome","notes","at"},
      "merged_into": null | node_id,     # union-find pointer
      "created_at": iso
  }},
  "edges": [ {                      # edge reads: parent "enabled by" -> child bottleneck removed
      "predecessor_id",             # the earlier advance (the "parent" in trace terms)
      "successor_id",               # the node whose bottleneck it removed
      "verdicts": { "Q1": {"verdict","evidence","source","falsification"}, ... },
      "score": float,
      "gate": {"q1_or_q2": bool, "q3_ok": bool, "passed": bool},
      "created_at": iso
  } ],
  "merge_log": [ {"at","from_id","into_id","signals":[],"scores":{},"reason"} ],
  "expansions": { successor_id: {   # per-expansion working state (resumable)
      "raw_candidates": [ candidate, ... ],
      "resolution": null | {...},   # output of identity resolution
      "judge_queue": [ pair, ... ],
      "judgments_applied": bool,
      "stage": "scouted" | "resolved" | "judged" | "evaluated"
  } }
}

Candidate shape (from the scout, DESIGN.md §4.3, plus identity-card fields
required by §4.5): {"name","year","domain","type","definition","lens",
"causal_claim","source_title","source_url", optional "wikidata"}.
"""

import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone

GRAPH_VERSION = 1

NODE_TYPES = {"device", "theory", "method", "material", "institution", "other"}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(name, year=None):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    s = re.sub(r"-+", "-", s)[:60].strip("-") or "node"
    if year is not None:
        s = f"{s}-{year}"
    return s


class Graph:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = None

    # ---------- lifecycle ----------
    @classmethod
    def create(cls, path, config, root):
        g = cls.__new__(cls)
        g.path = path
        root_id = slugify(root["name"], root.get("year"))
        node = {
            "id": root_id,
            "name": root["name"],
            "aliases": list(root.get("aliases", [])),
            "year": root.get("year"),
            "domain": root.get("domain", ""),
            "type": root.get("type", "other"),
            "definition": root.get("definition", ""),
            "bottleneck": root.get("bottleneck", ""),
            "status": "provisional",
            "depth": 0,
            "expanded": False,
            "priority": 0.0,
            "sources": list(root.get("sources", [])),
            "verification": None,
            "merged_into": None,
            "created_at": now_iso(),
        }
        g.data = {
            "version": GRAPH_VERSION,
            "config": config,
            "run_state": {
                "profile": config.get("profile", "full"),
                "started_at": now_iso(),
                "updated_at": now_iso(),
                "expansions_done": 0,
                "raw_candidates_seen": 0,
                "rejected": [],
            },
            "nodes": {root_id: node},
            "edges": [],
            "merge_log": [],
            "expansions": {},
        }
        g.save()
        return g

    def save(self):
        self.data["run_state"]["updated_at"] = now_iso()
        d = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)

    # ---------- nodes ----------
    def canonical_id(self, node_id):
        """Follow union-find pointers to the surviving node."""
        seen = set()
        cur = node_id
        while True:
            node = self.data["nodes"].get(cur)
            if node is None or node.get("merged_into") is None:
                return cur
            if cur in seen:  # cycle guard; should never happen
                return cur
            seen.add(cur)
            cur = node["merged_into"]

    def live_nodes(self):
        return [n for n in self.data["nodes"].values() if n.get("merged_into") is None]

    def get_node(self, node_id):
        return self.data["nodes"].get(self.canonical_id(node_id))

    def unique_id(self, base):
        if base not in self.data["nodes"]:
            return base
        i = 2
        while f"{base}-{i}" in self.data["nodes"]:
            i += 1
        return f"{base}-{i}"

    def add_node(self, fields):
        nid = self.unique_id(slugify(fields["name"], fields.get("year")))
        node = {
            "id": nid,
            "name": fields["name"],
            "aliases": list(fields.get("aliases", [])),
            "year": fields.get("year"),
            "domain": fields.get("domain", ""),
            "type": fields.get("type", "other"),
            "definition": fields.get("definition", ""),
            "bottleneck": fields.get("bottleneck", ""),
            "status": "provisional",
            "depth": fields.get("depth", 0),
            "expanded": False,
            "priority": float(fields.get("priority", 0.0)),
            "sources": list(fields.get("sources", [])),
            "verification": None,
            "merged_into": None,
            "created_at": now_iso(),
        }
        self.data["nodes"][nid] = node
        return node

    def find_edge(self, predecessor_id, successor_id):
        for e in self.data["edges"]:
            if e["predecessor_id"] == predecessor_id and e["successor_id"] == successor_id:
                return e
        return None

    def add_edge(self, predecessor_id, successor_id, verdicts, score, gate):
        existing = self.find_edge(predecessor_id, successor_id)
        if existing:
            return existing
        edge = {
            "predecessor_id": predecessor_id,
            "successor_id": successor_id,
            "verdicts": verdicts,
            "score": float(score),
            "gate": gate,
            "created_at": now_iso(),
        }
        self.data["edges"].append(edge)
        return edge

    # ---------- merging (union-find) ----------
    def merge_nodes(self, from_id, into_id, signals, scores, reason):
        """Merge node from_id into into_id. Survivor keeps its name, unions
        aliases and edges, keeps the earliest defensible year. Logged and
        reversible (see unmerge)."""
        src = self.data["nodes"][self.canonical_id(from_id)]
        dst = self.data["nodes"][self.canonical_id(into_id)]
        if src["id"] == dst["id"]:
            return dst
        # aliases: survivor absorbs the merged node's name + aliases
        for a in [src["name"]] + list(src.get("aliases", [])):
            if a != dst["name"] and a not in dst["aliases"]:
                dst["aliases"].append(a)
        # sources union
        seen = {(s.get("title"), s.get("url")) for s in dst["sources"]}
        for s in src["sources"]:
            if (s.get("title"), s.get("url")) not in seen:
                dst["sources"].append(s)
        # earliest defensible year
        years = [y for y in (dst.get("year"), src.get("year")) if y is not None]
        if years:
            dst["year"] = min(years)
        # edges: re-point src edges to dst (drop self-loops / duplicates)
        kept = []
        for e in self.data["edges"]:
            if e["predecessor_id"] == src["id"]:
                e["predecessor_id"] = dst["id"]
            if e["successor_id"] == src["id"]:
                e["successor_id"] = dst["id"]
            if e["predecessor_id"] == e["successor_id"]:
                continue
            if any(k["predecessor_id"] == e["predecessor_id"] and k["successor_id"] == e["successor_id"] for k in kept):
                continue
            kept.append(e)
        self.data["edges"] = kept
        src["merged_into"] = dst["id"]
        self.data["merge_log"].append({
            "at": now_iso(), "from_id": src["id"], "into_id": dst["id"],
            "signals": signals, "scores": scores, "reason": reason,
        })
        return dst

    def unmerge(self, from_id):
        node = self.data["nodes"].get(from_id)
        if node and node.get("merged_into") is not None:
            node["merged_into"] = None
            self.data["merge_log"].append({
                "at": now_iso(), "from_id": from_id, "into_id": None,
                "signals": ["unmerge"], "scores": {}, "reason": "manual unmerge",
            })

    # ---------- frontier ----------
    def frontier(self):
        cfg = self.data["config"]
        depth_cap = cfg.get("depth_cap", 10)
        out = [n for n in self.live_nodes()
               if not n["expanded"] and not n.get("dead") and n["depth"] < depth_cap]
        out.sort(key=lambda n: (-n["priority"], n["depth"], n["name"]))
        return out

    def in_degree(self, node_id):
        return sum(1 for e in self.data["edges"] if e["predecessor_id"] == node_id)

    def stats(self):
        nodes = self.live_nodes()
        by_depth = {}
        by_status = {}
        for n in nodes:
            by_depth[n["depth"]] = by_depth.get(n["depth"], 0) + 1
            by_status[n["status"]] = by_status.get(n["status"], 0) + 1
        return {
            "nodes_total": len(self.data["nodes"]),
            "nodes_live": len(nodes),
            "nodes_merged_away": len(self.data["nodes"]) - len(nodes),
            "edges": len(self.data["edges"]),
            "merges": len([m for m in self.data["merge_log"] if m.get("into_id")]),
            "by_depth": by_depth,
            "by_status": by_status,
            "expansions_done": self.data["run_state"]["expansions_done"],
            "raw_candidates_seen": self.data["run_state"]["raw_candidates_seen"],
            "rejected_total": len(self.data["run_state"]["rejected"]),
            "frontier": [n["id"] for n in self.frontier()],
            "node_budget_used": len(nodes),
            "node_budget": self.data["config"].get("node_budget"),
        }
