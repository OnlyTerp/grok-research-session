#!/usr/bin/env python3
"""Fail if working tree or harness CHANGED_FILES touches out-of-scope paths."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path("/tmp/grok-goal-adddf1ff4ea4/implementer")
ALLOWED_PREFIXES = (
    str(ROOT) + "/",
    str(SCRATCH) + "/",
)
FORBIDDEN_FRAGMENTS = (
    ".hermes",
    "auth.json",
    "discord",
    "grok-cli-harness-docs",
    "/.grok/",
    "GPUCache",
)


def git_changed_paths() -> list[str]:
    paths: set[str] = set()
    for args in (
        ["diff", "--name-only", "HEAD"],
        ["diff", "--name-only", "--cached", "HEAD"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        out = subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)
        for line in out.splitlines():
            line = line.strip()
            if line:
                paths.add(line)
    return sorted(paths)


def harness_changed_paths() -> list[str]:
    raw = os.environ.get("CHANGED_FILES", "").strip()
    if not raw:
        return []
    return [p for p in raw.split() if p]


def resolve_abs(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        return str(p.resolve())
    return str((ROOT / p).resolve())


def check_paths(paths: list[str], label: str, errors: list[str]) -> None:
    for rel in paths:
        abs_path = resolve_abs(rel) if not Path(rel).is_absolute() else str(Path(rel).resolve())
        if label == "git" and not any(abs_path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            if not str(ROOT) in abs_path and not str(SCRATCH) in abs_path:
                errors.append(f"{label}: out-of-scope path {rel}")
        if label == "harness":
            if not any(abs_path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
                errors.append(f"{label}: out-of-scope path {rel}")
        for frag in FORBIDDEN_FRAGMENTS:
            if frag in abs_path:
                errors.append(f"{label}: forbidden fragment {frag!r} in {rel}")


def main() -> int:
    errors: list[str] = []
    check_paths(git_changed_paths(), "git", errors)
    check_paths(harness_changed_paths(), "harness", errors)

    if errors:
        print("SCOPE GUARD FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SCOPE GUARD PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())