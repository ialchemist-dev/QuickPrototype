# RUNBOOK — The Behind 01: Recursive Milestone Pipeline

**Design v4 · 2026-11-24.** (v3 added the directness gate, the leap
record, the re-aimed scout, and the verifier's mediation attack, after
the owner found gradient descent sitting at depth 1 in the v2 smoke
graph. v3.1 added the Hardware & devices and Data scout lenses, the
"substrate is not a rejection class" gate guidance, and the one-time
retro-sweep protocol (§9), after the owner found run-01's graph
contained no hardware or data milestones at all. v4 replaced the
accreted lens list with a derived framework — 11 enabler kinds × 10
enabling relations → 23 lenses in 6 families + 2 meta passes (§6.1) —
after the owner rejected patching lenses one gap at a time and
required the scout's questions to be exhaustive by construction; it
also raised the FULL `raw_target` to 140, added the per-lens floor
with dry notes, admitted institutional enablers as nodes, and
extended the retro-sweep (§9). See the changelog in `DESIGN.md`.)

**Read only this file and you can execute the entire pipeline.** It is
self-contained: purpose, setup, configuration, the graph format, the
step-by-step loop, every prompt verbatim, exact commands, the
checkpoint/resume protocol, stop conditions, rendering, and
troubleshooting. Background and rationale live in `DESIGN.md`; you do
not need it to run.

---

## 0. Purpose (6 lines)

1. Trace the breakthroughs that made the modern AI agent possible, backwards through history, as a merged graph (DAG), not a tree.
2. Start from one root node; repeatedly expand the best unexpanded node: scout ≈140 earlier **proximate** candidate advances (23 lenses + 2 meta passes; per-lens floor ≥3 or a dry note), resolve their identities, interrogate each with 12 fixed questions plus the directness test, prune by fixed gates to a capped set of survivors.
3. Each survivor becomes a node with a "bottleneck sentence"; edges read "enabled by" and mean **direct enabler of the child's leap** — never a mediated ancestor. The same advance reached from many children is one node — convergence is the point.
4. Every node is a leap: a discontinuous jump over the state of the art immediately before it. Time is a first-class dimension; each step back moves one leap, not one era.
5. Survivors face an adversarial verifier (multiples test, date check, mediation attack) and are marked `verified` or stay `provisional`.
6. At any point, render the graph to a single interactive HTML page.

Your role as the executing agent: you do the judgment work (scouting,
evaluating, judging identity pairs, verifying). The CLI in `pipeline/`
does all bookkeeping deterministically. **Never edit `graph.json` by
hand** — every state change goes through the CLI, which checkpoints
after every mutation.

---

## 1. Prerequisites and setup

- Python 3.10+ (developed on 3.12). The pipeline is **stdlib-only** and
  runs with no installs.
- Optional: `pip install sentence-transformers` enables the semantic
  embedder (all-MiniLM-L6-v2) for identity resolution. Without it, a
  TF-IDF fallback is used automatically (recorded in every resolution
  output). The fallback is safe: it errs toward "different" (§4.5's
  precision-over-recall bias), and name-containment pairs are still
  routed to you as judge.
- Web search access (for the scout and verifier steps).
- Working directory for everything below: this folder, `the-behind/`.
- CLI entry point: `python3 pipeline/pipeline.py <command> --graph <path> ...`
  In all commands below, `G` means your graph path (see §2).

Sanity check before a run:

```sh
cd the-behind
python3 pipeline/pipeline.py init --graph /tmp/_check.json --profile smoke --force
python3 pipeline/pipeline.py status --graph /tmp/_check.json
```

---

## 2. Configuration

Two profiles ship with the code. `init` snapshots the chosen profile
into the graph file; the snapshot governs the whole run.

### FULL-RUN profile (the design values — DESIGN.md §7)

| Key | Value | Meaning |
|---|---|---|
| `raw_target` | 140 | raw candidates to scout per expansion (content lenses L1, L2, L4–L22; per-lens floor ≥3 or a dry note; the 2 meta passes are capped at ~10 combined and excluded from this count) |
| `survivor_cap` | 20 | max survivors admitted per expansion |
| `depth_cap` | 10 | maximum depth (root = 0) |
| `node_budget` | 2000 | global live-node budget for the run |
| `min_gate_survivors` | 5 | an expansion yielding fewer survivors does not stop the run, but a *node* whose own later expansion would start from a pool this thin is a stop signal (see §8) |
| `year_floor` | 1500 | do not expand nodes whose candidate pool falls before ~1500 |

Start a full run:

```sh
mkdir -p runs/full/work
python3 pipeline/pipeline.py init --graph runs/full/graph.json --profile full
# G = runs/full/graph.json ; root id is printed (the-modern-ai-agent-2023)
```

### SMOKE-RUN profile (pipeline validation only — NOT design values)

| Key | Value | Meaning |
|---|---|---|
| `raw_target` | 60 | scout target per expansion |
| `survivor_cap` | 8 | cap for the depth-1 expansion |
| `depth_cap` | 2 | root + two levels |
| `node_budget` | 60 | plenty for a smoke graph |
| `min_gate_survivors` | 2 | — |
| `year_floor` | 1500 | — |

Smoke procedure (exact): init smoke → expand the root (cap 8) → expand
**two** of the survivors with `--cap 6` on `apply-verdicts` → verify
**all** survivors → render → write up counts in `SMOKE_TEST.md`.

```sh
mkdir -p smoke/work
python3 pipeline/pipeline.py init --graph smoke/graph.json --profile smoke
# G = smoke/graph.json
```

---

## 3. The graph file

One JSON file per run (path = `G`). Top-level keys:

- `config` — the profile snapshot (§2).
- `run_state` — `expansions_done`, `raw_candidates_seen`, and
  `rejected`: every rejected candidate with its parent and reason.
  Rejections by mediation additionally carry `mediated_via` (the named
  mediator). This list is the `{already_rejected}` input for future
  scouts of the same parent, and `resolve` automatically drops exact
  repeats of it.
