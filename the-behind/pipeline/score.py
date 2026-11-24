"""Deterministic gate + ranking for The Behind 01 (DESIGN.md §5).

Input: verdicts for one candidate in relation to one parent node:
  {"Q1": {"verdict": "pass"|"partial"|"fail", "evidence": str,
          "source": str, "falsification": str}, ..., "Q12": {...}}

Rules:
  - Evidence discipline: a "pass" with no evidence text is downgraded to
    "partial" (no evidence, no pass).
  - Gate: (Q1 == pass OR Q2 == pass) AND Q3 != fail.
  - Score: across the nine non-gate questions (Q4..Q12):
    pass = 1.0, partial = 0.5, fail = 0.0. (Q3 contributes nothing to the
    score; it is gate-only. Q1/Q2 contribute nothing either; they are
    gate-only. Ranking therefore reflects the remaining nine dimensions,
    exactly as DESIGN.md §5 states: "ranked by their score across the
    remaining nine questions".)
  - Rank survivors by score desc, tie-break by number of passes, then name.
  - Cap at N (config survivor_cap, overridable per expansion).
"""

QUESTIONS = [f"Q{i}" for i in range(1, 13)]
GATE_QUESTIONS = {"Q1", "Q2", "Q3"}
SCORED_QUESTIONS = [q for q in QUESTIONS if q not in GATE_QUESTIONS]
POINTS = {"pass": 1.0, "partial": 0.5, "fail": 0.0}


def normalize_verdicts(verdicts):
    """Return a cleaned verdicts dict with evidence discipline applied."""
    out = {}
    for q in QUESTIONS:
        v = (verdicts or {}).get(q) or {}
        verdict = str(v.get("verdict", "fail")).lower()
        if verdict not in POINTS:
            verdict = "fail"
        evidence = (v.get("evidence") or "").strip()
        if verdict == "pass" and not evidence:
            verdict = "partial"  # no evidence, no pass
        out[q] = {
            "verdict": verdict,
            "evidence": evidence,
            "source": v.get("source", "") or "",
            "falsification": v.get("falsification", "") or "",
        }
    return out


def gate_and_score(verdicts):
    """Apply the §5 gate and compute the ranking score."""
    v = normalize_verdicts(verdicts)
    q1_or_q2 = v["Q1"]["verdict"] == "pass" or v["Q2"]["verdict"] == "pass"
    q3_ok = v["Q3"]["verdict"] != "fail"
    score = sum(POINTS[v[q]["verdict"]] for q in SCORED_QUESTIONS)
    passes = sum(1 for q in SCORED_QUESTIONS if v[q]["verdict"] == "pass")
    return {
        "verdicts": v,
        "gate": {"q1_or_q2": q1_or_q2, "q3_ok": q3_ok, "passed": bool(q1_or_q2 and q3_ok)},
        "score": score,
        "scored_passes": passes,
    }


def rejection_reason(result):
    g = result["gate"]
    if not g["q1_or_q2"]:
        return "gate: neither Q1 nor Q2 passes (no impossibility flip, no generativity)"
    if not g["q3_ok"]:
        return "gate: Q3 clear fail (demonstrably substitutable)"
    return "below cap after ranking"


def rank_candidates(evaluations, cap):
    """evaluations: list of {"cand_id", "name", "verdicts", ...}.
    Returns (survivors, rejected) with gate/score attached, deterministic."""
    scored = []
    for ev in evaluations:
        r = gate_and_score(ev.get("verdicts"))
        scored.append({**ev, "verdicts": r["verdicts"], "gate": r["gate"],
                       "score": r["score"], "scored_passes": r["scored_passes"]})
    passed = [s for s in scored if s["gate"]["passed"]]
    failed = [s for s in scored if not s["gate"]["passed"]]
    passed.sort(key=lambda s: (-s["score"], -s["scored_passes"], s.get("name", "")))
    survivors = passed[:cap]
    over_cap = passed[cap:]
    rejected = []
    for s in failed:
        rejected.append({**s, "reason": rejection_reason(s)})
    for s in over_cap:
        rejected.append({**s, "reason": f"below cap {cap} after ranking (score {s['score']})"})
    return survivors, rejected
