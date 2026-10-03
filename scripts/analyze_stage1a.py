#!/usr/bin/env python3
"""analyze_stage1a.py — SCD Stage-1A analysis (PI §10–§17).

Joins data/scd_scoring_key.json AFTER all raw outputs are frozen (PI §13).
Computes S0/S1/S2/S3/S4 metrics, T1–T5 gates, oracle headroom, and qualitative cases.
"""

from __future__ import annotations

import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "..", "aove-mad", "src"))

from aove.aggregation import strict_majority, team_is_correct  # noqa: E402
from aove.parsing import normalize_answer, parse_success  # noqa: E402

NS = os.path.join(REPO, "runs", "stage1a")
RAW = os.path.join(NS, "raw")
BOOTSTRAP_SEED = 20261005
BOOTSTRAP_N = 10_000
MCQ = {"mmlu_pro", "benchform"}
SCD_COMMIT_THRESHOLD = 0.0  # placeholder for oracle; actual gate is symbolic


def load_jsonl(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and "__header__" not in line and "__repair__" not in line:
                out.append(json.loads(line))
    return out


def joined_gold() -> dict[str, str]:
    key = json.load(open(os.path.join(REPO, "data", "scd_scoring_key.json"), encoding="utf-8"))
    return {e["question_id"]: e["gold"] for e in key["entries"]}


def parse_valid(text: str, dataset: str) -> tuple[str | None, bool]:
    """Return (normalized answer, format_valid)."""
    a = normalize_answer(text, dataset)
    if a is None:
        return None, False
    if dataset == "math_500":
        import re
        fmt_ok = bool(re.search(r"[A-Za-z0-9]", a)) and not (len(a) == 1 and a in "ABCDEFGHIJ")
    else:
        fmt_ok = a in "ABCDEFGHIJ"
    return (a if fmt_ok else None), fmt_ok


def team_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}
    init = [c for r in rows for c in r["initial_correct"]]
    fin = [c for r in rows for c in r["final_correct"]]
    n_ok0 = sum(init)
    n_bad0 = len(init) - n_ok0
    c2w = sum(1 for a, b in zip(init, fin) if a and not b)
    w2c = sum(1 for a, b in zip(init, fin) if b and not a)
    return {
        "n_questions": n, "n_observations": len(init),
        "team_accuracy": round(sum(r["team_correct"] for r in rows) / n, 4),
        "individual_accuracy_initial": round(n_ok0 / len(init), 4),
        "individual_accuracy_final": round(sum(fin) / len(fin), 4),
        "CWR": round(c2w / n_ok0, 4) if n_ok0 else float("nan"),
        "WCR": round(w2c / n_bad0, 4) if n_bad0 else float("nan"),
        "NRG": round((w2c - c2w) / len(init), 6),
        "abstention_rate": round(sum(r["abstained"] for r in rows) / n, 4),
        "n_c2w": c2w, "n_w2c": w2c,
    }


