# 01_COLLISION_DECISION.md — Stage-0 collision decision (PI Part M decision block)

Project **scd-mas** ｜ Stage 0 ｜ 2026-10-03

## Decision block

```
FULL_COLLISION = NO
LMAD_COLLISION = MEDIUM
COMED_COLLISION = LOW
ROLLBACK_COLLISION = MEDIUM
NOVELTY_WEDGE_CURRENTLY_DEFENSIBLE = YES
INFERENCE_AUTHORIZED = NO
```

## Reasoning

**FULL_COLLISION = NO.** No public/archival/preprint work 2024–2026 implements the five-factor
chain (immutable per-agent incumbent during exposure + peer info in a separate speculative
branch + separately represented transition + explicit COMMIT/ROLLBACK validator of that
transition + core multi-agent LLM reasoning). Evidence: three-pass audit (named papers,
rollback/recovery line with citation sweeps, 16-concept sweep) + main-agent full-text reads
of LMAD, ReAgent, Debate or Vote, and abstract reads of COMED, Thought Rollback, ExVerus,
AnyPoC and others. Explicit zero-hits recorded for "reversible debate/revision", "private
belief" + LM, "sandbox"+revision+reasoning, and speculative-branch semantics applied to
multi-agent reasoning.

**LMAD_COLLISION = MEDIUM.** Highest-priority item read in full (arXiv:2608.01463v2 HTML).
LMAD shares the committed-state vocabulary but the architecture is the inverse of SCD's on
the two load-bearing factors: ONE SHARED monotone committed document (agents' un-debated
suffixes regenerated afresh, acceptance never reopened) vs SCD's per-agent LOCAL immutable
incumbents with REVERSIBLE speculative transitions; controller-level repair gate vs per-agent
transition validator with a visibility contract. The adjacency is real (guarded-resolution
vocabulary) and must be preempted in any paper's related work; it is not a five-factor hit.

**COMED_COLLISION = LOW.** Verified on the arXiv abstract (2609.26913, AACL-IJCNLP 2026
archival): query-level preventive escalation ("accept confident answers, verify ambiguous
cases, escalate only when collaboration is likely beneficial") — no states, no speculation,
no rollback, no delta. Its "rescue-harm decomposition" framing overlaps SCD's motivation
(and the aove-mad frontier) and must be cited as concurrent problem-framing, not a mechanism
competitor.

**ROLLBACK_COLLISION = MEDIUM.** ReAgent (2503.06951, full-text read) rolls back states
changed by cross-agent contradictions (detect-and-undo over live per-agent knowledge sets
with checkpoint logs) — peer-induced state changes DO get undone there, satisfying the PART I
escalation trigger in partial form. But ReAgent has no immutable-during-exposure incumbent,
no speculative branch, and no commit decision; the follower pass (citation sweeps, author
follow-ups, phrase searches) found nothing closer. REVISE (2609.00643) is mechanically 4/5
factors in a coding-workflow runtime with a user-revision trigger. TomasuLLM realizes the
speculative-commit pattern for single-agent tool calls. ECON (ICML 2025) has the
peer-induced-transition half without rollback/immutability/validator.

**NOVELTY_WEDGE_CURRENTLY_DEFENSIBLE = YES.** The wedge per PI Part J/Stage-2A §18: a
*per-agent, transition-level, reversible commit gate over peer influence* inside multi-agent
LLM reasoning — unclaimed as a composition. Conditions that keep it defensible: (i) cite
LMAD/ReAgent/DoV/COMED as the nearest neighbors and state the state-architecture contrast
explicitly; (ii) cite the three bordering schools (transaction, runtime-recovery,
deliberation-belief) and their missing factors; (iii) re-run this audit at every stage
boundary (R7); (iv) never claim the individual factors as new — copy-on-write speculation,
commit validation, and rollback each exist elsewhere.

**INFERENCE_AUTHORIZED = NO.** Stage 0 is literature + architecture only (PI Part L honored:
no models downloaded/run, no P1, no benchmarks, no pilot questions, no validator prompt
tested, no synthetic justifications).

## What the PI should decide next

1. Whether the MEDIUM adjacencies (LMAD's guard vocabulary; ReAgent's peer-induced undo)
   demand a差异化 experiment plan in the Stage-1 pre-registration.
2. Which commit certificate(s) from `docs/04_COMMIT_GATE_DESIGN_SPACE.md` advance to
   implementation testing.
3. The numerical gates for the CWR/WCR target region (the sketch in
   `stage0/PRELIMINARY_PREREGISTRATION.md` deliberately leaves them open).
4. Whether the aove-mad P0 V2 dataset/benchmark family is reused for SCD's first measurement
   round (allowed as development data by the successor rule, or replaced entirely).
