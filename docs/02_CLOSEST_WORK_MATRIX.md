# 02_CLOSEST_WORK_MATRIX.md — closest-work comparison matrix (PI Part E)

Project **scd-mas** ｜ Stage 0 ｜ 2026-10-03 ｜ all rows verified against primary sources
(arXiv abs pages; full texts where marked). Five SCD factors per row:
**F1** immutable private incumbent preserved during exposure · **F2** peer info in a separate
speculative/shadow branch · **F3** transition/delta represented separately · **F4** explicit
COMMIT/ROLLBACK validator of a peer-induced transition · **F5** core multi-agent LLM
*reasoning* method (not tool exec / self-correction / trajectory rollback).

Legend: ✓ yes · ✗ no · ◐ partial/oracle-only · ? unverified · — n/a

## Tier 1 — highest collision priority (full-text main-agent reads)

| work | venue/status | task | F1 | F2 | F3 | F4 | F5 | what it actually does | exact distinction from SCD |
|---|---|---|---|---|---|---|---|---|---|
| **LMAD** — Where Reasoning Diverges: Localized Multi-Agent Debate (arXiv:2608.01463, preprint, Gao et al. 2026-08) | preprint | multi-hop QA (4 benchmarks, 10 backbones) | ✗ (shared global committed state P(ℓ); no per-agent incumbent) | ✗ (resolver proposal checked then appended directly; no living side-branch) | ◐ (resolver proposal (Ẑ,Q̂) separate before incorporation) | ◐ (controller resolver Φ guards a shared-state *repair*: subject/relation preserved + verbatim quotations; acceptance MONOTONE — "Nodes in P(ℓ) are not reopened"; fallback = majority vote; no rollback) | ✓ | represents rationales as nodes, localizes earliest conflict, debates only local segments, guarded resolution appends repairs to one shared committed state | SCD: per-agent LOCAL immutable incumbents (not shared), reversible COMMIT/ROLLBACK of speculative transitions (not monotone append), per-agent state-transition validation with a visibility contract (not controller repair of a shared document) |
| **COMED** — The Missing Middle Between Routing and Collaboration in Multi-LLM Inference (arXiv:2609.26913, **AACL-IJCNLP 2026**, Alballa et al. 2026-09) | archival | multi-LLM inference routing/collaboration | ✗ (no per-agent states at all — one-shot per query) | ✗ | ✗ | ✗ (accept/verify/escalate is a query-level routing decision, not a state-transition gate) | ◐ (multi-LLM inference, but escalation-based) | post-anchor controller: anchor self-consistency + router margin + a lightweight peer probe decide whether to escalate a query to cross-model collaboration | SCD allows collaboration SPECULATIVELY and gates the resulting transition; COMED *prevents* collaboration up-front. No states, no rollback, no delta. Overlap is motivational only: its "rescue-harm decomposition" mirrors the aove-mad harm–rescue frontier that motivates SCD |
| **ReAgent** — Reversible multi-agent reasoning for knowledge-enhanced multi-hop QA (arXiv:2503.06951, preprint, Zhao et al. 2025-03) | preprint | knowledge-enhanced multi-hop QA | ✗ (per-agent knowledge sets Φᵢ are the LIVE working state — mutated in place; checkpoints/log exist but nothing is immutable during exposure) | ✗ ("no true speculative branches"; corrections apply directly to the working state) | ◐ (backtracking graph LBGᵢ logs checkpoint states — a log, not a proposed-delta object) | ◐ (Verifier/Supervisor trigger rollback on detected inconsistencies — detect-and-UNDO, no COMMIT decision, no visibility contract) | ✓ | non-monotonic multi-agent QA: local + global rollback to checkpoint states when cross-agent contradictions appear | SCD's P_i is immutable *during* exposure and the gate is propose-then-approve with a visibility contract; ReAgent is conflict-triggered undo on a live shared-plus-local state. **Closest work on the rollback axis** (peer-induced changes ARE rolled back) — ROLLBACK collision MEDIUM |
| **Debate or Vote** (arXiv:2508.17536, **NeurIPS 2025 Spotlight**, Choi/Zhu/Li 2025) | archival | MAD analysis + interventions, 7 benchmarks | ◐ (MAD-oracle "locks" correct answers — explicitly an oracle upper bound, "not feasible in practice") | ✗ | ✗ | ◐ (MAD-Conformist retains majority-matching responses; MAD-Follower adopts majority w.p. 0.3 — heuristic update gates using the majority proxy; no delta, no validator) | ✓ | martingale theorem: debate alone does not improve expected correctness; voting accounts for most gains | SCD's commit gate is a deployable attempt at what DoV's oracle models (protect correct incumbents); but DoV has no speculative branch, no delta object, no validator contract, and treats update gates as biasing a stochastic process, not validating a transition |

