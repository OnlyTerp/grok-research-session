# Scope boundary

This repository contains **only** Grok CLI harness research artifacts under `repos/grok-research-session/`.

## Authentic sources

- Parent + child `updates.jsonl` session logs (pre-synthesis tool completions)
- Extracted transcripts in `swarm/raw/wave1/` (web) and `swarm/raw/wave2/` (X-discourse **web proxies**)

## Explicitly out of scope (never touch/commit)

- Hermes OAuth credential stores (`auth.json` under dot-hermes paths)
- Discord cache, GPUCache, unrelated host files
- `grok-cli-harness-docs` and `~/.grok` harness files (read-only reference)

## Native X tools — blocked in this harness

`x_keyword_search` / `x_semantic_search` were **not available** in the Cursor goal harness. See [LIMITATIONS.md](LIMITATIONS.md).

Pre-synthesis X-adjacent signal uses **web proxies only**:

- HN Algolia comment API (Shell in child Task session)
- HN thread WebFetch quoting X engineers (@skp1995, @ofek)

Failed `site:x.com` WebSearch attempts are metadata in `wave2/attempts/site-x-failures.json` only.