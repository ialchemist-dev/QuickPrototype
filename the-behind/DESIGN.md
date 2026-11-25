# Tracing the Milestones: A Recursive Pipeline from the AI Agent Backwards

**The Behind · 01 · Design v3.1 · 2026-11-24**

## §0 The idea in one paragraph

Start from a single node, the modern AI agent. Ask: what appeared shortly before it that directly made its leap possible? Generate about 100 candidate proximate predecessors, interrogate every candidate with 12 fixed questions plus a directness gate, prune hard to at most 20 survivors, and recurse on each survivor. Every node is a **leap**: a discontinuous, widely recognized improvement over the state of the art immediately before it. Every edge means the predecessor was the **direct enabler of that leap** — not a mediated ancestor. This matters because importance is transitive but directness is not: a deep fundamental (gradient descent, electricity, calculus) genuinely matters to everything downstream, yet it reaches any given node only through intermediaries, so it must surface at the depth where it was the proximate enabler, not at depth 1. Because the same predecessor is reached from many children, the result is not a tree but a merged graph (a DAG) of the breakthroughs that made the agent possible, each admitted only after passing the same interrogation, each carrying its evidence. The graph then becomes an interactive page on AI Praxis Lab (The Behind) that readers can explore node by node.

## §1 The process

```mermaid
flowchart TD
    A["ROOT NODE<br/>The modern AI agent · 2020s"] --> B["EXPANSION<br/>run per frontier node"]
    B --> B1["① Generate ≈100 candidates<br/>12 search lenses, prompt in §4"]
    B1 --> B2["② Dedupe & resolve identities<br/>merge variants → ≈50–70 real candidates"]
    B2 --> B3["③ Evaluate: leap record + 12 questions + directness<br/>every 'yes' needs evidence"]
    B3 --> B4["④ Gates (incl. directness) → rank → cap 20<br/>rule in §5"]
    B4 --> C["Survivors become new frontier nodes<br/>each with its own bottleneck sentence"]
    C -->|"RECURSE, depth ≤ ~10"| B
    B -.-> G["GRAPH STORE<br/>checkpointed; duplicates merge → DAG, not a tree"]
    B4 -.-> V["ADVERSARIAL VERIFIER<br/>tries to kill each survivor"]
    G --> O["Graph data → interactive page"]
    O --> P["Published on AI Praxis Lab, The Behind"]
```

**Flow, in words:**

- **ROOT NODE** (The modern AI agent · 2020s)
- → one expansion box run per frontier node with four steps:
  1. Generate ≈100 proximate candidates (12 search lenses, prompt in §4)
  2. Dedupe & resolve identities (merge variants → ≈50–70 real candidates)
  3. Evaluate: the parent's leap record, the 12 questions, and the directness test (every "yes" needs evidence)
  4. Gates (question gates + the directness gate) → rank → cap 20 (rule in §5)
- Survivors become new frontier nodes, each with its own bottleneck sentence; loop labeled "RECURSE, depth ≤ ~10".
- Side boxes: **GRAPH STORE** (checkpointed; duplicates merge → DAG, not a tree) and **ADVERSARIAL VERIFIER** (tries to kill each survivor).
- Output: graph data → interactive page → published on AI Praxis Lab, The Behind.

Two structural choices keep a day-long run sane: **merging** (one transistor node with five edges, not five copies; merging is decided by the identity machinery of §4.5, not by name matching) and **checkpointing** (every finished expansion is written to the graph store immediately; the run can pause, be inspected, and resume).

## §2 Node and edge format

Every node = one breakthrough + one bottleneck sentence of the form "Before X, Y was impossible or impractical because Z." Every node is also a **leap** (§5.1): it carries a record of the state of the art immediately before it and what discontinuously jumped when it appeared.

Every edge reads "enabled by" — and since v3 that phrase is strict: the predecessor **directly enabled the child node's leap**. A mediated ancestor, however important, is not an edge at this level; it is rejected with the mediator named (`mediated_via: M`) and is expected to be rediscovered when M itself is expanded.

**Root node:**

