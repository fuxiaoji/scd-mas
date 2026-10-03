# 03_SCD_FORMALIZATION.md — minimal formalization of Speculative-Commit Deliberation

Project **scd-mas** ｜ Stage 0 ｜ 2026-10-03 ｜ no models were run; this document only fixes
notation and the design questions that the collision review must answer before any
implementation.

## 1. Objects

For agent *i* in a team of *N* solvers on question *x*:

- **P_i — private incumbent state.** The agent's independently produced, *committed*
  solution state: final answer plus the reasoning state that produced it. **P_i is immutable
  during the entire peer-exposure phase.** (This is the factor-1 object.)
- **M_−i — peer information.** Whatever the exposure contract lets agent *i* see from
  peers (answers only, reasoning only, probe text, full rationales). The *width* of M_−i is
  a design axis, deliberately left open at Stage 0.
- **S_i — speculative peer-exposed state.** S_i = F(P_i, M_−i): the agent's revision computed
  **in a separate branch** that never touches P_i. (Factor-2 object. F is the same frozen
  solver model under the peer-exposure decoding contract.)
- **Δ_i — the proposed transition.** Δ_i = D(P_i, S_i): an explicit, separately represented
  delta between incumbent and speculative states — minimally "final answer changed from
  a_i^P to a_i^S"; optionally the load-bearing step(s) whose change accounts for the answer
  change, extracted by a deterministic differ or by the solver itself. (Factor-3 object.)

## 2. Commit policy

- **C_i = G(x, P_i, S_i, Δ_i) ∈ {COMMIT, ROLLBACK}** — an explicit per-agent validator
  decision over the proposed transition. (Factor-4 object.)
- Final answer state: **A_i = S_i if C_i = COMMIT else P_i.**
- Aggregation: frozen strict-majority-with-abstention over {A_1, …, A_N} (inherited from the
  aove-mad line so that the harm–rescue frontier stays comparable).

## 3. The central unresolved design issue: what may G see?

G must not trivially degenerate into a generic LLM judge ("which answer looks right?") — that
would reintroduce exactly the candidate-aware judge whose failure modes the aove-mad line
documented (Stage 2A: candidate-aware-but-peer-oblivious auditing could not rank; P0: judges
and peers that see conclusions carry contamination). The visibility contract for G is
therefore the central open question. Constraints any contract must satisfy:

1. G must be able to detect that S_i's reasoning actually *engages* with the probe/disagreement
   (otherwise speculative branches are cheap noise).
2. G must not become a third opinion whose verdict simply overrides the two states — it
   decides a *transition*, not the answer.
3. G's inputs must be auditable against the same leak taxonomy used in P0/2A/2B (serialized
   payload contract, zero gold, defined regions).

## 4. Candidate commit certificates (design space, NOT run)

Three candidate certificates for G, each with collision exposure and expected failure mode.
Stage 0 authorizes discussion only; selection and freezing happen at a later stage.

### Certificate C-A — Novel-evidence certificate
G checks whether S_i's reasoning contains a *concrete, checkable element absent from P_i*
(a recomputed quantity, an executed boundary case, a named constraint violation) that
resolves the disagreement the probe targeted, and whether that element is consistent with
the probe's execution instruction.
- *Collision risk*: LOW-MEDIUM. "Generate a check, then verify the check was done" is close
  to verifier-guided revision loops (LLM-as-an-Improver, ExVerus) — but those verify a single
  candidate against an oracle/verifier, not a peer-transition under a neutrality constraint.
- *Expected failure mode*: surface compliance — solvers fabricate a plausible "novel element"
  (a number that appears nowhere in P_i but proves nothing). The 2A lesson says audited
  structure is gameable; a certificate must bind the novel element to the probe's instruction,
  or it degenerates into decoration.

### Certificate C-B — Local contradiction resolution
G checks whether S_i resolves a *specific, previously stated* contradiction between P_i and
at least one peer position (or between P_i and the probe), where the contradiction was
identifiable from P_i + M_−i alone, and whether the resolution is consistent with the rest of
P_i (no new contradiction introduced elsewhere).
- *Collision risk*: MEDIUM. LMAD's guarded resolver validates a repair against a shared
  state ("subject and relation preserved, quotations verbatim") — C-B is a per-agent analogue
  ("old contradiction resolved, none introduced"). The distinction (local per-agent state,
  reversible, transition-scoped) must be stated explicitly in any paper.
- *Expected failure mode*: the resolver of contradictions may be wrong more often than the
  incumbent — a wrong agent can "resolve" its contradiction by rationalizing further. Without
  a link to correctness, this certificate may preserve P_i too often (motivating P0's
  obstinacy concern) or commit rationalizations.

### Certificate C-C — Independent recomputation certificate
G checks whether the delta Δ_i is *derivable* by an independent short recomputation: i.e.,
S_i's changed answer follows from executing the probe's instruction on P_i's own values, and
a fresh execution (by G, or by the solver with G checking determinism/self-consistency)
reproduces the change. This makes the commit decision hinge on agreement between two
independent executions rather than on G's judgment of quality.
- *Collision risk*: MEDIUM-HIGH for the general-reasoning case: "execute an independent check
  and compare" is the classic verifier pattern (self-verification, Math-Verify-style scoring);
  the multi-agent/social-transition wrapper is what would be new. For MCQ datasets the
  certificate needs a non-executable analogue (constraint enumeration), weakening it.
- *Expected failure mode*: compute cost per commit (an extra execution per agent per question)
  and the same failure the aove-mad line measured — recomputation checks that pass for both
  correct and wrong candidates (the Stage-2A zero-inflation problem returns as a commit-gate
  problem: 73.7% of audits found nothing to fail).

## 5. What Stage 0 fixes and what it does not

Fixed here: the five objects (P_i, M_−i, S_i, Δ_i, C_i), immutability of P_i during exposure,
separateness of S_i, explicitness of the transition, the commit-or-rollback decision, and
aggregation over committed states.

Open (for the PI, after the collision review): the width of M_−i; the representation of Δ_i
(answer-only vs step-delta); which certificate(s) G may use; whether G is the solver model
itself under a different contract or a separate context; and every numerical gate.
