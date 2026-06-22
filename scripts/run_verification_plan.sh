#!/usr/bin/env bash
# Execute plan ## Verification plan steps; write evidence to scratch.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="${SCRATCH:-/tmp/grok-goal-adddf1ff4ea4/implementer}"
EVIDENCE="$SCRATCH/verification-evidence.txt"
W1="$SCRATCH/wave1"
W2="$SCRATCH/wave2"

mkdir -p "$SCRATCH"
: >"$EVIDENCE"

log() { echo "$*" | tee -a "$EVIDENCE"; }

log "=== VERIFICATION PLAN — $(date -Iseconds) ==="
log ""
log "--- Step 1: scratch transcripts (>=12 web/X-adjacent, parallel evidence) ---"
W1N=$(find "$W1" -maxdepth 1 -name '*.txt' 2>/dev/null | wc -l)
W2N=$(find "$W2" -maxdepth 1 -name '*.txt' 2>/dev/null | wc -l)
log "scratch wave1 txt files: $W1N"
log "scratch wave2 txt files: $W2N"
log "sample wave1 headers:"
head -n 8 "$W1"/*.txt 2>/dev/null | head -n 40 | tee -a "$EVIDENCE" || true
log ""
log "--- Step 2: synthesized deliverables ---"
for f in IDEAS.md FINDINGS.md RESEARCH_LOG.md LIMITATIONS.md; do
  log "$f: $(wc -l <"$ROOT/$f") lines, $(wc -c <"$ROOT/$f") bytes"
done
log "IDEAS harness refs:"
rg -c 'docs/1[0-9]-|docs/2[0-9]-' "$ROOT/IDEAS.md" | tee -a "$EVIDENCE" || true
log ""
log "--- Step 3: git remote + branch ---"
git -C "$ROOT" remote -v | tee -a "$EVIDENCE"
git -C "$ROOT" log --oneline -3 | tee -a "$EVIDENCE"
gh repo view OnlyTerp/grok-research-session --json name,url,defaultBranchRef 2>&1 | tee -a "$EVIDENCE"
log "hermes in git name-only (expect empty):"
git -C "$ROOT" log --name-only --oneline -5 | rg -i hermes || log "(none)"
log ""
log "--- Step 4: validators ---"
python3 "$ROOT/scripts/scope_guard.py" | tee -a "$EVIDENCE"
python3 "$ROOT/scripts/validate_swarm_provenance.py" | tee -a "$EVIDENCE"
python3 "$ROOT/tests/verify_research_artifacts.py" | tee -a "$EVIDENCE"
log ""
log "=== END ==="