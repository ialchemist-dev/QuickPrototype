# The Behind 01 — Scout Lens Framework: An Exhaustive-by-Construction Design

**Status: PROPOSAL — awaiting owner review. Do not implement.**
**Date: 2026-11-24 · Prepared in response to the owner's rejection of the accreted lens list (v3's 10 lenses + v3.1's 2).**
**Scope of this document: the scout's question set only. The 12 evaluation questions, the directness gate, identity resolution, budgets-as-caps, and checkpointing are untouched except where §8 proposes a raw-target change.**

---

## 1. Why this document exists

The current 12 lenses were not derived; they accumulated. The original 10 were written ad hoc for the v2/v3 design, and when the owner found run-01's graph contained no hardware or data milestones at all, two more (Hardware & devices, Data) were patched on. The owner's objection, in substance:

> Patching lenses one gap at a time cannot guarantee the exploration design covers all important directions. The questions the scout asks should be exhaustive by construction.

He is right, and the hardware/data blindness is the proof: the miss was not a scout's carelessness, it was a question nobody's lens asked. A list built by brainstorming has no closure property — there is no argument you can make about what it *doesn't* contain. This proposal replaces the list with a framework in which the lens set is *generated* from a decomposition of the problem, so that coverage can be argued, audited, and falsified — and §6 falsifies it against the run's own history before asking the owner to believe it.

**Design principle.** A lens is not a topic. A lens is a *question the scout must answer about the parent*, phrased in the vocabulary in which that kind of answer is documented. The framework below derives the questions from two independent axes — what kind of thing an enabler can be, and how it can enable — and assigns at least one lens to every combination that can occur in reality. Combinations that cannot occur are named and dismissed with reasons (§3.2); the dismissal list is part of the exhaustiveness argument, not an appendix.

---

## 2. Method: derive the lenses, don't brainstorm them

A candidate in this pipeline is a **direct enabler of a parent leap**: a dated, named advance whose arrival shortly before the parent closed the gap between the parent's immediate prior state and the parent itself. Any such enabler, whatever it is, must satisfy three things:

1. It is **some kind of thing** — it belongs to some category of entity that can come into existence or change.
2. It stands in **some causal relation** to the parent — there is a specific way in which it enabled.
3. It **changed before the leap** — this is the trace's standing precondition (proximate, dated, earlier), not an axis.

The framework is the cross-product of (1) and (2), pruned by reality.

### 2.1 Axis 1 — the enabler ontology (what kinds of things can enable a leap)

A leap is a discontinuity in what a practice can do. For the leap to happen, something in the world must have become different. The stocks that can change:

| Code | Kind | The change that enables sounds like… | Examples |
|---|---|---|---|
| K1 | **Theory & explanatory knowledge** | "we now know / can prove / understand that…" | theorems, laws, statistical models, obstruction analyses |
| K2 | **Methods, algorithms & recipes** | "we now have a procedure for…" | algorithms, training recipes, protocols, prompting patterns |
| K3 | **Architectures & components** | "there is now a design / part that…" | mechanisms, modules, system architectures |
| K4 | **Data & corpora** | "there now exist records of…" | datasets, corpora, curated collections, data pipelines |
| K5 | **Machines & devices** | "there is now physical plant that can…" | processors, accelerators, clusters, end devices, lab machines |
| K6 | **Software & platforms** | "there is now code / a service that…" | libraries, frameworks, APIs, hosted services, programmability layers |
| K7 | **Instruments, metrics & evaluation schemes** | "we can now see / measure / compare…" | sensors, instruments, metrics, benchmarks-as-tests |
| K8 | **Standards & interfaces** | "there is now an agreed spec for…" | file formats, protocols, interface specifications, standard dimensions |
| K9 | **Problem formulations & demand** | "someone has now posed / asked for…" | task formulations, challenges, prizes-as-questions, articulated needs |
| K10 | **People, institutions & incentives** | "someone is now organized / funded / moved to…" | labs, programs, funders, communities, key-person moves |
| K11 | **Materials & physical phenomena** | "there is now a substance / harnessed effect that…" | reagents, substances, newly usable physical or biological effects |

**Why this is closed.** Any enabler is a change in the world, and a change is a change in one of: what is *known* (K1), what is *known how* (K2), what *designs exist* (K3), what *records exist* (K4), what *physical plant exists* (K5, K11 — plant as machinery vs. plant as substance/effect), what *code and services exist* (K6), what can be *observed* (K7), what *coordination agreements exist* (K8), what is *being asked* (K9), or *who is organized to act* (K10). §5.2 names the honest residuals (tacit knowledge, classified work, chance) — they are limits of *documentation*, not holes in the kind space: an undocumented enabler is still one of these kinds, merely unfindable by search.

**Classification rules** (a candidate gets exactly one primary kind — the kind under which its enabling change occurred):

- **Benchmark rule.** A benchmark is K4 when consumed as training data, K7 when used as the test that registered or guided the leap, K9 when posed as a challenge. Same artifact, three possible kinds — classified by use in *this* parent relation.
- **Instrument rule.** A device whose enabling change is "we could now compute/actuate" is K5; a device whose enabling change is "we could now observe" is K7, whatever it is made of.
- **Platform rule.** A software layer whose enabling change is "the hardware became usable" (CUDA over the GPU) is K6; the hardware is K5. The pair is expected to co-occur and both are in scope.
- **Carrier rule.** Knowledge that exists only inside a person is K10 for discovery purposes (it travels when the person travels), even though its content is K1/K2.

### 2.2 Axis 2 — the enabling relations (how a thing can enable a leap)

To enable is to stand in one of these relations to the parent. (The complement — "mere background condition" — is exactly what the directness gate exists to exclude; it is not a relation a *direct* enabler stands in.)