- `nodes` — id → node record: `name`, `aliases`, `year`, `domain`,
  `type` (`device|theory|method|material|institution|other`),
  `definition` (one sentence), `bottleneck` (one sentence, form:
  "Before X, Y was impossible or impractical because Z."), `leap`
  (one–two sentences: what discontinuously jumped when this node
  appeared), `prior_state` (the state of the art immediately before
  it), `status` (`provisional|verified`), `depth`, `expanded`,
  `priority` (admission score; frontier is best-first), `sources`
  (list of `{title, url}`), `verification`, `merged_into` (union-find
  pointer; non-null nodes are merged away and invisible).
- `edges` — `{predecessor_id, successor_id, verdicts, score, gate}`,
  plus v3 fields `leap` (`{prior_state, jump, date}` — the *successor's*
  leap, recorded with this evaluation) and `directness`
  (`{verdict, counterfactual, mediator, evidence}`), and optionally
  `mediation_challenges` (verifier attacks that landed as downgrades).
  Reads: predecessor **directly enabled** successor's leap.
  `verdicts` holds the 12 answers for that predecessor *in relation to
  that successor*.
- `merge_log` — every identity merge with signals, scores, and the
  judge's one-sentence reason. Merges are reversible in the data model
  (`graph.py: unmerge`); there is no CLI for it — if you need one, stop
  and escalate rather than editing JSON.
- `expansions` — per-node working state: raw candidates, resolution,
  judge queue, stage (`scouted → resolved → judged → evaluated`). This
  is what makes an interrupted expansion resumable.

Checkpointing: the CLI rewrites `G` atomically after **every** command.
A crash loses at most the command in flight.

---

## 4. The loop (one expansion, step by step)

Repeat until a stop condition (§8) fires. Each iteration expands ONE
node: the first entry of the frontier.

### Step 0 — Pick the node

```sh
python3 pipeline/pipeline.py status --graph $G
```

`frontier_detail[0]` is your node (best-first by admission score).
Note its `id`, `name`, `year`, `domain`, `bottleneck`. Call it PARENT.

### Step 1 — Scout (you, with web search)

Fill the SCOUT PROMPT (§6.1) slots for PARENT:

- `{immediate_prior_state}` and `{parent_leap}`: PARENT's `prior_state`
  and `leap` fields from its node record (the root ships with both;
  every admitted node carries the ones its evaluator wrote).
- `{existing_nodes}`: the canonical names of all live nodes — get them
  from `status` output / the graph's node names you already know.
- `{already_rejected}`: names in `run_state.rejected` with
  `parent_id == PARENT.id` (empty on a first expansion). Mediated
  rejections are included — never re-propose them for this parent.

Run all 23 lenses (§6.1), ≥2 query variants each, and write the
resulting JSON array to `work/candidates_<PARENT_ID>.json`. Every
content lens (L1, L2, L4–L22) is mandatory for every parent (v4),
even when a lens looks irrelevant to it. **Per-lens floor:** each
content lens must contribute ≥3 candidates; if a lens genuinely
finds nothing, record a **dry note** for it (lens id, queries run,
sources checked, why nothing qualified) in
`work/dry_notes_<PARENT_ID>.json` and note it in the run log — a lens
with neither candidates nor a dry note means the scout is incomplete;
do not proceed to Step 2. The 2 meta passes (L3 lineage surveys, L23
contemporaneous accounts) are capped at ~10 candidates combined and
do NOT count toward `raw_target`. There is no per-lens cap:
cross-lens duplicates are signal. Candidate objects
must carry the §4.3 fields **plus** the two identity-card fields §4.5
requires: `"type"` and `"definition"` (one sentence: what it is and
what it enabled). Then:

```sh
python3 pipeline/pipeline.py add-candidates --graph $G --parent <PARENT_ID> --file work/candidates_<PARENT_ID>.json
```

You may scout in several batches and call `add-candidates` repeatedly;
batches accumulate. Stop when you reach the profile's `raw_target` in
content-lens candidates; meta-pass candidates (≤ ~10 combined) are
added on top and excluded from the count.

### Step 2 — Resolve identities (CLI)

```sh
python3 pipeline/pipeline.py resolve --graph $G --parent <PARENT_ID>
```

Deterministic resolution per §4.5: canonical-ID and alias matches and
strong-band embedding matches are applied; candidates dated on/after
the parent are dropped; exact repeats of this parent's rejections are
dropped by the §4.4 pre-filter — with a record (`prefiltered_records`
in the output and the stored resolution), never silently. A candidate
marked `"rehearing": true` is exempt from the pre-filter and resolves
with a `rehearing_of` annotation (§9). Ambiguous pairs are written to
`judge_queue_<PARENT_ID>.json` **next to the graph file**. The command
prints `distinct`, `matched_existing`, `auto_merges`, and
`judge_queue` counts.

### Step 3 — Judge the gray zone (you) — skip if `judge_queue` is 0

Read the queue file. For every pair, decide using the IDENTITY JUDGE
instructions (§6.3): `SAME`, `DIFFERENT`, or `SUBTYPE`, with a
one-sentence reason. Write `work/judgments_<PARENT_ID>.json`:

```json
{"judgments": [{"pair_id": "cand-cand:3:7", "decision": "SAME", "reason": "…"}]}
```

```sh
python3 pipeline/pipeline.py apply-judgments --graph $G --parent <PARENT_ID> --file work/judgments_<PARENT_ID>.json
```

Every pair in the queue needs a decision; unjudged pairs stay separate
(the safe direction) but keep `pending_judge` flags in the output.

### Step 4 — Evaluate (you)

Get the final candidate list:

```sh
python3 pipeline/pipeline.py show-distinct --graph $G --parent <PARENT_ID>
```

