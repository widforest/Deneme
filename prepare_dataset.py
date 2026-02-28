#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# WhatsApp exported line formats (common variants)
LINE_PATTERNS = [
    re.compile(r"^(\d{1,2}[./]\d{1,2}[./]\d{2,4}),\s*(\d{1,2}:\d{2})(?:\s*([APMapm]{2}))?\s*-\s*([^:]+):\s*(.*)$"),
]

DATE_FORMATS = [
    "%d/%m/%y %H:%M",
    "%d/%m/%Y %H:%M",
    "%d.%m.%y %H:%M",
    "%d.%m.%Y %H:%M",
    "%m/%d/%y %H:%M",
    "%m/%d/%Y %H:%M",
    "%d/%m/%y %I:%M %p",
    "%d/%m/%Y %I:%M %p",
    "%d.%m.%y %I:%M %p",
    "%d.%m.%Y %I:%M %p",
    "%m/%d/%y %I:%M %p",
    "%m/%d/%Y %I:%M %p",
]

MEDIA_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^<media omitted>$",
        r"^image omitted$",
        r"^video omitted$",
        r"^audio omitted$",
        r"^document omitted$",
        r"^bu mesaj silindi$",
        r"^this message was deleted$",
    ]
]

SYSTEM_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"joined using this group's invite link",
        r"left",
        r"added",
        r"removed",
        r"changed the subject",
        r"security code changed",
    ]
]


@dataclass
class Message:
    ts: datetime
    speaker: str
    text: str


def parse_datetime(date_str: str, time_str: str, ampm: Optional[str]) -> Optional[datetime]:
    full = f"{date_str} {time_str}" + (f" {ampm.upper()}" if ampm else "")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(full, fmt)
        except ValueError:
            continue
    return None


def parse_whatsapp(path: str) -> List[Message]:
    messages: List[Message] = []
    current = None

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            matched = None
            for pat in LINE_PATTERNS:
                m = pat.match(line)
                if m:
                    matched = m
                    break

            if matched:
                date_s, time_s, ampm, speaker, text = matched.groups()
                ts = parse_datetime(date_s, time_s, ampm)
                if ts is None:
                    continue
                if current is not None:
                    messages.append(current)
                current = Message(ts=ts, speaker=speaker.strip(), text=text.strip())
            elif current is not None:
                # multi-line continuation
                if line.strip():
                    current.text += "\n" + line.strip()

    if current is not None:
        messages.append(current)
    return messages


def is_noise(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    for p in MEDIA_PATTERNS + SYSTEM_PATTERNS:
        if p.search(t):
            return True
    return False


def normalize_text(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"([!?.,])\1{2,}", r"\1\1", t)
    return t


def role_for_speaker(speaker: str, assistant_speaker: str) -> str:
    return "assistant" if speaker == assistant_speaker else "user"


def build_examples(messages: List[Message], assistant_speaker: str, session_gap_min: int, max_turns: int, system_prompt: Optional[str]):
    examples = []
    cleaned = [Message(m.ts, m.speaker, normalize_text(m.text)) for m in messages if not is_noise(m.text)]

    session_id = 0
    session_start = 0
    for i in range(1, len(cleaned) + 1):
        boundary = i == len(cleaned)
        if not boundary:
            gap_min = (cleaned[i].ts - cleaned[i - 1].ts).total_seconds() / 60
            boundary = gap_min > session_gap_min

        if boundary:
            sess = cleaned[session_start:i]
            session_id += 1
            for j, msg in enumerate(sess):
                if role_for_speaker(msg.speaker, assistant_speaker) != "assistant":
                    continue
                start = max(0, j - max_turns)
                window = sess[start : j + 1]
                role_msgs = []
                if system_prompt:
                    role_msgs.append({"role": "system", "content": system_prompt})

                for wm in window:
                    role_msgs.append({
                        "role": role_for_speaker(wm.speaker, assistant_speaker),
                        "content": wm.text,
                        "timestamp": wm.ts.isoformat(),
                        "speaker_id": wm.speaker,
                    })

                non_system = [m for m in role_msgs if m["role"] != "system"]
                if len(non_system) < 2:
                    continue

                examples.append({
                    "id": f"sess{session_id:05d}_msg{j:05d}",
                    "source": "whatsapp_export",
                    "language": "tr",
                    "messages": role_msgs,
                    "meta": {
                        "session_id": f"session_{session_id:05d}",
                        "context_turn_count": len(non_system),
                    },
                })
            session_start = i
    return examples


def main():
    ap = argparse.ArgumentParser(description="Prepare context-aware Qwen JSONL from WhatsApp export")
    ap.add_argument("--input", required=True, help="Path to WhatsApp .txt export")
    ap.add_argument("--output", required=True, help="Output JSONL path")
    ap.add_argument("--assistant-speaker", required=True, help="Speaker name to map as assistant")
    ap.add_argument("--session-gap-min", type=int, default=60)
    ap.add_argument("--max-turns", type=int, default=8)
    ap.add_argument("--system-prompt", default="Sen yardımsever bir asistansın.")
    args = ap.parse_args()

    parsed = parse_whatsapp(args.input)
    examples = build_examples(parsed, args.assistant_speaker, args.session_gap_min, args.max_turns, args.system_prompt)

    with open(args.output, "w", encoding="utf-8") as out:
        for ex in examples:
            out.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"parsed_messages={len(parsed)}")
    print(f"written_examples={len(examples)}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