| Code | Relation | Test sentence |
|---|---|---|
| R1 | **Incorporated** — the enabler is a part of the parent | "{parent} contains / is built out of {X}" |
| R2 | **Ancestor-modified** — the parent is a direct alteration or recombination of the enabler | "{parent} is {X}, changed in the following way…" |
| R3 | **Consumed** — the parent used the enabler up as an input | "{parent} ran on / was trained on / was made from {X}" |
| R4 | **Wielded** — the enabler was the tool, platform, or service used to build or run the parent, neither part nor input | "{parent} was built / run using {X}" |
| R5 | **Revealed** — the enabler made the phenomenon, or the improvement, observable or measurable | "without {X}, the leap could not have been seen, tuned, or proven" |
| R6 | **Posed** — the enabler formulated the problem, task, or objective the parent answers | "{parent} is an answer to the question {X} posed" |
| R7 | **Defined-against** — the enabler is the incumbent or reference point whose limits defined the leap | "{parent}'s leap is measured against {X}" |
| R8 | **Imported** — the enabler originated in a different field and was transferred in | "{X} came from {other field}" |
| R9 | **Ripened** — the enabler changed the surrounding conditions (cost, availability, demand) so the leap became possible or pointed *then* | "{parent} happened in {year} rather than earlier because {X} changed" |
| R10 | **Carried** — a person or institution transported the enabler, or organized its transport, into the parent's lineage | "{X} arrived at {parent} because {carrier} moved / convened / funded" |

R8 and R10 are *modifier* relations: an imported or carried enabler also stands in one of R1–R7 to the parent. They earn their own lenses anyway, because the *search vocabulary* differs — you find imports by searching the *other* field's literature, and carriers by searching biographies and institutional histories, not the parent's own field.

### 2.3 From matrix to lenses

The full matrix is 11 kinds × 10 relations = 110 cells. §3 tabulates every cell with one of three marks:

- a **lens number** — a lens asks this cell's question directly;
- **≡Ln** — the cell is realizable, but its enablers are found by the same searches as lens *n* (stated, not assumed);
- **✕ + reason code** — the cell cannot occur; §3.2 gives the reason.

Lenses are then defined at the granularity where *search behaviour* differs: cells that share a lens share query vocabulary. This is the "argued equivalent" of one-lens-per-cell — a lens per cell would multiply near-identical searches (e.g. K1×R7, K2×R7, K3×R7… are one search: "what was the incumbent?"), while a lens per kind (the v3.1 failure mode) merges questions with different vocabularies into a grab-bag (old lens 7, "infrastructure at hand", is exactly that failure).

Two further lenses are **source-genre passes**, not matrix cells: lineage surveys (L3) and contemporaneous accounts (L23). They search *genres of documents* (reference works; reportage from the moment) rather than kinds of enablers, and they catch enablers of any cell whose documentation is narrative rather than topical. They are retained from the old list, demoted to their proper status, and capped separately in the budget (§8).

---

## 3. The matrix

Rows: kinds K1–K11. Columns: relations R1–R10. Lens numbers refer to §4.

|  | R1 Incorp. | R2 Ancestor | R3 Consumed | R4 Wielded | R5 Revealed | R6 Posed | R7 Against | R8 Imported | R9 Ripened | R10 Carried |
|---|---|---|---|---|---|---|---|---|---|---|
| **K1 Theory** | **L1** | **L2** | ✕1 | ≡L1 | **L17** | **L4/L5** | ≡L6 | **L19** | ≡L22 | ≡L20 |
| **K2 Methods** | **L1** | **L2** | ✕1 | **L11** | ✕5 | ≡L4 | ≡L6 | **L19** | ≡L22 | ≡L20 |
| **K3 Architectures** | **L1** | **L2** | ✕1 | ≡L13 | ≡L18 | ✕4 | ≡L6 | **L19** | ≡L22 | ≡L20 |
| **K4 Data** | **L8** | **L8** | **L8** | ≡L8 | ✕5 | ≡L4 | ≡L6 | **L19** | ≡L22 | ≡L21 |
| **K5 Machines** | **L9** | ≡L9 | **L9** | **L14** | ✕5 | ✕4 | ≡L6 | **L19** | ≡L22 | ≡L21 |
| **K6 Software** | ≡L13 | ≡L13 | ✕1 | **L12/L13/L15** | ✕5 | ≡L4 | ≡L6 | **L19** | ≡L22 | ≡L21 |
| **K7 Instruments/metrics** | ≡L17 | ≡L17 | ✕1 | **L18** | **L17/L18** | **L4** | ≡L6 | **L19** | ≡L22 | ≡L21 |
| **K8 Standards** | **L16** | ≡L16 | ✕1 | **L16** | ✕3 | ≡L4 | ≡L6 | **L19** | ≡L22 | ≡L21 |
| **K9 Problems/demand** | ✕2 | **L4** | ✕1 | ≡L4 | ✕3 | **L4** | ≡L6 | **L19** | **L22** | ≡L21 |
| **K10 People/institutions** | ✕2 | ✕7 | ✕1 | **L21** | ✕3 | **L21** | ✕6 | ≡L20 | **L21** | **L20/L21** |
| **K11 Materials/phenomena** | **L10** | ≡L10 | **L10** | ≡L10 | ✕3 | ✕4 | ≡L6 | **L19** | ≡L22 | ✕8 |

### 3.1 Reading the matrix

