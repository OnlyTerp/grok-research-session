#!/usr/bin/env python3
"""Validate mega-swarm provenance from parent + child session updates.jsonl."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARENT_UPDATES = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638/updates.jsonl"
)
CHILD_BASE = Path("/home/terp/.grok/sessions/%2Fhome%2Fterp")
CHILDREN = [
    "019ef0ee-7434-7ff1-b320-d6015306e830",
    "019ef0ee-7434-7ff1-b320-d61838b9aac1",
    "019ef0ee-7434-7ff1-b320-d62a058ded9a",
    "019ef0ee-7434-7ff1-b320-d6307f4beba6",
]
WAVE1 = ROOT / "swarm" / "raw" / "wave1"
WAVE2 = ROOT / "swarm" / "raw" / "wave2"
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer")

MIN_RESEARCH = 12
MIN_BODY = 500
MIN_X_BODY = 2000
MIN_X_FILES = 2
SYNTHESIS_PATHS = ("IDEAS.md", "FINDINGS.md")
FORBIDDEN_MARKERS = (
    "captured_at:",
    "x_keyword_search_equivalent",
    "x_semantic_search_equivalent",
    "live_research_continuation",
)
PROVIDER_ERROR = "provider returned an error"


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
    out = raw.get("pre_formatted") or raw.get("content") or raw.get("output_for_prompt") or ""
    if isinstance(out, dict):
        return json.dumps(out, ensure_ascii=False)
    return str(out)


def load_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def first_synthesis_ts(events: list[dict]) -> int | None:
    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "tool_call" or upd.get("title") != "Write":
            continue
        path = upd.get("rawInput", {}).get("path", "")
        if any(p in path for p in SYNTHESIS_PATHS):
            return int(ev["timestamp"])
    return None


def union_pre_synth(events_list: list[tuple[str, list[dict]]], synth_ts: int) -> dict:
    pending: dict[str, dict] = {}
    completed: list[dict] = []
    batches: dict[int, int] = {}

    for label, events in events_list:
        for ev in events:
            upd = ev.get("params", {}).get("update", {})
            if upd.get("sessionUpdate") == "tool_call":
                title = upd.get("title", "")
                if title in {"WebSearch", "WebFetch", "Shell"}:
                    tid = upd["toolCallId"]
                    ts = int(ev["timestamp"])
                    pending[f"{label}:{tid}"] = {
                        "tool": title,
                        "call_ts": ts,
                        "rawInput": upd.get("rawInput", {}),
                        "label": label,
                    }
                    if ts < synth_ts:
                        batches[ts] = batches.get(ts, 0) + 1

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
            meta = pending.get(f"{label}:{tid}")
            if not meta:
                continue
            body = body_from_update(upd)
            if PROVIDER_ERROR in body.lower() and len(body) < MIN_BODY:
                continue
            if len(body) < MIN_BODY:
                continue
            completed.append(
                {
                    "tool": meta["tool"],
                    "tool_call_id": tid,
                    "label": label,
                    "call_ts": meta["call_ts"],
                    "result_ts": ts,
                    "bytes": len(body.encode()),
                    "rawInput": meta["rawInput"],
                }
            )

    return {
        "completed": completed,
        "parallel_max": max(batches.values()) if batches else 0,
    }


def parse_wave_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    header, _, body = text.partition("---\n")
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return {"path": path, "header": header, "body": body, "fields": fields, "bytes": len(body.encode())}


def is_x_wave_file(parsed: dict) -> bool:
    if parsed["fields"].get("logged_only") == "true":
        return False
    if parsed["bytes"] < MIN_X_BODY:
        return False
    args = parsed["fields"].get("tool_arguments", "")
    if re.search(r"https?://[^\"]*(?:x\.com|twitter\.com)", args, re.I):
        return True
    if parsed["fields"].get("x_discourse_via"):
        return True
    return False


def main() -> int:
    errors: list[str] = []

    rc = subprocess.call(["python3", str(ROOT / "scripts" / "scope_guard.py")], cwd=str(ROOT))
    if rc != 0:
        return 1

    if not PARENT_UPDATES.is_file():
        errors.append(f"missing parent updates: {PARENT_UPDATES}")
        synth_ts = 10**15
        parent_events: list[dict] = []
    else:
        parent_events = load_events(PARENT_UPDATES)
        synth_ts = first_synthesis_ts(parent_events)
        if synth_ts is None:
            errors.append("no IDEAS/FINDINGS Write in parent updates.jsonl")
            synth_ts = 10**15

    union_inputs: list[tuple[str, list[dict]]] = [("parent", parent_events)]
    for cid in CHILDREN:
        p = CHILD_BASE / cid / "updates.jsonl"
        if p.is_file():
            union_inputs.append((cid[-8:], load_events(p)))
        else:
            errors.append(f"missing child updates: {cid}")

    stats = union_pre_synth(union_inputs, synth_ts)
    n = len(stats["completed"])
    if n < MIN_RESEARCH:
        errors.append(f"union pre-synthesis bodies >=500B: {n} < {MIN_RESEARCH}")
    if stats["parallel_max"] < 3:
        errors.append(f"parallel fan-out: {stats['parallel_max']} < 3")

    for ev in parent_events:
        if int(ev["timestamp"]) >= synth_ts:
            break
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call" and upd.get("title") in {
            "x_keyword_search",
            "x_semantic_search",
        }:
            errors.append(f"unexpected native X tool in parent: {upd.get('title')}")

    w1_files = sorted(WAVE1.glob("*.txt"))
    w2_files = sorted(p for p in WAVE2.glob("*.txt") if p.parent == WAVE2)
    if len(w1_files) < MIN_RESEARCH:
        errors.append(f"wave1 files: {len(w1_files)} < {MIN_RESEARCH}")

    union_ids = {c["tool_call_id"] for c in stats["completed"]}
    x_count = 0
    for path in w1_files + w2_files:
        parsed = parse_wave_file(path)
        for bad in FORBIDDEN_MARKERS:
            if bad in parsed["header"]:
                errors.append(f"{path.name}: forbidden marker {bad!r}")

        src = parsed["fields"].get("capture_source", "")
        if src not in {"parent_session_updates.jsonl", "child_session_updates.jsonl"}:
            errors.append(f"{path.name}: bad capture_source {src!r}")

        rts = parsed["fields"].get("result_timestamp")
        fst = parsed["fields"].get("first_synthesis_timestamp")
        if rts and fst and int(rts) >= int(fst):
            errors.append(f"{path.name}: result_timestamp >= synthesis")

        tid = parsed["fields"].get("tool_call_id")
        if tid and tid not in union_ids:
            errors.append(f"{path.name}: tool_call_id not in union pre-synth log")

        if parsed["bytes"] < MIN_BODY and path.parent == WAVE2:
            errors.append(f"{path.name}: wave2 body < {MIN_BODY}B")

        if is_x_wave_file(parsed):
            x_count += 1

    if x_count < MIN_X_FILES:
        errors.append(f"wave2 X gate: {x_count} qualifying files < {MIN_X_FILES}")

    scratch_w1 = SCRATCH / "wave1"
    scratch_w2 = SCRATCH / "wave2"
    if not scratch_w1.is_dir() or len(list(scratch_w1.glob("*.txt"))) < MIN_RESEARCH:
        errors.append("scratch wave1 mirror incomplete")
    if not scratch_w2.is_dir() or len(list(scratch_w2.glob("*.txt"))) < MIN_X_FILES:
        errors.append("scratch wave2 mirror incomplete")

    if errors:
        print("SWARM PROVENANCE FAIL:")
        print(f"  first_synthesis_timestamp={synth_ts}")
        print(f"  union_pre_synth>={MIN_BODY}B={n}, parallel_max={stats['parallel_max']}")
        print(f"  wave1={len(w1_files)} wave2={len(w2_files)} x_gate={x_count}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"SWARM PROVENANCE PASS: synth_ts={synth_ts}, union={n}, "
        f"parallel={stats['parallel_max']}, wave1={len(w1_files)}, "
        f"wave2={len(w2_files)}, x_gate={x_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())