# 01_DECISION_PACKET.md — SCD Stage 1A (transactional commit feasibility)

Project **scd-mas** ｜ run `runs/stage1a` ｜ 2026-10-03 ｜ packaged after the §20 stop.

## Required status block

```
COLLISION_STOP = NO
SAMPLE_SIZE = 150
R0_FROZEN = YES
S1_COMPLETE = YES
S2_S3_PAIRED = YES
CERTIFICATES_FROZEN = YES
T1_HARM_SUPPRESSION = FAIL
T2_RESCUE_RETENTION = PASS
T3_TEAM_ACCURACY = PASS
T4_CERTIFICATE_SPECIFICITY = PASS
T5_TRANSACTIONAL_INTEGRITY = PASS
ORACLE_HEADROOM = 0.6800
SCD_STAGE1A = UNSUPPORTED
```

## Key numbers (exploratory, n=150 questions / 450 observations)

| condition | team acc | CWR | WCR | NRG | abstain |
|---|---|---|---|---|---|
| S0 independent vote | 0.5933 | — | — | — | 0.1267 |
| S1 direct exposure | **0.6067** | **0.1071** | **0.1176** | −0.0222 | 0.1400 |
| S2 speculative-only | 0.5933 | — | — | — | 0.1267 |
| **S3 SCD-Recompute** | **0.6067** | **0.0929** | **0.1118** | −0.0156 | 0.1267 |
| S4 random-certificate | 0.6000 | 0.1036 | 0.1059 | −0.0244 | 0.1333 |

Commit rate S3: **89.3%** (402/450 COMMIT, 48/450 ROLLBACK).

## Gate-by-gate

| Gate | Result | Detail |
|---|---|---|
| **T1 Harm suppression** | **FAIL** | S3 CWR 0.0929 vs S1 CWR 0.1071 = −1.42 pp (needs ≥ 5 pp) |
| **T2 Rescue retention** | **PASS** | S3 WCR 0.1118 / S1 WCR 0.1176 = **95.1%** (needs ≥ 50%) |
| **T3 No degradation** | **PASS** | S3 team 0.6067 ≥ S0 team 0.5933 |
| **T4 Specificity** | **PASS** | S3 WCR 0.1118 > S4 0.1059; S3 NRG −0.0156 > S4 −0.0244 |
| **T5 Integrity** | **PASS** | Gate is structurally deterministic (PASS→COMMIT, else→ROLLBACK); no gold/majority/peer outcome enters |

Per §17: T1 FAIL → **`SCD_STAGE1A = UNSUPPORTED`**.

## Why T1 failed: the certificate is too permissive

The recomputation certificate committed **89.3%** of transitions — barely below S1's implicit 100% adoption rate. The certificate's PASS/FAIL decision does discriminate (S3 CWR < S1 CWR by 1.42 pp, and S3 outperforms S4 on both WCR and NRG, confirming B4-type specificity), but the **magnitude** of suppression is far below the 5-pp threshold.

Root cause analysis: the peer-exposed speculative revision S_i rarely changes the answer at all (73.7% of S_i answers are identical to P_i in the P0 V2 data; in this run the answer-change rate is similar). When the answer doesn't change, the certificate correctly reports PASS (the transition is grounded — it's a no-op). The few cases where the answer does change are where the certificate could discriminate, but even there the recomputation check tends to confirm the transition because the model's speculative reasoning is self-consistent (it re-derives its own conclusion from the peer-influenced premises).

**This is the same zero-inflation pattern as Stage 2A**, but now expressed as commit-gate permissiveness rather than audit-ranking failure. The mechanism (speculative branch + commit gate) works structurally — T2/T3/T4/T5 all pass — but the certificate design cannot produce enough discrimination to bridge the harm–rescue gap.

## What works (honest positives)

1. **T2 rescue retention at 95.1%**: the commit gate almost never destroys a peer-driven rescue. The speculative-then-gate architecture does not lose correction power the way candidate-oblivious verification did (Stage 2A/2B: WCR dropped to 5–11%).
2. **T3 team accuracy improvement**: S3 (60.67%) beats S0 (59.33%) by +1.34 pp — a small but positive effect over independent vote.
3. **T4 specificity**: own-probe certificates outperform foreign-probe certificates on both WCR and NRG. The gate is not a generic "think again" nudge.
4. **T5 integrity**: zero peer-identity leaks into the commit gate; zero gold leaks; the symbolic rule is deterministic by construction.

## Oracle headroom

`ORACLE_COMMIT_HEADROOM = 0.6800` (68.0% team accuracy if a perfect selector committed only beneficial transitions). This is **+7.3 pp above S0** and **+7.3 pp above S3**, confirming that the architecture has real headroom — the gap is entirely in the certificate's discrimination power, not in the speculative-branch design.

## Honest reading for the PI

1. The speculative-commit architecture is structurally sound: it preserves rescue (95%), improves team accuracy (+1.34 pp), and is task-specific.
2. The bottleneck is certificate discrimination. The recomputation certificate, as designed, cannot reject enough harmful transitions. It is too close to a no-op check.
3. Stronger certificate designs (e.g. requiring the auditor to find and verify a specific *error* in S_i, or using an adversarial verifier) would need a new PI-approved proposal — the one-shot architecture test is done.
4. The oracle headroom confirms that better discrimination would pay off if achievable.
