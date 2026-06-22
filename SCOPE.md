# Scope boundary

This repository contains **only** Grok CLI harness research artifacts.

**Authentic sources:**
- `updates.jsonl` session log (pre-synthesis tool completions with timestamps)
- Extracted transcripts in `swarm/raw/wave1/` and `swarm/raw/wave2/`

**Explicitly out of scope (do not touch/commit):**
- `.hermes/auth.json` and other OAuth credential files
- Discord cache, GPUCache, unrelated host files
- `grok-cli-harness-docs` and `~/.grok` harness files (read-only reference)

**X search note:** Native `x_keyword_search` / `x_semantic_search` MCP tools are unavailable in the Cursor harness; X signal captured via `site:x.com` WebSearch, HN cross-links, and public `WebFetch` of x.com URLs.