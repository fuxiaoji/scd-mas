# stage0/LITERATURE_AUDIT.md — Stage-0 collision literature audit (PI Parts D–I)

Project **scd-mas** ｜ 2026-10-03 ｜ three-pass audit (named MAD papers; rollback/recovery
line; concept sweep) + main-agent primary-source reads of the four highest-risk items.
All claims carry URLs in the companion matrix (`docs/02_CLOSEST_WORK_MATRIX.md`); phantom or
misattributed entries are listed in §6. Nothing was inferred or run.

## 1. Method

- Three independent passes: (i) PI's named list; (ii) rollback/recovery line including
  citation followers of ReAgent and Thought Rollback; (iii) 16-concept sweep over arXiv API
  (export.arxiv.org), arXiv abs/HTML pages, WebSearch, DBLP/venue checks. Known papers from
  the predecessor project's audits were carried forward, not re-derived.
- Main-agent personal reads (PART G/H/I duty): **LMAD full text** (arXiv:2608.01463v2 HTML),
**COMED abstract** (arXiv:2609.26913, AACL-IJCNLP 2026), **ReAgent full text**
(arXiv:2503.06951v2 HTML), **Thought Rollback abstract** (arXiv:2412.19707, ICML),
**Debate or Vote full text** (arXiv:2508.17536v2 HTML, NeurIPS 2025).
- Five factors tracked for every item: F1 immutable private incumbent during exposure ·
F2 separate speculative/shadow branch for peer info · F3 delta represented separately ·
F4 explicit COMMIT/ROLLBACK validator of a peer-induced transition · F5 core multi-agent LLM
reasoning method.

## 2. Headline result

**No public work (archival or preprint, 2024–2026) implements the five-factor chain.**
Several works implement ONE factor each, in adjacent domains or in weak form:

- F1 alone: Mem++ (never-overwrite memory, single-agent); DAR (immutability of debate
  *messages*, not agent states); Debate or Vote's MAD-oracle (locks correct answers — oracle
  only, explicitly "not feasible in practice").
- F2+F4 alone: TomasuLLM (copy-on-write speculative branch + validation-then-commit — for
  the agent's OWN tool calls); DeepRewind (binary commit-blocking controller + rollback —
  self-induced, single agent); CoAgent (speculative in-place writes with saga undo — infra).
- F4-adjacent soft gating inside MAD: R²-MAD confidence weights; self-social weighting
  (2601.05606) — no binary validator, no represented transition.
- Peer-induced rollback: **ReAgent** rolls back states changed by cross-agent contradictions
  (detect-and-undo with checkpoint logs) — the closest rollback-line item; it has no
  immutable-during-exposure incumbent, no speculative branch, and no commit decision.

## 3. The four PI-flagged priorities

### LMAD (PART G — highest priority) — full-text read
Shared/global committed state P(ℓ) initialized by a controller; agents condition on it;
localized debate over the earliest conflict; guarded resolution appends repairs
("subject and relation preserved, every quotation verbatim"); acceptance is MONOTONE
("Nodes in P(ℓ) are not reopened"); un-debated suffixes are regenerated afresh; agents see
brief descriptions of competing claims.
Five factors: F1 ✗ (no per-agent incumbent — one shared document), F2 ✗, F3 ◐, F4 ◐
(controller repair-gate, no rollback), F5 ✓.
**LMAD_COLLISION = MEDIUM.** Distinction to defend in writing: per-agent LOCAL immutable
incumbents + REVERSIBLE transitions vs ONE SHARED monotone document.

### COMED (PART H) — abstract read (AACL-IJCNLP 2026, archival)
Post-anchor controller; unit of control = the whole QUERY (accept confident answers, verify
ambiguous, escalate when collaboration is likely beneficial); preventive, not speculative;
no states, no rollback, no delta validation. Its "rescue-harm decomposition" framing overlaps
our motivation (and echoes the aove-mad frontier). **COMED_COLLISION = LOW-MEDIUM**
(low on the five factors; the framing overlap must be cited, not claimed).

### Rollback literature (PART I) — full-text ReAgent + abstracts
Thought Rollback: single-agent own-trajectory rollback (ICML 2025). ReAgent: per-agent
knowledge sets + checkpoint graphs + verifier/supervisor undo, triggered by internal OR
cross-agent contradictions — **the closest rollback-line item to peer-induced social-state
rollback**; still detect-and-undo on live states, no immutable incumbent, no speculative
branch, no commit decision. GA-Rollback resolved to arXiv:2503.02519 (EMNLP 2025,
transactional agent runtime, not peer reasoning). RIR/CLEANER/VST/CoAgent: single-agent or
infrastructure. **ROLLBACK_COLLISION = MEDIUM** (ReAgent), pending the rollback-line
subagent's follower pass to confirm no closer item exists.

### Named MAD line — subagent audit
AgentAuditor (post-hoc reasoning-tree adjudication), Free-MAD (prompt-level retention,
revisions not gated), Debate or Vote (oracle locking = upper bound; heuristic update gates),
Not All Flips Are Conformity (measurement), Minority Sentinel (post-hoc vote overturn,
workshop), Cost of Consensus (empirical harm study), Collaboration Tax (in-place acceptance
cascade), MAD-M²/CascadeDebate/SELENE/BANDMAS — none passes F1+F2+F3+F4. Phantom/misattribution
corrections in §6.

