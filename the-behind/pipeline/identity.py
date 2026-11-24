"""Node identity resolution for The Behind 01 (DESIGN.md §4.5).

Decides whether two candidate/node identity cards refer to the same
advance. Layered signals, never the name string alone:

  1. Canonical ID match (Wikidata QID, else normalized reference title).
  2. Alias & normalization match against a node's alias table.
  3. Embedding similarity over the identity-card text, banded:
       >= 0.92  strong same-node candidate (auto-merge if no veto)
       0.80-0.92 gray zone -> exported to the judge queue
       <  0.80  treated as different
  4. Hard vetoes (override any similarity): year gap > 25 years,
     type mismatch.

Gray-zone pairs are NOT decided here. They are exported as a judge queue
(JSON) for the executing agent to adjudicate SAME / DIFFERENT / SUBTYPE;
decisions are ingested back by `apply_judgments`.

Embedder: pluggable. If `sentence-transformers` is installed, the
all-MiniLM-L6-v2 model is used (semantic embeddings; the §4.5 bands are
calibrated for this). Otherwise a stdlib TF-IDF embedder over word +
character n-grams of the identity card is used. The fallback always
works, but its cosine scale runs lower than a semantic embedder's, so
with the fallback most non-obvious pairs land in "different" rather
than the gray zone — the designed precision-over-recall bias. The
embedder in use is recorded in the resolution output.
"""

import math
import re
import unicodedata
from collections import Counter

BAND_STRONG = 0.92
BAND_GRAY = 0.80
YEAR_VETO_GAP = 25

_STOP = {"the", "a", "an", "of", "for", "in", "on", "and", "to"}


