# 04_STAGE1A_RUN_REPORT.md — SCD Stage 1A execution narrative

## Environment
Same validated stack: RTX 5070 (sm_120), torch 2.11.0+cu128, transformers 4.49.0, autoawq
0.2.7.post3, triton-windows 3.8.0, AutoAWQ-Triton kernel path, model Qwen2.5-7B-Instruct-AWQ
@ b25037543e9394b818fdfca67ab2a00ecc7dd641. Fingerprint e459ef89eb03f178.

## Execution
- Registry: 150 questions (50 per dataset), seed 20261101, 0 overlap with aove-mad (1750 IDs excluded)
- R0: 450 generations (3 seeds x 150), temp 0.7, 28 min
- Speculative: 450 generations (temp 0, shared S1/S2/S3), 52 min
- Certificates: 450 generations (temp 0, cap 1024), 42 min
- Total: 1350 generations / ~1.4M tokens (within 1.6M ceiling)
- Assemble: 450 commit decisions (402 COMMIT / 48 ROLLBACK), S4 foreign-certificate decisions

## Key result
T1 FAIL: the recomputation certificate committed 89.3% of transitions, providing only 1.42pp
CWR suppression (threshold: 5pp). The certificate is task-specific (T4 PASS) but not
discriminative enough to bridge the harm-rescue gap on its own.
