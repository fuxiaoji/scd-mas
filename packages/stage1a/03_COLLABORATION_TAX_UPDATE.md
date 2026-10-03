# 03_COLLABORATION_TAX_UPDATE.md — Collaboration Tax in the SCD context

The Collaboration Tax (arXiv:2608.22152, EMNLP 2026 Main) is added to the core related-work
matrix per PI Stage-1A §1.

## Relation to SCD

The Tax's four-stage conversational cascade (ungrounded claims → failure to query → skipping
integration → accepting without re-derivation) describes the *in-place acceptance* failure
mode that SCD's speculative-commit design directly targets: the Tax shows agents accepting
peer answers without re-derivation, which is exactly what SCD's rollback mechanism prevents
by requiring a recomputation certificate before adopting the peer-influenced state.

However, the Tax's intervention (a prompt-level "show re-derivation work" instruction) is
a *prompting* fix, not a *transactional state* fix. SCD's contribution is the architectural
mechanism (immutable incumbent + speculative branch + commit gate), not a prompt instruction.
The Tax's L4 re-derivation intervention is conceptually the closest existing analog to the
SCD commit gate's intent, but operates at the conversation level rather than the state level.

No novelty claim is made for rollback, verification, speculation, or commit individually.
The specific composition — speculative branch + immutable incumbent + recomputation
certificate + per-agent commit/rollback inside multi-agent reasoning — is the tested wedge.
