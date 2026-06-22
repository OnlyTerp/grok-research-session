#!/usr/bin/env python3
"""Verify grok-research-session deliverables with swarm-union provenance checks."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer")
UPDATES = Path(
    "/home/terp/.grok/sessions/%2Fhome%2Fterp/019ef0e7-e353-7822-89e0-412709416638/updates.jsonl"
)
MIN_IDEAS = 40
MIN_CITATIONS = 40
MIN_WAVE1 = 12
MIN_WAVE2 = 2
MIN_X_GATE = 2
REQUIRED_FILES = [
    "README.md",
    "IDEAS.md",
    "FINDINGS.md",
    "RESEARCH_LOG.md",
    "SCOPE.md",
    "swarm/raw/MANIFEST.json",
    "swarm/raw/wave1/MANIFEST.json",
    "swarm/raw/wave2/MANIFEST.json",
    "scripts/scope_guard.py",
    "scripts/extract_swarm_union.py",
    "scripts/validate_swarm_provenance.py",
    "swarm/runs/2026-06-22-mega-swarm/track-grok-feedback.md",
    "swarm/runs/2026-06-22-mega-swarm/track-competitive.md",
    "swarm/runs/2026-06-22-mega-swarm/track-mcp-swarm.md",
    "swarm/runs/2026-06-22-mega-swarm/track-tui-onboarding.md",
]
HARNESS_REFS = [
    "docs/10-skills-agents-subagents.md",
    "docs/22-interactive-tui.md",
    "docs/21-mission-mode-local.md",
    "docs/07-acp-protocol.md",
    "docs/23-headless-mode.md",
]
FORBIDDEN = [
    "=== TOOL: web_fetch ===",
    "x_search_skill",
    "x_keyword_search_equivalent",
    "x_semantic_search_equivalent",
    "live_research_continuation",
    "capture_research_transcripts",
    "capture_live_transcript",
    "capture_wave2_x_search",
    "x_search.py",
    ".hermes/auth.json",
]


def x_gate_count() -> int:
    count = 0
    for path in (ROOT / "swarm" / "raw" / "wave2").glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        if "logged_only: true" in text:
            continue
        header, _, body = text.partition("---\n")
        if len(body.encode()) < 2000:
            continue
        if re.search(r"https?://[^\"]*(?:x\.com|twitter\.com)", header, re.I):
            count += 1
            continue
        if "x_discourse_via:" in header:
            count += 1
    return count


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")

    if not UPDATES.is_file():
        errors.append(f"missing updates.jsonl: {UPDATES}")

    ideas = (ROOT / "IDEAS.md").read_text(encoding="utf-8") if (ROOT / "IDEAS.md").exists() else ""
    findings = (ROOT / "FINDINGS.md").read_text(encoding="utf-8") if (ROOT / "FINDINGS.md").exists() else ""
    idea_count = len(re.findall(r"^### \d+\.", ideas, re.MULTILINE))
    if idea_count < MIN_IDEAS:
        errors.append(f"IDEAS.md has {idea_count} ideas, need >= {MIN_IDEAS}")

    urls = set(re.findall(r"https?://[^\s\)>\]]+", ideas + findings))
    if len(urls) < MIN_CITATIONS:
        errors.append(f"found {len(urls)} unique URLs, need >= {MIN_CITATIONS}")

    for ref in HARNESS_REFS:
        if ref not in ideas:
            errors.append(f"IDEAS.md missing harness ref: {ref}")

    scan_roots = [ROOT / "swarm" / "raw", ROOT / "scripts"]
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.name.startswith("validate_swarm"):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for marker in FORBIDDEN:
                if marker in text:
                    errors.append(f"forbidden marker '{marker}' in {path.relative_to(ROOT)}")

    w1 = list((ROOT / "swarm" / "raw" / "wave1").glob("*.txt"))
    w2 = [p for p in (ROOT / "swarm" / "raw" / "wave2").glob("*.txt") if p.parent.name == "wave2"]
    if len(w1) < MIN_WAVE1:
        errors.append(f"wave1: {len(w1)} < {MIN_WAVE1}")
    if len(w2) < MIN_WAVE2:
        errors.append(f"wave2: {len(w2)} < {MIN_WAVE2}")

    x_gate = x_gate_count()
    if x_gate < MIN_X_GATE:
        errors.append(f"wave2 X gate: {x_gate} < {MIN_X_GATE}")

    attempts = list((ROOT / "swarm" / "raw" / "wave2" / "attempts").glob("**/*.txt"))
    if len(attempts) < 2:
        errors.append("wave2/attempts missing logged site:x failures")

    rc = subprocess.call(
        ["python3", str(ROOT / "scripts" / "validate_swarm_provenance.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        errors.append("validate_swarm_provenance.py failed")

    if not (SCRATCH / "wave1").is_dir() or len(list((SCRATCH / "wave1").glob("*.txt"))) < MIN_WAVE1:
        errors.append("scratch wave1 mirror incomplete")
    if not (SCRATCH / "wave2").is_dir() or len(list((SCRATCH / "wave2").glob("*.txt"))) < MIN_WAVE2:
        errors.append("scratch wave2 mirror incomplete")

    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"PASS: {idea_count} ideas, {len(urls)} citations, "
        f"wave1={len(w1)} wave2={len(w2)} x_gate={x_gate}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())