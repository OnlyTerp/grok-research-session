#!/usr/bin/env python3
"""Validate research predates synthesis using immutable updates.jsonl only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SESSION_DIR = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638"
)
UPDATES = SESSION_DIR / "updates.jsonl"
ROOT = Path(__file__).resolve().parent.parent
WAVE1 = ROOT / "swarm" / "raw" / "wave1"
WAVE2 = ROOT / "swarm" / "raw" / "wave2"
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer")
MIN_RESEARCH = 12
MIN_X_ATTEMPTS = 2
MIN_X_NONTRIVIAL = 1
MIN_X_BODY = 2000
SYNTHESIS_PATHS = ("IDEAS.md", "FINDINGS.md")
FORBIDDEN_WAVE2 = (
    "live_research_continuation",
    "x_keyword_search_equivalent",
    "x_semantic_search_equivalent",
    "captured_at:",
)


def text_from_content(items: list) -> str:
    parts: list[str] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        c = item.get("content")
        if isinstance(c, dict):
            t = c.get("text") or c.get("content") or ""
            if t:
                parts.append(str(t))
        elif isinstance(c, str) and c:
            parts.append(c)
    return "\n".join(parts).strip()


def body_from_update(upd: dict) -> str:
    body = text_from_content(upd.get("content", []))
    if body:
        return body
    raw = upd.get("rawOutput") or {}
    out = raw.get("pre_formatted") or raw.get("content") or ""
    return str(out) if not isinstance(out, str) else out


def load_events() -> list[dict]:
    return [json.loads(line) for line in UPDATES.read_text().splitlines() if line.strip()]


def first_synthesis_ts(events: list[dict]) -> int | None:
    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "tool_call" or upd.get("title") != "Write":
            continue
        path = upd.get("rawInput", {}).get("path", "")
        if any(p in path for p in SYNTHESIS_PATHS):
            return int(ev["timestamp"])
    return None


def research_before_synthesis(events: list[dict], synth_ts: int) -> dict:
    pending: dict[str, dict] = {}
    completed: list[dict] = []
    x_attempts: list[dict] = []
    batches: dict[int, int] = {}

    for ev in events:
        ts = int(ev["timestamp"])
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call":
            title = upd.get("title", "")
            if title in {"WebSearch", "WebFetch"}:
                tid = upd["toolCallId"]
                raw = upd.get("rawInput", {})
                pending[tid] = {"tool": title, "call_ts": ts, "rawInput": raw}
                if ts < synth_ts:
                    batches[ts] = batches.get(ts, 0) + 1
                q = json.dumps(raw)
                if "site:x.com" in q or "site:twitter.com" in q:
                    x_attempts.append({"tool_call_id": tid, "call_ts": ts})

        if upd.get("sessionUpdate") != "tool_call_update":
            continue
        if upd.get("status") != "completed":
            continue
        tid = upd.get("toolCallId", "")
        meta = pending.get(tid)
        if not meta or int(ev["timestamp"]) >= synth_ts:
            continue
        body = body_from_update(upd)
        if len(body) < 200:
            continue
        completed.append(
            {
                "tool": meta["tool"],
                "tool_call_id": tid,
                "call_ts": meta["call_ts"],
                "result_ts": int(ev["timestamp"]),
                "bytes": len(body.encode()),
            }
        )

    return {
        "completed": completed,
        "x_attempts": x_attempts,
        "parallel_max": max(batches.values()) if batches else 0,
    }


def validate_wave_files(synth_ts: int, research_ids: set[str]) -> list[str]:
    errors: list[str] = []
    x_nontrivial = 0

    for d, label in ((WAVE1, "wave1"), (WAVE2, "wave2")):
        if not d.is_dir():
            errors.append(f"missing {label} dir")
            continue
        for p in d.glob("*.txt"):
            text = p.read_text(encoding="utf-8")
            for bad in FORBIDDEN_WAVE2:
                if bad in text:
                    errors.append(f"{p.name}: forbidden marker {bad!r}")

            if "capture_source: goal_session_updates.jsonl" not in text:
                errors.append(f"{p.name}: must cite updates.jsonl")

            fst_m = re.search(r"first_synthesis_timestamp: (\d+)", text)
            rts_m = re.search(r"result_timestamp: (\d+)", text)
            if fst_m and rts_m:
                if int(rts_m.group(1)) >= int(fst_m.group(1)):
                    errors.append(f"{p.name}: result_timestamp >= synthesis")
            elif label == "wave2" and "result_timestamp:" not in text:
                errors.append(f"{p.name}: missing result_timestamp")

            m = re.search(r"tool_call_id: (\S+)", text)
            if m and m.group(1) not in research_ids:
                errors.append(f"{p.name}: tool_call_id not in pre-synthesis research")

            body = text.split("---\n", 1)[-1] if "---\n" in text else ""
            if label == "wave2" and "x_discourse_via:" in text and len(body) >= MIN_X_BODY:
                x_nontrivial += 1

    if x_nontrivial < MIN_X_NONTRIVIAL:
        errors.append(
            f"wave2: {x_nontrivial} non-trivial X-discourse transcripts < {MIN_X_NONTRIVIAL}"
        )
    return errors


def main() -> int:
    errors: list[str] = []
    if not UPDATES.is_file():
        print(f"MISSING {UPDATES}")
        return 1

    events = load_events()
    synth_ts = first_synthesis_ts(events)
    if synth_ts is None:
        errors.append("no IDEAS/FINDINGS Write in updates.jsonl")
        synth_ts = 10**15

    stats = research_before_synthesis(events, synth_ts)
    n = len(stats["completed"])
    if n < MIN_RESEARCH:
        errors.append(f"pre-synthesis research transcripts: {n} < {MIN_RESEARCH}")
    if stats["parallel_max"] < 3:
        errors.append(f"parallel fan-out: {stats['parallel_max']} < 3")

    x_attempts = [q for q in stats["x_attempts"] if q["call_ts"] < synth_ts]
    if len(x_attempts) < MIN_X_ATTEMPTS:
        errors.append(f"site:x.com attempts: {len(x_attempts)} < {MIN_X_ATTEMPTS}")

    # No native x_keyword_search/x_semantic_search in session
    for ev in events:
        if int(ev["timestamp"]) >= synth_ts:
            break
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call":
            title = upd.get("title", "")
            if title in {"x_keyword_search", "x_semantic_search"}:
                errors.append(f"unexpected native X tool call: {title}")

    research_ids = {c["tool_call_id"] for c in stats["completed"]}
    research_ids |= {q["tool_call_id"] for q in x_attempts}
    errors.extend(validate_wave_files(synth_ts, research_ids))

    scratch_w1 = SCRATCH / "wave1"
    scratch_w2 = SCRATCH / "wave2"
    if not scratch_w1.is_dir() or len(list(scratch_w1.glob("*.txt"))) < MIN_RESEARCH:
        errors.append(f"scratch wave1 incomplete at {scratch_w1}")
    if not scratch_w2.is_dir() or len(list(scratch_w2.glob("*.txt"))) < 2:
        errors.append(f"scratch wave2 incomplete at {scratch_w2}")

    if errors:
        print("UPDATES TIMELINE FAIL:")
        print(f"  first_synthesis_timestamp={synth_ts}")
        print(f"  pre_synthesis_research={n}, parallel_max={stats['parallel_max']}")
        print(f"  site_x_attempts={len(x_attempts)}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"UPDATES TIMELINE PASS: synth_ts={synth_ts}, research={n}, "
        f"parallel={stats['parallel_max']}, site_x_attempts={len(x_attempts)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())