def normalize_name(name):
    """Lowercase, strip accents/punctuation, collapse word order."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    tokens = [t for t in s.split() if t not in _STOP]
    return " ".join(sorted(tokens))


def card_text(card):
    """The text that represents an identity card for embedding."""
    parts = [card.get("name", "")]
    parts += list(card.get("aliases", []) or [])
    if card.get("definition"):
        parts.append(card["definition"])
    if card.get("domain"):
        parts.append(card["domain"])
    return ". ".join(p for p in parts if p)


# ---------------- embedders ----------------

class TFIDFEmbedder:
    """Stdlib fallback: TF-IDF over word unigrams/bigrams + char 3-5 grams."""

    name = "tfidf-fallback"

    def __init__(self):
        self.vocab = {}
        self.idf = []

    def _features(self, text):
        t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
        words = re.findall(r"[a-z0-9]+", t)
        feats = list(words)
        feats += [" ".join(words[i:i + 2]) for i in range(len(words) - 1)]
        compact = " ".join(words)
        for n in (3, 4, 5):
            feats += [compact[i:i + n] for i in range(len(compact) - n + 1)]
        return feats

    def fit_transform(self, texts):
        docs = [Counter(self._features(t)) for t in texts]
        df = Counter()
        for d in docs:
            for term in d:
                df[term] += 1
        terms = sorted(df)
        self.vocab = {t: i for i, t in enumerate(terms)}
        n_docs = max(len(docs), 1)
        self.idf = [math.log((1 + n_docs) / (1 + df[t])) + 1.0 for t in terms]
        return [self._vec(d) for d in docs]

    def _vec(self, counter):
        v = [0.0] * len(self.vocab)
        for term, c in counter.items():
            i = self.vocab.get(term)
            if i is not None:
                v[i] = (1.0 + math.log(c)) * self.idf[i]
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]

    def transform(self, texts):
        return [self._vec(Counter(self._features(t))) for t in texts]


class MiniLMEmbedder:
    name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def fit_transform(self, texts):
        return [list(map(float, v)) for v in self.model.encode(texts, normalize_embeddings=True)]

    def transform(self, texts):
        return self.fit_transform(texts)


def get_embedder():
    try:
        return MiniLMEmbedder()
    except Exception:
        return TFIDFEmbedder()


def cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


# ---------------- vetoes & classification ----------------

def veto(a, b):
    """Return a veto reason string, or None. a/b are identity cards."""
    ya, yb = a.get("year"), b.get("year")
    if ya is not None and yb is not None and abs(int(ya) - int(yb)) > YEAR_VETO_GAP:
        return f"year gap {abs(int(ya) - int(yb))} > {YEAR_VETO_GAP}"
    ta, tb = a.get("type"), b.get("type")
    if ta and tb and ta != "other" and tb != "other" and ta != tb:
        return f"type mismatch {ta} vs {tb}"
    return None


def _name_containment(a_name, b_name):
    """True when one normalized name's token set strictly contains the
    other's ('transformer' vs 'transformer architecture'). Such pairs are
    classic SAME-vs-SUBTYPE ambiguity, so they are forced into the gray
    zone for the judge even when embedding similarity is low."""
    ta = set(normalize_name(a_name).split())
    tb = set(normalize_name(b_name).split())
    if not ta or not tb or ta == tb:
        return False
    return ta < tb or tb < ta


def classify_pair(sim, veto_reason, name_containment=False):
    if veto_reason:
        return "different"
    if sim >= BAND_STRONG:
        return "same"
    if sim >= BAND_GRAY or name_containment:
        return "gray"
    return "different"


# ---------------- resolution ----------------

def _card_from_candidate(c):
    return {
        "name": c.get("name", ""),
        "aliases": c.get("aliases", []) or [],
        "year": c.get("year"),
        "domain": c.get("domain", ""),
        "type": c.get("type", "other"),
        "definition": c.get("definition") or c.get("causal_claim", ""),
        "wikidata": c.get("wikidata"),
    }


def _card_from_node(n):
    return {
        "name": n.get("name", ""),
        "aliases": n.get("aliases", []) or [],
        "year": n.get("year"),
        "domain": n.get("domain", ""),
        "type": n.get("type", "other"),
        "definition": n.get("definition", ""),
        "wikidata": n.get("wikidata"),
    }


def resolve(candidates, existing_nodes, parent_year=None):
    """Resolve a batch of scout candidates against each other and against
    existing graph nodes.

    Returns a resolution dict:
    {
      "embedder": name,
      "distinct": [ {cand_id, representative candidate, members: [raw idx],
                     matched_node_id: str|null} ],
      "judge_queue": [ {pair_id, kind: "cand-cand"|"cand-node", a, b,
                        similarity, note} ],
      "auto_merges": [ {members, into, signals, scores} ],
      "dropped": [ {candidate, reason} ]
    }
    Pairs in the judge queue keep both sides separate until judgments are
    applied; `distinct` therefore lists gray-zone candidates individually
    with a "pending_judge" flag on the affected entries.
    """
    embedder = get_embedder()
    dropped = []
    kept = []
    for i, c in enumerate(candidates):
        if parent_year is not None and c.get("year") is not None and int(c["year"]) >= int(parent_year):
            dropped.append({"candidate": c, "reason": f"dated on/after parent year {parent_year}"})
        else:
            kept.append((i, c))

    cards = [_card_from_candidate(c) for _, c in kept]
    node_cards = [_card_from_node(n) for n in existing_nodes]
    all_texts = [card_text(c) for c in cards] + [card_text(c) for c in node_cards]
    vecs = embedder.fit_transform(all_texts) if all_texts else []
    cand_vecs = vecs[:len(cards)]
    node_vecs = vecs[len(cards):]

    # union-find over kept candidates
    parent = list(range(len(kept)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    judge_queue = []
    auto_merges = []
    gray_pairs = set()

    def pair_key(kind, a, b):
        return f"{kind}:{a}:{b}"

    # candidate vs existing node
    matched_node = {}
    for ci, card in enumerate(cards):
        best = None
        for ni, ncard in enumerate(node_cards):
            node = existing_nodes[ni]
            # signal 1: canonical ID
            if card.get("wikidata") and ncard.get("wikidata") and card["wikidata"] == ncard["wikidata"]:
                matched_node[ci] = (node["id"], "wikidata", 1.0)
                best = "matched"
                break
            # signal 2: alias / normalized name. Per §4.5 the signals apply
            # in order: an exact name match with the SAME year settles
            # identity here and is not blocked by the signal-4 type veto
            # (scout type labels for one milestone can disagree); a year
            # mismatch still blocks the name-only match.
            names = {normalize_name(ncard["name"])} | {normalize_name(a) for a in ncard["aliases"]}
            if normalize_name(card["name"]) in names:
                v = veto(card, ncard)
                same_year = (card.get("year") is not None and ncard.get("year") is not None
                             and int(card["year"]) == int(ncard["year"]))
                if v is None or (same_year and v.startswith("type mismatch")):
                    matched_node[ci] = (node["id"], "alias", 1.0)
                    best = "matched"
                    break
            sim = cosine(cand_vecs[ci], node_vecs[ni])
            v = veto(card, ncard)
            cls = classify_pair(sim, v, _name_containment(card["name"], ncard["name"]))
            if cls == "same":
                matched_node[ci] = (node["id"], "embedding", round(sim, 4))
                best = "matched"
                break
            if cls == "gray":
                judge_queue.append({
                    "pair_id": pair_key("cand-node", kept[ci][0], node["id"]),
                    "kind": "cand-node",
                    "a": {"cand_index": kept[ci][0], "card": card},
                    "b": {"node_id": node["id"], "card": ncard},
                    "similarity": round(sim, 4),
                    "note": "gray-zone band 0.80-0.92; adjudicate SAME / DIFFERENT / SUBTYPE",
                })
                gray_pairs.add(kept[ci][0])
        _ = best

    # candidate vs candidate
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            if find(i) == find(j):
                continue
            a, b = cards[i], cards[j]
            if a.get("wikidata") and b.get("wikidata") and a["wikidata"] == b["wikidata"]:
                union(i, j)
                auto_merges.append({"members": [kept[i][0], kept[j][0]], "signals": ["wikidata"], "scores": {"cosine": 1.0}})
                continue
            # signal 2 (alias tier): exact normalized-name match with the
            # same year settles identity before vetoes (§4.5 order); the
            # type veto alone must not split one named, dated milestone
            # whose scout records merely carry different type labels.
            _v = veto(a, b)
            _same_year = (a.get("year") is not None and b.get("year") is not None
                          and int(a["year"]) == int(b["year"]))
            if normalize_name(a["name"]) == normalize_name(b["name"]) and (
                    _v is None or (_same_year and _v.startswith("type mismatch"))):
                union(i, j)
                auto_merges.append({"members": [kept[i][0], kept[j][0]], "signals": ["alias"], "scores": {"cosine": 1.0}})
                continue
            sim = cosine(cand_vecs[i], cand_vecs[j])
            cls = classify_pair(sim, veto(a, b), _name_containment(a["name"], b["name"]))
            if cls == "same":
                union(i, j)
                auto_merges.append({"members": [kept[i][0], kept[j][0]], "signals": ["embedding"], "scores": {"cosine": round(sim, 4)}})
            elif cls == "gray":
                judge_queue.append({
                    "pair_id": pair_key("cand-cand", kept[i][0], kept[j][0]),
                    "kind": "cand-cand",
                    "a": {"cand_index": kept[i][0], "card": a},
                    "b": {"cand_index": kept[j][0], "card": b},
                    "similarity": round(sim, 4),
                    "note": "gray-zone band 0.80-0.92; adjudicate SAME / DIFFERENT / SUBTYPE",
                })
                gray_pairs.add(kept[i][0])
                gray_pairs.add(kept[j][0])

    # build distinct list from union-find groups
    groups = {}
    for ci in range(len(kept)):
        groups.setdefault(find(ci), []).append(ci)
    distinct = []
    used_cand_ids = set()
    for root, members in groups.items():
        rep_ci = members[0]
        rep = kept[rep_ci][1]
        cand_id = _cand_id(rep)
        # guard: two clusters must never share a cand_id (slug collision
        # would silently alias them in every downstream lookup)
        if cand_id in used_cand_ids:
            k = 2
            while f"{cand_id}-{k}" in used_cand_ids:
                k += 1
            cand_id = f"{cand_id}-{k}"
        used_cand_ids.add(cand_id)
        entry = {
            "cand_id": cand_id,
            "candidate": rep,
            "members": [kept[m][0] for m in members],
            "member_names": [kept[m][1].get("name") for m in members],
            "matched_node_id": matched_node.get(rep_ci, (None,))[0] if rep_ci in matched_node else None,
            "pending_judge": any(kept[m][0] in gray_pairs for m in members),
        }
        distinct.append(entry)

    return {
        "embedder": embedder.name,
        "distinct": distinct,
        "judge_queue": judge_queue,
        "auto_merges": auto_merges,
        "dropped": dropped,
    }


def _cand_id(candidate):
    from graph import slugify
    return slugify(candidate.get("name", "candidate"), candidate.get("year"))
