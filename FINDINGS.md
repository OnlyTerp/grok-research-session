# Findings — Grok CLI Harness Research Synthesis

**Date:** 2026-06-22  
**Baseline:** Grok CLI 0.2.16+ (harness docs), Grok Build changelog through v0.2.52  
**Harness repo:** https://github.com/OnlyTerp/grok-cli-harness-docs

## Executive summary

Grok Build entered the coding-agent race in May 2026 with a **mature feature surface** on paper: Ratatui TUI, plan mode, subagents, skills/plugins/MCP, headless `-p`, full ACP, hooks, sandbox, and rapid changelog velocity (~daily fixes). External sentiment is **split**: engineers praise TUI craft and automation support; users criticize **pricing gates**, **verbosity/hallucination** (pre–Composer 2.5), and **immature Windows native support**.

The harness-docs repo (`grok-cli-harness-docs`) is well-positioned as a private source of truth. The highest-value additions are not net-new features but **closing gaps vs. table-stakes competitors** and **shipping Terp's Mission Mode upstream**.

## Competitive positioning

| Dimension | Grok strength | Gap vs leaders |
|-----------|---------------|----------------|
| Cursor ACP harness | Best-in-class IDE delegation | Limited ACP client docs beyond Cursor |
| Compat layers | Claude/Cursor skills, hooks, agents | Empty marketplace on many installs |
| TUI polish | Ratatui, vim+mouse, Mermaid | No `/terminal-setup`, no remappable keys |
| Headless | `-p`, `streaming-json`, `--best-of-n` | Thin JSONL event model vs Codex |
| Long-horizon | Subagents + worktrees | No stock Mission Mode / agent teams |
| Extensibility | MCP + plugins architecture | MCP progressive disclosure undocumented |
| Pricing | SuperGrok bundle | No developer-only tier; credits UI leaked |

## Top 10 priority recommendations (P0)

1. **Ship Mission Mode upstream** — Terp already has Factory-parity orchestration (`docs/21-mission-mode-local.md`); xAI subagents + worktrees are the foundation but lack multi-day validation gates.

2. **ACP ecosystem expansion** — npx distribution ([registry#366](https://github.com/agentclientprotocol/registry/issues/366)), Zed/OpenCode certification, conformance tests (`docs/07-acp-protocol.md`).

3. **Headless CI parity** — Rich JSONL + `--output-schema` + `xai/grok-action` (`docs/23-headless-mode.md`).

4. **Plan artifact persistence** — `.grok/plans/*.md` saved to workspace like Cursor/Gemini (`docs/02-cursor-harness.md`).

5. **TUI discoverability** — `/terminal-setup`, `?` help, `/docs` bridge (`docs/22-interactive-tui.md`).

6. **Developer pricing tier** — HN consensus: $300/mo Heavy blocks evaluation; credits hybrid in development ([TestingCatalog](https://www.testingcatalog.com/xai-prepares-credits-system-for-upcoming-grok-build-launch/)).

7. **Windows native QA matrix** — Changelog v0.2.52 fixes paths; HN users want no-WSL binaries (`docs/03-binary-and-installation.md`).

8. **Agent teams / swarm task store** — Claude agent-teams pattern; align with Mission handoffs (`docs/10-skills-agents-subagents.md`).

9. **Verifier plugin + stop hooks** — Deterministic build/test gates before ship (`docs/18-permissions-sandbox-hooks.md`).

10. **OTel + proxy ops docs** — v0.2.52 ships OTel; `GROK_PROXY_URL` needs harness documentation (`docs/20-operations-and-telemetry.md`).

## xAI official feature claims (verified)

From [x.ai/cli](https://x.ai/cli) and [launch post](https://x.ai/news/grok-build-cli):

- Skills: AGENTS.md, plugins, hooks, MCP, `/skillify`
- Plan mode: approve/comment/rewrite before edits
- Plugins: marketplace + git self-host
- Subagents: parallel with worktrees
- Q&A: multiple-choice for ambiguous tasks
- Headless: `-p` + full ACP

Changelog v0.2.52 adds: OTel export, Agent Dashboard without leader mode, ER/Mermaid rendering, compaction fixes, Windows path cleanup.

## User feedback themes (HN + ecosystem)

| Theme | Representative quote | Source |
|-------|---------------------|--------|
| TUI quality | *"quite beautiful… written in Rust… Ratatui is quite customizable"* | HN ofek / skp1995 |
| Automation | *"explicitly supporting automation similar to OpenAI"* | HN 2001zhaozhao |
| Pricing barrier | *"not spending $300 a month… pricing will have to come drastically down"* | HN giancarlostoro |
| Windows gap | *"native binaries (no WSL)… normal environment"* | HN ofek |
| Zed demand | *"Wonder if they will ever add this to Zed"* | HN giancarlostoro |
| Quality complaints | *"Hallucination to the max, too chatty"* | HN nikolay |

## Mission track alignment

Maps to `find-out-ways-to-improve-grok-cli` research tracks:

| Track | Key external finding |
|-------|---------------------|
| 01 TUI | `/terminal-setup`, keybindings, queue/checkpoints |
| 02 Skills | Marketplace, `/skillify`, record/replay |
| 03 Mission Dashboard | Ship Terp pattern; ACP mission control plane |
| 04 Agents/ACP | Agent teams, handoff protocol, npx registry |
| 05 Onboarding | First-run checklist, `/docs`, pricing table |
| 06 Performance | OTel, proxy URL, usage in JSONL |
| 07 Competitive | Codex JSONL, Claude teams, Factory missions |

## X-adjacent signals (pre-synthesis, via HN WebFetch)

Native X MCP tools were unavailable; `site:x.com` WebSearch failed. X engineer discourse captured from HN item 48139115:

| Signal | Source in HN thread | Implication |
|--------|---------------------|-------------|
| TUI built in Ratatui, vim+mouse | @skp1995 (xAI engineer) | Document TUI architecture in harness |
| Windows native binaries gap | @ofek, @skp1995 | QA matrix for no-WSL Windows |
| $300/mo SuperGrok pricing barrier | @giancarlostoro | Developer tier needed |
| @skcd42 X thread on TUI craft | HN link to x.com/skcd42 | Cross-link harness docs to engineer posts |

## Risks for implementers

- **Closed source:** No `xai-org/grok-cli` repo; ideas flow via `/feedback`, HN, integrator issues.
- **Rapid changelog:** Harness docs at 0.2.16 need refresh against v0.2.52.
- **Harness X MCP gap:** Cursor harness lacks native X search; used `site:x.com` WebSearch + public WebFetch of x.com URLs (no OAuth).

## Phased roadmap

**Phase 1 (0–3 months):** Docs + ops — CI cookbook, OTel/proxy, plan artifacts, onboarding, pricing table in harness.

**Phase 2 (3–6 months):** Orchestration — Mission Mode beta, handoff protocol, verifier plugin, agent teams task store.

**Phase 3 (6+ months):** Ecosystem — skills marketplace, ACP certification, desktop↔CLI sync, arena mode, developer pricing tier.