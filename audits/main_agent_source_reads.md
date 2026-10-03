# main-agent primary-source read notes (PART G/H/I duty)

1. LMAD — arXiv:2608.01463v2 (HTML full text, fetched 2026-10-03)
   - shared committed state P(ℓ): "The controller initializes an empty committed state P(0)";
     agents generate "(r_i, a_i) ∼ A_i(· | q, x, P(ℓ))" — no per-agent persistent states
   - guarded resolution: admits repair iff "the question's subject and relation are preserved,
     and every quotation appears verbatim in the provided context"; rejection → state unchanged,
     "falls back to a majority vote"; acceptance MONOTONE: "Nodes in P(ℓ) are not reopened"
   - suffix nodes "not debated but regenerated afresh from the updated state"
   - revisions: resolver proposal separate pre-check, then applied directly as append — no
     living side-branch
   - agents see: "(q, x), the committed state P(ℓ), its own localized segment, and brief
     descriptions of the competing claims"

2. COMED — arXiv:2609.26913 (abstract, AACL-IJCNLP 2026)
   - "anchor self-consistency, router margin, and a lightweight peer probe" decide
     accept/verify/escalate per QUERY; preventive ("only when collaboration is likely
     beneficial"); "dense collaboration invokes peers on every query" as contrast
   - no rollback, no per-agent immutable state, no delta validation

3. ReAgent — arXiv:2503.06951v2 (HTML full text)
   - per-agent local knowledge sets Φᵢᵗ ("its proposed assertions, retrieved evidence, or
     intermediate inferences") + global Φᵗ = ⋃ᵢ Φᵢᵗ; non-monotonic: statements "can be revoked
     if they lead to logical conflicts"
   - rollback object: knowledge-state checkpoints (per-agent LBGᵢ + global); local rollback
     "Φᵢᵗ ⟶ Φᵢʳ" invoked by Verifier on inconsistencies; global rollback by Supervisor
     (minimum conflict set, SAT-based)
   - "no true speculative branches" — corrections apply directly to the working state
   - triggers: internal conflict OR "contradictory evidence from other agents" (peer-induced
     changes ARE rolled back — detect-and-undo, not propose-and-approve)
   - agents see broadcast decompositions, assert/inform/reject/challenge messages; Answer-
     Assembler consumes other agents' knowledge sets

4. Debate or Vote — arXiv:2508.17536v2 (HTML full text, NeurIPS 2025 Spotlight)
   - MAD-oracle locking: "if agent i outputs the correct answer at round t, we use this
     response in all subsequent rounds" — explicitly "not feasible in practice"
   - MAD-Conformist/Follower: deployable heuristic gates using majority proxy
   - "no mechanism where peer influence is computed on a separate branch"; vanilla MAD
     overwrites in place ("incorrect signals can still be revised" — correct answers lost)
   - martingale theorem: debate alone does not improve expected correctness