- Every row has at least two direct-lens cells; every column has at least two. No kind and no relation is lens-less.
- The dense columns are R1/R2 (constitution — the old framework's home turf) and the sparse ones are R5/R6/R9/R10 (observation, problem-posing, timing, carriage) — precisely the territory the accreted list covered thinly or not at all. The matrix makes the old list's bias *visible*: old lenses 1–3, 6, 8, 10 all live in R1/R2/R4.
- ≡ marks are claims, and they are the weakest part of the closure argument (see §5.2, residual risk 4). Each is justified in one line in the lens definitions (§4) where the lens's query set is specified to actually include the ≡ cell's vocabulary.

### 3.2 Dismissed cells — the impossibility list

| Code | Reason | Cells dismissed |
|---|---|---|
| ✕1 | **Non-rivalry.** Knowledge, methods, designs, code, metrics, and formulations are not used up by use; nothing in these kinds is *consumed*. (What is consumed when code runs is compute — K5×R3.) | K1,K2,K3,K6,K7,K8,K9,K10 × R3 (8 cells) |
| ✕2 | **Not-a-part.** A formulation or a person cannot be a *component* of an artifact in this trace's node grammar. Formulations guide (R6/R4); people carry and organize (R10/R4). | K9×R1, K10×R1 |
| ✕3 | **No observation without an observer.** Standards, problems, institutions, and materials do not themselves reveal anything; the instruments built to a standard, posed by an institution, or made from a material do — and those are K7. | K8,K9,K10,K11 × R5 |
| ✕4 | **Posing requires a representation.** Machines, designs, and materials do not formulate problems. (A design's *limits* can pose the parent's problem — but the posing is done by the analysis of those limits, K1×R6 → L5.) | K3,K5,K11 × R6 |
| ✕5 | **Reclassified by rule.** The cell describes something real, but a §2.1 classification rule assigns it to another kind: an evaluation procedure is K7, not K2; data used as a test is K7, not K4; a machine whose enabling change is observability is K7, not K5; an evaluation harness is K7, not K6. The enabler is still covered — under its primary kind's lens. | K2×R5, K4×R5, K5×R5, K6×R5 |
| ✕6 | **The rival is the artifact, not the actor.** An institution can be a competitor, but what the parent's leap is measured against is the rival's *system* (K3/K6×R7 → L6). | K10×R7 |
| ✕7 | **Ancestry requires an artifact lineage.** An institution is not modified into the parent; its *prior products* are, and those are K3/K6×R2 → L2. | K10×R2 |
| ✕8 | **Carriage of a material is logistics.** A substance reaches the parent by becoming *available* (R9 → L22), not by being carried as knowledge (R10). | K11×R10 |

Total dismissed: 24 cells. Covered by a direct lens: 40 cells. Covered by an argued ≡: 46 cells. 40 + 46 + 24 = 110. ✓ *(Totals corrected 2026-11-24, at implementation: as first written this line read 41/44/25, which did not match the tabulation above — an independent cell-by-cell recount gives 40/46/24, and the per-code list in this section also sums to 24. The same correction is applied to the restated total in §5.2, risk 4.)*

---

## 4. The lens set (23 lenses)

Conventions: `{parent}`, `{parent_year}`, `{domain}`, `{capability}`, `{prior_approach}`, `{bottleneck}` are the existing scout-prompt slots. Query templates are starting points; the standing rule (≥2 variants per lens) is unchanged. Each lens states the cells it covers, including its ≡ obligations — a lens that claims a ≡ cell must run queries in that cell's vocabulary, or the claim lapses.

### Family I — Constitution: what the parent is made of, and what it descends from

**L1 · Components incorporated** — *Cells: K1×R1, K2×R1, K3×R1.*
Question: *What parts — mechanisms, procedures, theorems — are inside the parent, one step in and no deeper?*
Queries: `"{parent} architecture components"` · `"{parent} built on what {mechanism/theorem/model}"` · `"{component} in {parent} design"`.
(The theorem-in-the-design vocabulary is this lens's ≡ duty to K1×R4: a theorem the parent *uses* is found by the same "built on" searches.)

**L2 · Ancestor modified** — *Cells: K2×R2, K3×R2, K1×R2.*
Question: *Which single direct precursor did the parent alter, extend, or recombine — the thing the parent is a changed version of?*
Queries: `"{parent} extended {precursor}"` · `"{parent} based on {prior_system} difference"` · `"from {prior_system} to {parent} what changed"`.

**L3 · Lineage surveys** *(source-genre pass)* — *Cells: all, via reference works.*
Question: *What do surveys, textbooks, and histories of the immediate lineage list as the parent's ancestry?*
Queries: `"timeline of {domain} {parent_year}"` · `"history of {parent} development"` · `"survey of {lineage} before {parent_year}"`.

### Family II — The problem side: what the parent answers

**L4 · Problem posed** — *Cells: K9×R6, K9×R2, K1×R6 (formulation side), K7×R6, ≡ K2×R6, K4×R6, K6×R6, K8×R6, K9×R4.*
Question: *Who first formulated the task, objective, or challenge the parent answers — and when was it re-posed in the form the parent actually answered?*
Queries: `"{task} first formulated"` · `"{challenge} proposed {domain}"` · `"{parent} task definition origin"` · `"{benchmark_task} introduced as a problem"`.
(This lens owns the formulation vocabulary for every kind: a benchmark-as-challenge, a platform constraint, and a theory's open problem are all found by asking who *posed* the question.)

**L5 · Obstruction diagnosed** — *Cells: K1×R6 (diagnosis side), K1×R2 (analysis side).*
Question: *Who first analyzed and named the bottleneck the parent removed — the diagnosis the parent's design is an answer to, whether or not the diagnostician proposed the cure?*
Queries: `"analysis of why {prior_approach} fails"` · `"{bottleneck} first shown / proved"` · `"limitations of {prior_approach} theoretical analysis"`.
(No old lens asked this question. §6.1 shows a run-01 survivor that only this lens asks for.)

**L6 · Incumbent defined-against** — *Cells: R7 for all kinds (≡ obligations: K1,K2,K3,K4,K5,K6,K7,K8,K9,K11 × R7).*
Question: *What was the parent compared against — the incumbent systems, methods, metrics, and materials whose documented limits define the leap?*
Queries: `"{parent} vs {predecessor_system} comparison"` · `"limitations of {prior_approach}"` · `"state of the art before {parent}"`.

**L7 · Negative space** — *Cells: the failure record adjacent to R6/R7.*
Question: *What did the immediate predecessors try that failed, and what specific fix replaced each failure?*
Queries: `"failed attempts at {capability} before {parent}"` · `"{prior_approach} problems solved by {parent}"`.

### Family III — Consumed: what the parent used up

**L8 · Data consumed** — *Cells: K4×R3, K4×R1, K4×R2, ≡ K4×R4.*
Question: *What records did the parent actually eat — training corpora, datasets, built-in indexes — and what collection/curation work produced them?*
Queries: `"{parent} training data"` · `"{dataset} collected how"` · `"data curation pipeline behind {parent}"` · `"{parent} trained on what corpus"`.
(The production-pipeline queries are the ≡ duty to K4×R4: data wielded during construction — lexicons, reference corpora — surfaces in the same searches.)

**L9 · Compute & machines consumed** — *Cells: K5×R3, K5×R1, ≡ K5×R2.*
Question: *What physical plant did the leap actually run on or ship in — which machines, how many, at what scale — and, when the parent is itself a machine, what machine generation did it modify?*
Queries: `"{parent} trained on how many {accelerator}"` · `"{parent} compute used hardware"` · `"{parent} ran on what machine"` · `"{parent} cluster / supercomputer built for"`.

**L10 · Materials & phenomena harnessed** — *Cells: K11×R1, K11×R3, ≡ K11×R2, K11×R4.*
Question: *What substance, reagent, or newly harnessed physical/biological effect does the parent physically depend on — built in, used up, or wielded?*
Queries: `"{parent} depends on what material / effect"` · `"{reagent} first used in {parent}"` · `"{effect} harnessed for {capability}"`.
(Usually dry for software parents — and the dryness must be recorded, §8. It is the lens that keeps the framework honest below the software layer and outside AI entirely; §6.3's PCR check runs on it.)

### Family IV — Wielded: what the parent was built and run with

**L11 · Recipe & process** — *Cells: K2×R4.*
Question: *What procedure — training recipe, manufacturing process, run-time protocol — was wielded to produce or operate the parent?*
Queries: `"{parent} training method"` · `"how was {parent} made"` · `"{technique} first used for {parent}"`.

**L12 · Programmability layer** — *Cells: K6×R4 (over K5).*
Question: *What software layer made the consumed hardware usable — the programming model, compiler, or abstraction without which the machines in L9 could not have been applied to this problem?*
Queries: `"{accelerator} programming model introduced"` · `"{platform} first used to {verb} {domain} problems"` · `"{parent} code written in {layer}"`.

**L13 · Frameworks & software tooling** — *Cells: K6×R4 (build side), ≡ K6×R1, K6×R2, K3×R4.*
Question: *What libraries, frameworks, and off-the-shelf components was the parent built with or out of?*
Queries: `"{parent} built with what framework / library"` · `"{parent} implementation based on"` · `"{parent} used {framework} for"`.

**L14 · Equipment wielded** — *Cells: K5×R4.*
Question: *What physical equipment — lab machines, fabrication tools, capture rigs — was used to produce or test the parent, without being part of it or consumed by it?*
Queries: `"{parent} produced using what equipment"` · `"{machine} automated {process} {parent_year}"` · `"apparatus used to build {parent}"`.

**L15 · Services & APIs** — *Cells: K6×R4 (run side).*
Question: *What hosted services, APIs, or platforms does the parent run on or call at run time?*
Queries: `"{parent} built on {platform} API"` · `"{service} launched {parent_year} enabled"` · `"{parent} runs on what service"`.

**L16 · Standards & interfaces** — *Cells: K8×R1, K8×R4, ≡ K8×R2.*
Question: *What agreed spec — format, protocol, interface, standard dimension — does the parent implement, or interoperate through?*
Queries: `"{parent} implements what standard / specification"` · `"{interface} standard adopted {parent_year}"` · `"{protocol} specification enabled {parent}"`.

### Family V — Observation: how the leap was seen

**L17 · Benchmarks & metrics** — *Cells: K7×R5 (scheme side), K1×R5, ≡ K7×R1, K7×R2.*
Question: *What metric, benchmark-as-test, or measurement model registered the leap — made the improvement visible, comparable, or optimizable — including metrics built into the parent's own objective?*
Queries: `"{parent} benchmark results"` · `"{metric} introduced"` · `"evaluation of {parent} vs prior"` · `"{parent} optimized what metric"`.

**L18 · Instruments of observation** — *Cells: K7×R5 (apparatus side), K7×R4, ≡ K3×R5.*
Question: *What instrument, sensor, or diagnostic apparatus made the phenomenon — or the parent's behaviour — observable in the first place, including instruments wielded during development?*
Queries: `"{phenomenon} first measured / observed with"` · `"{instrument} made {measurement} possible"` · `"diagnostic for {parent} behaviour"`.

### Family VI — Origin & timing: where it came from, and why then

**L19 · Cross-field import** — *Cells: R8 for all kinds (K1–K9, K11 × R8).*
Question: *Which enablers originated in a different field and were transferred in — and what is the other field's name for them?*
Queries: `"{technique} originally from {other_field} applied to {domain}"` · `"{parent} borrowed from {other_field}"` · `"{method} first used in {other_field} then {domain}"`.
(Queries must be run from the *donor* field's vocabulary, not the parent's — that is what makes this a separate lens rather than a note on the others.)

**L20 · Creator lineage** — *Cells: K10×R10 (person side), ≡ K1,K2,K3 × R10.*
Question: *What did the parent's makers themselves do immediately before — and who physically carried the key knowledge into the room?*
Queries: `"{creator} previous work before {parent}"` · `"{creator} moved from {lab} to {lab}"` · `"{parent} team background"`.

**L21 · Institutions, funding & incentives** — *Cells: K10×R4, K10×R6, K10×R9, ≡ K4,K5,K6,K7,K8,K9 × R10.*
Question: *What organization, program, prize, or funding structure organized, posed, or paid for the work — the institutional vehicle without which the leap does not happen in that place and year?*
Queries: `"{parent} funded by what program"` · `"{lab} launched {project} {parent_year}"` · `"{prize / program} led to {parent}"`.
(**Scope-flagged**: whether this family's survivors may be admitted as nodes is Open Decision 1, §9. The lens runs either way; the gate policy is the owner's call.)

**L22 · Timeliness & cost conditions** — *Cells: R9 for all kinds (≡ obligations across K1–K9, K11 × R9), K9×R9.*
Question: *What changed in the surroundings — a cost curve, an availability event, a release, a demand shift — that made the leap happen in the parent's year rather than five years earlier?*
Queries: `"{capability} became feasible when"` · `"cost of {resource} {parent_year}"` · `"{resource} became available / open-sourced / released {parent_year}"`.
(Candidates from this lens will often fail the directness gate as background — that is expected and fine. The lens exists so that the *gate*, not the scout's silence, makes that judgment, and so that genuinely proximate conditions — a release the parent consumed the month it appeared — are not missed.)

### Meta passes

**L23 · Contemporaneous accounts** *(source-genre pass)* — *Cells: all, via reportage.*
Question: *What did papers, reviews, and reports from the parent's own moment say made it jump?*
Queries: `"{parent} review {parent_year}"` · `"why {parent} is a breakthrough"` · contemporary analysis of `{parent}`.

---

## 5. The exhaustiveness argument

### 5.1 Closure logic

1. **Every direct enabler is a thing of some kind.** By §2.1, it is a change in one of eleven stocks. The kind list is closed by the argument there: there is no twelfth stock for a change to occur in — a change is in what is known, known-how, designed, recorded, built (as machine or as substance), coded, observable, agreed, asked, or organized.
2. **Every direct enabler enables in some way.** By §2.2, it is incorporated, ancestral, consumed, wielded, revealing, posing, defined-against, imported, ripening, or carried — or it is mere background, which is the directness gate's category, not the scout's.
3. **Therefore every direct enabler occupies at least one matrix cell** (imported/carried enablers occupy two: their R1–R7 cell and their R8/R10 cell — redundancy by design).
4. **Every cell that can occur is assigned at least one lens** whose query templates are phrased in that cell's documentation vocabulary (§3, §4); every cell that cannot occur is dismissed with a stated reason (§3.2).
5. **The two source-genre passes (L3, L23) cover the documentation residue**: enablers of any cell that are recorded only inside narratives — surveys and contemporary accounts — rather than under topical keywords.

So: any direct enabler of any leap, *if it is documented under any name in any searchable source*, is discoverable by at least one lens — usually two or three, which is what dedupe overlap is for. That is the strongest claim the design supports, and it is deliberately bounded by the italicized clause.

### 5.2 Residual risks — what this framework can still miss

1. **Tacit knowledge.** Craft skill that was never written down (the technician's hands, the lab's unwritten tricks) is a real enabler class with almost no searchable trace. Partially reachable via L20 (creator lineage — the *person* is documentable even when the skill is not), but the skill itself will not be found. Named, not solved.
2. **Classified and unpublished work.** Industrial and military pre-histories (GPT-3's cluster engineering; GPS's classified decade) are documented late or never. L3/L23 catch the retrospective literature when it exists; when it doesn't, no lens helps.
3. **Vocabulary mismatch.** A lens's templates are phrased in today's standard names. An enabler documented only under a dead name or a foreign-language literature can evade every template. Mitigated, not eliminated, by the meta passes and by the scout's ≥2-variants rule.
4. **The ≡ claims.** 46 of 110 cells are covered by "same searches as lens *n*" arguments. Each is stated in §4, but they are judgments, not proofs; if the owner distrusts one, the fix is cheap (split that cell into its own lens) and the matrix says exactly which split to make. This is the framework's intended maintenance path: future misses should arrive as *named cells*, and the repair is a matrix edit, not another patch on a list.
5. **Admission is not discovery.** The lenses govern what the scout *finds*. Separate pipeline rules can still drop a found enabler — e.g. the resolver's year bound dropped WMT'14 (dated the same year as its parent, seq2seq) in run-01. That is a resolver question, outside this document's scope, but named here because §6.2's third case turns on it.

---

## 6. Validation

The framework was tested three ways before being proposed: against the run's own survivors (6.1), against known misses (6.2), and against leaps outside AI (6.3).

### 6.1 Coverage audit over run-01's existing survivors

Method: for every node in `run-01/graph.json` (41 nodes; the root is the seed and has no parent, leaving 40), the node's parent edge(s) were taken from the graph, and the question asked: *which proposed lens's queries, run for that parent, would have surfaced this node as a candidate?* A survivor no lens would surface falsifies the framework.

| # | Survivor (year) | Parent | Lens(es) that surface it |
|---|---|---|---|
| 1 | In-context learning (2020) | AI agent | L1 (the agent's steering mechanism is incorporated few-shot conditioning), L23 |
| 2 | ReAct (2022) | AI agent | L1 (the agent's loop *is* ReAct), L23 |
| 3 | Transformer architecture (2017) | AI agent | L1 |
| 4 | Large-scale pretraining / GPT-3 (2020) | AI agent | L2 (the agent's base models are its direct descendants), L1 |
| 5 | RLHF (2022) | AI agent | L11 (the recipe that produced the agent's model), L2 |
| 6 | Hosted LLM APIs (2020) | AI agent | **L15** (run-time service) |
| 7 | Chain-of-thought prompting (2022) | AI agent | L11 (run-time procedure), L1 |
| 8 | ChatGPT (2022) | AI agent | L2 (product ancestor), L6 (the incumbent it displaced) |
| 9 | Codex (2021) | AI agent | L2, L1 |
| 10 | Instruction tuning / FLAN (2021) | AI agent | L11 |
| 11 | Retrieval-augmented generation (2020) | AI agent | L1 (architecture incorporated) |
| 12 | InstructGPT (2022) | AI agent | L2, L11 |
| 13 | GPT-2 (2019) | In-context learning; GPT-3 | L2, L6 |
| 14 | Common Crawl (2008) | GPT-3 | **L8** (data consumed) |
| 15 | Sparse Transformer (2019) | GPT-3 | L1, L2 |
| 16 | PPO (2017) | RLHF | L1 (the optimizer inside the recipe) |
| 17 | Deep RL from human preferences (2017) | RLHF | L2 |
| 18 | Learning to summarize from human feedback (2020) | RLHF | L2 |
| 19 | Fine-tuning LMs from human preferences (2019) | RLHF | L2 |
| 20 | GPT-3 (2020, linked) | RLHF | L2 (RLHF is a modification *of* GPT-3 — the artifact modified) |
| 21 | Bahdanau attention (2014) | Transformer | L1, L2 |
| 22 | Sequence-to-sequence learning (2014) | Transformer | L2, L6 |
| 23 | TRPO (2015) | PPO | L2 |
| 24 | REINFORCE (1992) | PPO | L2, L3 |
| 25 | Generalized advantage estimation (2016) | PPO | L1 (estimator component) |
| 26 | Policy gradient theorem (2000) | PPO | **L1** (K1×R1: the theorem inside the design) |
| 27 | Bradley–Terry model (1952) | Christiano et al. | **L19** (psychometrics → RL import), L1 |
| 28 | Inverse reinforcement learning (2000) | Christiano et al. | **L4** (IRL *posed* reward-recovery; Christiano answers it with a different input channel), L2 |
| 29 | TAMER framework (2009) | Christiano et al. | L2, L4 |
| 30 | Bidirectional RNNs (1997) | Bahdanau attention | L1 (RNNsearch's encoder *is* a BRNN) |
| 31 | Graves soft window (2013) | Bahdanau attention | L2 (the mechanism Bahdanau generalized) |
| 32 | LSTM (1997) | Seq2seq; Graves 2013 | L1 (the cell) |
| 33 | RNN language model (2010) | Seq2seq | L1 (the decoder formulation), L2 |
| 34 | Elman recurrent network (1990) | Bidirectional RNNs | L2 |
| 35 | Hochreiter's vanishing-gradient analysis (1991) | LSTM | **L5** (the diagnosis LSTM's design answers) |
| 36 | Mixture density networks (1994) | Graves 2013 | L1 (the output head) |
| 37 | IAM-OnDB handwriting database (2005) | Graves 2013 | **L8** (data consumed) |
| 38 | Generative pretraining / GPT-1 (2018) | GPT-2 | L2 (GPT-2 is GPT-1's recipe at scale); its convergence edge from Transformer is L1 |
| 39 | Byte-pair encoding for NMT (2016) | GPT-1 | L1 (tokenizer component), **L19** (imported from data compression) |
| 40 | Semi-supervised sequence learning (2015) | GPT-1 | L2 |
| 41 | BooksCorpus (2015) | GPT-1 | **L8** (data consumed), L19 (built for movie description, imported into LM training) |

**Result: all 40 non-root nodes are surfaced by at least one proposed lens, most by two (41 audit rows above — GPT-3 is audited once per parent, rows 4 and 20). No falsification of the proposed framework.**

**But the audit did falsify two earlier drafts of this framework, and changed it — reported here because that is what the audit is for:**

- **Falsification A — the diagnosis hole.** A first draft of the matrix gave K1 (theory) a single home under L1 (incorporation). Row 35 breaks that draft: Hochreiter's 1991 thesis is not *inside* LSTM; it is the *diagnosis* LSTM's design answers (K1×R6). Under the old 12 lenses, no lens asks for it either — it entered run-01 through scout improvisation, not through a question the design posed. Fix: K1×R6 was split into L4 (formulations) and **L5 (obstruction diagnosed)**, now a lens of its own. Row 28 (IRL) confirms the same split from the other side: IRL enables Christiano chiefly by *posing* the problem.
- **Falsification B — the services hole.** A kinds-first draft (one lens per kind) put Hosted LLM APIs (row 6) in a single "software & infrastructure" lens with frameworks and hardware — recreating old lens 7's grab-bag, whose queries ("built with what tools") do not ask what a system *runs on at run time*. Fix: K6×R4 was split by role into L12 (programmability), L13 (build tooling), and **L15 (services & APIs, run side)**. The relation axis, not the kind axis, is what separates them.

A pattern worth the owner's attention: the survivors the *old* list covers only by improvisation are exactly rows 6, 14, 27, 28, 35, 37, 41 — services, data, imports, posed problems, diagnoses. The old list's centre of gravity (L1/L2 territory) covers the other 33 comfortably. The framework's new weight sits where the old list was thin, which is the expected signature if the owner's suspicion — *the list was never complete, only familiar* — is correct.

### 6.2 Known-miss cases

Three enablers the owner (and the v3.1 changelog) identified as missed or mishandled. For each: the parent, the lens, and the query that catches it.

**Case 1 — CUDA / GPU computing, for deep-learning leaps and for GPT-3-scale pretraining.**
Two depths, two different catches, and the distinction matters:
- *Parent: a CUDA-era deep-learning leap (AlexNet-class).* CUDA is arguably a **direct** enabler here — AlexNet's implementation (cuda-convnet) was written in CUDA on two GTX 580s. **L12 (programmability layer)**: `"{accelerator} programming model introduced"`, `"CUDA first used to train neural networks"`; corroborated by **L9**: `"AlexNet trained on how many GPUs"` and **L19**: `"graphics processors imported into scientific computing (GPGPU)"`.
- *Parent: GPT-3 (already in run-01).* Here CUDA itself is one level too deep — what GPT-3 *directly* consumed was a specific V100 cluster (built with Microsoft on Azure). **L9 (compute consumed)**: `"GPT-3 trained on what hardware / how many GPUs"`, `"supercomputer built for GPT-3 training"`. CUDA then surfaces at its correct depth when the GPU-training node is expanded, via L12. The framework thus reproduces, by construction, the proximate-leap discipline v3 exists for: the same enabler is depth-1 for one parent and depth-2 for another, and different lenses catch it at each depth.

**Case 2 — ImageNet, for AlexNet (hypothetical parent).**
**L8 (data consumed)**: `"AlexNet trained on what dataset"`, `"ImageNet dataset collected how"` — the second query also surfaces the MTurk labeling pipeline, which is part of why ImageNet is a milestone and not just a file. Corroboration: **L17** (ILSVRC as the benchmark that registered the leap) and **L4** (ILSVRC as the posed challenge). Three lenses, three different relations (R3, R5, R6) — the same artifact in three kinds, per the benchmark rule.

**Case 3 — WMT'14, for seq2seq (in run-01).**
**L8**: `"seq2seq trained on what dataset / corpus"`, `"Sutskever 2014 WMT'14 English-French training data"`. Honest caveat: in run-01 the scout *did* effectively find WMT'14 and the resolver then dropped it at the year bound (it is dated 2014, the same year as seq2seq) — the run log records it among the coeval drops. The lens framework fixes *discovery*; the coeval-drop is a resolver rule and is flagged in §5.2 (risk 5) as a separate question the owner may want to revisit. Coverage by the lens is necessary, not sufficient.

### 6.3 Out-of-domain spot checks

Three famous leaps outside AI, chosen because each is dominated by a *different* family of enablers — if the framework were secretly AI-shaped, at least one of these should break it.

**PCR (Mullis, 1983–85).** The leap: targeted DNA amplification becomes routine.
- Thermostable polymerase (Taq, from *Thermus aquaticus*) — the reagent whose absence forced fresh enzyme every cycle → **L10** (K11×R3), and **L19** (imported from extremophile microbiology).
- Automated oligonucleotide synthesis (phosphoramidite chemistry, 1981) — primers become orderable → **L14** (equipment wielded) / L11 (process).
- The thermal cycler — cycling becomes a machine's job → **L14**.
- Klenow-fragment amplification attempts — the ancestor it modified → **L2**; the gene-synthesis tradition that posed amplification as a need → **L4**.
Verdict: covered; the dominant lens (L10) is one the AI-shaped old list did not have at all.

**GPS (first satellite 1978; full constellation 1990s).** The leap: metre-scale global positioning as a service.
- Atomic clocks flown on the satellites → **L9** (K5×R1, machines incorporated) — with the relativity corrections they require → **L1** (K1 theory in the design).
- TRANSIT, the Navy's predecessor system → **L2**.
- The GPS signal/interface specification (ICD-GPS-200), which let anyone build receivers → **L16** (standards) — the enabler that turned a military system into an ecosystem.
- The DoD program structure that organized and funded it → **L21**.
Verdict: covered — and it exercises L16 and L21, the two lenses AI parents will rarely trigger. A framework built from the AI trace alone would likely have missed both.

**Container shipping (McLean, 1956).** The leap: freight cost per ton collapses by an order of magnitude (the canonical figure: loading a ship falls from $5.86 to $0.16 per ton).
- ISO standardization of container dimensions and corner fittings (1960s) → **L16** — arguably *the* enabler; without it, boxes don't interchange between ships, trains, and trucks.
- Cellular container ships and shipboard/port cranes → **L9/L14**.
- The break-bulk incumbent and its documented costs → **L6**; port-cost pressure as the posed problem → **L4/L22**.
- Sea-Land as the institutional vehicle → **L21**.
Verdict: covered. This is the strongest of the three checks: container shipping has essentially *no* "method" content — its enablers are a standard, machines, and institutions. An ontology derived from software alone would have nothing to say about it; the matrix's K8/K10 rows are what carry it.

---

## 7. Mapping: the old 12 lenses → the new framework

| Old lens | Fate | New home |
|---|---|---|
| 1 Immediate prior state of the art | Subsumed | L6 (Incumbent defined-against) — and its "what was the bottleneck" half sharpened into L5 |
| 2 The differentiating move | Split | L2 (ancestor modified) + L1 (the new thing is often a component) |
| 3 First-order components | Subsumed, widened | L1 — now explicitly includes theorems (K1) and methods (K2) as components, not only subsystems |
| 4 Contemporaneous accounts | Kept, reclassified | L23 — recognized as a source-genre pass, not a content lens |
| 5 Benchmarks & measurement | Split | L17 (metrics/benchmarks-as-tests) + L18 (instruments) — the old lens conflated schemes with apparatus |
| 6 Method / recipe | Subsumed | L11 (Recipe & process) |
| 7 Infrastructure at hand | **Split four ways** | L9 (compute consumed) + L12 (programmability) + L13 (tooling) + L15 (services) — this grab-bag was the single largest structural defect in the old list; "at hand" named no relation |
| 8 Direct transfers | Split | L19 (cross-field import) + L20 (creator lineage) — a technique imported and a person arriving are different searches |
| 9 Negative space | Kept | L7 |
| 10 Timelines of the immediate lineage | Kept, reclassified | L3 — source-genre pass |
| 11 Hardware & devices (v3.1) | Split | L9 (machines consumed/incorporated) + L12 (the programmability half, promoted to its own lens) + L14 (devices as wielded equipment) |
| 12 Data (v3.1) | Subsumed, sharpened | L8 — gains the production-pipeline queries and the K4×R1/R2 cells (data built in, corpus ancestry) |

**Genuinely new** (no old lens asked these questions): **L4** Problem posed · **L5** Obstruction diagnosed · **L10** Materials & phenomena · **L16** Standards & interfaces · **L21** Institutions & incentives · **L22** Timeliness & cost conditions.
**New by split** (the old list had the words but not the question): **L12** Programmability layer · **L15** Services & APIs · **L18** Instruments · **L20** Creator lineage (as distinct from technique transfer).

---

## 8. Cost: what 23 lenses do to the candidate budget

Observed run-01 economics (15 expansions): scouts returned 75–123 raw candidates per expansion against `raw_target = 100`; resolution yielded ~63–114 distinct; survivors per expansion were 1–5 after the root's 12 (the cap of 20 has never bound). **Evaluation is the expensive step** — every distinct candidate costs a leap record check, 12 evidenced verdicts, and a directness test. The survivor cap, not the scout, governs graph growth.

The new framework's arithmetic:

- 21 content lenses. Narrower lenses yield fewer candidates each; at ~5–6 raw per lens the scout returns **~115–135 raw**, vs. ~100 today.
- The two meta passes (L3, L23) are source passes feeding the content lenses; cap them at ~10 candidates combined and **exclude them from raw_target accounting** (Open Decision 4).
- Expected distinct yield: **~85–100**, i.e. evaluation cost rises roughly **+30–40% per expansion**. Node growth is unchanged (survivor cap 20; observed survivors ≤12, at the root).

**Proposal:** raise the FULL profile's `raw_target` from 100 to **140**, with two guardrails:

1. **Per-lens floor, not per-lens quota-chasing.** Each content lens must return ≥3 candidates *or* an explicit **dry note** ("L10 dry for this parent: no material dependency found in {sources}") recorded in the expansion's work file. A dry note is data — it converts a lens's silence from an oversight into evidence, and it is what makes per-expansion coverage auditable after the fact. (This is the operational form of the owner's exhaustiveness demand: not "trust the list", but "show me, per parent, that every question was asked".)
2. **No per-lens cap.** Cross-lens duplication is signal, not waste — a candidate surfaced by three lenses is likelier proximate — and dedupe already absorbs it.

The alternative — keep `raw_target = 100` and let 23 lenses share it (~4.3 per lens) — is **not recommended**: it recreates the original failure in a subtler form, starving exactly the unfamiliar lenses (L10, L16, L21, L22) whose candidates the scout finds slowest, while the fluent L1/L2 searches fill the budget first. Exhaustiveness that evaporates under a budget cap is not exhaustiveness.

Smoke profile scales proportionally (60 → 85) if the owner wants the smoke test to remain a faithful miniature.

Retro-sweep implication: the v3.1 retro-sweep (RUNBOOK §9) currently re-checks expanded nodes under lenses 11–12 only. Under this framework the honest sweep is: already-expanded nodes × the *genuinely new* lenses (L4, L5, L10, L12, L16, L21, L22) — not a full re-scout. Costed in Open Decision 5.

---

## 9. Open decisions for the owner

1. **Are institutional enablers admissible as nodes?** L21 will surface labs, programs, and prizes (e.g. the DoD for GPS; a funder's program for an AI leap). Options: (a) admit them as nodes when they pass the same gates — the schema already has `type: institution`; (b) scout them but record as context on edges, never as nodes; (c) drop L21 entirely. **Recommendation: (a).** Excluding a kind by class, after it has been *found* and has passed the counterfactual and directness tests, is the v3.1 "substrate" error in a new costume. But it does change the graph's flavour toward the sociological, and the trace is the owner's — hence a decision, not a default. Note the asymmetry: choosing (b) or (c) should be recorded as a *scope* decision ("this trace is of technical enablers"), not disguised as a quality judgment.
2. **Ontology granularity — 11 kinds.** The debatable merges are K7 into K5/K1 (instruments are machines; metrics are knowledge) and K9 into K1 (formulations are knowledge). **Recommendation: keep 11.** The classification rules in §2.1 do the disambiguation work, and §§6.1/6.3 show rows (ImageNet-as-challenge, ICD-GPS-200) that only exist because K7/K8/K9 are separate. Collapsing them re-creates ≡ claims the audit cannot check.
3. **Raise `raw_target` 100 → 140** (FULL profile), per §8. **Recommendation: yes.** The cost is real (+30–40% evaluation per expansion) and buys the per-lens floor that makes coverage auditable.
4. **Meta passes outside the budget.** L3/L23 capped at ~10 combined, excluded from `raw_target`. **Recommendation: yes** — they are source passes, not content lenses; counting them against the target taxes exactly the narratives that catch vocabulary-mismatch misses (§5.2, risk 3).
5. **Retro-sweep scope.** Extend the planned v3.1 sweep from "lenses 11–12 over expanded nodes" to "the genuinely-new lenses (L4, L5, L10, L12, L16, L21, L22) over expanded nodes", priority order unchanged (root, GPT-3, Transformer, RLHF, ICL first). **Recommendation: yes, and run it as one session after this framework is approved** — otherwise the shallow graph (the part readers see first, and the part the article will describe) permanently reflects the old list's blind spots while the deep graph doesn't.
6. **The dry-note requirement** (§8, guardrail 1): every lens, every expansion, returns candidates or a recorded dry note. **Recommendation: adopt.** It is cheap, and it converts exhaustiveness from a design claim into per-expansion evidence the owner can inspect.

---

## Appendix — what this proposal does not change

The 12 evaluation questions and their gates; the directness test and `mediated_via` discipline; §4.5 identity resolution; the survivor cap (20); depth cap (~10) and node budget (~2,000); checkpoint/resume. If approved, implementation is a DESIGN.md §4 rewrite + RUNBOOK §6.1 lens attachment swap, versioned as **v4** with this document cited as its source — a separate task, not begun here.

*The Behind 01 · Lens Framework Design (PROPOSAL) · 2026-11-24.*
