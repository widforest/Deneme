#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("$", " ".join(cmd))
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main():
    ap = argparse.ArgumentParser(description="One-command WhatsApp -> Qwen dataset pipeline")
    ap.add_argument("--input", required=True, help="WhatsApp txt export path")
    ap.add_argument("--assistant-speaker", required=True, help="Name mapped to assistant role")
    ap.add_argument("--out-dir", default="outputs", help="Output directory")
    ap.add_argument("--dataset-version", default="v0.1.0")
    ap.add_argument("--session-gap-min", type=int, default=60)
    ap.add_argument("--max-turns", type=int, default=8)
    ap.add_argument("--system-prompt", default="Sen yardımsever bir asistansın.")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    training = out_dir / "training.jsonl"
    report_json = out_dir / "report.json"
    report_csv = out_dir / "report.csv"

    py = sys.executable

    run([
        py,
        "prepare_dataset.py",
        "--input",
        args.input,
        "--output",
        str(training),
        "--assistant-speaker",
        args.assistant_speaker,
        "--session-gap-min",
        str(args.session_gap_min),
        "--max-turns",
        str(args.max_turns),
        "--system-prompt",
        args.system_prompt,
    ])

    run([
        py,
        "score_dataset.py",
        "--input",
        str(training),
        "--report-json",
        str(report_json),
        "--report-csv",
        str(report_csv),
        "--dataset-version",
        args.dataset_version,
    ])

    print("\nBitti ✅")
    print(f"- Training: {training}")
    print(f"- Report JSON: {report_json}")
    print(f"- Report CSV: {report_csv}")


if __name__ == "__main__":
    main()
