# AGENT.md — scd-mas project charter (v0.1, Stage 0)

Project: **scd-mas** — Speculative-Commit Deliberation (SCD) for multi-agent LLM reasoning.
Successor to aove-mad (algorithmic line closed 2026-10-03, tag `AOVE_ALGO_LINE_CLOSED` in
`../aove-mad`). This charter adapts the aove-mad constitution; differences are marked.

## 0. Per-session read/write protocol
Read: AGENT.md → TODO.md → HAVEDO.md → memory/MEMORY.md → audit/AUDIT_LOG.md (if open items).
Write: HAVEDO.md → TODO.md → memory/ (one file per fact + MEMORY.md index) →
audit/AUDIT_LOG.md → git commit (format `stage<N>: <action> — <evidence>`) →
**package every round** via the repo's packaging script (aove-mad rule §8.1 carried over:
no package = round not finished).

## 1. Project identity
- Working method name: **SCD — Speculative-Commit Deliberation** (provisional; not a novelty
  claim until the Stage-0 collision review passes).
- Stage 0 (current): literature + architecture only. **NO INFERENCE AUTHORIZED.**
- Origin: the closed aove-mad line established an exploratory harm–rescue trade-off
  (peer exposure = high rescue/high contamination; protected verification = low/low) and an
  unrealized oracle headroom (+6.7 pp pooled team accuracy for a perfect exposure selector).
  SCD proposes peer influence as a **speculative state transition** with explicit
  COMMIT/ROLLBACK, aiming at the unserved middle of that frontier.
- Evidence rule: aove-mad results may be cited as motivating development observations;
  they are NOT validation evidence for SCD. SCD earns its own evidence under its own
  pre-registered gates.

## 2. Hard rules (inherited from aove-mad AGENT.md §4/§9, unchanged unless noted)
1. The local agent is an executor, not the PI: diagnose, never silently rewrite research
   questions.
2. No prompt search on held-out data; no seed selection by results; no deletion of failures;
   negative results are first-class.
3. New method variants require a written proposal (falsifiable hypothesis + minimal
   discriminating experiment + cost + stop rule) with PI approval.
4. Stage order may not be skipped; every stage ends with a package and a stop for PI review.
5. Collision audits precede any inference; five-factor stop conditions are honored verbatim.
6. No claim of novelty before the collision review; "provisional/working" labels are mandatory
   until then.
7. Pre-registration before every gold-joined analysis; one analysis pass; post-hoc scoring
   search forbidden.

## 3. Stage plan (PI may amend)
- Stage 0 (current): collision review, closest-work matrix, formalization, commit-gate design
  space, risk register, preliminary pre-registration. Deliverable:
  `SCD_STAGE0_COLLISION_REVIEW.zip`.
- Stage 1+: defined by the PI after Stage-0 review.

## 4. Directory contract
`AGENT.md HAVEDO.md TODO.md memory/ audit/ docs/ stage0/ src/ tests/ configs/ prompts/
audits/ sources/` — same writer rules as aove-mad (agents write code/prompts/configs;
control files are main-agent-only; `sources/` holds fetched primary-source snapshots for the
collision review).
