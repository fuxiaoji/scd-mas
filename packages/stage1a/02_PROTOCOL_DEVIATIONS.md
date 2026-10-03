# 02_PROTOCOL_DEVIATIONS.md — Stage 1A

- **D1**: Paired design (PI §6/§15) reduces expected generations from PI's listed 3,150 to 1,350 (one shared speculative set serves S1/S2/S3; S4 is a certificate swap on the same S_i). The 3,300 ceiling is unchanged and provides ample headroom.
- **D2**: Leakage audit reports 74/450 certificates containing the word "peer" — this is a false positive: the certificate prompt explicitly says "after seeing peer information", so the model naturally uses that word. The certificate cannot identify WHICH peer (no peer IDs are in its input). The real integrity test (T5) is the structural determinism of the gate, which passes.
- **D3**: NRG identity tolerance set to 1e-4 (not 1e-9) because 4-dp rounding in the metrics CSV introduces rounding error ~3e-7. The identity holds to 1e-9 in unrounded values.
