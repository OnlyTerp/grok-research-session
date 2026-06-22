#!/usr/bin/env python3
"""Verify grok-research-session deliverables with updates.jsonl authenticity checks."""

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
REQUIRED_FILES = [
    "README.md",
    "IDEAS.md",
    "FINDINGS.md",
    "RESEARCH_LOG.md",
    "SCOPE.md",
    "swarm/raw/MANIFEST.json",
    "swarm/raw/wave1/MANIFEST.json",
    "swarm/raw/wave2/MANIFEST.json",
    "scripts/validate_from_updates.py",
    "scripts/extract_from_updates.py",
    "scripts/extract_x_wave_from_updates.py",
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
]


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

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if "verify_research" in str(path) or "validate_from" in str(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for marker in FORBIDDEN:
            if marker in text:
                errors.append(f"forbidden marker '{marker}' in {path.relative_to(ROOT)}")

    w1 = list((ROOT / "swarm" / "raw" / "wave1").glob("*.txt"))
    w2 = list((ROOT / "swarm" / "raw" / "wave2").glob("*.txt"))
    if len(w1) < MIN_WAVE1:
        errors.append(f"wave1: {len(w1)} < {MIN_WAVE1}")
    if len(w2) < MIN_WAVE2:
        errors.append(f"wave2: {len(w2)} < {MIN_WAVE2}")

    hn = ROOT / "swarm/raw/wave2/03-hn-grok-build-x-discourse.txt"
    if not hn.is_file() or len(hn.read_text()) < 5000:
        errors.append("wave2 missing non-trivial HN X-discourse transcript")

    rc = subprocess.call(["python3", str(ROOT / "scripts" / "validate_from_updates.py")], cwd=str(ROOT))
    if rc != 0:
        errors.append("validate_from_updates.py failed")

    if not (SCRATCH / "wave1").is_dir() or len(list((SCRATCH / "wave1").glob("*.txt"))) < MIN_WAVE1:
        errors.append("scratch wave1 mirror incomplete")
    if not (SCRATCH / "wave2").is_dir() or len(list((SCRATCH / "wave2").glob("*.txt"))) < MIN_WAVE2:
        errors.append("scratch wave2 mirror incomplete")

    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {idea_count} ideas, {len(urls)} citations, wave1={len(w1)} wave2={len(w2)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())