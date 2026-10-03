#!/usr/bin/env python3
"""prepare_scd_registry.py — SCD Stage-1A development sample (PI §3).

150 questions (50 MMLU-Pro + 50 MATH-500 + 50 BenchForm) sampled from the SAME pinned
source revisions as the aove-mad P0 registry, with a NEW seed (SCD_SAMPLE_SEED = 20261101),
EXCLUDING every question registered in the aove-mad sample registry (any role) so the SCD
sample is fully disjoint from all AOVE data. Sampling is a permutation over canonical IDs —
gold is never read, and no AOVE outcome is consulted.

Outputs: data/sample_registry.json + data/sample_registry_audit.md (with SHA256).
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
AOVE = os.path.abspath(os.path.join(REPO, "..", "aove-mad"))
sys.path.insert(0, os.path.join(AOVE, "src"))  # reuse the pinned dataset loaders' environment

SCD_SAMPLE_SEED = 20261101
MMLU_PRO_REPO = "TIGER-Lab/MMLU-Pro"
MMLU_PRO_REVISION = "b189ec765aa7ed75c8acfea42df31fdae71f97be"
MATH_500_REPO = "HuggingFaceH4/MATH-500"
MATH_500_REVISION = "6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be"
BENCHFORM_COMMIT = "6425ecaebd9dd273a13ea28e32767c452e04c6a6"
BENCHFORM_DIR = os.environ.get("AOVE_BENCHFORM_DIR", os.path.join(os.path.dirname(REPO), "datasets_cache", "BenchForm"))
N_PER = 50


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def norm_ws(s: str) -> str:
    return " ".join(s.split())


def fmt_options(options: list[str]) -> str:
    return "\n".join(f"({chr(65 + i)}) {o}" for i, o in enumerate(options))


def load_aove_registered() -> set[str]:
    """Every canonical ID in the aove-mad sample registry (P0 + P1 reservations)."""
    path = os.path.join(AOVE, "data", "sample_registry.json")
    reg = json.load(open(path, encoding="utf-8"))
    return {r["canonical_question_id"] for r in reg["rows"]}


def load_mmlu_pro() -> list[dict]:
    import datasets

    ds = datasets.load_dataset(MMLU_PRO_REPO, split="test", revision=MMLU_PRO_REVISION)
    assert len(ds) == 12032
    rows = []
    for i, r in enumerate(ds):
        question = f"{r['question'].strip()}\n\nAnswer choices:\n{fmt_options(r['options'])}"
        rows.append({
            "question_id": f"mmlu_pro:test:{i}:{sha256_text(norm_ws(question))[:12]}",
            "dataset": "mmlu_pro", "prompt": question,
            "gold": chr(65 + int(r["answer_index"])), "category": r["category"],
        })
    return rows


def load_math_500() -> list[dict]:
    import datasets

    ds = datasets.load_dataset(MATH_500_REPO, split="test", revision=MATH_500_REVISION)
    assert len(ds) == 500
    rows = []
    for i, r in enumerate(ds):
        question = r["problem"].strip()
        rows.append({
            "question_id": f"math500:{r['unique_id']}:{sha256_text(norm_ws(question))[:12]}",
            "dataset": "math_500", "prompt": question,
            "gold": str(r["answer"]).strip(), "category": r.get("subject"),
        })
    return rows


def load_benchform() -> list[dict]:
    expected = {
        "causal_judgment.jsonl": 160, "date_understanding.jsonl": 300, "disambiguation_qa.jsonl": 228,
        "hyperbaton.jsonl": 300, "logical_deduction_five_objects.jsonl": 220,
        "movie_recommendation.jsonl": 300, "navigate.jsonl": 300, "ruin_names.jsonl": 300,
        "snarks.jsonl": 151, "sports_understanding.jsonl": 300, "temporal_sequences.jsonl": 300,
        "tracking_shuffled_objects_three_objects.jsonl": 220, "web_of_lies.jsonl": 220,
    }
    rows = []
    base = os.path.join(BENCHFORM_DIR, "data", "jsonl")
    for fname in sorted(expected):
        n = 0
        for line in open(os.path.join(base, fname), encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            gold = chr(65 + r["multiple_choice_scores"].index(1))
            question = r["parsed_inputs"].strip()
            task = fname[: -len(".jsonl")]
            rows.append({
                "question_id": f"benchform:{task}:{n}:{sha256_text(norm_ws(question))[:12]}",
                "dataset": "benchform", "prompt": question, "gold": gold, "category": task,
            })
            n += 1
        assert n == expected[fname], fname
    return rows


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    aove_ids = load_aove_registered()
    print(f"aove-mad registered IDs to exclude: {len(aove_ids)}")
    loaders = {"mmlu_pro": load_mmlu_pro, "math_500": load_math_500, "benchform": load_benchform}
    registry, per_ds = [], {}
    questions_frozen, scoring_key = [], []
    for ds, loader in loaders.items():
        catalog = loader()
        ids = [r["question_id"] for r in catalog]
        fresh = [r for r in catalog if r["question_id"] not in aove_ids]
        rng = random.Random(SCD_SAMPLE_SEED + hash(ds) % 1000)  # per-dataset deterministic stream
        perm = list(range(len(fresh)))
        rng.shuffle(perm)
        taken = [fresh[i] for i in perm[:N_PER]]
        assert len(taken) == N_PER, f"{ds}: only {len(taken)} fresh questions"
        for r in taken:
            registry.append({
                "dataset": ds,
                "canonical_question_id": r["question_id"],
                "source_revision": {"mmlu_pro": MMLU_PRO_REVISION, "math_500": MATH_500_REVISION,
                                    "benchform": BENCHFORM_COMMIT}[ds],
                "sample_role": "SCD_DEV",
                "question_hash": sha256_text(norm_ws(r["prompt"])),
                "gold_hash": sha256_text(r["gold"])[:16],  # hash only; gold text stays out of the registry
            })
            questions_frozen.append({
                "question_id": r["question_id"], "dataset": ds, "prompt": r["prompt"],
                "category": r["category"], "question_hash": sha256_text(norm_ws(r["prompt"])),
            })  # NO gold here — scoring key is separate and joined only after the audit freeze
            scoring_key.append({"question_id": r["question_id"], "gold": r["gold"],
                                "gold_hash": sha256_text(r["gold"])[:16]})
        per_ds[ds] = {"catalog": len(catalog), "fresh_after_aove_exclusion": len(fresh), "sampled": len(taken)}
        print(f"{ds}: catalog {len(catalog)} | fresh {len(fresh)} | sampled {len(taken)}")

    assert len(registry) == 150
    registry.sort(key=lambda r: r["canonical_question_id"])
    payload = {
        "created_utc": stamp,
        "scd_sample_seed": SCD_SAMPLE_SEED,
        "selection_rule": "deterministic permutation of the pinned catalogs EXCLUDING all aove-mad registered IDs; gold never read; AOVE outcomes never consulted",
        "excluded_aove_ids": len(aove_ids),
        "per_dataset": per_ds,
        "rows": registry,
    }
    os.makedirs(os.path.join(REPO, "data"), exist_ok=True)
    with open(os.path.join(REPO, "data", "scd_questions_frozen.jsonl"), "w", encoding="utf-8") as fh:
        for r in questions_frozen:
            fh.write(json.dumps(r, ensure_ascii=False) + chr(10))
    with open(os.path.join(REPO, "data", "scd_scoring_key.json"), "w", encoding="utf-8") as fh:
        json.dump({"note": "gold scoring key — joined ONLY after runs/stage1a/raw outputs are frozen (PI §13)",
                   "created_utc": stamp, "entries": scoring_key}, fh, indent=1, ensure_ascii=False)
    out = os.path.join(REPO, "data", "sample_registry.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    sha = sha256_text(open(out, encoding="utf-8").read())

    # gold-blind disjointness proof vs the aove-mad registry
    overlap = sum(1 for r in registry if r["canonical_question_id"] in aove_ids)
    audit = "\n".join([
        "# sample_registry_audit.md — SCD Stage-1A (PI §3)",
        "",
        f"Created {stamp}. Seed {SCD_SAMPLE_SEED}. 150 questions (50 per dataset).",
        f"- overlap with the aove-mad sample registry (any role): **{overlap}** (must be 0)",
        "- gold: never read during sampling (only gold HASHES recorded, for post-hoc scoring joins)",
        "- AOVE outcomes: never consulted",
        f"- sample_registry.json SHA256: `{sha}`",
        "",
        "The registry is frozen before any SCD inference.",
    ])
    with open(os.path.join(REPO, "data", "sample_registry_audit.md"), "w", encoding="utf-8") as fh:
        fh.write(audit + "\n")
    print(f"registry frozen: 150 rows | overlap={overlap} | sha={sha[:16]}…")
    return 0 if overlap == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
