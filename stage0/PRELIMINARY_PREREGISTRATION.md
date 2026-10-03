# stage0/PRELIMINARY_PREREGISTRATION.md — one-page preregistration sketch (PI Part K)

Project **scd-mas** ｜ Stage 0 sketch ｜ 2026-10-03 ｜ **numerical gates deliberately NOT
chosen** — they will be frozen by the PI after the Stage-0 collision review. Nothing here is
a claim; the working claim is under collision audit.

## Falsifiable thesis

**SCD (Speculative-Commit Deliberation) is only interesting if it can beat BOTH extremes of
the harm–rescue frontier that the closed aove-mad line measured on its P0 development set:**

- **Direct peer exposure** (C3/C5-style): high rescue (W→C), high harm (C→W). Measured on the
  aove-mad disagreement subset: WCR 0.367 / CWR 0.526 (C5).
- **No/low peer exposure** (C7-style candidate-oblivious verification): low harm, low rescue.
  Measured: WCR 0.078 / CWR 0.105 (C7). Plain aggregation without revision sits at the origin.

**SCD's thesis**: treating peer influence as a *speculative state transition* with an explicit
commit gate separates the two effects — the peer information can drive rescue in the
speculative branch, while the immutability of the incumbent plus the commit gate prevents
irreversible social overwrite — so that:

> **Future feasibility target: SCD should reduce CWR relative to direct exposure while
> retaining a substantial fraction of direct exposure's WCR.**

Operationally, on a frozen disagreement subset of a development benchmark, SCD's (CWR, WCR)
point should (i) sit strictly inside the harm–rescue gap between the two frozen endpoints —
CWR meaningfully below the exposed endpoint's and WCR meaningfully above the protected
endpoint's — and (ii) do so *because of* the commit gate (a mismatch/ablation control must
show the gate, not the probe content, accounts for the contamination suppression). Stage 2B's
B4-style task-specificity control (own-probe vs mismatched-probe) is inherited as a mandatory
control: a gate that helps regardless of probe provenance is not evidence of the mechanism.

## What would falsify the thesis

- SCD's contamination matches direct exposure despite the gate (the gate commits socially
  overwritten states too often — commit-rate pathology).
- SCD's rescue matches the protected endpoint despite speculation (the gate rolls back
  peer-driven corrections — obstinacy pathology).
- SCD only matches both extremes without entering the gap (the transition representation adds
  cost, not separation).
- The advantage disappears under the mismatch control (the effect is probe content, not the
  commit mechanism).

All four are reportable negatives; the pivot-loop rule from the predecessor project applies
to SCD's own gates once frozen by the PI.

## Measurement inheritance (what carries over from aove-mad)

- Metrics and definitions: CWR, WCR, NRG (= Δindividual accuracy), TransitionBalance named
  separately, MCPR/MWRR minority-truth strata (1C2W primary), strict-majority aggregation
  with abstention counting as incorrect, question-level clustered bootstrap CIs.
- Discipline: freeze-then-audit-then-gate; per-request serialized-payload visibility audits;
  fail-closed validity; invalid/leaking instruments excluded by pre-registered rule, never
  silently repaired; a mismatched-probe/ablation control in every generation round.
- What does NOT carry over: any aove-mad result as validation. The P0 observations motivate;
  SCD's evidence must be generated under SCD's own pre-registration on SCD's own runs.

## Open for the PI (explicitly not decided here)

1. Numerical gate values for the CWR/WCR target region (after Stage-0 review).
2. Datasets and sample sizes for the first SCD measurement round.
3. Which commit certificate(s) are admissible (03/04 docs propose three with collision and
   failure-mode analysis).
4. The width of M_−i (peer answers? reasoning? probe text only?) — the exposure contract.
5. Whether the second model family enters at the confirmation stage (the aove-mad line never
   ran its Gemma/Phi confirmation).
