#!/usr/bin/env python3
"""Union parent + child session updates.jsonl into wave1/wave2 transcripts."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

PARENT_SESSION = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638"
)
PARENT_UPDATES = PARENT_SESSION / "updates.jsonl"
CHILD_BASE = Path("/home/terp/.grok/sessions/%2Fhome%2Fterp")
ROOT = Path(__file__).resolve().parent.parent
WAVE1 = ROOT / "swarm" / "raw" / "wave1"
WAVE2 = ROOT / "swarm" / "raw" / "wave2"
WAVE2_ATTEMPTS = WAVE2 / "attempts"
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer")

RESEARCH_CHILDREN = [
    "019ef0ee-7434-7ff1-b320-d6015306e830",
    "019ef0ee-7434-7ff1-b320-d61838b9aac1",
    "019ef0ee-7434-7ff1-b320-d62a058ded9a",
    "019ef0ee-7434-7ff1-b320-d6307f4beba6",
]
SYNTHESIS_PATHS = ("IDEAS.md", "FINDINGS.md")
PARENT_TOOLS_WAVE1 = {"WebSearch", "WebFetch"}
CHILD_TOOLS_WAVE2 = {"WebSearch", "WebFetch", "Shell"}
MIN_WAVE1_BODY = 500
MIN_WAVE2_BODY = 500
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
    if isinstance(out, list):
        try:
            return bytes(out).decode("utf-8", errors="replace")
        except Exception:
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


def child_spawn_ts(parent_events: list[dict], child_id: str) -> int | None:
    for ev in parent_events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") != "subagent_spawned":
            continue
        if upd.get("child_session_id") == child_id:
            return int(ev["timestamp"])
    return None


def is_provider_error(body: str) -> bool:
    low = body.lower()
    return PROVIDER_ERROR in low and len(body) < 500


def x_discourse_via(tool: str, raw_input: dict, body: str) -> str | None:
    blob = json.dumps(raw_input, ensure_ascii=False) + body
    if re.search(r"site:x\.com|site:twitter\.com", blob, re.I):
        return None
    if tool == "Shell" and "hn.algolia.com" in blob and "tags=comment" in blob:
        return "hn_algolia_comment_api"
    if tool == "WebFetch" and "news.ycombinator.com/item" in blob:
        if re.search(r"@skp1995|@ofek|skcd42|x\.com|twitter\.com", body, re.I):
            return "hn_webfetch_thread"
    return None


def is_site_x_attempt(raw_input: dict) -> bool:
    blob = json.dumps(raw_input, ensure_ascii=False)
    return bool(re.search(r"site:x\.com|site:twitter\.com", blob, re.I))


def write_transcript(
    out_dir: Path,
    fname: str,
    header_lines: list[str],
    body: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    header = "\n".join(header_lines) + "\n---\n"
    path = out_dir / fname
    path.write_text(header + body, encoding="utf-8")
    return path


def extract_session(
    updates_path: Path,
    synth_ts: int,
    *,
    session_id: str,
    capture_source: str,
    allowed_tools: set[str],
    min_body: int,
    parent_spawn_ts: int | None,
    wave2_only_x: bool,
) -> tuple[list[dict], list[dict], list[dict]]:
    events = load_events(updates_path)
    pending: dict[str, dict] = {}
    wave: list[dict] = []
    attempts: list[dict] = []
    seen_hashes: set[str] = set()

    for ev in events:
        upd = ev.get("params", {}).get("update", {})
        if upd.get("sessionUpdate") == "tool_call":
            title = upd.get("title", "")
            if title in allowed_tools:
                pending[upd["toolCallId"]] = {
                    "tool": title,
                    "call_ts": int(ev["timestamp"]),
                    "rawInput": upd.get("rawInput", {}),
                }

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
        if not meta:
            continue
        body = body_from_update(upd)
        if is_provider_error(body):
            if is_site_x_attempt(meta["rawInput"]):
                attempts.append(
                    {
                        "tool": meta["tool"],
                        "tool_call_id": tid,
                        "call_ts": meta["call_ts"],
                        "result_ts": ts,
                        "bytes": len(body.encode()),
                        "reason": "site_x_provider_error",
                    }
                )
            continue
        if len(body) < min_body:
            continue

        h = hashlib.sha256(body.encode()).hexdigest()[:16]
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        x_via = x_discourse_via(meta["tool"], meta["rawInput"], body)
        if wave2_only_x and not x_via:
            continue

        wave.append(
            {
                "tool": meta["tool"],
                "tool_call_id": tid,
                "call_ts": meta["call_ts"],
                "result_ts": ts,
                "bytes": len(body.encode()),
                "session_id": session_id,
                "capture_source": capture_source,
                "parent_spawn_timestamp": parent_spawn_ts,
                "rawInput": meta["rawInput"],
                "body": body,
                "x_discourse_via": x_via,
                "body_hash": h,
            }
        )

    return wave, attempts, events


def main() -> int:
    if not PARENT_UPDATES.is_file():
        print(f"MISSING {PARENT_UPDATES}")
        return 1

    parent_events = load_events(PARENT_UPDATES)
    synth_ts = first_synthesis_ts(parent_events)
    if synth_ts is None:
        print("No synthesis timestamp found")
        return 1

    for d in (WAVE1, WAVE2, WAVE2_ATTEMPTS):
        if d.exists():
            for p in d.glob("*.txt"):
                p.unlink()
    for scratch_sub in ("wave1", "wave2", "wave2/attempts"):
        sd = SCRATCH / scratch_sub
        if sd.exists():
            for p in sd.glob("*.txt"):
                p.unlink()

    parent_wave1, parent_attempts, _ = extract_session(
        PARENT_UPDATES,
        synth_ts,
        session_id="019ef0e7-e353-7822-89e0-412709416638",
        capture_source="parent_session_updates.jsonl",
        allowed_tools=PARENT_TOOLS_WAVE1,
        min_body=MIN_WAVE1_BODY,
        parent_spawn_ts=None,
        wave2_only_x=False,
    )

    wave2_items: list[dict] = []
    all_attempts: list[dict] = list(parent_attempts)

    for child_id in RESEARCH_CHILDREN:
        child_path = CHILD_BASE / child_id / "updates.jsonl"
        if not child_path.is_file():
            print(f"WARN missing child updates: {child_path}")
            continue
        spawn_ts = child_spawn_ts(parent_events, child_id)
        child_wave2, child_attempts, _ = extract_session(
            child_path,
            synth_ts,
            session_id=child_id,
            capture_source="child_session_updates.jsonl",
            allowed_tools=CHILD_TOOLS_WAVE2,
            min_body=MIN_WAVE2_BODY,
            parent_spawn_ts=spawn_ts,
            wave2_only_x=True,
        )
        wave2_items.extend(child_wave2)
        all_attempts.extend(child_attempts)

    # Promote parent HN X-discourse WebFetch if not deduped from child
    for item in parent_wave1:
        x_via = x_discourse_via(item["tool"], item["rawInput"], item["body"])
        if x_via:
            wave2_items.append({**item, "x_discourse_via": x_via})

    parent_wave1 = [i for i in parent_wave1 if not x_discourse_via(i["tool"], i["rawInput"], i["body"])]

    # Dedupe wave2 by body hash, prefer child over parent
    deduped: dict[str, dict] = {}
    for item in sorted(wave2_items, key=lambda x: (x["capture_source"] != "child_session_updates.jsonl", x["result_ts"])):
        deduped[item["body_hash"]] = item
    wave2_items = sorted(deduped.values(), key=lambda x: x["result_ts"])

    def emit(items: list[dict], out_dir: Path, scratch_dir: Path, prefix: str) -> list[dict]:
        manifest: list[dict] = []
        for idx, item in enumerate(items, 1):
            short = re.sub(r"[^a-zA-Z0-9]", "", item["tool_call_id"])[-12:]
            fname = f"{idx:02d}-{item['tool']}-{short}.txt"
            header = [
                f"capture_source: {item['capture_source']}",
                f"session_id: {item['session_id']}",
                f"tool: {item['tool']}",
                f"tool_call_id: {item['tool_call_id']}",
                f"tool_arguments: {json.dumps(item['rawInput'], ensure_ascii=False)}",
                f"call_timestamp: {item['call_ts']}",
                f"result_timestamp: {item['result_ts']}",
                f"first_synthesis_timestamp: {synth_ts}",
                f"bytes: {item['bytes']}",
            ]
            if item.get("parent_spawn_timestamp") is not None:
                header.append(f"parent_spawn_timestamp: {item['parent_spawn_timestamp']}")
            if item.get("x_discourse_via"):
                header.append(f"x_discourse_via: {item['x_discourse_via']}")
            path = write_transcript(out_dir, fname, header, item["body"])
            scratch_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, scratch_dir / fname)
            manifest.append({k: v for k, v in item.items() if k != "body"})
        return manifest

    w1_manifest = emit(parent_wave1, WAVE1, SCRATCH / "wave1", "wave1")
    w2_manifest = emit(wave2_items, WAVE2, SCRATCH / "wave2", "wave2")

    attempt_manifest: list[dict] = []
    for att in all_attempts:
        attempt_manifest.append(
            {
                **att,
                "note": "Provider error body omitted; see parent updates.jsonl tool_call_update.",
            }
        )
    attempts_json = {
        "logged_only": True,
        "not_counted_toward_any_gate": True,
        "first_synthesis_timestamp": synth_ts,
        "native_x_tools_available": False,
        "site_x_websearch_failures": attempt_manifest,
    }
    WAVE2_ATTEMPTS.mkdir(parents=True, exist_ok=True)
    attempts_path = WAVE2_ATTEMPTS / "site-x-failures.json"
    attempts_path.write_text(json.dumps(attempts_json, indent=2), encoding="utf-8")
    scratch_attempts = SCRATCH / "wave2" / "attempts"
    scratch_attempts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(attempts_path, scratch_attempts / "site-x-failures.json")

    (WAVE1 / "MANIFEST.json").write_text(
        json.dumps(
            {
                "wave": 1,
                "first_synthesis_timestamp": synth_ts,
                "count": len(w1_manifest),
                "transcripts": w1_manifest,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (WAVE2 / "MANIFEST.json").write_text(
        json.dumps(
            {
                "wave": 2,
                "first_synthesis_timestamp": synth_ts,
                "count": len(w2_manifest),
                "x_discourse_count": sum(1 for m in w2_manifest if m.get("x_discourse_via")),
                "attempts_logged": len(attempt_manifest),
                "transcripts": w2_manifest,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (ROOT / "swarm" / "raw" / "MANIFEST.json").write_text(
        json.dumps(
            {
                "first_synthesis_timestamp": synth_ts,
                "wave1": len(w1_manifest),
                "wave2": len(w2_manifest),
                "wave2_attempts": len(attempt_manifest),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Union extract: wave1={len(w1_manifest)} wave2={len(w2_manifest)} "
        f"attempts={len(attempt_manifest)} synth_ts={synth_ts}"
    )
    return 0 if len(w1_manifest) >= 12 and len(w2_manifest) >= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())