For **every** distinct candidate, apply the EVALUATOR CONTRACT (§6.2):
answer Q1–Q12 in relation to PARENT, each verdict `pass|partial|fail`,
every pass carrying evidence + source + a falsification note; record
PARENT's **leap** (§5.1 of DESIGN.md: prior state / jump / date — the
same record for every candidate of this parent, stored per edge); run
the **directness test** (§5.2: counterfactual + mediation check — if a
mediator can be named, directness is `fail` and `mediator` names it).
Also write the candidate's own `bottleneck` sentence (the bottleneck IT
removed, in the §3 form — this becomes its node text if admitted), its
own `node_leap` and `node_prior_state` (used when IT is expanded), and
confirm its `year`, `type`, `definition`. Write
`work/verdicts_<PARENT_ID>.json`:

```json
{"evaluations": [
  {"cand_id": "<from show-distinct>", "bottleneck": "Before X, …",
   "node_leap": "…", "node_prior_state": "…",
   "leap": {"prior_state": "…", "jump": "…", "date": 2023},
   "directness": {"verdict": "pass", "counterfactual": "…",
                  "mediator": null, "evidence": "…"},
   "verdicts": {"Q1": {"verdict": "pass", "evidence": "…", "source": "…", "falsification": "…"},
                "Q2": {"…": "…"}, "Q12": {"…": "…"}}}
]}
```

All 12 keys are required per evaluation (missing keys count as `fail`),
and the `directness` object is required: a missing one counts as
`fail` (fail-closed), and a named `mediator` forces `fail` whatever
verdict label was written.

### Step 5 — Apply verdicts (CLI: gates, ranking, insertion)

```sh
python3 pipeline/pipeline.py apply-verdicts --graph $G --parent <PARENT_ID> --file work/verdicts_<PARENT_ID>.json
# smoke depth-2 expansions only: add --cap 6
```

The CLI applies the §5 gates ((Q1 or Q2 pass) and Q3 not a clear fail
**and the v3 directness gate**: directness `pass` with no mediator
named), downgrades evidence-less passes to `partial`, ranks survivors
by score across the other nine questions, caps them, creates nodes (or
links to existing nodes the candidates matched — that is convergence),
writes edges with the verdicts + leap + directness records, records
every rejection with its reason (mediated rejections as
`mediated_via: M`, also listed separately in the command output as
`mediated_rejections`), marks PARENT expanded, and checkpoints. It
prints survivor / created / linked / rejected counts and the next
frontier.

### Step 6 — Verify (you, then CLI)

For each survivor created or linked in Step 5, run the VERIFIER
instructions (§6.4): multiples test on Q3, attack on Q1, date and
causal-direction check, and the **mediation attack** on the edge that
admitted it (try to name an intermediate M: X→M→PARENT). Write
`work/verification_<PARENT_ID>.json`:

```json
{"verifications": [{"node_id": "…", "outcome": "verified|provisional|killed", "notes": "…",
                     "mediation": {"mediator": "M", "action": "kill_edge|downgrade",
                                   "successor_id": "<PARENT_ID>"}}]}
```

The `mediation` object is present only when the attack lands.
`kill_edge` removes that edge, logs the rejection as
`mediated_via: M`, and — if the node is left with no edges — takes the
node out of the frontier (it stays visible in the graph). `downgrade`
keeps the edge, records the challenge on it, and caps the node at
provisional. Any mediation finding also caps a `verified` outcome at
provisional in the CLI.

```sh
python3 pipeline/pipeline.py apply-verification --graph $G --file work/verification_<PARENT_ID>.json
```

`killed` keeps the node visible but removes it from the frontier
forever. When in doubt, use `provisional`, never `verified`.

### Step 7 — Render (CLI) and loop

```sh
python3 pipeline/pipeline.py render --graph $G --out runs/full/index.html
```

Render after every expansion (cheap) so the page is always current.
Then go back to Step 0.

---

## 5. Checkpoint / resume protocol

The graph file is the only state that matters. To resume after any
interruption (crash, restart, new agent):

1. `python3 pipeline/pipeline.py status --graph $G` — read counts,
   `expansions` stages, and the frontier.
2. If some node has an expansion in stage `scouted`, `resolved`, or
   `judged` but not `evaluated`, resume THAT expansion at the matching
   step in §4 (its raw candidates, resolution, and judge queue are all
   stored in the graph / queue file). Do not re-scout it.
3. Otherwise continue at Step 0 with `frontier_detail[0]`.
4. Never re-run `init` on an existing graph (it refuses without
   `--force`; `--force` destroys the run — do not use it mid-run).

---

## 6. Prompts (verbatim)

### 6.1 Scout prompt (DESIGN.md §4.3, v4)

