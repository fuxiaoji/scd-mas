#!/usr/bin/env python3
"""run_stage1a.py — SCD transactional commit feasibility runner (PI §3–§10, §13, §15).

Phases (all resumable via journals):
  r0           450 R0 generations (3 seeds x 150 questions), dataset-specific contracts
  speculative  450 peer-exposed speculative revisions — ONE shared generation set
               serving S1 (adopt), S2 (discard), S3 (gate) per PI §6/§15
  certificates 450 recomputation certificates (temp 0) over the P->S transitions
  assemble     deterministic commit decisions (PASS->COMMIT else ROLLBACK; S4 = foreign
               certificate status), per-condition outcome rows, freeze + SHA256s

Gold lives only in data/scd_scoring_key.json and is joined exclusively by
analyze_stage1a.py AFTER the raw outputs are frozen (PI §13).
Backend: the exact validated aove-mad stack imported from ../aove-mad/src.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
AOVE = os.path.abspath(os.path.join(REPO, "..", "aove-mad"))
sys.path.insert(0, os.path.join(AOVE, "src"))

from aove.backend import (  # noqa: E402
    Backend,
    GenerationRequest,
    GenerationResult,
    LocalBackend,
)
from aove.parsing import normalize_answer, parse_success  # noqa: E402

MODEL_REPO = "Qwen/Qwen2.5-7B-Instruct-AWQ"
MODEL_REVISION = "b25037543e9394b818fdfca67ab2a00ecc7dd641"
R0_SEEDS = (20261011, 20261012, 20261013)
SPEC_SEED = 20261014
CERT_SEED = 20261015
SOLVER_CAP = 2048
CERT_CAP = 1024
MAX_GENERATIONS = 3300
TOKEN_CEILING = 1_600_000
MCQ = {"mmlu_pro", "benchform"}
NS = os.path.join(REPO, "runs", "stage1a")
RAW = os.path.join(NS, "raw")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_comment(t: str) -> str:
    return re.sub(r"<!--.*?-->", "", t, flags=re.DOTALL).lstrip()


def render(template: str, **kwargs: str) -> str:
    def sub(m: re.Match) -> str:
        if m.group(1) not in kwargs:
            raise KeyError(f"marker <<{m.group(1)}>> unfilled")
        return kwargs[m.group(1)]
    out = re.sub(r"<<([a-z_]+)>>", sub, template)
    if re.search(r"<<[a-z_]+>>", out):
        raise KeyError("unfilled markers remain")
    return out


def load_jsonl(path: str) -> list[dict]:
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and "__header__" not in line and "__repair__" not in line:
                out.append(json.loads(line))
    return out


def prompt_text(name: str) -> str:
    return strip_comment(open(os.path.join(REPO, "prompts", name), encoding="utf-8").read())


def fmt_block(dataset: str) -> str:
    name = "r0.md" if dataset in MCQ else "r0_math.md"
    t = prompt_text(name)
    # extract just the output-contract instructions (after "Instructions:")
    idx = t.find("Instructions:")
    return t[idx:].strip() if idx != -1 else t


class Journal:
    name = "journal"

    def __init__(self, inner: Backend, path: str) -> None:
        self.inner = inner
        self._records: dict[str, GenerationResult] = {}
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    rec = json.loads(line)
                    self._records[rec["request_key"]] = GenerationResult(**rec["result"])
        self.path = path
        self._fh = open(path, "a", encoding="utf-8")

    def generate(self, req: GenerationRequest) -> GenerationResult:
        hit = self._records.get(req.key())
        if hit is not None:
            return GenerationResult(**{**hit.__dict__, "is_fresh": False})
        res = self.inner.generate(req)
        self._fh.write(json.dumps({"request_key": req.key(), "ts": now_utc(), "result": res.__dict__}, ensure_ascii=False) + "\n")
        self._fh.flush()
        self._records[req.key()] = res
        return res

    def close(self) -> None:
        if self._fh and not self._fh.closed:
            self._fh.close()


def fingerprint() -> tuple[str, dict]:
    import importlib.metadata as md

    import torch
    import transformers
    import triton

    props = torch.cuda.get_device_properties(0)
    fp = {
        "model": MODEL_REPO, "model_revision": MODEL_REVISION,
        "torch": str(torch.__version__), "cuda_runtime": str(torch.version.cuda),
        "gpu": props.name, "compute_capability": f"sm{props.major}{props.minor}",
        "transformers": str(transformers.__version__), "autoawq": str(md.version("autoawq")),
        "triton": str(triton.__version__),
        "kernel_path": "AutoAWQ Triton (identical to P0-V2/GPU-acceptance stack)",
        "os": platform.platform(),
    }
    return hashlib.sha256(json.dumps(fp, sort_keys=True).encode()).hexdigest()[:16], fp


def questions() -> dict[str, dict]:
    out = {}
    for r in load_jsonl(os.path.join(REPO, "data", "scd_questions_frozen.jsonl")):
        out[r["question_id"]] = r
    assert len(out) == 150
    return out


def r0_request(qid: str, prompt: str, dataset: str, seed: int) -> GenerationRequest:
    tpl = prompt_text("r0.md") if dataset in MCQ else prompt_text("r0_math.md")
    return GenerationRequest(
        purpose="r0", question_id=qid, prompt=render(tpl, question=prompt), seed=seed,
        temperature=0.7, top_p=0.95, max_tokens=SOLVER_CAP,
        model=MODEL_REPO, model_revision=MODEL_REVISION, agent_index=R0_SEEDS.index(seed),
    )


def phase_r0() -> None:
    qs = questions()
    journal = Journal(LocalBackend(MODEL_REPO, MODEL_REVISION), os.path.join(NS, "r0_journal.jsonl"))
    budget = BudgetGuardLite(MAX_GENERATIONS, TOKEN_CEILING)
    n_new = 0
    t0 = time.time()
    try:
        with open(os.path.join(RAW, "r0.jsonl"), "a", encoding="utf-8") as out:
            if not os.path.getsize(os.path.join(RAW, "r0.jsonl")):
                out.write(json.dumps({"__header__": {"label": "SCD STAGE1A R0", "stage": "STAGE1A",
                                                     "scientific_data": True, "model": MODEL_REPO,
                                                     "model_revision": MODEL_REVISION, "created_utc": now_utc()}}, ensure_ascii=False) + "\n")
            for qid in sorted(qs):
                q = qs[qid]
                for seed in R0_SEEDS:
                    req = r0_request(qid, q["prompt"], q["dataset"], seed)
                    res = journal.generate(req)
                    if res.is_fresh:
                        n_new += 1
                        budget.charge(res)
                        out.write(json.dumps({
                            "question_id": qid, "dataset": q["dataset"], "agent_index": R0_SEEDS.index(seed),
                            "seed": seed, "request_key": req.key(),
                            "raw_output": res.text,
                            "parsed_answer": normalize_answer(res.text, q["dataset"]),
                            "prompt_tokens": res.prompt_tokens, "completion_tokens": res.completion_tokens,
                            "hit_length_cap": res.completion_tokens >= SOLVER_CAP,
                            "scientific_data": True, "stage": "STAGE1A", "ts": now_utc(),
                        }, ensure_ascii=False) + "\n")
                        out.flush()
                    if n_new % 50 == 0 and n_new:
                        print(f"[r0] {n_new} new in {(time.time()-t0)/60:.1f} min | budget {budget.report()}")
    finally:
        journal.close()
    print(f"[r0] complete: {n_new} new | {budget.report()}")


def peer_pairs(qid: str, agents: dict[int, dict]) -> list[tuple[int, int, int]]:
    """For agent i, the two peers (by agent_index)."""
    out = []
    for i in range(3):
        peers = [j for j in range(3) if j != i]
        out.append((i, peers[0], peers[1]))
    return out


def phase_speculative() -> None:
    """ONE shared peer-exposed speculative generation per (question, agent) — serves S1/S2/S3."""
    qs = questions()
    r0 = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "r0.jsonl")):
        r0[r["question_id"]][r["agent_index"]] = r
    missing = [q for q in sorted(r0) if len(r0[q]) < 3]
    if missing:
        raise SystemExit(f"R0 incomplete for {len(missing)} questions — run r0 first")
    tpl = prompt_text("speculative_revision.md")
    journal = Journal(LocalBackend(MODEL_REPO, MODEL_REVISION), os.path.join(NS, "spec_journal.jsonl"))
    budget = BudgetGuardLite(MAX_GENERATIONS, TOKEN_CEILING)
    n_new = 0
    t0 = time.time()
    try:
        with open(os.path.join(RAW, "speculative_states.jsonl"), "a", encoding="utf-8") as out:
            if not os.path.getsize(os.path.join(RAW, "speculative_states.jsonl")):
                out.write(json.dumps({"__header__": {"label": "SCD STAGE1A speculative states (shared S1/S2/S3)",
                                                     "stage": "STAGE1A", "scientific_data": True,
                                                     "model": MODEL_REPO, "model_revision": MODEL_REVISION,
                                                     "created_utc": now_utc()}}, ensure_ascii=False) + "\n")
            for qid in sorted(r0):
                q = qs[qid]
                for i, p1, p2 in peer_pairs(qid, r0[qid]):
                    own, a1, a2 = r0[qid][i], r0[qid][p1], r0[qid][p2]
                    prompt = render(tpl, question=q["prompt"],
                                    own_reasoning=own["raw_output"],
                                    own_answer=str(own["parsed_answer"]),
                                    peer1_reasoning=a1["raw_output"], peer1_answer=str(a1["parsed_answer"]),
                                    peer2_reasoning=a2["raw_output"], peer2_answer=str(a2["parsed_answer"]),
                                    answer_format=fmt_block(q["dataset"]))
                    req = GenerationRequest(purpose="speculative", question_id=qid, prompt=prompt,
                                            seed=SPEC_SEED + i, temperature=0.0, top_p=1.0,
                                            max_tokens=SOLVER_CAP, model=MODEL_REPO,
                                            model_revision=MODEL_REVISION, agent_index=i)
                    res = journal.generate(req)
                    if res.is_fresh:
                        n_new += 1
                        budget.charge(res)
                        out.write(json.dumps({
                            "question_id": qid, "dataset": q["dataset"], "agent_index": i,
                            "seed": req.seed, "request_key": req.key(),
                            "raw_output": res.text,
                            "parsed_answer": normalize_answer(res.text, q["dataset"]),
                            "p_answer": own["parsed_answer"],
                            "prompt_tokens": res.prompt_tokens, "completion_tokens": res.completion_tokens,
                            "hit_length_cap": res.completion_tokens >= SOLVER_CAP,
                            "serves_conditions": ["S1", "S2", "S3"],
                            "scientific_data": True, "stage": "STAGE1A", "ts": now_utc(),
                        }, ensure_ascii=False) + "\n")
                        out.flush()
                    if n_new % 50 == 0 and n_new:
                        print(f"[spec] {n_new} new in {(time.time()-t0)/60:.1f} min | budget {budget.report()}")
    finally:
        journal.close()
    print(f"[spec] complete: {n_new} new | {budget.report()}")


def delta_description(p_ans, s_ans, p_txt: str, s_txt: str) -> str:
    if p_ans == s_ans:
        return f"The stated final answer did NOT change (remains {p_ans!r}); the delta, if any, is in the reasoning only."
    return f"The stated final answer CHANGED from {p_ans!r} (state P) to {s_ans!r} (state S)."


def phase_certificates() -> None:
    qs = questions()
    r0 = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "r0.jsonl")):
        r0[r["question_id"]][r["agent_index"]] = r
    spec = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "speculative_states.jsonl")):
        spec[r["question_id"]][r["agent_index"]] = r
    missing = [q for q in sorted(spec) if len(spec[q]) < 3]
    if missing:
        raise SystemExit(f"speculative incomplete for {len(missing)} questions — run speculative first")
    tpl = prompt_text("recompute_certificate.md")
    journal = Journal(LocalBackend(MODEL_REPO, MODEL_REVISION), os.path.join(NS, "cert_journal.jsonl"))
    budget = BudgetGuardLite(MAX_GENERATIONS, TOKEN_CEILING)
    n_new = 0
    t0 = time.time()
    try:
        with open(os.path.join(RAW, "certificates.jsonl"), "a", encoding="utf-8") as out:
            if not os.path.getsize(os.path.join(RAW, "certificates.jsonl")):
                out.write(json.dumps({"__header__": {"label": "SCD STAGE1A recomputation certificates",
                                                     "stage": "STAGE1A", "scientific_data": True,
                                                     "model": MODEL_REPO, "model_revision": MODEL_REVISION,
                                                     "created_utc": now_utc()}}, ensure_ascii=False) + "\n")
            for qid in sorted(spec):
                q = qs[qid]
                for i in range(3):
                    p, s = r0[qid][i], spec[qid][i]
                    p_ans, s_ans = p["parsed_answer"], s["parsed_answer"]
                    delta = delta_description(p_ans, s_ans, p["raw_output"], s["raw_output"])
                    prompt = render(tpl, question=q["prompt"], p_reasoning=p["raw_output"],
                                    p_answer=str(p_ans), s_reasoning=s["raw_output"],
                                    s_answer=str(s_ans), delta=delta)
                    req = GenerationRequest(purpose="certificate", question_id=qid, prompt=prompt,
                                            seed=CERT_SEED + i, temperature=0.0, top_p=1.0,
                                            max_tokens=CERT_CAP, model=MODEL_REPO,
                                            model_revision=MODEL_REVISION, agent_index=i)
                    res = journal.generate(req)
                    if res.is_fresh:
                        n_new += 1
                        budget.charge(res)
                        truncated = res.completion_tokens >= CERT_CAP
                        parsed = parse_certificate(res.text)
                        if parsed["parse_ok"] and not truncated:
                            status = parsed["certificate_status"]
                        else:
                            status = "UNABLE"  # fail closed (PI §13): truncated/invalid => UNABLE => ROLLBACK
                        out.write(json.dumps({
                            "question_id": qid, "dataset": q["dataset"], "agent_index": i,
                            "seed": req.seed, "request_key": req.key(),
                            "p_answer": p_ans, "s_answer": s_ans, "delta": delta,
                            "raw_output": res.text, "parsed": parsed,
                            "certificate_status": status,
                            "truncated": truncated,
                            "prompt_tokens": res.prompt_tokens, "completion_tokens": res.completion_tokens,
                            "scientific_data": True, "stage": "STAGE1A", "ts": now_utc(),
                        }, ensure_ascii=False) + "\n")
                        out.flush()
                    if n_new % 50 == 0 and n_new:
                        print(f"[cert] {n_new} new in {(time.time()-t0)/60:.1f} min | budget {budget.report()}")
    finally:
        journal.close()
    print(f"[cert] complete: {n_new} new | {budget.report()}")


def parse_certificate(text: str) -> dict:
    out = {"parse_ok": False, "claim_changed": None, "old_value": None, "new_value": None,
           "recomputation": None, "expected_check_result": None, "certificate_status": "UNABLE",
           "error": None}
    if not text or not text.strip():
        out["error"] = "empty"
        return out
    blob = re.sub(r"^```(?:json)?\s*", "", text.strip())
    blob = re.sub(r"\s*```$", "", blob).strip()
    try:
        st, en = blob.find("{"), blob.rfind("}")
        if st == -1 or en <= st:
            raise ValueError("no JSON object")
        data = json.loads(blob[st : en + 1])
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"unparseable:{type(exc).__name__}"
        return out
    keys = ("claim_changed", "old_value", "new_value", "recomputation", "expected_check_result")
    if any(not isinstance(data.get(k), str) or not data.get(k).strip() for k in keys):
        out["error"] = "missing_or_empty_fields"
        return out
    status = str(data.get("certificate_status", "")).upper()
    if status not in {"PASS", "FAIL", "UNABLE"}:
        out["error"] = "invalid_status"
        return out
    out.update({k: data[k][:600] for k in keys}, certificate_status=status, parse_ok=True)
    return out


class BudgetGuardLite:
    def __init__(self, max_gens: int, max_tokens: int) -> None:
        self.max_gens, self.max_tokens = max_gens, max_tokens
        self.gens = self.toks = 0

    def charge(self, res: GenerationResult) -> None:
        self.gens += 1
        self.toks += res.prompt_tokens + res.completion_tokens
        if self.gens > self.max_gens or self.toks > self.max_tokens:
            raise SystemExit(f"STAGE1A BUDGET EXCEEDED: {self.gens} gens / {self.toks} tokens vs "
                             f"ceilings {self.max_gens}/{self.max_tokens} — STOP_AND_REPORT (PI §14)")

    def report(self) -> str:
        return f"{self.gens} gens / {self.toks} tokens (ceilings {self.max_gens}/{self.max_tokens})"


def git_state() -> dict:
    def g(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
    return {"commit": g("rev-parse", "HEAD"), "dirty": len([l for l in g("status", "--porcelain").splitlines() if l.strip() and "runs/" not in l and "data/" not in l])}


def phase_assemble() -> None:
    """Deterministic commit decisions + per-condition outcome rows + freeze."""
    fp_id, fp = fingerprint()
    r0 = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "r0.jsonl")):
        r0[r["question_id"]][r["agent_index"]] = r
    spec = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "speculative_states.jsonl")):
        spec[r["question_id"]][r["agent_index"]] = r
    certs = {(r["question_id"], r["agent_index"]): r for r in load_jsonl(os.path.join(RAW, "certificates.jsonl"))}
    if len(certs) != 450:
        raise SystemExit(f"certificates incomplete: {len(certs)}/450")

    # S4 foreign certificate: same dataset, similar certificate length, different question (seed 20261102)
    rng = random.Random(20261102)
    cert_meta = []
    for (qid, i), c in sorted(certs.items()):
        cert_meta.append({"qid": qid, "agent": i, "dataset": c["dataset"],
                          "len": len(c["raw_output"]), "status": c["certificate_status"]})
    foreign = {}
    for qid in sorted({c["qid"] for c in cert_meta}):
        for i in range(3):
            own = next(c for c in cert_meta if c["qid"] == qid and c["agent"] == i)
            cands = [c for c in cert_meta if c["qid"] != qid and c["dataset"] == own["dataset"]]
            if not cands:
                cands = [c for c in cert_meta if c["qid"] != qid]
            cands.sort(key=lambda c: (abs(c["len"] - own["len"]), c["qid"], c["agent"]))
            top = [c for c in cands if abs(c["len"] - own["len"]) == abs(cands[0]["len"] - own["len"])]
            pick = rng.choice(sorted(top, key=lambda c: (c["qid"], c["agent"])))
            foreign[(qid, i)] = pick

    os.makedirs(RAW, exist_ok=True)
    with open(os.path.join(RAW, "s3_decisions.jsonl"), "w", encoding="utf-8") as out:
        out.write(json.dumps({"__header__": {"label": "SCD STAGE1A commit decisions (S3 own-cert; S4 foreign-cert)",
                                             "stage": "STAGE1A", "scientific_data": True,
                                             "gate": "PASS->COMMIT; FAIL/UNABLE->ROLLBACK; deterministic",
                                             "created_utc": now_utc()}}, ensure_ascii=False) + "\n")
        for (qid, i), c in sorted(certs.items()):
            own_status = c["certificate_status"]
            s3_commit = own_status == "PASS"
            f = foreign[(qid, i)]
            fstatus = next(cc["status"] for cc in cert_meta if cc["qid"] == f["qid"] and cc["agent"] == f["agent"])
            s4_commit = fstatus == "PASS"
            out.write(json.dumps({
                "question_id": qid, "agent_index": i, "dataset": c["dataset"],
                "own_certificate_status": own_status, "s3_commit": s3_commit,
                "foreign_certificate": {"question_id": f["qid"], "agent_index": f["agent"],
                                        "status": fstatus, "matched_by": "same dataset, similar length"},
                "s4_commit": s4_commit,
                "p_answer_hash": hashlib.sha256(str(r0[qid][i]["parsed_answer"]).encode()).hexdigest()[:16],
                "s_answer_hash": hashlib.sha256(str(spec[qid][i]["parsed_answer"]).encode()).hexdigest()[:16],
                "certificate_hash": hashlib.sha256(c["raw_output"].encode()).hexdigest()[:16],
                "scientific_data": True, "stage": "STAGE1A", "ts": now_utc(),
            }, ensure_ascii=False) + "\n")

    for name, path in (("r0.jsonl", os.path.join(RAW, "r0.jsonl")),
                       ("speculative_states.jsonl", os.path.join(RAW, "speculative_states.jsonl")),
                       ("certificates.jsonl", os.path.join(RAW, "certificates.jsonl")),
                       ("s3_decisions.jsonl", os.path.join(RAW, "s3_decisions.jsonl"))):
        sha = sha256_file(path)
        with open(os.path.join(RAW, f"freeze_{name}.sha256"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"file": f"runs/stage1a/raw/{name}", "sha256": sha, "frozen_utc": now_utc()}, indent=2) + "\n")
        import shutil

        os.makedirs(os.path.join(REPO, "raw"), exist_ok=True)
        shutil.copy(path, os.path.join(REPO, "raw", f"stage1a_{name}"))
    import yaml

    manifest = {
        "run_id": f"STAGE1A-{now_utc().replace(':', '').replace('-', '')}",
        "created_utc": now_utc(), "git": git_state(),
        "model": fp, "backend_fingerprint_id": fp_id,
        "registry_sha256": sha256_file(os.path.join(REPO, "data", "sample_registry.json")),
        "decoding": {"r0": {"temperature": 0.7, "top_p": 0.95, "seeds": list(R0_SEEDS), "max_new_tokens": SOLVER_CAP},
                     "speculative": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": SOLVER_CAP},
                     "certificate": {"temperature": 0.0, "top_p": 1.0, "max_new_tokens": CERT_CAP}},
        "commit_gate": "PASS->COMMIT; FAIL/UNABLE->ROLLBACK (deterministic, PI §8)",
        "budget": {"MAX_STAGE1A_GENERATIONS": MAX_GENERATIONS, "TOKEN_CEILING": TOKEN_CEILING},
        "note": "S1/S2/S3 share one speculative generation set (PI §6/§15 paired design)",
    }
    with open(os.path.join(NS, "RUN_MANIFEST.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True)
    print(f"[assemble] frozen: {len(certs)} certificates, decisions written, manifest fingerprint={fp_id}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phase", choices=("r0", "speculative", "certificates", "assemble"))
    args = ap.parse_args()
    os.makedirs(NS, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    for f, p in (("r0.jsonl", "r0"), ("speculative_states.jsonl", "speculative"),
                 ("certificates.jsonl", "certificates")):
        if not os.path.exists(os.path.join(RAW, f)):
            open(os.path.join(RAW, f), "w", encoding="utf-8").close()
    if args.phase == "r0":
        phase_r0()
    elif args.phase == "speculative":
        phase_speculative()
    elif args.phase == "certificates":
        phase_certificates()
    else:
        phase_assemble()
    return 0


if __name__ == "__main__":
    sys.exit(main())