## Tier 2 — audited, weaker overlaps (abstract-level unless noted)

| work | venue/status | F1 | F2 | F3 | F4 | F5 | note |
|---|---|---|---|---|---|---|---|
| AgentAuditor (arXiv:2602.09341) | preprint | ✗ | ◐ post-hoc reasoning tree | ◐ divergence points | ◐ adjudication at the end (aggregation-time, not transition-time) | ✓ | drop-in aggregation replacing majority vote/LLM-judge; name collision with a 2025 safety paper — cite 2602.09341 |
| Free-MAD (arXiv:2509.11035) | preprint | ◐ prompt-level retention pressure only | ✗ | ✗ (score dict tracks answer evolution) | ✗ revisions explicitly NOT gated | ✓ | single-round consensus-free MAD |
| Not All Flips Are Conformity (arXiv:2606.00820) | preprint | ✗ | ✗ | ✗ | ✗ | ✗ (analysis paper) | decomposes flips: instability vs conformity vs persuasion; documents the phenomenon SCD targets |
| Minority Sentinel (arXiv:2606.29270, SIGIR 2026 workshop — non-archival) | workshop | ✗ | ✗ | ✗ | ✗ post-hoc vote-overturn classifier | ◐ | "minority truth" framing overlaps our MCPR stratum |
| The Cost of Consensus (arXiv:2605.00914) | preprint (archival status ?) | ✗ | ✗ | ✗ | ✗ | ✗ (empirical study) | sycophantic conformity up to 85.5%, consensus collapse — motivation, not mechanism |
| The Collaboration Tax (arXiv:2608.22152, EMNLP 2026) | archival | ✗ | ✗ | ✗ | ✗ (prompt intervention only) | ✓ (setting) | four-stage cascade incl. "accepting answers without re-derivation" — the in-place-overwrite failure SCD gates |
| MAD-M² (ICLR 2026, arXiv:2603.20215) | archival | ✗ | ✗ | ✗ | ✗ | ✓ | memory masking, globally applied |
| CascadeDebate (arXiv:2604.12262) | preprint | ✗ | ✗ | ✗ | ✗ query-level routing | ✓ | confidence-routed cascade |
| SELENE (EACL 2026 Industry) | archival (industry track) | ✗ | ✗ | ✗ | ✗ query-level | ✓ | selective debate initiation |
| Thought Rollback (ICML 2025... arXiv:2412.19707) | archival (ICML) | ✗ single-agent own-trajectory | ✗ | ✗ | ✗ | ✗ | rollback of OWN steps (PART I: internal-trajectory class) |
| BANDMAS (arXiv:2608.00458) | preprint | ✗ | ✗ | ✗ | ✗ | ✗ (communication layer) | semantic packet scheduling — caller's "bandit selection" guess wrong |
| E2-Explainer | — | — | — | — | — | — | **PHANTOM**: no such paper found (E2LLM name belongs to two unrelated papers) — do not cite |
| Memory line: Mem++ (2610.02002), Learning What to Remember/MGPO (2609.37930), TreeMem (2605.04811) | preprints | ✓ Mem++ (never-overwrite documents, single-agent) | ✗ | ◐ MGPO gates memory rewrites by utility (single-agent) | ◐ MGPO | ✗ | the only hard "immutable incumbent" found — in single-agent MEMORY management, not multi-agent reasoning |
| Belief-preservation phenomenon papers: Epistemic Resilience (2605.23932), Conformity→Misalignment (2605.10721) | preprints | ✗ (measure, no mechanism) | ✗ | ✗ | ✗ | ✗ | document belief collapse under social pressure — motivation |

