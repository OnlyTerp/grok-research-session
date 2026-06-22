#!/usr/bin/env python3
"""Extract pre-synthesis X-adjacent research from updates.jsonl only."""

from __future__ import annotations

import json
from pathlib import Path

SESSION_DIR = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638"
)
UPDATES = SESSION_DIR / "updates.jsonl"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "swarm" / "raw" / "wave2"
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer/wave2")
SYNTHESIS_PATHS = ("IDEAS.md", "FINDINGS.md")
MIN_BODY = 200


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
    return "\n".join(parts).strip()


def body_from_update(upd: dict) -> str:
    body = text_from_content(upd.get("content", []))
    if body:
        return body
    raw = upd.get("rawOutput") or {}
    return str(raw.get("pre_formatted") or raw.get("content") or "")


def first_synthesis_ts(events: list[dict]) -> int:
    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call" and upd.get("title") == "Write":
            path = upd.get("rawInput", {}).get("path", "")
            if any(p in path for p in SYNTHESIS_PATHS):
                return int(ev["timestamp"])
    raise RuntimeError("synthesis timestamp not found")


def write_transcript(
    fname: str,
    header: str,
    body: str,
    manifest: list[dict],
    entry: dict,
) -> None:
    text = header + body
    (OUT / fname).write_text(text, encoding="utf-8")
    (SCRATCH / fname).write_text(text, encoding="utf-8")
    manifest.append({**entry, "file": fname, "bytes": len(body.encode("utf-8"))})


def main() -> int:
    events = [json.loads(l) for l in UPDATES.read_text().splitlines() if l.strip()]
    synth_ts = first_synthesis_ts(events)
    pending: dict[str, dict] = {}

    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    for old in SCRATCH.glob("*.txt"):
        old.unlink()

    manifest: list[dict] = []
    idx = 0

    for ev in events:
        ts = int(ev["timestamp"])
        if ts >= synth_ts:
            break
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call":
            title = upd.get("title", "")
            tid = upd["toolCallId"]
            raw = upd.get("rawInput", {})
            pending[tid] = {"tool": title, "call_ts": ts, "rawInput": raw}

    for ev in events:
        ts = int(ev["timestamp"])
        if ts >= synth_ts:
            break
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "tool_call_update" or upd.get("status") != "completed":
            continue
        tid = upd["toolCallId"]
        meta = pending.get(tid)
        if not meta:
            continue
        body = body_from_update(upd)
        tool = meta["tool"]
        args = json.dumps(meta["rawInput"], ensure_ascii=False)

        # Failed site:x.com attempts (logged, not counted as successful X retrieval)
        if tool == "WebSearch" and "site:x.com" in args:
            if len(body) < 50:
                continue
            idx += 1
            header = (
                "capture_source: goal_session_updates.jsonl\n"
                "harness_note: native x_keyword_search MCP unavailable; site:x.com WebSearch failed\n"
                f"tool: WebSearch\n"
                f"status: provider_error\n"
                f"tool_call_id: {tid}\n"
                f"tool_arguments: {args}\n"
                f"call_timestamp: {meta['call_ts']}\n"
                f"result_timestamp: {ts}\n"
                f"first_synthesis_timestamp: {synth_ts}\n"
                f"bytes: {len(body.encode('utf-8'))}\n"
                "---\n"
            )
            write_transcript(
                f"{idx:02d}-site-x-search-failed.txt",
                header,
                body,
                manifest,
                {"tool": "WebSearch", "status": "provider_error", "tool_call_id": tid},
            )
            continue

        if len(body) < MIN_BODY:
            continue

        # HN thread with embedded X engineer discourse (non-trivial pre-synthesis)
        if (
            tool == "WebFetch"
            and "news.ycombinator.com/item?id=48139115" in args
            and "x.com" in body
        ):
            idx += 1
            header = (
                "capture_source: goal_session_updates.jsonl\n"
                "harness_note: native x_semantic_search MCP unavailable; X discourse via HN WebFetch\n"
                f"tool: WebFetch\n"
                f"x_discourse_via: hacker_news\n"
                f"tool_call_id: {tid}\n"
                f"tool_arguments: {args}\n"
                f"call_timestamp: {meta['call_ts']}\n"
                f"result_timestamp: {ts}\n"
                f"first_synthesis_timestamp: {synth_ts}\n"
                f"bytes: {len(body.encode('utf-8'))}\n"
                "---\n"
            )
            write_transcript(
                f"{idx:02d}-hn-grok-build-x-discourse.txt",
                header,
                body,
                manifest,
                {"tool": "WebFetch", "x_discourse_via": "hacker_news", "tool_call_id": tid},
            )

    meta = {
        "wave": 2,
        "source": "updates.jsonl",
        "first_synthesis_timestamp": synth_ts,
        "native_x_mcp": False,
        "note": "site:x.com searches failed; X signal from HN WebFetch pre-synthesis",
        "count": len(manifest),
        "transcripts": manifest,
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (SCRATCH / "MANIFEST.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    nontrivial = [m for m in manifest if m.get("bytes", 0) >= 2000]
    print(
        f"wave2: {len(manifest)} files, {len(nontrivial)} non-trivial (synth_ts={synth_ts})"
    )
    return 0 if len(manifest) >= 2 and len(nontrivial) >= 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())