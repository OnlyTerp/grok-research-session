# Research limitations (honest)

## Native X tools — not executed

The **Cursor harness** for this goal session exposes only `WebSearch`, `WebFetch`, `Shell`, and `Task`. It does **not** expose:

- `x_keyword_search`
- `x_semantic_search`
- `open_page` (browser)

This is recorded in parent `updates.jsonl` agent thought at timestamp `1782158364`.

**Implication:** Acceptance criterion 1’s native X tool requirement was **not met**. Mega-swarm web research + Task subagents **were** met.

## X discourse — web proxies only

Pre-synthesis “X signal” in `swarm/raw/wave2/` comes from **web proxies**, not native X MCP:

| File | Actual tool | Proxy method |
|------|-------------|--------------|
| `01-Shell-*.txt` | Shell | HN Algolia comment API (`tags=comment`) |
| `03-WebFetch-*.txt` | WebFetch | HN thread HTML quoting @skp1995, @ofek, `x.com/skcd42` links |

Failed `site:x.com` `WebSearch` calls (~123B provider errors) are logged as **metadata only** in `wave2/attempts/site-x-failures.json` — no error bodies committed.

## Out-of-scope host files

This repo must not modify `.hermes/auth.json`, Discord caches, or harness dirs. Earlier rejected fix rounds in the parent session may have touched `.hermes` outside this git repo; **no commit in `grok-research-session` contains Hermes paths** (`git log --name-only` verified).