## 4. Five-factor assessment (PART F input)

| closest work | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|
| LMAD (full text) | ✗ | ✗ | ◐ | ◐ (shared-repair gate, monotone) | ✓ |
| ReAgent (full text) | ✗ | ✗ | ◐ (checkpoint log) | ◐ (undo only) | ✓ |
| TomasuLLM | ✓ | ✓ | ◐ | ✓ | ✗ (own actions, single agent) |
| DeepRewind | ✓ | ✗ | ◐ | ✓ | ✗ (single agent) |
| Debate or Vote | ◐ (oracle) | ✗ | ✗ | ◐ (heuristic) | ✓ |
| DAR | ◐ (messages) | ✗ | ✗ | ✗ | ✓ |
| Mem++ / MGPO | ✓ / ◐ | ✗ | ◐ | ◐ | ✗ (memory mgmt) |

No row has all five. The only rows with four are outside multi-agent reasoning
(TomasuLLM, DeepRewind: own-actions/single-agent), and the only rows inside multi-agent
reasoning have at most two, both partial.

## 5. Residual audit risk

- ReAgent full text was read from arXiv HTML v2 — mechanism statements above are from that
  version; a v3 could shift details (tracked in 05_RISK_REGISTER.md R7).
- The rollback-line follower pass (citations of ReAgent/Thought Rollback) is completing in a
  second subagent pass; its results append here before packaging.
- LMAD/ReAgent/COMED are preprints or recently-accepted; the space is moving (R7).

## 6. Phantom and misattributed entries (do not cite)

1. **E2-Explainer** — no such paper exists (the E2LLM name belongs to two unrelated papers:
   long-context 2409.06679; edge-serving 2606.03770).
2. **CAPS** — real ID is arXiv:2605.15513; 2607.05391 (circulated with CAPS) is a different
   paper ("LLM-as-a-Verifier").
3. **Free-MAD ≠ arXiv:2311.12316** (pathology diffusion paper); real: 2509.11035.
4. **AgentAuditor name collision**: the MAD reasoning-tree paper is 2602.09341; 2506.00641
   (NeurIPS 2025) is an unrelated safety-evaluation paper.
5. **Debate or Vote ≠ arXiv:2411.05263** (unrelated optimization paper); real: 2508.17536.
6. **GA-Rollback** resolves to arXiv:2503.02519 (EMNLP 2025 agent-runtime rollback), not a
   "generator-assistant stepwise" reasoning paper.

## 7. Concept-sweep appendix (completed after §5 was drafted)

Sweep verdicts now incorporated in the matrix (Tier 3). Headline zero-hits (novelty evidence):
"speculative branch/state" + agents → only speculative-decoding/CPU papers; "shadow
reasoning/branch" → zero LLM-agent hits; "reversible debate/revision" → 0; "private belief" +
language model → 0; "sandbox"+revision+reasoning+LLM → 0; "speculative revision"/"draft-then-
verify" → 25 hits, all decoding acceleration. No 2026 successors of the known-list papers.
Closest sweep finds: TomasuLLM (full speculative→validate→commit semantics for OWN tool
calls, single-agent), DeepRewind (binary commit-blocking controller + rollback, self-induced
single-agent), DAR (message immutability inside MAD), R²-MAD (soft peer-influence weighting),
GA-Rollback resolved to 2503.02519 (EMNLP 2025 agent-runtime rollback, not peer reasoning).

## 8. Rollback follower pass (completed; PART I closure)

Semantic Scholar citation sweeps on ReAgent/Thought Rollback/GA-Rollback/SagaLLM anchors +
OpenReview search + author follow-ups. **Verdict: no paper applies rollback to a state
changed by another agent's information in multi-agent LLM reasoning.**

Three bordering schools, each missing different factors:
1. **Transaction/compensation school** — SagaLLM (2503.11951: validation agents + compensation
   for multi-agent planning), ALAS (2505.12501: local compensation on disruptions): has F4+F5
   but rollback is post-hoc compensation of workflow *actions*; no immutable incumbent, no
   speculative branch, no peer-information transition.
2. **Runtime recovery school** — REVISE (2609.00643: delta ∩ dependencies, incumbent
   progress preserved, revalidation before commit — mechanically 4/5 factors but the trigger
   is a user revision in a coding workflow), TomasuLLM (speculative copy-on-write +
   validate-then-commit for OWN tool calls), Checkpoint/Fork/Restore/Merge exact decider
   (2608.22928, Lean-mechanized), CoAgent, AgentRewind, Planarian: has F1-analogue, F2, F3,
   F4 mechanically — but single-agent own-execution.
3. **Deliberation/belief school** — ECON (2506.08292, ICML 2025): agents hold belief states
   about other agents during debate (peer-induced transitions exist) but no rollback, no
   immutability, no validator. Key contrast point for the paper.
Also verified: no ReAgent/Thought-Rollback author follow-ups extend the mechanisms; phrase
searches for peer-induced-rollback combinations return nothing; anchor correction — Thought
Rollback authors are Sijia Chen and Baochun Li (iQua, U Toronto).
Closest single paper overall: **REVISE (2609.00643)** — 4/5 factors, wrong domain.