## Tier 3 — concept-sweep pass (completed 2026-10-03)

**Explicit zero-hit concepts (novelty evidence):** "speculative branch/state" + agents → 16
arXiv hits, ALL speculative decoding / CPU architecture; "shadow reasoning/branch" → zero
LLM-agent hits; "reversible debate/revision" → 0; "private belief" + language model → 0;
"sandbox"+revision+reasoning+LLM → 0; "speculative revision"/"draft-then-verify" → 25 hits,
all decoding acceleration; no 2026 successors of the known-list papers surfaced.

| work | venue/status | F1 | F2 | F3 | F4 | F5 | note |
|---|---|---|---|---|---|---|---|
| DAR / Hear Both Sides (arXiv:2603.20640) | preprint | ◐ (index-based retention keeps ORIGINAL MESSAGES unchanged — message immutability, not a per-agent committed solution) | ✗ | ✗ | ✗ (selection/filtering only) | ✓ | broadcasts maximally-disagreeing responses; the F1-adjacent mechanism in MAD |
| TomasuLLM (arXiv:2609.38201) | preprint | ✓ (committed state) | ✓ (copy-on-write speculative branch) | ◐ | ✓ (validation gate before commit) | ✗ (single-agent tool-call runtime) | **the full speculative→validate→commit semantics exist — but for the agent's OWN future actions, never peer reasoning** |
| DeepRewind (arXiv:2609.36344) | preprint | ✓ (commitments as typed-graph nodes) | ✗ (self-generated conclusions, no peers) | ◐ | ✓ (binary controller blocks risky commitments + dependency-aware rollback) | ✗ (single deep-research agent) | commit/rollback controller exists — self-induced only |
| CoAgent/MTPO (arXiv:2606.15376) | cs.DC, ATC submission (non-archival) | ◐ (writes applied speculatively IN PLACE — incumbent not immutable) | ◐ (speculation of own writes) | ✗ | ◐ (advisory LLM conflict judge + mechanical saga-undo) | ✗ (concurrency infra) | speculative-write semantics without reasoning content |
| R²-MAD (arXiv:2609.03619) | EMNLP 2026 Findings | ✗ | ✗ | ✗ | ◐ (confidence weights modulate peer influence — soft gate, no binary validator/rollback) | ✓ | soft peer-influence gating; the strongest "gate" found inside MAD |
| Conformity Dynamics / Self-Social Weighting (arXiv:2601.05606) | under review | ✗ | ✗ | ✗ | ◐ (self-vs-social weighting rule) | ✓ | soft weighting, no transition object |
| Herd Behavior (arXiv:2505.21588) | preprint | ✗ | ✗ | ✗ | ✗ | ✓ (analysis) | measures peer-influence conformity — SCD's threat model, no mechanism |
| GA-Rollback (arXiv:2503.02519) | EMNLP 2025 | ✗ (agent runtime rollback) | ✗ | ✗ | ◐ | ✗ (infrastructure) | transactional/rollback runtime for agents; NOT peer reasoning (caller's "generator-assistant stepwise" guess resolved to this ID) |
| RIR (arXiv:2609.18304), CLEANER/SAAR (2601.15141), VST (2609.07065), Cordon/XFlow/Planarian/ChronoMem/Revisable-by-Design | preprints/infra | ✗ or partial | ✗ (self/infra) | ◐ | ◐ (infra controllers) | ✗ | rollback/transactional infra outside peer-reasoning scope |
| Memory line: Mem++ (2610.02002), MGPO (2609.37930), TreeMem (2605.04811) | preprints | ✓ Mem++ (never-overwrite) / ◐ | ✗ | ◐ MGPO (utility-gated memory rewrites, single-agent) | ◐ MGPO | ✗ | hard immutability exists only in single-agent memory management |
