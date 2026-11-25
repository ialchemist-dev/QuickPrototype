#!/usr/bin/env python3
"""CLI for The Behind 01 recursive milestone pipeline.

This is the deterministic half of the system. The executing agent does
the judgment work (scouting, evaluating, judging, verifying) by
following RUNBOOK.md; this CLI manages the graph state around it.

Commands (all take --graph PATH):
  init               create graph.json with the root node
  add-candidates     register a scout batch for a parent node
  resolve            run identity resolution (DESIGN.md §4.5); writes the
                     judge queue next to the graph file
  apply-judgments    ingest SAME / DIFFERENT / SUBTYPE decisions
  apply-verdicts     apply gates (score.py), insert survivors, record
                     rejections, advance the frontier
  apply-verification ingest adversarial verifier outcomes
  status             print run status and the frontier (best-first)
  render             write the interactive HTML page

Every command prints a JSON summary to stdout and checkpoints the graph.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import graph as graph_mod
import identity
import render as render_mod
import score as score_mod

PROFILES = {
    "full": {
        "profile": "full", "raw_target": 140, "survivor_cap": 20,
        "depth_cap": 10, "node_budget": 2000, "min_gate_survivors": 5,
        "year_floor": 1500,
    },
    "smoke": {
        "profile": "smoke", "raw_target": 60, "survivor_cap": 8,
        "depth_cap": 2, "node_budget": 60, "min_gate_survivors": 2,
        "year_floor": 1500,
    },
}

ROOT = {
    "name": "The modern AI agent",
    "year": 2023,
    "domain": "artificial intelligence",
    "type": "other",
    "definition": "A software system built on a large language model that perceives its environment, reasons over open-ended tasks, and acts through tools in a loop.",
    "bottleneck": "Before the modern AI agent, machines could not perceive, reason over, and act on open-ended tasks in a loop, because no model could flexibly convert between language, perception and action, and there was no practical way to train or steer such a model.",
    "prior_state": "Chatbots and task-specific ML systems: models could complete text or classify inputs, but could not follow open-ended instructions reliably, use external tools, or chain reasoning and action toward a goal.",
    "leap": "Instruction-following LLMs wrapped in a reason-act loop with tool use (2022-23: ChatGPT, ReAct, function calling) turned a text completer into a general task executor — a capability jump, not an incremental accuracy gain.",
    "sources": [],
}


def load(path):
    g = graph_mod.Graph(path)
    if g.data is None:
        print(json.dumps({"error": f"graph file not found: {path} (run init first)"}))
        sys.exit(2)
    return g


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def cmd_init(args):
    if os.path.exists(args.graph) and not args.force:
        out({"error": f"{args.graph} exists; pass --force to overwrite"})
        return
    config = dict(PROFILES[args.profile])
    g = graph_mod.Graph.create(args.graph, config, ROOT)
    out({"ok": True, "graph": args.graph, "profile": args.profile,
         "root_id": next(iter(g.data["nodes"])), "config": config})


def _expansion(g, parent_id):
    return g.data["expansions"].setdefault(parent_id, {
        "raw_candidates": [], "resolution": None, "judge_queue": [],
        "judgments_applied": False, "stage": "new",
    })


def cmd_add_candidates(args):
    g = load(args.graph)
    parent = g.get_node(args.parent)
    if parent is None:
        out({"error": f"parent node not found: {args.parent}"})
        return
    with open(args.file, encoding="utf-8") as f:
        batch = json.load(f)
    if not isinstance(batch, list):
        out({"error": "candidates file must be a JSON array"})
        return
    exp = _expansion(g, parent["id"])
    exp["raw_candidates"].extend(batch)
    exp["stage"] = "scouted"
    g.data["run_state"]["raw_candidates_seen"] += len(batch)
    g.save()
    out({"ok": True, "parent": parent["id"], "added": len(batch),
         "raw_total_for_parent": len(exp["raw_candidates"])})


def cmd_resolve(args):
    g = load(args.graph)
    parent = g.get_node(args.parent)
    if parent is None:
        out({"error": f"parent node not found: {args.parent}"})
        return
    exp = _expansion(g, parent["id"])
    # Pre-filter (§4.4): exact repeats of candidates already rejected for
    # this parent are dropped before resolution — but never silently:
    # every drop is recorded in the resolution and echoed on stdout.
    # A candidate the scout marks "rehearing": true (a retro-sweep
    # re-proposal, RUNBOOK §9) is NOT dropped: it proceeds through
    # resolution carrying a rehearing_of annotation naming the original
    # rejection it re-opens, so the new judgment supersedes or confirms
    # the old one on the record. (Rejections are appended chronologically,
    # so the first record per name is the original rejection.)
    prior_rejections = {}
    for r in g.data["run_state"]["rejected"]:
        if r["parent_id"] == parent["id"]:
            prior_rejections.setdefault(identity.normalize_name(r["name"]), r)
    cands, prefiltered = [], []
    for c in exp["raw_candidates"]:
        prior = prior_rejections.get(identity.normalize_name(c.get("name", "")))
        if prior is None:
            cands.append(c)
        elif c.get("rehearing"):
            annotation = {
                "parent_id": prior["parent_id"],
                "name": prior["name"],
                "reason": prior.get("reason", ""),
                "at": prior.get("at"),
            }
            if prior.get("mediated_via"):
                annotation["mediated_via"] = prior["mediated_via"]
            c["rehearing_of"] = annotation
            cands.append(c)
        else:
            prefiltered.append({
                "candidate": c.get("name", ""),
                "parent_id": parent["id"],
                "matched_rejection": {
                    "name": prior["name"],
                    "reason": prior.get("reason", ""),
                    "at": prior.get("at"),
                },
                "reason": "exact repeat of a prior rejection for this parent "
                          "(§4.4 pre-filter); not submitted as a retro-sweep "
                          "re-hearing",
            })
    others = [n for n in g.live_nodes() if n["id"] != parent["id"]]
    res = identity.resolve(cands, others, parent_year=parent.get("year"))
    res["prefiltered"] = prefiltered
    # a rehearing annotation must survive candidate merging: if a merged
    # group's representative does not carry it, inherit it from a member
    for d in res["distinct"]:
        if not d["candidate"].get("rehearing_of"):
            for mi in d["members"]:
                if cands[mi].get("rehearing_of"):
                    d["candidate"]["rehearing_of"] = cands[mi]["rehearing_of"]
                    break
    rehearings = [c.get("name", "") for c in cands if c.get("rehearing_of")]
    exp["resolution"] = res
    exp["judge_queue"] = res["judge_queue"]
    exp["judgments_applied"] = len(res["judge_queue"]) == 0
    exp["stage"] = "resolved"
    g.save()
    qpath = os.path.join(os.path.dirname(os.path.abspath(args.graph)),
                         f"judge_queue_{parent['id']}.json")
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(res["judge_queue"], f, ensure_ascii=False, indent=1)
    out({"ok": True, "parent": parent["id"], "embedder": res["embedder"],
         "raw": len(exp["raw_candidates"]), "dropped": len(res["dropped"]),
         "prefiltered": len(prefiltered), "prefiltered_records": prefiltered,
         "rehearings": rehearings,
         "distinct": len(res["distinct"]),
         "matched_existing": sum(1 for d in res["distinct"] if d["matched_node_id"]),
         "auto_merges": len(res["auto_merges"]),
         "judge_queue": len(res["judge_queue"]), "judge_queue_file": qpath})


def cmd_apply_judgments(args):
    g = load(args.graph)
    parent = g.get_node(args.parent)
    exp = _expansion(g, parent["id"])
    res = exp.get("resolution")
    if res is None:
        out({"error": "no resolution for this parent; run resolve first"})
        return
    with open(args.file, encoding="utf-8") as f:
        judgments = json.load(f).get("judgments", [])
    queue = {q["pair_id"]: q for q in exp["judge_queue"]}
    applied, unknown = 0, []
    # index raw candidates by their original index within the expansion
    raw = exp["raw_candidates"]
    for j in judgments:
        q = queue.get(j["pair_id"])
        if q is None:
            unknown.append(j["pair_id"])
            continue
        decision = str(j.get("decision", "")).upper()
        reason = j.get("reason", "")
        if q["kind"] == "cand-node" and decision == "SAME":
            node_id = q["b"]["node_id"]
            ci = q["a"]["cand_index"]
            for d in res["distinct"]:
                if ci in d["members"]:
                    d["matched_node_id"] = node_id
            g.data["merge_log"].append({
                "at": graph_mod.now_iso(), "from_id": f"cand:{raw[ci].get('name')}",
                "into_id": node_id, "signals": ["judge"],
                "scores": {"cosine": q["similarity"]}, "reason": reason})
        elif q["kind"] == "cand-cand" and decision == "SAME":
            ai, bi = q["a"]["cand_index"], q["b"]["cand_index"]
            da = next((d for d in res["distinct"] if ai in d["members"]), None)
            db = next((d for d in res["distinct"] if bi in d["members"]), None)
            if da is not None and db is not None and da is not db:
                da["members"] = sorted(set(da["members"]) | set(db["members"]))
                da["member_names"] = sorted(set(da["member_names"]) | set(db["member_names"]))
                if db.get("matched_node_id"):
                    da["matched_node_id"] = db["matched_node_id"]
                res["distinct"].remove(db)
            g.data["merge_log"].append({
                "at": graph_mod.now_iso(), "from_id": f"cand:{raw[bi].get('name')}",
                "into_id": f"cand:{raw[ai].get('name')}", "signals": ["judge"],
                "scores": {"cosine": q["similarity"]}, "reason": reason})
        elif decision == "SUBTYPE":
            for side in ("a", "b"):
                ci = q[side].get("cand_index")
                if ci is not None:
                    for d in res["distinct"]:
                        if ci in d["members"]:
                            d.setdefault("notes", []).append(
                                f"judge SUBTYPE in pair {q['pair_id']}: {reason}")
        # DIFFERENT: nothing to merge; flags cleared below.
        applied += 1
    for d in res["distinct"]:
        d["pending_judge"] = False
    exp["judgments_applied"] = True
    exp["stage"] = "judged"
    g.save()
    out({"ok": True, "parent": parent["id"], "applied": applied,
         "unknown_pair_ids": unknown, "distinct_now": len(res["distinct"])})


def cmd_apply_verdicts(args):
    g = load(args.graph)
    parent = g.get_node(args.parent)
    exp = _expansion(g, parent["id"])
    res = exp.get("resolution")
    if res is None:
        out({"error": "no resolution for this parent; run resolve first"})
        return
    with open(args.file, encoding="utf-8") as f:
        payload = json.load(f)
    evaluations = payload.get("evaluations", [])
    distinct = {d["cand_id"]: d for d in res["distinct"]}
    for ev in evaluations:
        d = distinct.get(ev.get("cand_id"))
        if d is None:
            out({"error": f"unknown cand_id in verdicts: {ev.get('cand_id')}"})
            return
        cand = d["candidate"]
        ev.setdefault("name", cand.get("name"))
        ev["_distinct"] = d
    cap = args.cap if args.cap is not None else g.data["config"].get("survivor_cap", 20)
    survivors, rejected = score_mod.rank_candidates(evaluations, cap)
    created, linked = [], []
    rehearings = []
    for s in survivors:
        d = s["_distinct"]
        cand = d["candidate"]
        sources = [{"title": cand.get("source_title", ""), "url": cand.get("source_url", "")}] \
            if cand.get("source_url") else []
        if d.get("matched_node_id"):
            node = g.get_node(d["matched_node_id"])
            for alias in d["member_names"]:
                if alias != node["name"] and alias not in node["aliases"]:
                    node["aliases"].append(alias)
            for src in sources:
                if src not in node["sources"]:
                    node["sources"].append(src)
            linked.append(node["id"])
        else:
            node = g.add_node({
                "name": s.get("name") or cand.get("name"),
                "aliases": [n for n in d["member_names"] if n != (s.get("name") or cand.get("name"))],
                "year": s.get("year", cand.get("year")),
                "domain": s.get("domain", cand.get("domain", "")),
                "type": s.get("type", cand.get("type", "other")),
                "definition": s.get("definition", cand.get("definition") or cand.get("causal_claim", "")),
                "bottleneck": s.get("bottleneck", ""),
                "leap": s.get("node_leap", ""),
                "prior_state": s.get("node_prior_state", ""),
                "depth": parent["depth"] + 1,
                "priority": s["score"],
                "sources": sources,
            })
            created.append(node["id"])
        rehearing_of = cand.get("rehearing_of")
        g.add_edge(node["id"], parent["id"], s["verdicts"], s["score"], s["gate"],
                   leap=s.get("leap"), directness=s.get("directness"),
                   rehearing_of=rehearing_of)
        if rehearing_of:
            rehearings.append({"name": s.get("name") or cand.get("name"),
                               "outcome": "admitted", "node_id": node["id"],
                               "rehearing_of": rehearing_of})
    mediated = []
    for r in rejected:
        rec = {
            "parent_id": parent["id"], "name": r.get("name", ""),
            "reason": r["reason"], "at": graph_mod.now_iso(),
        }
        med = (r.get("directness") or {}).get("mediator")
        if med:
            rec["mediated_via"] = med
            mediated.append({"name": r.get("name", ""), "mediated_via": med})
        rehearing_of = ((r.get("_distinct") or {}).get("candidate") or {}).get("rehearing_of")
        if rehearing_of:
            rec["rehearing_of"] = rehearing_of
            rehearings.append({"name": r.get("name", ""), "outcome": "rejected",
                               "rehearing_of": rehearing_of})
        g.data["run_state"]["rejected"].append(rec)
    parent_node = g.data["nodes"][parent["id"]]
    parent_node["expanded"] = True
    g.data["run_state"]["expansions_done"] += 1
    exp["stage"] = "evaluated"
    g.save()
    st = g.stats()
    out({"ok": True, "parent": parent["id"], "cap": cap,
         "evaluated": len(evaluations), "survivors": len(survivors),
         "created_nodes": created, "linked_existing": linked,
         "rejected": len(rejected), "mediated_rejections": mediated,
         "rehearings": rehearings,
         "node_budget_used": st["node_budget_used"], "node_budget": st["node_budget"],
         "frontier_next": st["frontier"][:5]})


def cmd_show_distinct(args):
    g = load(args.graph)
    parent = g.get_node(args.parent)
    exp = _expansion(g, parent["id"])
    res = exp.get("resolution")
    if res is None:
        out({"error": "no resolution for this parent; run resolve first"})
        return
    out({"parent": parent["id"], "embedder": res["embedder"],
         "distinct": [{"cand_id": d["cand_id"], "name": d["candidate"].get("name"),
                       "year": d["candidate"].get("year"),
                       "members": d["member_names"],
                       "matched_node_id": d["matched_node_id"],
                       "pending_judge": d["pending_judge"],
                       "rehearing_of": d["candidate"].get("rehearing_of")}
                      for d in res["distinct"]]})


def cmd_apply_verification(args):
    g = load(args.graph)
    with open(args.file, encoding="utf-8") as f:
        items = json.load(f).get("verifications", [])
    applied = []
    mediation_actions = []
    for it in items:
        node = g.get_node(it["node_id"])
        if node is None:
            continue
        outcome = it.get("outcome", "provisional")
        node["verification"] = {"outcome": outcome, "notes": it.get("notes", ""),
                                "at": graph_mod.now_iso()}
        if outcome == "verified":
            node["status"] = "verified"
        elif outcome == "killed":
            node["status"] = "provisional"
            node["dead"] = True
        # v3 mediation attack (§6.4 attack 4): the verifier may name an
        # intermediate M for an edge that admitted this node. A
        # "kill_edge" removes the edge and logs the rejection as
        # mediated_via: M; a "downgrade" keeps the edge, records the
        # challenge on it, and caps the node at provisional.
        med = it.get("mediation") or {}
        mediator = str(med.get("mediator") or "").strip()
        if mediator:
            action = str(med.get("action", "downgrade")).lower()
            succ = med.get("successor_id")
            targets = [e for e in g.data["edges"]
                       if e["predecessor_id"] == node["id"]
                       and (succ is None or e["successor_id"] == succ)]
            for e in targets:
                e.setdefault("mediation_challenges", []).append(
                    {"mediator": mediator, "action": action,
                     "at": graph_mod.now_iso()})
                if action == "kill_edge":
                    g.data["edges"].remove(e)
                    g.data["run_state"]["rejected"].append({
                        "parent_id": e["successor_id"], "name": node["name"],
                        "reason": f"mediated_via: {mediator}",
                        "mediated_via": mediator, "via_verifier": True,
                        "at": graph_mod.now_iso()})
                    mediation_actions.append({
                        "node": node["id"], "successor": e["successor_id"],
                        "mediator": mediator, "action": "kill_edge"})
                else:
                    mediation_actions.append({
                        "node": node["id"], "successor": e["successor_id"],
                        "mediator": mediator, "action": "downgrade"})
            if node["status"] == "verified":
                node["status"] = "provisional"  # a live mediation challenge caps verification
            if action == "kill_edge":
                remaining = [e for e in g.data["edges"]
                             if e["predecessor_id"] == node["id"]]
                if not remaining and node["depth"] > 0:
                    # orphaned by the mediation kill: out of the frontier,
                    # still visible in the graph and the render.
                    node["dead"] = True
        applied.append(node["id"])
    g.save()
    out({"ok": True, "applied": applied, "mediation_actions": mediation_actions})


def cmd_status(args):
    g = load(args.graph)
    st = g.stats()
    st["config"] = g.data["config"]
    st["frontier_detail"] = [
        {"id": n["id"], "name": n["name"], "year": n["year"],
         "depth": n["depth"], "priority": n["priority"], "status": n["status"]}
        for n in g.frontier()
    ]
    st["expansions"] = {pid: {"stage": e["stage"], "raw": len(e["raw_candidates"])}
                        for pid, e in g.data["expansions"].items()}
    out(st)


def cmd_render(args):
    g = load(args.graph)
    html = render_mod.render(g.data)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    out({"ok": True, "out": args.out, "bytes": len(html),
         "nodes": len([n for n in g.live_nodes()]), "edges": len(g.data["edges"])})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        sp = sub.add_parser(name)
        sp.add_argument("--graph", default="graph.json")
        sp.set_defaults(fn=fn)
        return sp

    sp = add("init", cmd_init)
    sp.add_argument("--profile", choices=list(PROFILES), default="full")
    sp.add_argument("--force", action="store_true")

    for name, fn in (("add-candidates", cmd_add_candidates), ("resolve", cmd_resolve),
                     ("apply-judgments", cmd_apply_judgments),
                     ("show-distinct", cmd_show_distinct)):
        sp = add(name, fn)
        sp.add_argument("--parent", required=True)
        if name in ("add-candidates", "apply-judgments"):
            sp.add_argument("--file", required=True)

    sp = add("apply-verdicts", cmd_apply_verdicts)
    sp.add_argument("--parent", required=True)
    sp.add_argument("--file", required=True)
    sp.add_argument("--cap", type=int, default=None)

    sp = add("apply-verification", cmd_apply_verification)
    sp.add_argument("--file", required=True)

    add("status", cmd_status)

    sp = add("render", cmd_render)
    sp.add_argument("--out", default="index.html")

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