```
ROLE
You are the candidate scout for a recursive history-of-technology trace.
Your job is breadth, not judgment — but breadth in ONE direction only:
backwards by a single step. This trace is built from proximate leaps.
Each node is a discontinuity: a jump over the state of the art that
immediately preceded it. Your candidates are the advances that appeared
shortly before the parent and directly made the parent's leap possible.
A later stage will interrogate every candidate with 12 fixed questions,
a directness gate, and hard pruning. If you pre-filter by importance,
or reach back to deep fundamentals, you corrupt the trace: importance
is transitive, directness is not. A fundamental that enabled the parent
only through intermediaries does NOT belong at this level — it will be
found when the intermediary is expanded. Over-propose proximate
candidates; never propose mediated ones you can already see through.

PARENT NODE
Name: {parent_name}
Year: {parent_year}  (hard upper bound: every candidate must be earlier)
Domain: {parent_domain}
Bottleneck this node removed: {bottleneck_statement}
Read it as: "Before {parent_name}, {capability} was impossible or
impractical because {constraint}."
State of the art immediately before {parent_name}: {immediate_prior_state}
The parent's leap: {parent_leap}

TASK
Find approximately 140 advances that appeared shortly before
{parent_name} and directly enabled its leap: the techniques,
components, results, or resources whose arrival closed the gap between
the immediate prior state of the art and {parent_name}. Work through
all 23 search lenses in the attached LENS SET, in family order, plus
the two meta passes (L3 lineage surveys, L23 contemporaneous
accounts), which are capped at about 10 candidates combined and do
not count toward the 140. Run real web searches for each lens, at
least 2 query variants per lens, and read the strongest sources,
preferring reference works, textbooks, and scholarly histories over
popular listicles. Anchor every search in the parent's immediate
pre-history: the years just before {parent_year}, the systems it was
directly compared against, and the accounts written at the time of why
it outperformed them. EVERY content lens is mandatory for every
parent, even when a lens looks irrelevant to it: each content lens
(L1, L2, L4–L22) must return at least 3 candidates, and a lens that
genuinely finds nothing must be reported as a DRY NOTE (see OUTPUT) —
a lens with neither candidates nor a dry note is an incomplete scout.

RULES
- Proximate, dated, named. Every candidate is a specific advance with
  an approximate year, close enough to the parent that no other named
  milestone sits causally between it and the parent. Era-words are
  banned: not "electricity" but "Gramme dynamo (1871)"; not
  "computers" but "stored-program architecture (1945)".
- Directness is the claim. One sentence: "{candidate} directly enabled
  {parent_name}'s leap by ..." — the sentence must describe the last
  causal step, not a chain. If writing it honestly requires "...which
  later made X possible, which in turn ...", the candidate is mediated:
  drop it (it belongs to a deeper level).
- Contemporaneous evidence preferred. Why did {parent_name} beat its
  immediate predecessors, according to sources from its own moment or
  careful retrospectives? Candidates that answer that question rank
  first in your list.
- Reuse canonical names. If a candidate matches a node in EXISTING
  NODES (attached), use that exact name. This is what lets the graph merge.
- Never re-propose anything in ALREADY REJECTED (attached) — including
  candidates previously rejected as mediated for this parent.
- Borderline is fine. Duplicates across lenses are fine; dedupe comes
  later. Importance filtering is NOT your job — but neither is
  deep-history trawling: distant fundamentals are explicitly out of
  scope at this level.
- Coverage is auditable. For every content lens, either propose at
  least 3 candidates from it or record a dry note naming what you
  searched and why nothing qualified. Do NOT pad a dry lens with
  mediated or distant candidates to hit the floor — the dry note is
  the honest output, and it is data.

OUTPUT
A JSON array only, one object per candidate:
{"name": "...", "year": 1871, "domain": "...", "lens": "L9",
 "causal_claim": "...", "source_title": "...", "source_url": "..."}
Accompany the array with a dry-notes list, one entry per content lens
that returned fewer than 3 candidates:
{"lens": "L10", "searched": "...", "note": "..."}
```

Pipeline addendum to the OUTPUT schema (required by §4.5's identity
card; add these two fields to every object):
`"type": "device|theory|method|material|institution|other"` and
`"definition": "one sentence: what it is and what it enabled"`.
The `"lens"` field carries the lens id (`"L1"`…`"L23"`). Write the
dry-notes list to `work/dry_notes_<PARENT_ID>.json` (same object
shape as above, as a JSON array) and summarize it in the run log.
For a smoke run, "approximately 140" reads as the smoke `raw_target`.

**THE LENS SET, v4 (attach to the prompt).** The lenses are derived
from an 11-kind enabler ontology (K1 theory · K2 methods · K3
architectures · K4 data · K5 machines · K6 software · K7
instruments/metrics · K8 standards · K9 problems/demand · K10
people/institutions · K11 materials/phenomena) crossed with 10
enabling relations (R1 incorporated · R2 ancestor-modified · R3
consumed · R4 wielded · R5 revealed · R6 posed · R7 defined-against ·
R8 imported · R9 ripened · R10 carried). Each lens below states the
matrix cells it covers, including its ≡ obligations — a lens that
claims a ≡ cell must run queries in that cell's vocabulary, or the
claim lapses. The full matrix, the classification rules, and the
dismissal list are in DESIGN.md §4.2. Classification rules that
matter while scouting: a benchmark is K4 as training data, K7 as the
test that registered the leap, K9 as a posed challenge; a device is
K5 if its change is "could compute/actuate", K7 if "could observe";
a layer that made hardware usable (CUDA-class) is K6, the hardware
K5; knowledge that lives only inside a person is K10.

*Family I — Constitution (what the parent is made of, what it
descends from):*
**L1 Components incorporated** (K1×R1, K2×R1, K3×R1; ≡ duty K1×R4) —
*What parts — mechanisms, procedures, theorems — are inside the
parent, one step in and no deeper?* ("{parent} architecture
components", "{parent} built on what {mechanism/theorem/model}",
"{component} in {parent} design") ·
**L2 Ancestor modified** (K2×R2, K3×R2, K1×R2) — *Which single direct
precursor did the parent alter, extend, or recombine?* ("{parent}
extended {precursor}", "{parent} based on {prior_system} difference",
"from {prior_system} to {parent} what changed").

