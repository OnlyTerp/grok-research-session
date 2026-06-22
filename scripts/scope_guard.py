#!/usr/bin/env python3
"""Fail if git working tree touches paths outside the research repo and scratch."""

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
    ".hermes/",
    "discord",
    "grok-cli-harness-docs",
    "/.grok/",
)


def changed_paths() -> list[str]:
    env_paths = os.environ.get("CHANGED_FILES", "").strip()
    if env_paths:
        return [p for p in env_paths.split() if p]
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", "HEAD"],
        text=True,
    )
    staged = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", "--cached", "HEAD"],
        text=True,
    )
    untracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"],
        text=True,
    )
    paths = set()
    for block in (out, staged, untracked):
        for line in block.splitlines():
            line = line.strip()
            if line:
                paths.add(line)
    return sorted(paths)


def resolve_abs(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        return str(p.resolve())
    return str((ROOT / p).resolve())


def main() -> int:
    errors: list[str] = []
    for rel in changed_paths():
        abs_path = resolve_abs(rel)
        if not any(abs_path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            errors.append(f"out-of-scope path: {rel} -> {abs_path}")
        for frag in FORBIDDEN_FRAGMENTS:
            if frag in abs_path:
                errors.append(f"forbidden fragment {frag!r} in {rel}")
    if errors:
        print("SCOPE GUARD FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SCOPE GUARD PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())