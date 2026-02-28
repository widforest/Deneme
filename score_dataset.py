#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")


WS_RE = re.compile(r"\s+")

def normalize_messages(messages):
    rows = []
    for m in messages:
        content = WS_RE.sub(' ', m.get('content', '')).strip().lower()
        rows.append(f"{m.get('role','')}::{content}")
    return "\n".join(rows)


def has_pii(text: str) -> bool:
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text))


def main():
    ap = argparse.ArgumentParser(description="Score prepared JSONL dataset")
    ap.add_argument("--input", required=True, help="Prepared JSONL path")
    ap.add_argument("--report-json", required=True)
    ap.add_argument("--report-csv", required=True)
    ap.add_argument("--dataset-version", default="v0.1.0")
    args = ap.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    total_records = len(rows)
    total_messages = sum(len(r.get("messages", [])) for r in rows)

    keys = [normalize_messages(r.get("messages", [])) for r in rows]
    counts = Counter(keys)
    duplicate_records = sum(c - 1 for c in counts.values() if c > 1)

    short_or_empty_messages = 0
    for r in rows:
        for m in r.get("messages", []):
            if m.get("role") == "system":
                continue
            if len(m.get("content", "").strip()) < 2:
                short_or_empty_messages += 1

    single_turn_samples = 0
    pii_leak_samples = 0
    for r in rows:
        non_system = [m for m in r.get("messages", []) if m.get("role") != "system"]
        if len(non_system) < 2:
            single_turn_samples += 1
        if any(has_pii(m.get("content", "")) for m in non_system):
            pii_leak_samples += 1

    def pct(n, d):
        return (n / d * 100.0) if d else 0.0

    duplicate_rate = pct(duplicate_records, total_records)
    short_or_empty_rate = pct(short_or_empty_messages, total_messages)
    single_turn_rate = pct(single_turn_samples, total_records)
    pii_leak_rate = pct(pii_leak_samples, total_records)

    threshold_duplicate_rate = 5.0
    threshold_short_or_empty_rate = 2.0
    threshold_single_turn_rate = 15.0
    threshold_pii_leak_rate = 0.1

    passes_duplicate_threshold = duplicate_rate < threshold_duplicate_rate
    passes_short_or_empty_threshold = short_or_empty_rate < threshold_short_or_empty_rate
    passes_single_turn_threshold = single_turn_rate < threshold_single_turn_rate
    passes_pii_threshold = pii_leak_rate < threshold_pii_leak_rate

    release_gate_status = (
        "ready_for_sft"
        if all([
            passes_duplicate_threshold,
            passes_short_or_empty_threshold,
            passes_single_turn_threshold,
            passes_pii_threshold,
        ])
        else "needs_rework"
    )

    report = {
        "dataset_version": args.dataset_version,
        "run_id": f"qa_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": total_records,
        "total_messages": total_messages,
        "duplicate_records": duplicate_records,
        "duplicate_rate": round(duplicate_rate, 4),
        "short_or_empty_messages": short_or_empty_messages,
        "short_or_empty_rate": round(short_or_empty_rate, 4),
        "single_turn_samples": single_turn_samples,
        "single_turn_rate": round(single_turn_rate, 4),
        "pii_leak_samples": pii_leak_samples,
        "pii_leak_rate": round(pii_leak_rate, 4),
        "threshold_duplicate_rate": threshold_duplicate_rate,
        "threshold_short_or_empty_rate": threshold_short_or_empty_rate,
        "threshold_single_turn_rate": threshold_single_turn_rate,
        "threshold_pii_leak_rate": threshold_pii_leak_rate,
        "passes_duplicate_threshold": passes_duplicate_threshold,
        "passes_short_or_empty_threshold": passes_short_or_empty_threshold,
        "passes_single_turn_threshold": passes_single_turn_threshold,
        "passes_pii_threshold": passes_pii_threshold,
        "release_gate_status": release_gate_status,
    }

    with open(args.report_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(args.report_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(report.keys()))
        writer.writeheader()
        writer.writerow(report)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