*Family II — The problem side (what the parent answers):*
**L4 Problem posed** (K9×R6, K9×R2, K1×R6 formulation side, K7×R6;
≡ K2×R6, K4×R6, K6×R6, K8×R6, K9×R4) — *Who first formulated the task,
objective, or challenge the parent answers — and when was it re-posed
in the form the parent actually answered?* ("{task} first
formulated", "{challenge} proposed {domain}", "{parent} task
definition origin", "{benchmark_task} introduced as a problem") ·
**L5 Obstruction diagnosed** (K1×R6 diagnosis side, K1×R2) — *Who
first analyzed and named the bottleneck the parent removed — the
diagnosis the parent's design answers, whether or not the
diagnostician proposed the cure?* ("analysis of why {prior_approach}
fails", "{bottleneck} first shown / proved", "limitations of
{prior_approach} theoretical analysis") ·
**L6 Incumbent defined-against** (R7 for all kinds; ≡ K1,K2,K3,K4,K5,
K6,K7,K8,K9,K11 × R7) — *What was the parent compared against — the
incumbent systems, methods, metrics, and materials whose documented
limits define the leap?* ("{parent} vs {predecessor_system}
comparison", "limitations of {prior_approach}", "state of the art
before {parent}") ·
**L7 Negative space** (the failure record adjacent to R6/R7) — *What
did the immediate predecessors try that failed, and what specific fix
replaced each failure?* ("failed attempts at {capability} before
{parent}", "{prior_approach} problems solved by {parent}").

*Family III — Consumed (what the parent used up):*
**L8 Data consumed** (K4×R3, K4×R1, K4×R2; ≡ K4×R4) — *What records
did the parent actually eat — training corpora, datasets, built-in
indexes — and what collection/curation work produced them?*
("{parent} training data", "{dataset} collected how", "data curation
pipeline behind {parent}", "{parent} trained on what corpus") ·
**L9 Compute & machines consumed** (K5×R3, K5×R1; ≡ K5×R2) — *What
physical plant did the leap actually run on or ship in — which
machines, how many, at what scale — and, when the parent is itself a
machine, what machine generation did it modify?* ("{parent} trained
on how many {accelerator}", "{parent} compute used hardware",
"{parent} ran on what machine", "{parent} cluster / supercomputer
built for") ·
**L10 Materials & phenomena harnessed** (K11×R1, K11×R3; ≡ K11×R2,
K11×R4) — *What substance, reagent, or newly harnessed
physical/biological effect does the parent physically depend on —
built in, used up, or wielded?* ("{parent} depends on what material /
effect", "{reagent} first used in {parent}", "{effect} harnessed for
{capability}"). Usually dry for software parents — record the dry
note; do not skip the lens.

*Family IV — Wielded (what the parent was built and run with):*
**L11 Recipe & process** (K2×R4) — *What procedure — training recipe,
manufacturing process, run-time protocol — was wielded to produce or
operate the parent?* ("{parent} training method", "how was {parent}
made", "{technique} first used for {parent}") ·
**L12 Programmability layer** (K6×R4 over K5) — *What software layer
made the consumed hardware usable — the programming model, compiler,
or abstraction without which the machines in L9 could not have been
applied to this problem?* ("{accelerator} programming model
introduced", "{platform} first used to {verb} {domain} problems",
"{parent} code written in {layer}") ·
**L13 Frameworks & software tooling** (K6×R4 build side; ≡ K6×R1,
K6×R2, K3×R4) — *What libraries, frameworks, and off-the-shelf
components was the parent built with or out of?* ("{parent} built
with what framework / library", "{parent} implementation based on",
"{parent} used {framework} for") ·
**L14 Equipment wielded** (K5×R4) — *What physical equipment — lab
machines, fabrication tools, capture rigs — was used to produce or
test the parent, without being part of it or consumed by it?*
("{parent} produced using what equipment", "{machine} automated
{process} {parent_year}", "apparatus used to build {parent}") ·
**L15 Services & APIs** (K6×R4 run side) — *What hosted services,
APIs, or platforms does the parent run on or call at run time?*
("{parent} built on {platform} API", "{service} launched
{parent_year} enabled", "{parent} runs on what service") ·
**L16 Standards & interfaces** (K8×R1, K8×R4; ≡ K8×R2) — *What agreed
spec — format, protocol, interface, standard dimension — does the
parent implement, or interoperate through?* ("{parent} implements
what standard / specification", "{interface} standard adopted
{parent_year}", "{protocol} specification enabled {parent}").

*Family V — Observation (how the leap was seen):*
**L17 Benchmarks & metrics** (K7×R5 scheme side, K1×R5; ≡ K7×R1,
K7×R2) — *What metric, benchmark-as-test, or measurement model
registered the leap — made the improvement visible, comparable, or
optimizable — including metrics built into the parent's own
objective?* ("{parent} benchmark results", "{metric} introduced",
"evaluation of {parent} vs prior", "{parent} optimized what metric") ·
**L18 Instruments of observation** (K7×R5 apparatus side, K7×R4;
≡ K3×R5) — *What instrument, sensor, or diagnostic apparatus made the
phenomenon — or the parent's behaviour — observable in the first
place, including instruments wielded during development?*
("{phenomenon} first measured / observed with", "{instrument} made
{measurement} possible", "diagnostic for {parent} behaviour").

*Family VI — Origin & timing (where it came from, and why then):*
**L19 Cross-field import** (R8 for all kinds: K1–K9, K11 × R8) —
*Which enablers originated in a different field and were transferred
in — and what is the other field's name for them? Run the queries
from the DONOR field's vocabulary, not the parent's.* ("{technique}
originally from {other_field} applied to {domain}", "{parent}
borrowed from {other_field}", "{method} first used in {other_field}
then {domain}") ·
**L20 Creator lineage** (K10×R10 person side; ≡ K1,K2,K3 × R10) —
*What did the parent's makers themselves do immediately before — and
who physically carried the key knowledge into the room?* ("{creator}
previous work before {parent}", "{creator} moved from {lab} to
{lab}", "{parent} team background") ·
**L21 Institutions, funding & incentives** (K10×R4, K10×R6, K10×R9;
≡ K4,K5,K6,K7,K8,K9 × R10) — *What organization, program, prize, or
funding structure organized, posed, or paid for the work — the
institutional vehicle without which the leap does not happen in that
place and year?* ("{parent} funded by what program", "{lab} launched
{project} {parent_year}", "{prize / program} led to {parent}").
Survivors of this lens ARE admissible as nodes (owner decision,
2026-11-24) when they pass the same gates as any candidate — node
type `institution` already exists. ·
**L22 Timeliness & cost conditions** (R9 for all kinds; ≡ K1–K9,
K11 × R9; K9×R9) — *What changed in the surroundings — a cost curve,
an availability event, a release, a demand shift — that made the leap
happen in the parent's year rather than five years earlier?*
("{capability} became feasible when", "cost of {resource}
{parent_year}", "{resource} became available / open-sourced /
released {parent_year}"). Candidates from this lens will often fail
the directness gate as background — expected; the lens exists so the
GATE, not the scout's silence, makes that judgment.

*Meta passes (source-genre passes — they search genres of documents,
not kinds of enablers; together capped at ~10 candidates per
expansion, NOT counted toward raw_target; no per-lens floor and no
dry notes for these two):*
**L3 Lineage surveys** (all cells, via reference works) — *What do
surveys, textbooks, and histories of the immediate lineage list as
the parent's ancestry?* ("timeline of {domain} {parent_year}",
"history of {parent} development", "survey of {lineage} before
{parent_year}") ·
**L23 Contemporaneous accounts** (all cells, via reportage) — *What
did papers, reviews, and reports from the parent's own moment say
made it jump?* ("{parent} review {parent_year}", "why {parent} is a
breakthrough", contemporary analysis of {parent}).


### 6.2 Evaluator contract (DESIGN.md §5, v3.1)

```
You receive ONE candidate, the PARENT node it claims to enable, and the
candidate's causal claim. You produce three things: the parent's LEAP
RECORD, the 12 question verdicts about the candidate IN RELATION TO
THE PARENT, and the DIRECTNESS verdict for the candidate–parent pair.

THE LEAP RECORD (required — it belongs to the parent, and the
directness test is meaningless without it). State, with evidence:
- prior_state: the state of the art immediately before the PARENT
  appeared (what the best existing approach could and could not do).
- jump: what discontinuously improved when the parent appeared — the
  metric or benchmark that jumped, or the capability that was
  impossible just before and possible just after.
- date: the parent's year.
Measure the leap against the IMMEDIATE predecessor state, never
against a distant past.

THE 12 QUESTIONS. Verdicts: pass / partial / fail.

Q1 Impossibility flip — Before this, was there a specific problem that
   could not be solved at all, and did this make it solvable?
Q2 Generativity — Did this unblock a whole space of previously
   impossible things, not just one problem?
Q3 Necessity — For the parent, was this the only path through, or could
   the parent have emerged another way?
Q4 Cost collapse — Did it drop the cost, time, or effort of something
   by orders of magnitude, making the impractical routine?
Q5 Measurability — Did it make something previously unobservable into
   something measurable?
Q6 Understanding — Did it supply a new explanatory model, so people
   could design deliberately instead of by trial and error?
Q7 Composability — Did it create a standard, interface, or abstraction
   others could build on without understanding its internals?
Q8 Cross-domain reach — Did it unlock progress in fields beyond the one
   it was created for?
Q9 Iteration speed — Did it collapse the experiment feedback loop,
   making the next try dramatically faster?
Q10 Displacement — Did it replace the incumbent default, so the old way
   stopped being the standard path?
Q11 Lineage centrality — In the history that actually happened, is this
   a trunk node or a side branch?
Q12 Irreversibility — Once it existed, could the field ever go back, or
   did it permanently reset the baseline?

Evidence discipline: every "pass" requires (a) a short evidence quote
or concrete factual claim, (b) a source, (c) a falsification note of
the form "this pass dies if …". A pass without evidence is recorded as
partial by the pipeline. Be strict: partial is the honest verdict for
"plausibly yes, thin evidence".

THE DIRECTNESS TEST (required, hard gate). Candidate X is a DIRECT
enabler of the parent's leap only if BOTH hold:
(a) Counterfactual: remove X, and the parent's leap does not happen
    when it did — it is delayed, diminished, or takes a different form.
(b) No mediation: there is no other milestone M such that X enabled
    the parent only through M. If you can name such an M, X FAILS
    directness for this parent: set verdict "fail" and "mediator" to
    M's name. X is not unimportant; it is one level too deep, and will
    be rediscovered when M is expanded.
A large year gap between X and the parent is a red flag: it demands a
stronger directness argument (why did nothing between them mediate?),
not an automatic fail. A "partial" — mediation genuinely unresolvable
on current evidence — does NOT satisfy the gate.
Return: {"verdict": "pass|partial|fail", "counterfactual": "…",
"mediator": null or "M", "evidence": "…"}.

SUBSTRATE IS NOT A REJECTION CLASS (v3.1). A hardware or data
candidate is judged by exactly the tests above — never rejected merely
for being "substrate" or "infrastructure". Ask: (i) counterfactual at
the parent's time and scale — could the leap have happened then, at
that scale, without it? An algorithm can exist on paper for years
before the hardware lets it run. (ii) direct consumption — did the
parent actually use it: named in the paper or system, part of the
demonstrated result? (iii) mediation, exactly as above — no exemption,
no special suspicion. The SPECIFIC enabling step can pass: a
programmability layer the parent's code was actually written in, a
cluster-scale training capability the run demonstrably used, the
dataset the headline result was produced on. GENERIC infrastructure
fails: electricity, the transistor in the abstract, "computers".

Also return the candidate's own bottleneck sentence ("Before
<candidate>, <capability> was impossible or impractical because
<constraint>."), its own leap sentence and prior-state sentence (they
become its node record if it is admitted), and confirm its year, type,
and definition.
```

Gates applied by the CLI (you do not apply them): survive iff
(Q1 pass OR Q2 pass) AND Q3 is not a clear fail AND directness passes
with no mediator named; rank by score across Q4–Q12 (pass 1.0, partial
0.5, fail 0); cap per profile.

### 6.3 Identity judge instructions (DESIGN.md §4.5)

```
You receive a pair of identity cards (name, aliases, year, domain,
type, one-sentence definition) that automated signals could not
separate: their embedding similarity fell in the 0.80–0.92 gray zone,
or their names stand in a containment relation. Decide:

SAME — both cards denote one and the same advance (same event /
  artifact / publication / formulation, allowing name variants,
  translations, and inventor-name prefixes).
DIFFERENT — two distinct advances, however related.
SUBTYPE — one card denotes a specific instance or variant of the other
  (e.g. "Gramme dynamo" vs "dynamo"): keep both; do NOT merge.

Rules: a year gap over ~25 years or a type clash (person vs device,
theory vs material) forces DIFFERENT. When genuinely unsure, choose
DIFFERENT — a false split is cheap, a false merge silently rewrites
history. Answer with the decision and ONE sentence of reason; the
reason is written to the merge log.
```

### 6.4 Verifier instructions (DESIGN.md §6, v3)

```
You are the adversarial verifier. Your job is to KILL this node. For a
survivor node and the edge that admitted it, run four attacks:

1. Attack Q1: was the problem truly impossible before this advance, or
   merely hard, expensive, or unfashionable? Search for prior art.
2. Multiples test on Q3: search for independent, near-simultaneous
   discoverers or inventors of the same advance. If two others did it
   in the same decade, necessity is downgraded to "ripe" — record that
   in your notes (the node may still stand, but never as "verified"
   on necessity grounds).
3. Check the date and the causal direction: is the year defensible, and
   did the influence really run from this node toward the child?
4. Mediation attack (v3): for the edge X -> parent, try to name an
   intermediate milestone M such that X enabled the parent only
   through M (X -> M -> parent). Search deliberately for what sits
   between X and the parent, in time and in the causal chain. If you
   find a convincing M, record it in your verification entry as
   "mediation": {"mediator": "M", "action": "kill_edge"} when the
   mediation is complete (X contributed nothing to the parent except
   through M — the edge is removed and the rejection logged as
   mediated_via: M; X is expected to resurface when M is expanded),
   or {"mediator": "M", "action": "downgrade"} when X also had a
   direct channel but the mediated path dominates (the edge stays,
   the challenge is recorded on it, the node is capped at
   provisional).

Outcomes: "verified" only if all four attacks fail to land. "killed"
if the date is wrong, the causal direction is reversed, or the advance
did not exist as described. Otherwise "provisional", with the strongest
attack recorded in your notes. A node whose edge you killed via the
mediation attack is not "killed" as a node — it is re-filed one level
down; use outcome "provisional" with the mediation object set.
```

---

## 7. Rendering

```sh
python3 pipeline/pipeline.py render --graph $G --out <path>.html
```

Produces ONE self-contained HTML file (no external assets; graph data
embedded). Open it in any browser. Features: Trace view (layered DAG by
depth, +/− collapse on nodes with predecessors), Timeline view (nodes
on a year axis), search by name/alias, and a detail panel per node:
bottleneck sentence, its leap and prior-state sentences, definition,
status badge, sources, and — for every node it enables — the leap
record, the directness record (with any mediation challenges), and the
full 12-question verdict table with evidence and falsification notes.
Render after every expansion; rendering never mutates the graph.

For the eventual AI Praxis Lab integration, this same file is the
artifact to embed (DESIGN.md §9).

---

## 8. Stop conditions

Stop the run (and render a final page) when ANY fires:

1. The frontier is empty (everything admitted has been expanded or hit
   the depth cap).
2. Live-node count reaches the profile `node_budget` (2000 full / 60
   smoke). The graph is still complete and publishable as-is.
3. An expansion yields fewer than `min_gate_survivors` survivors AND
   the frontier nodes behind it are all at or beyond the depth where
   their candidate pools fall before the `year_floor` (~1500) — the
   written record has thinned out.
4. Smoke profile only: root expanded + exactly two survivors expanded
   + all survivors verified + page rendered. Stop there by design.

Also stop a single node's expansion (mark it expanded via a verdicts
file with zero evaluations only if truly nothing passed — in practice,
record what happened in the run log instead) when its candidate pool is
exhausted: scouts return only already-rejected or post-dated items.

---

## 9. Retro-sweep protocol (v4 — one-time supplementary pass; scope extended from v3.1)

**Why.** The already-expanded part of run-01 was scouted under the
accreted lens lists: the early expansions under the original 10
lenses, the later ones under 12. Those lists had no closure property,
and their blind spots are baked into the shallow graph — the part
readers see first. The v3.1 sweep repaired *discovery* for the
hardware and data lenses only. V4 extends it: the genuinely-new
questions (problem posed, obstruction diagnosed, materials,
programmability, standards, institutions, timeliness) have never been
asked of the already-expanded nodes at all. This protocol repairs
*discovery* only. It does NOT re-open or alter any existing verdict:
everything the sweep finds enters through the normal gates, and
everything it rejects is recorded like any other rejection.

**When.** As its own dedicated run session, after the v4 doc revision
lands, before (or interleaved with) further frontier expansion. Run
it once.

**Lens set.** The union of the genuinely-new v4 lenses and the v3.1
hardware/data lenses in v4 numbering — 10 lenses:

- Genuinely new: **L4** Problem posed · **L5** Obstruction diagnosed ·
  **L10** Materials & phenomena · **L12** Programmability layer ·
  **L16** Standards & interfaces · **L21** Institutions, funding &
  incentives · **L22** Timeliness & cost conditions
- V3.1 hardware/data, in v4 numbering: **L8** Data consumed ·
  **L9** Compute & machines consumed · **L12** Programmability layer
  (already listed above) · **L14** Equipment wielded

**Scope and priority.** Already-expanded nodes, in this order:

1. The root (the modern AI agent)
2. Large-scale pretraining / GPT-3
3. Transformer architecture
4. RLHF
5. In-context learning
6. Learning to summarize from human feedback (Stiennon et al. 2020)

Then any other already-expanded node, in frontier order, as budget
allows.

**Procedure, per node P:**

1. Scout ONLY the 10 sweep lenses for P, using the §6.1 prompt with
   the lens set restricted to those lenses. Fill every other slot
   exactly as in §4 Step 1 (`{immediate_prior_state}`, `{parent_leap}`,
   `{existing_nodes}`, `{already_rejected}`). The per-lens floor
   applies within the sweep set: each of the 10 lenses returns ≥3
   candidates or a dry note in `work/dry_notes_<P_ID>.json` (expect
   ~40–60 raw candidates per node). Meta passes are not part of the
   sweep.
2. Run §4 Steps 2–6 unchanged: resolve identities, judge the gray
   zone, evaluate every distinct candidate (12 questions + leap record
   + directness test, under the gate guidance — substrate is not a
   rejection class, §6.2), apply verdicts, verify survivors (multiples
   / Q1 / mediation attacks). L21 survivors are admissible as nodes
   (type `institution`) on the same terms as any candidate.
3. Survivors are inserted or linked, and edges recorded, exactly as in
   a normal expansion. Mark every run-log line for the sweep with
   `retro-sweep` so the additions stay distinguishable from frontier
   expansions.

**Two cautions.**

- *Previously rejected candidates.* A candidate rejected for P under
  the superseded substrate-class judgment (or never scouted because
  its lens did not exist) may be re-proposed in the sweep when its
  claim is one the original evaluation never considered. To get it
  heard, mark the candidate `"rehearing": true` in the scout batch:
  `resolve` then carries it through identity resolution with a
  `rehearing_of` annotation naming the original rejection (parent,
  date, reason), and the annotation lands on the admission edge or
  the new rejection record — the new judgment supersedes or confirms
  the old one on the record. Log every re-hearing and its outcome in
  the run log (see the `rehearings` list in the `apply-verdicts`
  output). Only mark genuine re-hearings under a claim the original
  evaluation never considered. An UNMARKED exact repeat is still
  dropped by the §4.4 pre-filter — now with a record
  (`prefiltered_records`), never silently — and renaming a candidate
  to evade the filter remains forbidden.
- *CLI limits.* If the CLI refuses a supplementary expansion on an
  already-expanded node, stop and escalate. Never edit `graph.json` by
  hand to force it (§0).

**Stop.** The sweep ends when the priority list is exhausted or the
profile `node_budget` is reached (sweep survivors count against the
same global budget). Render (§7), sync, and then resume the normal
loop (§4, §5).

---


## 10. Troubleshooting

- **`graph file not found`** — run `init` first, and check `--graph`
  points at the run's graph (paths are relative to where you invoke).
- **`unknown cand_id in verdicts`** — verdicts must use the `cand_id`s
  from `show-distinct` for THIS parent, after judgments were applied.
  Re-run `show-distinct`; do not invent ids.
- **Judge queue file missing** — it is written next to the graph file
  (`judge_queue_<PARENT_ID>.json` in the graph's directory), not in
  `work/`. Re-run `resolve` to regenerate it.
- **A survivor links to an existing node instead of creating one** —
  that is convergence working as designed (§4.5), not a bug. It appears
  under `linked_existing` in the `apply-verdicts` output.
- **Everything is being rejected at the gate** — check evidence
  discipline first: passes without evidence text are downgraded to
  `partial`, and a `partial` Q1/Q2 does NOT satisfy the gate. Add real
  evidence quotes and re-apply verdicts for that parent (the expansion
  is still open until `apply-verdicts` succeeds once — after it has,
  re-applying is not supported; escalate instead).
- **Everything is failing the directness gate (v3)** — three usual
  causes: (1) the verdicts file is missing the `directness` object per
  evaluation (missing counts as `fail`, fail-closed); (2) evaluators
  are writing `partial` — honest, but it does not satisfy the gate;
  the mediation question must actually be resolved; (3) the scout
  trawled deep history instead of the parent's immediate pre-history,
  so most candidates genuinely are mediated for this parent — re-scout
  with the v4 lenses rather than weakening verdicts.
- **A famous fundamental was rejected as `mediated_via: M`** — that is
  v3 working as designed, not a bug. Importance is transitive;
  directness is not. The candidate is expected to resurface when M is
  expanded; the rejection record (with `mediated_via`) is what keeps
  the scout from re-proposing it at this level.
- **Hardware/data candidates keep dying as "substrate" (v3.1)** —
  that is the pre-v3.1 habit the gate guidance removed. "Substrate" is
  not a rejection class: apply the counterfactual at the parent's time
  and scale, ask whether the parent directly consumed it, and run the
  mediation check — no more, no less (§6.2). If the candidate is
  generic infrastructure (electricity, "computers"), it fails on those
  tests, not on its category.
- **A sweep re-proposal vanished at `resolve` (pre-filter)** — before
  the rehearing fix, `resolve` silently dropped any candidate whose
  normalized name exactly matched a prior rejection for the same
  parent: no dropped record, no claim-awareness, so candidates
  rejected under superseded judgments (CUDA / cuDNN under the
  substrate-era directness class, the OpenAPI specification's
  never-evaluated standards claim) could never be re-heard. Now every
  pre-filter drop is recorded (`prefiltered` count and
  `prefiltered_records` in the resolve output and the stored
  resolution), and a candidate marked `"rehearing": true` in the
  scout batch is heard with a `rehearing_of` annotation (§9). If a
  marked re-proposal still disappears, check its name against the
  rejection list — the match is on the normalized name; if the names
  genuinely differ, it was never pre-filtered, so look at the
  resolution `dropped` list (date bound) instead.
- **A lens returned nothing and there is no dry note (v4)** — the
  scout is incomplete: every content lens owes ≥3 candidates or a
  recorded dry note in `work/dry_notes_<PARENT_ID>.json` (§4 Step 1).
  Go back and finish that lens before applying verdicts; a silent
  lens is exactly the failure the v4 framework exists to prevent.
- **Embedder shows `tfidf-fallback`** — expected without
  `sentence-transformers`. Consequences: fewer auto-merges, more pairs
  decided "different" by default, name-containment pairs still routed
  to the judge. Safe to run; note it in the run log.
- **Duplicate node names with different ids** — ids carry the year
  (`name-year`); two advances with the same name and year get `-2`
  suffixes. Check `aliases` before concluding a duplicate exists.
- **JSON errors in your work files** — validate before applying:
  `python3 -m json.tool work/<file>.json > /dev/null`.

---

## 11. File map

```
the-behind/
  README.md          what this is (humans)
  DESIGN.md          the approved design (humans)
  LENS-FRAMEWORK-DESIGN.md  the v4 lens framework's source design (approved 2026-11-24)
  RUNBOOK.md         this file (executing agents)
  SMOKE_TEST.md      smoke-run log and results
  pipeline/
    pipeline.py      CLI (init/add-candidates/resolve/show-distinct/
                     apply-judgments/apply-verdicts/apply-verification/
                     status/render)
    graph.py         graph store: nodes, edges, union-find merges,
                     frontier, checkpointing
    identity.py      §4.5 identity resolution (signals, bands, vetoes)
    score.py         §5 gates + ranking (deterministic)
    render.py        graph.json -> single-file interactive HTML
  runs/full/         full-run graph + rendered page (created at runtime)
  smoke/             smoke-run graph + rendered page
```