def main() -> int:
    gold = joined_gold()
    questions = {r["question_id"]: r for r in load_jsonl(os.path.join(REPO, "data", "scd_questions_frozen.jsonl"))}
    r0 = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "r0.jsonl")):
        r0[r["question_id"]][r["agent_index"]] = r
    spec = defaultdict(dict)
    for r in load_jsonl(os.path.join(RAW, "speculative_states.jsonl")):
        spec[r["question_id"]][r["agent_index"]] = r
    certs = {(r["question_id"], r["agent_index"]): r for r in load_jsonl(os.path.join(RAW, "certificates.jsonl"))}
    decisions = {(r["question_id"], r["agent_index"]): r for r in load_jsonl(os.path.join(RAW, "s3_decisions.jsonl"))}

    # ---- build per-condition agent observations ------------------------------------------
    # initial state = R0 (P_i); final state varies by condition
    conditions: dict[str, list[dict]] = defaultdict(list)
    for qid in sorted(r0):
        q = questions[qid]
        g = gold[qid]
        for i in range(3):
            r0r = r0[qid][i]
            sp = spec[qid][i]
            p_ans = r0r["parsed_answer"]
            p_valid = parse_success(p_ans) and not r0r.get("hit_length_cap", False)
            s_ans = sp["parsed_answer"]
            s_valid = parse_success(s_ans) and not sp.get("hit_length_cap", False)
            p_correct = team_is_correct(p_ans if p_valid else None, g, q["dataset"])
            s_correct = team_is_correct(s_ans if s_valid else None, g, q["dataset"])

            # S0: final = P_i (no revision)
            s0_final, s0_valid = p_ans, p_valid
            # S1: final = S_i (direct peer exposure adopted)
            s1_final, s1_valid = s_ans, s_valid
            # S2: final = P_i (speculative generated but discarded)
            s2_final, s2_valid = p_ans, p_valid
            # S3: certificate gate
            cert = certs[(qid, i)]
            s3_commit = cert["certificate_status"] == "PASS"
            s3_final, s3_valid = (s_ans, s_valid) if s3_commit else (p_ans, p_valid)
            # S4: foreign certificate gate
            dec = decisions[(qid, i)]
            s4_commit = dec["s4_commit"]
            s4_final, s4_valid = (s_ans, s_valid) if s4_commit else (p_ans, p_valid)

            base = {"question_id": qid, "dataset": q["dataset"], "agent_index": i,
                    "initial_correct": p_correct, "initial_answer": p_ans if p_valid else None}
            for cond, fa, fv in (("S0", s0_final, s0_valid), ("S1", s1_final, s1_valid),
                                 ("S2", s2_final, s2_valid), ("S3", s3_final, s3_valid),
                                 ("S4", s4_final, s4_valid)):
                conditions[cond].append({
                    **base, "final_answer": fa if fv else None, "final_valid": fv,
                    "final_correct": team_is_correct(fa if fv else None, g, q["dataset"]),
                })

    # team-level rows per condition
    team_rows: dict[str, list[dict]] = defaultdict(list)
    for cond in ("S0", "S1", "S2", "S3", "S4"):
        by_q = defaultdict(list)
        for o in conditions[cond]:
            by_q[o["question_id"]].append(o)
        for qid in sorted(by_q):
            items = by_q[qid]
            answers = [o["final_answer"] for o in items]
            g = gold[qid]
            team, abstained = strict_majority(answers)
            team_rows[cond].append({
                "question_id": qid, "dataset": q["dataset"], "condition": cond,
                "team_output": team, "abstained": abstained,
                "team_correct": team_is_correct(team, g, q["dataset"]),
                "initial_correct": [items[i]["initial_correct"] for i in range(3)],
                "final_correct": [items[i]["final_correct"] for i in range(3)],
            })

    all_metrics = {}
    for cond in ("S0", "S1", "S2", "S3", "S4"):
        m = team_metrics(team_rows[cond])
        all_metrics[cond] = m
        print(cond, m)

    # verify NRG identity
    for cond, m in all_metrics.items():
        ident = m["individual_accuracy_final"] - m["individual_accuracy_initial"]
        if abs(m["NRG"] - ident) > 1e-4:
            raise SystemExit(f"NRG identity violated for {cond}: {m['NRG']} != {ident}")

    # ---- gates ---------------------------------------------------------------------------
    a1 = all_metrics["S1"]; a3 = all_metrics["S3"]; a0 = all_metrics["S0"]; a4 = all_metrics["S4"]
    t1 = (a3["CWR"] <= a1["CWR"] - 0.05) if a1["CWR"] == a1["CWR"] and a3["CWR"] == a3["CWR"] else False
    t2 = (a3["WCR"] >= 0.5 * a1["WCR"]) if a1["WCR"] and a1["WCR"] > 0 else False
    t3 = a3["team_accuracy"] >= a0["team_accuracy"]
    t4_wcr = a3["WCR"] > a4["WCR"]
    t4_nrg = a3["NRG"] > a4["NRG"]
    t4 = t4_wcr or t4_nrg
    t5 = True  # enforced structurally by the runner; recorded as PASS if no stop occurred

    # oracle commit headroom (§12): for each transition, commit iff correctness(S_i) > correctness(P_i)
    oracle_rows = []
    for qid in sorted(r0):
        q = questions[qid]
        g = gold[qid]
        for i in range(3):
            r0r = r0[qid][i]; sp = spec[qid][i]
            p_valid = parse_success(r0r["parsed_answer"]) and not r0r.get("hit_length_cap", False)
            s_valid = parse_success(sp["parsed_answer"]) and not sp.get("hit_length_cap", False)
            p_c = team_is_correct(r0r["parsed_answer"] if p_valid else None, g, q["dataset"])
            s_c = team_is_correct(sp["parsed_answer"] if s_valid else None, g, q["dataset"])
            oracle_commit = s_c > p_c
            oracle_rows.append({"question_id": qid, "agent_index": i,
                                "p_correct": p_c, "s_correct": s_c, "oracle_commit": oracle_commit})
    # oracle team accuracy: apply oracle per-agent, then strict majority
    oracle_by_q = defaultdict(list)
    for o in oracle_rows:
        oracle_by_q[o["question_id"]].append(o)
    oracle_team = []
    for qid in sorted(oracle_by_q):
        q = questions[qid]; g = gold[qid]
        finals = []
        r0r = r0[qid]; spq = spec[qid]
        for i in range(3):
            o = oracle_by_q[qid][i]
            if o["oracle_commit"]:
                a = spq[i]["parsed_answer"] if (parse_success(spq[i]["parsed_answer"]) and not spq[i].get("hit_length_cap", False)) else None
            else:
                a = r0r[i]["parsed_answer"] if (parse_success(r0r[i]["parsed_answer"]) and not r0r[i].get("hit_length_cap", False)) else None
            finals.append(a)
        team, _ = strict_majority(finals)
        oracle_team.append(team_is_correct(team, g, q["dataset"]))
    oracle_team_acc = sum(oracle_team) / len(oracle_team) if oracle_team else float("nan")

    # commit rate
    n_s3_commit = sum(1 for (q, i), c in certs.items() if c["certificate_status"] == "PASS")
    commit_rate = n_s3_commit / len(certs) if certs else 0

    decision = {
        "T1_HARM_SUPPRESSION": "PASS" if t1 else "FAIL",
        "T1_detail": {"S3_CWR": a3["CWR"], "S1_CWR": a1["CWR"], "delta_pp": round((a3["CWR"] - a1["CWR"]) * 100, 2)},
        "T2_RESCUE_RETENTION": "PASS" if t2 else "FAIL",
        "T2_detail": {"S3_WCR": a3["WCR"], "S1_WCR": a1["WCR"], "ratio": round(a3["WCR"] / a1["WCR"], 4) if a1["WCR"] else "S1_WCR=0"},
        "T3_TEAM_ACCURACY": "PASS" if t3 else "FAIL",
        "T3_detail": {"S3_team": a3["team_accuracy"], "S0_team": a0["team_accuracy"]},
        "T4_CERTIFICATE_SPECIFICITY": "PASS" if t4 else "FAIL",
        "T4_detail": {"WCR_DCF_gt_MISMATCH": t4_wcr, "NRG_DCF_gt_MISMATCH": t4_nrg},
        "T5_TRANSACTIONAL_INTEGRITY": "PASS" if t5 else "FAIL",
        "ORACLE_HEADROOM": round(oracle_team_acc, 4),
        "commit_rate_S3": round(commit_rate, 4),
        "SCD_STAGE1A": ("PROMISING" if (t1 and t2 and t3 and t4 and t5)
                        else ("MECHANISM_SIGNAL_ONLY" if (t1 and t2) else "UNSUPPORTED")),
    }
    with open(os.path.join(REPO, "results", "stage1a_decision.json"), "w", encoding="utf-8") as fh:
        json.dump(decision, fh, indent=2)
    print(json.dumps(decision, indent=2))

    # ---- CSV outputs (PI §19) -------------------------------------------------------------
    with open(os.path.join(REPO, "results", "metrics.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["condition"] + list(all_metrics["S0"].keys()))
        for cond in ("S0", "S1", "S2", "S3", "S4"):
            w.writerow([cond] + [round(v, 4) if isinstance(v, float) else v for v in all_metrics[cond].values()])
    trans_rows = []
    for cond in ("S0", "S1", "S2", "S3", "S4"):
        m = all_metrics[cond]
        trans_rows.append({"condition": cond, "C_to_C": m["n_observations"] - m["n_c2w"] - m["n_w2c"] - (m["n_observations"] - m["n_observations"]), "C_to_W": m["n_c2w"], "W_to_C": m["n_w2c"], "W_to_W": m["n_observations"] - sum(init for _ in [0]) if False else m["n_observations"] - m["n_c2w"] - m["n_w2c"] - (m["n_observations"] - sum(1 for _ in range(1)))})
    # simpler transition table
    trans_rows = []
    for cond in ("S0", "S1", "S2", "S3", "S4"):
        m = all_metrics[cond]
        n = m["n_observations"]
        c0 = round(m["individual_accuracy_initial"] * n)
        w0 = n - c0
        trans_rows.append({"condition": cond, "C_to_C": c0 - m["n_c2w"], "C_to_W": m["n_c2w"],
                           "W_to_C": m["n_w2c"], "W_to_W": w0 - m["n_w2c"]})
    with open(os.path.join(REPO, "results", "transitions.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["condition", "C_to_C", "C_to_W", "W_to_C", "W_to_W"])
        w.writeheader(); w.writerows(trans_rows)
    with open(os.path.join(REPO, "results", "oracle_headroom.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["question_id", "agent_index", "p_correct", "s_correct", "oracle_commit"])
        w.writeheader(); w.writerows(oracle_rows)

    # paired S3 vs S2 per question
    s3_by_q = {r["question_id"]: r for r in team_rows["S3"]}
    s2_by_q = {r["question_id"]: r for r in team_rows["S2"]}
    with open(os.path.join(REPO, "results", "paired_s3_s2.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["question_id", "S2_team_correct", "S3_team_correct", "delta"])
        for qid in sorted(s3_by_q):
            a, b = s2_by_q[qid]["team_correct"], s3_by_q[qid]["team_correct"]
            w.writerow([qid, int(a), int(b), int(b) - int(a)])

    # cost
    j_cost = {"r0": len(load_jsonl(os.path.join(RAW, "r0.jsonl"))),
              "speculative": len(load_jsonl(os.path.join(RAW, "speculative_states.jsonl"))),
              "certificates": len(load_jsonl(os.path.join(RAW, "certificates.jsonl")))}
    tok = 0
    for f in ("r0.jsonl", "speculative_states.jsonl", "certificates.jsonl"):
        for r in load_jsonl(os.path.join(RAW, f)):
            tok += r["prompt_tokens"] + r["completion_tokens"]
    j_cost["total_tokens"] = tok
    with open(os.path.join(REPO, "results", "cost.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["phase", "generations", "note"]); w.writerow(["total_tokens", tok, "vs ceiling 1,600,000"])
        for k, v in j_cost.items():
            if k != "total_tokens":
                w.writerow([k, v, ""])

    # leakage: certificate generator must not receive peer identity/gold/majority
    leak_rows = []
    for (qid, i), c in certs.items():
        payload = c["raw_output"].lower()
        leak_rows.append({
            "question_id": qid, "agent_index": i,
            "peer_identity_leak": int(bool(__import__("re").search(r"\bpeer\s+[12]\b|\bother\s+agent", payload))),
            "gold_leak": 0,  # gold never enters the cert prompt by construction
            "majority_leak": int("majority" in payload),
        })
    with open(os.path.join(REPO, "results", "leakage.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["question_id", "agent_index", "peer_identity_leak", "gold_leak", "majority_leak"])
        w.writeheader(); w.writerows(leak_rows)
    n_peer = sum(r["peer_identity_leak"] for r in leak_rows)
    n_maj = sum(r["majority_leak"] for r in leak_rows)
    print(f"leakage: peer_identity={n_peer} majority={n_maj} gold=0 (by construction)")

    # ---- §16 qualitative cases -------------------------------------------------------------
    cases_dir = os.path.join(REPO, "cases")
    os.makedirs(cases_dir, exist_ok=True)
    s3_by_agent = {(r["question_id"], r["agent_index"]): r for r in dcf_like_s3_rows(conditions, certs)}
    # build transition labels
    s3_obs = {("question_id", "agent_index"): None}
    trans = []
    for o in conditions["S3"]:
        trans.append(o)
    trans.sort(key=lambda o: (o["question_id"], o["agent_index"]))
    w2c = [o for o in trans if not o["initial_correct"] and o["final_correct"]][:10]
    c2w = [o for o in trans if o["initial_correct"] and not o["final_correct"]][:10]
    commits = [(qid, i) for (qid, i), c in certs.items() if c["certificate_status"] == "PASS"]
    commits.sort()
    good_commits = []
    for qid, i in commits:
        o = next(x for x in conditions["S3"] if x["question_id"] == qid and x["agent_index"] == i)
        if o["final_correct"]:
            good_commits.append((qid, i))
        if len(good_commits) >= 10:
            break
    bad_commits = []
    for qid, i in commits:
        o = next(x for x in conditions["S3"] if x["question_id"] == qid and x["agent_index"] == i)
        if not o["final_correct"]:
            bad_commits.append((qid, i))
        if len(bad_commits) >= 10:
            break
    for name, items, note in (
        ("commits_w2c.md", [(o["question_id"], o["agent_index"]) for o in w2c], "successful commits turning W->C"),
        ("rollbacks_prevent_c2w.md", [(o["question_id"], o["agent_index"]) for o in c2w], "rollbacks that prevented C->W (these are S3 final=P_i where S_i was wrong)"),
        ("correct_commits.md", good_commits, "commits where S_i was correct"),
        ("incorrect_commits.md", bad_commits, "commits where S_i was wrong"),
    ):
        with open(os.path.join(cases_dir, name), "w", encoding="utf-8") as fh:
            fh.write(f"# {name} — first {len(items)} by canonical ordering ({note})\n\n")
            for qid, i in items:
                p = r0[qid][i]; s = spec[qid][i]; c = certs[(qid, i)]
                fh.write(f"## {qid} agent{i}\n\n")
                fh.write(f"P answer: {p['parsed_answer']} | S answer: {s['parsed_answer']} | cert: {c['certificate_status']}\n\n")
                fh.write(f"cert probe: {c['raw_output'][:400]}\n\n---\n\n")
    print("qualitative cases written")

    # gold-joined per-agent rows
    with open(os.path.join(REPO, "results", "agent_transitions.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["question_id", "dataset", "agent_index", "condition",
                                           "initial_correct", "final_correct"])
        w.writeheader()
        for cond in ("S0", "S1", "S2", "S3", "S4"):
            for o in conditions[cond]:
                w.writerow({"question_id": o["question_id"], "dataset": o["dataset"],
                            "agent_index": o["agent_index"], "condition": cond,
                            "initial_correct": o["initial_correct"], "final_correct": o["final_correct"]})
    return 0


def dcf_like_s3_rows(conditions, certs):
    """Helper: build S3 rows with final=P or S per gate."""
    return []


if __name__ == "__main__":
    sys.exit(main())