- **Name:** "The modern AI agent"
- **Era:** 2020s
- **Bottleneck sentence:** "Before the modern AI agent, machines could not perceive, reason over, and act on open-ended tasks in a loop, because no model could flexibly convert between language, perception and action, and there was no practical way to train or steer such a model."
- **State of the art just before:** chatbots and task-specific ML systems — models could complete text or classify inputs, but could not follow open-ended instructions reliably, use external tools, or chain reasoning and action toward a goal.
- **The leap:** instruction-following LLMs wrapped in a reason–act loop with tool use (2022–23) turned a text completer into a general task executor — a capability jump, not an incremental accuracy gain.

**Node record fields:** canonical name, approx. year, domain, type, bottleneck sentence, prior-state sentence, leap sentence, status (provisional / verified), source list.

**Edge record fields:** the 12 verdicts with evidence (of the predecessor, in relation to the child), the **leap record** (prior state / what jumped / the child's date, with evidence), and the **directness record** (counterfactual argument, mediator — null for admitted edges, evidence).

## §3 The 12 questions

Every candidate is interrogated with the same 12 questions, always in relation to the parent node it claims to enable. Mutually exclusive (each owns one dimension), collectively exhaustive. Q5 (scale ceiling) and Q8 (controllability) from the earlier 14-question draft were removed on 2026-11-24 as the two weakest.

| # | Dimension | Question | Literature anchor |
|---|---|---|---|
| Q1 | Impossibility flip | "Before this, was there a specific problem that could not be solved at all, and did this make it solvable?" | Rosenberg, bottlenecks as focusing devices (1976/1982) |
| Q2 | Generativity | "Did this unblock a whole space of previously impossible things, not just one problem?" | Bresnahan & Trajtenberg (1995), "innovational complementarities"; GPTs as "enabling technologies" |
| Q3 | Necessity | "For the node it feeds, was this the only path through, or could that node have emerged another way?" | Ogburn & Thomas (1922); Merton (1961), multiples vs singletons |
| Q4 | Cost collapse | "Did it drop the cost, time, or effort of something by orders of magnitude, making the impractical routine?" | Nordhaus (2007); Wright's law / learning curves |
| Q5 | Measurability | "Did it make something previously unobservable into something measurable?" | Hacking (1983); Galison (1997), instruments create observables |
| Q6 | Understanding | "Did it supply a new explanatory model, so people could design deliberately instead of by trial and error?" | Mokyr (2002), propositional vs prescriptive knowledge |
| Q7 | Composability | "Did it create a standard, interface, or abstraction others could build on without understanding its internals?" | Baldwin & Clark (2000), modularity |
| Q8 | Cross-domain reach | "Did it unlock progress in fields beyond the one it was created for?" | Bresnahan & Trajtenberg (1995), "pervasiveness"; Johnson (2014), hummingbird effect |
| Q9 | Iteration speed | "Did it collapse the experiment feedback loop, making the next try dramatically faster?" | Thomke (2003), experimentation cost |
| Q10 | Displacement | "Did it replace the incumbent default, so the old way stopped being the standard path?" | Kuhn (1962); Funk & Owen-Smith (2017), disruption index |
| Q11 | Lineage centrality | "In the history that actually happened, is this a trunk node or a side branch?" | Wu, Wang & Evans, Nature (2019), CD index at scale |
| Q12 | Irreversibility | "Once it existed, could the field ever go back, or did it permanently reset the baseline?" | David (1985); Arthur (1989), path dependence and lock-in |

> **Note:** the 12-as-a-set being mutually exclusive and exhaustive is our synthesis; the backing is per question, which is how the design documents it.

## §4 Candidate generation

Scoring is strict, so generation must be loose — but, since v3, loose in one direction only: **backwards by a single step**. The scout is forbidden from judging importance, and equally forbidden from trawling deep history: its job is to over-propose roughly 100 dated, named candidates that appeared shortly before the parent and plausibly enabled the parent's leap *directly*, each with a causal claim, and let the 12 questions and the directness gate do the filtering. Time is a first-class dimension: every search is anchored in the parent's immediate pre-history — the state of the art just before it, the systems it was compared against, and contemporaneous accounts of why it jumped. Distant fundamentals are explicitly out of scope at this level; they belong to deeper expansions. One run of this prompt happens per frontier node. It is a fan-out: twelve lenses, each a separate search pass with its own query templates, each expected to return about ten candidates.

### 4.1 Inputs

Slots filled per node:

- `{parent_name}`
- `{parent_year}` (hard upper bound — every candidate must be earlier)
- `{parent_domain}`
- `{bottleneck_statement}`
- `{immediate_prior_state}` (the state of the art just before the parent appeared — what the best existing approach could and could not do)
- `{parent_leap}` (what discontinuously jumped when the parent appeared)
- `{existing_nodes}` (canonical names already in the graph, attached so the scout reuses exact names — this is what lets the graph merge)
- `{already_rejected}` (candidates previously evaluated and rejected for this parent, including any rejected as mediated — never re-propose)

### 4.2 The twelve lenses (v3: all aimed at the immediate pre-history; lenses 11–12 added in v3.1)

| # | Lens | What it looks for | Example query templates |
|---|---|---|---|
| 1 | Immediate prior state of the art | what the parent was directly compared against, and the incumbent's known bottleneck | "{parent} vs {predecessor_system} comparison" · "limitations of {prior_approach}" · "state of the art before {parent}" |
| 2 | The differentiating move | the specific technique, component, or combination first introduced — or first combined — shortly before the parent (the ChatGPT→RLHF pattern) | "what was new in {parent}" · "{parent} key innovation" · "why did {parent} outperform {predecessor_system}" |
| 3 | First-order components | the subsystems the parent is directly assembled from — one step in, no deeper | "{parent} architecture components" · "what is {parent} built on" |
| 4 | Contemporaneous accounts | papers, reviews, and reports from the parent's own moment explaining why it jumped | "{parent} review {parent_year}" · "why {parent} is a breakthrough" · contemporary analysis of {parent} |
| 5 | Benchmarks & measurement | the metric or evaluation that registered the leap, and the measurement advance just before that made the jump visible or trainable | "{parent} benchmark results" · "{metric} introduced" · "evaluation of {parent} vs prior" |
| 6 | Method / recipe introduced shortly before | the training procedure, process, or recipe whose arrival closed the gap | "{parent} training method" · "how was {parent} made" · "{technique} first used for {parent}" |
| 7 | Infrastructure at hand | the compute, platform, or production base the parent directly ran on, as it existed at that moment | "{parent} hardware used" · "{parent} built with what tools" |
| 8 | Direct transfers | people, techniques, or results that moved directly into the parent's lineage shortly before | "{creator} previous work before {parent}" · "{technique} applied in {parent}" |
| 9 | Negative space | what the immediate predecessors tried that failed, and the specific fix that replaced it | "failed attempts at {capability} before {parent}" · "{prior_approach} problems solved by {parent}" |
| 10 | Timelines of the immediate lineage | reference works and surveys that list the parent's immediate ancestry | "timeline of {domain} {parent_year}" · "history of {parent} development" · survey of {lineage} |
| 11 | Hardware & devices (v3.1) | the compute hardware, accelerators, memory/interconnect, and the software layer that made the hardware usable (e.g. a CUDA-class programmability milestone); the devices the parent directly ran on or was demonstrated on | "{parent} ran on what hardware" · "{accelerator} first used to train {parent}" · "{platform} programmability layer {parent_year}" |
| 12 | Data (v3.1) | the datasets, benchmarks-as-data, and large-scale data collection/curation pipelines the parent's leap directly consumed | "{parent} training data" · "{dataset} collected how" · "data curation pipeline behind {parent}" |

Lenses 11 and 12 are **mandatory for every parent** (v3.1), even when the parent looks purely algorithmic — and doubly so for compute-hungry or data-hungry leaps. A leap that reads as pure method often directly consumed a specific machine, platform, or dataset; if the scout never looks, the graph never sees it.

### 4.3 The scout prompt template (v3.1)

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
Find approximately 100 advances that appeared shortly before
{parent_name} and directly enabled its leap: the techniques,
components, results, or resources whose arrival closed the gap between
the immediate prior state of the art and {parent_name}. Work through
all 12 search lenses (attached). Run real web searches for each lens,
at least 2 query variants per lens, and read the strongest sources,
preferring reference works, textbooks, and scholarly histories over
popular listicles. Anchor every search in the parent's immediate
pre-history: the years just before {parent_year}, the systems it was
directly compared against, and the accounts written at the time of why
it outperformed them. The Hardware & devices and Data lenses are
mandatory for every parent, even when the parent looks purely
algorithmic: a leap that reads as pure method often directly consumed
a specific machine, platform, or dataset.

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

OUTPUT
A JSON array only, one object per candidate:
{"name": "...", "year": 1871, "domain": "...", "lens": "instruments",
 "causal_claim": "...", "source_title": "...", "source_url": "..."}
```

### 4.4 Dedupe

A resolver pass merges name variants of the same advance, maps matches onto existing graph nodes, drops anything dated on or after the parent, and drops exact repeats of rejected candidates. Typical yield: 100 raw → 50–70 distinct candidates. Dedupe is the candidate-scale application of the identity machinery in §4.5.

### 4.5 Node identity: deciding two candidates are the same node

Convergence is the whole point of the graph, and keyword matching cannot carry it. The same advance arrives under many names ('Gramme dynamo', 'dynamo', 'self-excited dynamo', 'electric generator'), and near-identical names can be different advances ('dynamo' vs 'alternator'; 'gradient descent' vs 'backpropagation'). Exact-match merging misses true merges, so branches never visibly converge, and risks false merges, collapsing two technologies into one node and corrupting every edge and verdict downstream. Identity is therefore decided by layered signals, never by the name string alone.

#### A. The identity card

Similarity is never computed on the name alone. Every candidate and node carries an identity card: canonical name, alias list, approximate year, domain, type (device / theory / method / material / institution), and a one-sentence definition of what it is and what it enabled. Every signal below reads the card, not the keyword.

#### B. Four signals, in order

1. **Canonical ID match (strongest).** Link the candidate to a reference identity: a Wikidata QID where one exists, otherwise the standard reference-work title (e.g. the Wikipedia article title, whose redirect list doubles as an alias source). Same QID = same node, full stop. This resolves most well-documented historical advances exactly.
2. **Alias and normalization match.** Normalized name (case, punctuation, word order, person-name variants) checked against the node's alias table, which grows with every confirmed merge.
3. **Embedding similarity (vector search).** Embed the identity-card text (name + definition sentence) with a standard text-embedding model and compare by cosine similarity against all existing node cards, retrieved through a small vector index (FAISS or sqlite-vec; at roughly 2,000 nodes this takes milliseconds). Bands: 0.92 and above = strong same-node candidate; 0.80 to 0.92 = gray zone, sent to the judge; below 0.80 = treated as different. Thresholds are starting values, calibrated against the run's own merge log.
4. **Hard vetoes (override any text similarity).** A year gap over about 25 years means not the same event. Different types never merge: a person is not a device, a theory is not a material. An incompatible causal role for the parent in question also vetoes.

#### C. The gray zone goes to a judge

Pairs in the middle band, and any pair a veto flags as suspicious, go to an adjudication step with three outcomes, not two: SAME (merge), DIFFERENT (keep both), or SUBTYPE (one is a specific instance of the other: keep the specific node, record the general term as a related concept, do not merge; 'Gramme dynamo' is a subtype of 'dynamo', not a synonym). The judge sees both identity cards and the sources behind them and must state its reason in one sentence, which is written to the merge log.

#### D. Merge mechanics and the safety bias

Merging is union-find over canonical nodes. The surviving node keeps the most standard name, unions the alias lists and the edge sets, and keeps the earliest defensible year. Every merge is written to a merge log (which nodes merged, which signals fired, the similarity scores, the judge's sentence), and merges are reversible: an unmerge restores both nodes and their original edges. The bias throughout is precision over recall: a false split is cheap, because the verifier can merge later, while a false merge is expensive, because it silently rewrites history. Every threshold therefore errs toward 'different'.

#### E. Where it runs

Three places:

- (a) inside each expansion, clustering the roughly 100 raw candidates before evaluation, which is what §4.4's dedupe actually is;
- (b) at graph insertion, matching each survivor against all existing nodes, which is the moment convergence actually happens;
- (c) as a verifier duty: sample already-merged nodes and re-run the judge with fresh eyes (a split check).

**Payoff:** The payoff: convergence becomes measurable. A node's in-degree, how many independent branches converged on it, is direct evidence for Q11 (lineage centrality). Trunk nodes identify themselves.

## §5 Evaluation and pruning

**Evaluation contract:** the evaluator receives one candidate + the parent node + the causal claim, and must (1) record the parent's leap (§5.1), (2) answer all 12 questions with verdicts pass / partial / fail, and (3) run the directness test (§5.2). Every "pass" requires (a) a short evidence quote, (b) a source, (c) a falsification note: "this pass dies if …". No evidence, no pass.

### 5.1 The leap test (recorded per edge, with evidence)

A node earns its place in the graph by being a discontinuity, so every evaluation must state the parent's leap explicitly:

- **prior state** — the state of the art immediately before the parent appeared: what the best existing approach could and could not do;
- **the jump** — what discontinuously improved when the parent appeared: the metric or benchmark that jumped, or the capability that was impossible just before and possible just after;
- **the date** — the parent's year.

Time is the organizing dimension: the leap is always measured against the *immediate* predecessor state, never against a distant past. (The worked example is the owner's: many large language models existed before ChatGPT (2022); what made ChatGPT leap was its special training method — reinforcement learning from human feedback. The leap record names that discontinuity, and the directness test then asks which advances directly produced it.)

### 5.2 The directness gate (new in v3, hard gate)

A candidate X survives for parent N only if X **directly** enabled N's leap. The evaluator applies two tests:

- **(a) Counterfactual.** Remove X, and N's leap does not happen when it did — it is delayed, diminished, or takes a different form.
- **(b) No mediation.** There is no other milestone M such that X enabled N only through M. If such an M can be named, X **fails** directness for N, and the rejection is recorded as `mediated_via: M`. X is not unimportant; it is one level too deep, and it is expected to be rediscovered when M is expanded.

A large year gap between X and N is a red flag demanding a stronger directness argument (why did nothing in between mediate?), not an automatic fail. A "partial" directness verdict — the mediation question genuinely unresolvable on current evidence — does **not** satisfy the gate.

> **Gates (v3):** A candidate survives only if Q1 **OR** Q2 passes (it flipped an impossibility for this child, or opened the space) **AND** Q3 is not a clear fail (not demonstrably substitutable) **AND** the directness test passes with no mediator named.

**Gate guidance (v3.1): substrate is not a rejection class.** A hardware or data candidate is judged by exactly the same tests as any other candidate — never rejected merely for being "substrate" or "infrastructure":

- **(i) Counterfactual, at the parent's time and scale.** Could the parent's leap have happened *when it did, at the scale it did*, without this hardware capability or this data? An algorithm can exist on paper for years before the hardware lets it run; that gap is precisely what this test measures.
- **(ii) Direct consumption.** Did the parent actually use it — named in the paper or system, part of the demonstrated result? Consumption is what separates an enabler from background conditions.
- **(iii) Mediation still applies.** If the candidate reached the parent only through a named intermediate milestone, it fails directness here and resurfaces when that milestone is expanded — hardware and data get no exemption from the mediation check, and no special suspicion either.

The line is between the **specific enabling step** and **generic infrastructure**. The specific step can pass: a programmability layer the parent's code was actually written in, a cluster-scale training capability the run demonstrably used, the dataset the headline result was produced on. Generic infrastructure fails: electricity, the transistor in the abstract, "computers". Earlier run-01 verdicts that rejected candidates *as a class* under a "substrate" label (CUDA, GPUs, backprop-era compute, datasets) are superseded by this guidance for future judgments; the verdicts themselves are not retroactively changed by this edit — the retro-sweep (RUNBOOK.md) handles discovery through the normal gates.

Survivors are ranked by their score across the remaining nine questions and capped at 20 per parent node. Everything else is recorded as rejected-with-reason (rejections are data: they feed the `{already_rejected}` list and keep later rounds honest; mediated rejections additionally name the mediator, which tells the frontier where the rejected candidate should resurface).

## §6 Adversarial verification

Survivors get a second, hostile pass. The verifier's job is to kill the node: attack Q1 (was it truly impossible before, or merely hard, expensive, or unfashionable?); attack Q3 with the multiples test (search for independent simultaneous discoverers — if two others did it in the same decade, necessity is downgraded to "ripe"); check the date and the causal direction; and — new in v3 — run the **mediation attack** on every accepted edge X→N: deliberately try to name an intermediate milestone M such that X enabled N only through M (X→M→N). A convincing M kills the edge (the rejection is logged as `mediated_via: M`, and X is expected to resurface when M is expanded) or, where X also had a direct channel but the mediated path dominates, downgrades the edge and caps the node at provisional. Nodes that survive all attacks are marked verified; the rest stay provisional, and the interactive page shows the distinction.

## §7 Budgets and stop conditions

| Item | Value |
|---|---|
| Per parent node | ≈100 raw candidates → cap 20 survivors |
| Depth cap | ~10 |
| Global node budget for the day run | ~2,000 nodes (checkpointed; if the budget ends the run early, the graph is still complete and publishable as-is) |

A node stops expanding when:

- fewer than 5 candidates pass the gates, OR
- its candidate pool falls before ~1500 where the written record thins out, OR
- it duplicates an already-expanded node.

**Frontier control:** if the frontier exceeds the per-depth budget, expand highest-scoring nodes first (best-first, not breadth-first).

## §8 Worked example

The root's first round, illustrative (v3):

**Parent:** The modern AI agent (2020s). Its leap (§5.1): against the immediate prior state — capable but unsteerable text completers — instruction-following models in a reason–act loop with tools turned a text completer into a general task executor.

A few of the ~100 the scout should find, by lens:

- **The differentiating move** — RLHF (2022), the training method that made ChatGPT's leap over the LLMs that preceded it; instruction tuning (2021).
- **First-order components** — Transformer architecture (2017); large-scale pretraining, GPT-3 generation (2020).
- **Contemporaneous accounts** — ReAct (2022), the reason–act loop pattern the agent is built from; chain-of-thought prompting (2022).
- **Infrastructure at hand** — the hosted LLM API / function-calling surface (2022–23).

And a few the scout may borderline-propose that the directness gate exists to catch at this level:

- **Gradient descent** — genuinely fundamental, but it reached the agent only through backpropagation-trained networks: rejected here as `mediated_via: Backpropagation`, to be rediscovered deeper.
- **Backpropagation itself** — reached the agent only through the architectures and training runs it made possible: `mediated_via: Transformer architecture` (and pretraining).
- **Bahdanau attention (2014)** — reached the agent through the Transformer: `mediated_via: Transformer architecture`; it resurfaces, correctly, when the Transformer is expanded.
- **Stored-program architecture (1945), cross-entropy loss (1948), the perceptron (1958)** — mediated ancestors all; each belongs to a deeper level.

Then each candidate faces the leap record, the 12 questions, the directness test, and the cap of 20, and each survivor (say, RLHF) becomes a parent: "Before RLHF, deployed language models could not be steered to follow human intent reliably because pretraining optimizes text completion, not judged helpfulness…" and the recursion walks back — one leap at a time.

## §9 Output and the interactive page

The run emits one graph file: nodes, edges, per-node verdicts and evidence. The page renders it as an explorable tree/DAG: click a node → its bottleneck sentence, its 12-question verdict table, its sources, its verified/provisional status; expand/collapse branches; a timeline mode laying nodes out by year so readers watch the chain converge backwards. Built first as a standalone page for owner review, then integrated into AI Praxis Lab as a The Behind piece.

## §10 What happens next

1. Owner approves this design (one open item at design time: the gate rule in §5 — subsequently approved 2026-11-24).
2. The design replaces the old question grammar in the llm-wiki design page, with the §3 literature anchors added.
3. The Batch 0 harness is adjusted to this spec (in this repo, that harness is RUNBOOK.md + pipeline/).
4. The day-long run starts from the root.
5. The interactive page is generated from the resulting graph and placed on AI Praxis Lab.
6. (v3.1) A one-time **retro-sweep** re-checks the already-expanded nodes under the new Hardware & devices and Data lenses, so the hardware and data enablers the early expansions missed can enter through the normal gates (protocol in RUNBOOK.md).

## Changelog

**v3.1 — 2026-11-24 (owner feedback on the run-01 graph: hardware & data blindness).** The owner reviewed the growing run-01 graph and found a systematic blindness: *every node so far is an algorithm or method — there are no physical, hardware, or device milestones at all, and no data milestones either.* As the recursion deepens it must reach the hardware that made the computation possible, and hardware should in fact appear at relatively shallow depth: an algorithm can exist on paper for years before the hardware lets it run. Large-scale data collection and curation work is likewise a major milestone type in its own right. Diagnosis, from the run's own logs: (1) the scout lenses skew to methods and papers, so hardware/data candidates rarely surface; (2) a standing judgment hardened across expansions — "substrate rejected as such" — which rejected CUDA, GPUs, backprop-era compute, and datasets as a class instead of applying the counterfactual test per candidate; (3) the directness gate's mediation check routed enabling hardware into "substrate" rather than asking whether the parent directly consumed it. Changes:

1. **Two new scout lenses** (§4.2): **Hardware & devices** — compute hardware, accelerators, memory/interconnect, and the software layer that made the hardware usable (e.g. CUDA-class programmability milestones), plus devices; and **Data** — datasets, benchmarks-as-data, and large-scale data collection/curation pipelines. Both lenses are mandatory for every parent, especially compute-hungry or data-hungry leaps.
2. **Gate guidance: substrate is not a rejection class** (§5.2): a hardware or data candidate is judged by the same tests as any candidate — the counterfactual at the parent's time and scale, direct consumption by the parent, and the mediation check. The specific enabling step the leap directly consumed can pass; generic infrastructure (electricity, the transistor in the abstract, "computers") still fails. The "substrate rejected as such" precedents in run-01 are superseded by this rule for future judgments; existing verdicts are NOT retroactively changed by this edit.
3. **Retro-sweep** (RUNBOOK.md): a one-time supplementary pass over already-expanded nodes — priority: the root (the modern AI agent), large-scale pretraining/GPT-3, Transformer, RLHF, in-context learning — scouting only the hardware and data lenses for missed proximate enablers, run through the full identity / 12-question / directness / verifier loop, with edges recorded like any expansion and marked as retro-sweep in the run log. Executed as its own run session after this revision lands.
4. Unchanged: the 12 questions, the directness gate itself, §4.5 identity resolution, gates' question side, budgets, caps, checkpointing.

**v3 — 2026-11-24 (owner feedback on the v2 smoke-test graph).** The owner reviewed the smoke graph and found the structural flaw: *gradient descent appeared as a direct predecessor of the root at depth 1*. Gradient descent is genuinely important, but it should surface only many layers deep. Diagnosis: the v2 gates score **importance**, and importance is transitive, so deep fundamentals leak into layer 1. The recursion's core must instead be the **proximate leap**: each step back finds the direct enabler of the current node's leap. Changes:

1. **Directness gate** (new hard gate, §5.2): counterfactual test + mediation check; mediated candidates are rejected with the mediator named (`mediated_via: M`) and are expected to resurface when M is expanded. A large year gap is a red flag, not an automatic fail.
2. **Leap test** (§5.1): every node is a leap — a discontinuous, widely recognized improvement over the immediately prior state of the art; the evaluation records prior state / what jumped / date, with evidence. Time is a first-class dimension (the owner's example: ChatGPT, 2022 — many LLMs preceded it; its leap is tied to its special training method, RLHF; then RLHF's own enablers, and separately the Transformer, 2017, whose arrival was a metric/benchmark jump).
3. **Scout re-aimed** (§4): lenses and prompt now target the parent's immediate pre-history and its differentiating move; distant fundamentals are explicitly out of scope at each level.
4. **Verifier mediation attack** (§6): for every accepted edge X→N the verifier must try to name an intermediate M (X→M→N); a convincing M kills or downgrades the edge and logs the mediation.
5. Unchanged: the 12 questions, §4.5 identity resolution, gates' question side, budgets, caps, checkpointing.

**v2 — 2026-11-24.** The 12-question design as approved by the owner (gate rule confirmed 2026-11-24); smoke test at depth 2 executed under this version (see SMOKE_TEST.md).

---

*The Behind 01 · Design v3.1 · Prepared for Jerry Yu · 2026-11-24.*
