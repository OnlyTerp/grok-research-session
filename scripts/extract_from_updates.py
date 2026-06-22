#!/usr/bin/env python3
"""Extract authentic pre-synthesis tool transcripts from goal session updates.jsonl."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SESSION_DIR = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638"
)
UPDATES = SESSION_DIR / "updates.jsonl"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "swarm" / "raw" / "wave1"
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer/wave1")

RESEARCH_TOOLS = {"WebSearch", "WebFetch", "Task"}
SYNTHESIS_PATHS = ("IDEAS.md", "FINDINGS.md")
MIN_BODY = 200


def text_from_content(items: list) -> str:
    parts: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            c = item.get("content")
            if isinstance(c, dict):
                t = c.get("text") or c.get("content") or ""
                if t:
                    parts.append(str(t))
            elif isinstance(c, str) and c:
                parts.append(c)
            elif item.get("type") == "content" and isinstance(item.get("content"), str):
                parts.append(item["content"])
    return "\n".join(parts).strip()


def first_synthesis_ts(events: list[dict]) -> int | None:
    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "tool_call":
            continue
        if upd.get("title") != "Write":
            continue
        path = upd.get("rawInput", {}).get("path", "")
        if any(p in path for p in SYNTHESIS_PATHS):
            return int(ev["timestamp"])
    return None


def load_events() -> list[dict]:
    return [json.loads(line) for line in UPDATES.read_text().splitlines() if line.strip()]


def extract_body(ev: dict) -> tuple[str, str, str, dict]:
    upd = ev["params"]["update"]
    title = upd.get("title", "")
    tid = upd.get("toolCallId", "")
    ts = int(ev["timestamp"])
    body = text_from_content(upd.get("content", []))
    if not body:
        raw = upd.get("rawOutput") or {}
        body = raw.get("pre_formatted") or raw.get("content") or ""
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False)
        body = str(body)
    return title, tid, body, {"timestamp": ts, "rawInput": upd.get("rawInput", {})}


def main() -> int:
    if not UPDATES.is_file():
        print(f"MISSING {UPDATES}")
        return 1

    events = load_events()
    synth_ts = first_synthesis_ts(events)
    if synth_ts is None:
        print("No synthesis Write found in updates.jsonl")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    for old in SCRATCH.glob("*.txt"):
        old.unlink()

    pending: dict[str, dict] = {}
    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call":
            title = upd.get("title", "")
            if title in RESEARCH_TOOLS:
                pending[upd["toolCallId"]] = {
                    "tool": title,
                    "rawInput": upd.get("rawInput", {}),
                    "call_ts": int(ev["timestamp"]),
                }

    seen: set[str] = set()
    manifest: list[dict] = []
    idx = 0
    parallel_batches: dict[int, int] = {}

    for ev in events:
        ts = int(ev["timestamp"])
        if ts >= synth_ts:
            continue
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "tool_call_update":
            continue
        if upd.get("status") != "completed":
            continue
        tid = upd.get("toolCallId", "")
        meta = pending.get(tid)
        if not meta or meta["tool"] not in {"WebSearch", "WebFetch"}:
            continue
        tool = meta["tool"]
        _, _, body, extra = extract_body(ev)
        if len(body) < MIN_BODY:
            continue
        h = hashlib.sha256(body.encode()).hexdigest()[:16]
        if h in seen:
            continue
        seen.add(h)
        idx += 1
        short = re.sub(r"[^a-zA-Z0-9]", "", tid)[-12:]
        fname = f"{idx:02d}-{tool}-{short}.txt"
        call_ts = meta["call_ts"]
        parallel_batches[call_ts] = parallel_batches.get(call_ts, 0) + 1
        header = (
            "capture_source: goal_session_updates.jsonl\n"
            f"session_id: 019ef0e7-e353-7822-89e0-412709416638\n"
            f"tool: {tool}\n"
            f"tool_call_id: {tid}\n"
            f"tool_arguments: {json.dumps(meta['rawInput'], ensure_ascii=False)}\n"
            f"call_timestamp: {call_ts}\n"
            f"result_timestamp: {ts}\n"
            f"first_synthesis_timestamp: {synth_ts}\n"
            f"bytes: {len(body.encode('utf-8'))}\n"
            "---\n"
        )
        out = header + body
        (OUT / fname).write_text(out, encoding="utf-8")
        (SCRATCH / fname).write_text(out, encoding="utf-8")
        manifest.append(
            {
                "file": fname,
                "tool": tool,
                "tool_call_id": tid,
                "call_timestamp": call_ts,
                "result_timestamp": ts,
                "bytes": len(body.encode("utf-8")),
            }
        )

    parallel_max = max(parallel_batches.values()) if parallel_batches else 0
    meta = {
        "wave": 1,
        "source": "updates.jsonl",
        "first_synthesis_timestamp": synth_ts,
        "parallel_batch_max": parallel_max,
        "count": len(manifest),
        "transcripts": manifest,
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (SCRATCH / "MANIFEST.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(
        f"Extracted {len(manifest)} transcripts from updates.jsonl "
        f"(synth_ts={synth_ts}, parallel_max={parallel_max})"
    )
    return 0 if len(manifest) >= 12 else 1


if __name__ == "__main__":
    raise SystemExit(main())