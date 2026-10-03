# stage0/COLLISION_ALERT.md — five-factor stop condition (PI Part F)

Project **scd-mas** ｜ Stage 0 ｜ 2026-10-03 ｜ verdict: **COLLISION_ALERT NOT RAISED**

## The five-factor stop condition (verbatim from PI Part F)

Stop the project before implementation if ONE existing public work already contains ALL of:

1. an immutable or explicitly preserved private/incumbent agent state;
2. peer information is processed in a separate speculative/shadow branch;
3. the peer-induced transition is represented separately from the incumbent state;
4. an explicit validator/gate decides COMMIT versus ROLLBACK of that transition;
5. this mechanism is the core method for multi-agent LLM reasoning rather than tool
   execution, generic self-correction, or single-agent trajectory rollback.

## Assessment (evidence: stage0/LITERATURE_AUDIT.md + docs/02_CLOSEST_WORK_MATRIX.md)

| closest work | F1 | F2 | F3 | F4 | F5 | why it fails the conjunction |
|---|---|---|---|---|---|---|
| LMAD (2608.01463, preprint) — full-text read | ✗ shared global committed state; agents' un-debated suffixes regenerated | ✗ | ◐ resolver proposal separate pre-check | ◐ controller repair-gate; MONOTONE, no rollback | ✓ | shared/monotone, not per-agent/reversible |
| ReAgent (2503.06951, preprint) — full-text read | ✗ live per-agent knowledge sets (checkpoint logs; mutated in place) | ✗ corrections apply directly to working state | ◐ checkpoint log | ◐ detect-and-UNDO by Verifier/Supervisor; no COMMIT decision or visibility contract | ✓ | peer-induced changes CAN trigger undo — but no immutable incumbency, no speculation, no commit |
| TomasuLLM (2609.38201, preprint) | ✓ committed state | ✓ copy-on-write speculative branch | ◐ | ✓ validate-then-commit | ✗ single-agent tool-call runtime | the speculative-commit machinery exists — for OWN actions, not peer reasoning |
| DeepRewind (2609.36344, preprint) | ✓ | ✗ (self-generated conclusions) | ◐ | ✓ binary commit-block controller | ✗ single agent | same domain failure |
| Debate or Vote (2508.17536, NeurIPS 2025) — full-text read | ◐ oracle-only locking ("not feasible in practice") | ✗ | ✗ | ◐ heuristic update gates (majority proxy) | ✓ | no speculation, no delta, no validator |
| REVISE (2609.00643, preprint) | ✓ | ◐ (externally triggered revision, not peer) | ✓ | ✓ | ✗ coding-workflow runtime | 4/5 factors, wrong domain |
| SagaLLM (2503.11951, preprint) | ✗ (compensated post hoc) | ✗ | ◐ | ✓ validation agents | ✓ (planning) | workflow actions, not reasoning states |
| ECON (2506.08292, ICML 2025) | ✗ | ✗ (peer-induced belief transitions, but in-place) | ✗ | ✗ | ✓ | the peer-transition half alone |
| DAR (2603.20640, preprint) | ◐ message immutability | ✗ | ✗ | ✗ | ✓ | originals kept unchanged — but agents still read peers directly |

**No work contains all five factors. No work contains F1+F2+F3+F4 together in any domain.**
The three schools that border the idea (transaction/compensation; runtime recovery;
deliberation/belief) each miss a different subset, documented per-row.

## Verdict

**COLLISION_ALERT NOT RAISED. The project does NOT stop.** The five-factor chain is unclaimed
in everything reachable (arXiv, ACL Anthology, OpenReview partial, Semantic Scholar citation
sweeps, DBLP attempted — bot-blocked, recorded as a caveat). Partial overlaps are recorded
honestly in the matrix; the two that must be defended head-on in any paper are LMAD (shared
monotone committed state vs per-agent reversible incumbents) and ReAgent (peer-induced undo
vs propose-and-approve commit).
