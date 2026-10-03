# 04_COMMIT_GATE_DESIGN_SPACE.md — commit gate design space (PI Part J)

Project **scd-mas** ｜ Stage 0 ｜ discussion only; nothing implemented.

## 1. The degeneration trap

Any validator G that sees (x, P_i, S_i) and answers "which is better?" *is* a generic LLM
judge. The aove-mad line gives two measured reasons to avoid that: (i) P0 showed conclusion-
bearing channels carry contamination (C5/C3 harm), so a judge that reasons to its own
conclusion re-imports it; (ii) Stage 2A showed candidate-aware auditing cannot reliably rank
candidates (AUROC 0.59), so G-as-judge would likely add noise, not discipline. The commit
gate must therefore decide a **transition**, using **anchored, checkable** criteria — never
a free-form quality verdict.

## 2. Design axes (orthogonal; each needs a Stage-1 decision after collision review)

| axis | options |
|---|---|
| G's inputs | (a) Δ_i only (blind minimal); (b) Δ_i + probe/disagreement context; (c) Δ_i + P_i reasoning; (d) full (x, P_i, S_i) — explicitly the degenerate end |
| G's identity | same frozen model, different context vs a separate model/context |
| certificate | C-A novel-evidence / C-B contradiction-resolution / C-C independent recomputation (see 03_SCD_FORMALIZATION.md §4) — or a conjunction |
| decision output | binary COMMIT/ROLLBACK; or COMMIT/ROLLBACK/ESCALATE (escalate = defer to aggregation with both states visible? — rejected at Stage 0: leaks peer influence into aggregation) |
| failure default | ROLLBACK (fail closed: an unparseable/undecidable transition never overwrites the incumbent) — inherited from the Stage-2A fail-closed rule |
| scope | per-agent (each solver's transition decided separately) — fixed by the architecture; a team-level commit would collapse back toward a shared state (LMAD territory) |

## 3. The three certificates — collision exposure and expected failure modes

### C-A — Novel-evidence certificate
**Rule (sketch).** COMMIT iff S_i's reasoning contains a concrete element (recomputed value,
executed boundary case, named violated constraint) that (i) is absent from P_i, (ii) responds
to the probe's execution instruction, and (iii) does not contradict the rest of S_i.
**Collision exposure.** LOW-MEDIUM: closest are verifier-guided repair loops (LLM-as-an-
Improver 2609.19515; ExVerus 2603.25810) — single-candidate, oracle- or verifier-conditioned,
no immutable incumbent, no social transition. The peer-transition wrapper is the difference.
**Expected failure mode.** Decorative novelty: solvers invent an element that satisfies the
letter (a number, a mention) without causal force. Stage 2A measured exactly this gaming
capacity (audited structure with 73.7% empty results). A C-A gate must bind the novel element
to the instruction deterministically or it will commit noise.

### C-B — Local contradiction resolution
**Rule (sketch).** COMMIT iff (i) a contradiction between P_i and the peer information (or the
probe) was *stated* in Δ_i, (ii) S_i resolves it, and (iii) S_i introduces no new
contradiction into the parts of P_i it leaves untouched.
**Collision exposure.** MEDIUM: LMAD's guarded resolver is the nearest neighbour — but it
validates a repair to a SHARED state, monotone, no rollback, controller-level. C-B is
per-agent, reversible, and transition-scoped; the distinction is real but must be written
defensively (a reviewer will ask "how is this not per-agent LMAD guards?").
**Expected failure mode.** Rationalization: wrong agents "resolve" contradictions by
constructing post-hoc justifications. Without a correctness anchor the gate may preserve
obstinate wrong incumbents (the P0 obstinacy problem in reverse) or commit well-written
rationalizations. Detection of "new contradiction introduced" is also non-trivial for free-
form reasoning.

### C-C — Independent recomputation certificate
**Rule (sketch).** COMMIT iff an independent execution of the probe's instruction (by G, or
twice by the solver under different orderings) reproduces the transition — i.e., the delta is
*derivable*, not merely asserted.
**Collision exposure.** MEDIUM-HIGH: this is the classic self-verification/execution pattern
(Math-Verify-style scoring; execution-guided repair); only the social-transition wrapper is
new. On MCQ data no executable exists, so the certificate degrades to constraint
enumeration — much weaker.
**Expected failure mode.** The Stage-2A zero-inflation result returns as a commit problem:
recomputation checks passed for both correct and wrong candidates (73.7% of audits found
nothing), so C-C may commit nothing (obstinate) on exactly the questions where peers could
help, while costing an extra execution per commit.

## 4. Cross-cutting risks recorded now (feeds 05_RISK_REGISTER.md)

1. **Gate-as-judge degeneration** — mitigated by anchored certificates, never free-form.
2. **Commit-rate pathology** — a gate that commits ~0% reduces SCD to C7-like protection
   (measured: no rescue); a gate that commits ~100% reduces it to C3-like exposure (measured:
   high contamination). The interesting operating point is narrow; the gate must be evaluated
   for its commit-rate *by dataset* before any accuracy claim.
3. **Delta extraction is the hidden hard part** — for free-form math, "the transition" may
   involve re-derivation chains, not just the final answer; answer-only deltas may miss
   reasoning-level influence, step-deltas may leak peer content into G's context.
4. **Two-sided baseline discipline** — SCD must be compared against BOTH frozen extremes
   (C3/C5-style exposure and C7-style protection) under the same aggregated metric, or the
   harm–rescue claim is unfalsifiable.
