# Improvement Ideas — Grok CLI Harness

45 externally-sourced ideas for `grok-cli-harness-docs` and harness usage patterns. Each entry: **harness area**, **source**, **quote/paraphrase**.

---

## Subagents & Swarm Orchestration

### 1. Agent Teams with Shared Task List
- **Area:** `docs/10-skills-agents-subagents.md`, `docs/02-cursor-harness.md`
- **Source:** https://code.claude.com/docs/en/agent-teams
- **Quote:** *"Agent teams are independent Claude Code sessions that communicate with each other… Shared task list with self-coordination."*

### 2. Parallel Arena / Best-of-N Mode (8 agents)
- **Area:** `docs/10-skills-agents-subagents.md`, `docs/23-headless-mode.md`
- **Source:** https://www.testingcatalog.com/xai-tests-parralel-agents-and-arena-mode-for-grok-build/
- **Quote:** *"Users could run eight agents at once"* with tournament-style ranking.

### 3. Read-Parallel / Write-Serialized Topology Policy
- **Area:** `docs/10-skills-agents-subagents.md`, `docs/21-mission-mode-local.md`
- **Source:** https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems
- **Quote:** *"Multi-agent systems that primarily 'read' are easier than those that 'write'."*

### 4. Structured Handoff Protocol (HandoffV1)
- **Area:** `docs/07-acp-protocol.md`, `docs/21-mission-mode-local.md`
- **Source:** https://cognition.com/blog/dont-build-multi-agents
- **Quote:** *"Share context, and share full agent traces, not just individual messages."*

### 5. Subagents Inherit `web_search` + `x_search` (document + extend)
- **Area:** `docs/10-skills-agents-subagents.md`
- **Source:** https://x.ai/build/changelog (v0.2.37)
- **Quote:** Changelog: *"Subagents now correctly receive `web_search` and `x_search` tools from the parent session."* — harness should document inheritance rules.

### 6. Deep Worktree Subagent Isolation (first-class)
- **Area:** `docs/10-skills-agents-subagents.md`
- **Source:** https://x.ai/news/grok-build-cli
- **Quote:** *"Deep worktree support — launch subagents in their own worktrees."*

### 7. `/agents` TUI Panel + Agent Memory Dirs
- **Area:** `docs/10-skills-agents-subagents.md`, `docs/22-interactive-tui.md`
- **Source:** https://code.claude.com/docs/en/sub-agents
- **Quote:** *"Run `/agents` to create or open… `memory: user` stores in `~/.claude/agent-memory/`."*

### 8. Architect/Editor Dual-Model Split
- **Area:** `docs/05-models-and-api.md`, `docs/10-skills-agents-subagents.md`
- **Source:** https://aider.chat/docs/usage/modes.html
- **Quote:** *"Architect mode: reasoning model proposes; editor model emits file edits."*

---

## Mission Mode & Long-Horizon Orchestration

### 9. Ship First-Party Mission Mode (Factory parity)
- **Area:** `docs/21-mission-mode-local.md`
- **Source:** https://factory.ai/news/missions
- **Quote:** *"Describe what you want and approve the plan. Droid handles decomposition, execution, and validation."*

### 10. Mission Control via ACP Extension (`x.ai/mission/*`)
- **Area:** `docs/07-acp-protocol.md`, `docs/21-mission-mode-local.md`
- **Source:** https://agentclientprotocol.com
- **Quote:** *"ACP standardizes communication between code editors/IDEs and coding agents."*

### 11. Three-Gate Validation (scrutiny / integration / UAT)
- **Area:** `docs/21-mission-mode-local.md`
- **Source:** Terp mission + Factory missions docs
- **Quote:** Factory: *"Every milestone ends with a validation phase: workers review… run tests, check for regressions."*

### 12. Model-Agnostic Orchestrator (role-based routing)
- **Area:** `docs/05-models-and-api.md`, `docs/21-mission-mode-local.md`
- **Source:** https://factory.ai/news/missions
- **Quote:** *"Orchestration: Opus 4.6; Feature implementation: Sonnet 4.6; Validation: GPT-5.3-Codex; Research: Kimi K2.5."*

### 13. Plan ↔ Mission Bridge (auto-materialize features)
- **Area:** `docs/07-acp-protocol.md`, `docs/21-mission-mode-local.md`
- **Source:** https://cursor.com/blog/plan-mode
- **Quote:** *"Creates a Markdown file with file paths and code references."* — bridge ACP `plan` entries to mission `features/`.

### 14. Durable Mission Checkpoints on Compaction
- **Area:** `docs/08-session-persistence.md`, `docs/21-mission-mode-local.md`
- **Source:** https://x.ai/build/changelog (v0.2.52 fork fix)
- **Quote:** *"Forked sessions now retain the parent's full pre-compaction transcripts."*

### 15. Local→Cloud Handoff (`/handoff`)
- **Area:** `docs/07-acp-protocol.md`, `docs/08-session-persistence.md`
- **Source:** https://docs.devin.ai/work-with-devin/devin-cli
- **Quote:** Devin CLI packages conversation + git branch for cloud continuation.

---

## Skills, Plugins & MCP

### 16. Curated xAI Skills Marketplace (signed manifests)
- **Area:** `docs/19-plugins-mcp-lsp.md`, `docs/10-skills-agents-subagents.md`
- **Source:** https://x.ai/cli
- **Quote:** *"Marketplace install, or self-host from any git repo."*

### 17. `/skillify` — Capture Session as Skill
- **Area:** `docs/10-skills-agents-subagents.md`
- **Source:** https://x.ai/cli
- **Quote:** *"Capture any session as a new skill with /skillify."*

### 18. Record & Replay Skill Authoring (Codex-style)
- **Area:** `docs/10-skills-agents-subagents.md`
- **Source:** https://developers.openai.com/codex/skills
- **Quote:** Progressive disclosure keeps skills at ~2% context budget.

### 19. MCP Progressive Disclosure / Code-Execution Bridge
- **Area:** `docs/19-plugins-mcp-lsp.md`
- **Source:** https://www.anthropic.com/engineering/code-execution-with-mcp
- **Quote:** *"98.7% token reduction"* when agents read tool definitions on demand.

### 20. First-Party MCP Session Bridge (reduce wrapper latency)
- **Area:** `docs/19-plugins-mcp-lsp.md`
- **Source:** https://github.com/BasisSetVentures/grok-cli-mcp (Show HN)
- **Quote:** Community wrapper: *"~50-200ms extra latency from process spawning."*

### 21. Verifier Plugin + Stop-Hook Auto-Continue
- **Area:** `docs/18-permissions-sandbox-hooks.md`, `docs/19-plugins-mcp-lsp.md`
- **Source:** https://agentic-patterns.com/patterns/stop-hook-auto-continue-pattern/
- **Quote:** *"Keep going until the thing is done"* via stop hooks + success criteria.

### 22. LSP Diagnostics in Subagent Verification Loop
- **Area:** `docs/19-plugins-mcp-lsp.md`
- **Source:** https://foojay.io/today/best-practices-for-working-with-ai-agents-subagents-skills-and-mcp/
- **Quote:** *"When a subagent edits a file, OpenCode queries the LSP server and feeds diagnostics back."*

### 23. Plugin Trust as Orchestration Policy
- **Area:** `docs/19-plugins-mcp-lsp.md`, `docs/18-permissions-sandbox-hooks.md`
- **Source:** https://modelcontextprotocol.io/specification/2025-11-25
- **Quote:** *"Tools represent arbitrary code execution… Hosts must obtain explicit user consent."*

---

## TUI & Interaction

### 24. `/terminal-setup` First-Run Wizard
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://code.claude.com/docs/en/terminal-config
- **Quote:** *"Run `/terminal-setup` once"* for VS Code, Cursor, Alacritty, Zed.

### 25. Remappable `keybindings.json`
- **Area:** `docs/22-interactive-tui.md`, `docs/17-config-schema.md`
- **Source:** https://code.claude.com/docs/en/keybindings
- **Quote:** *"Changes… automatically detected and applied without restarting."*

### 26. `?` In-TUI Contextual Shortcut Help
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://code.claude.com/docs/en/interactive-mode
- **Quote:** *"Press `?` in the transcript viewer to see available shortcuts."*

### 27. Unified `/` Palette (builtins + skills + MCP)
- **Area:** `docs/22-interactive-tui.md`, `docs/19-plugins-mcp-lsp.md`
- **Source:** https://code.claude.com/docs/en/commands
- **Quote:** *"The `/` menu shows everything you can invoke."*

### 28. Message Queue During Active Turns
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://docs.devin.ai/desktop/cascade
- **Quote:** Windsurf Cascade: queued messages while agent works.

### 29. Named Checkpoints + One-Click Revert
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://docs.devin.ai/desktop/cascade
- **Quote:** *"Named checkpoints"* for rollback without losing context.

### 30. `Shift+Tab` Mode Cycle Banner (already shipping — document)
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://x.ai/build/changelog (v0.2.43, v0.2.11)
- **Quote:** *"Show 'Switched to mode' banner above prompt for `Shift+Tab` cycles."*

### 31. Shell Escape Hatch (`!` prefix)
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://code.claude.com/docs/en/interactive-mode
- **Quote:** *"`!` at start — Shell mode — Run commands directly."*

### 32. `ask_user` Multiple-Choice Q&A (productize in harness docs)
- **Area:** `docs/22-interactive-tui.md`, `docs/02-cursor-harness.md`
- **Source:** https://x.ai/cli
- **Quote:** *"Ambiguous tasks get a quick multiple-choice… Answers flow straight into the plan."*

---

## Plan Mode

### 33. Persistent `.grok/plans/<session>.md` Artifact
- **Area:** `docs/02-cursor-harness.md`, `docs/24-external-topics-index.md`
- **Source:** https://cursor.com/blog/plan-mode
- **Quote:** *"Optionally, save the plan as a Markdown file in your repository."*

### 34. Plan Approval UX (`[a]pprove [c]omment [q]uit`)
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://x.ai/cli
- **Quote:** *"Approve the plan, comment on individual steps, or rewrite it entirely."*

### 35. External Editor for Plan (`Ctrl+X`)
- **Area:** `docs/22-interactive-tui.md`
- **Source:** https://geminicli.com/docs/cli/plan-mode/
- **Quote:** *"Press `Ctrl+X` to open the plan directly in your configured external editor."*

### 36. Background Planner Thread (cheaper model)
- **Area:** `docs/05-models-and-api.md`
- **Source:** https://devin.ai/blog/windsurf-wave-10-planning-mode/
- **Quote:** Persistent markdown plan file updated by background planner.

---

## Headless, CI & Operations

### 37. Rich JSONL Event Stream (ACP-aligned)
- **Area:** `docs/23-headless-mode.md`, `docs/16-acp-events-catalog.md`
- **Source:** https://developers.openai.com/codex/noninteractive
- **Quote:** JSONL: `thread.started`, `turn.completed`, `item.*` for tool events.

### 38. `--output-schema` Structured Final Response
- **Area:** `docs/23-headless-mode.md`
- **Source:** https://developers.openai.com/codex/noninteractive
- **Quote:** JSON Schema constrained output for CI pipelines.

### 39. First-Party `xai/grok-action` GitHub Action
- **Area:** `docs/23-headless-mode.md`, `docs/20-operations-and-telemetry.md`
- **Source:** https://developers.openai.com/codex/github-action
- **Quote:** `openai/codex-action@v1` pattern for PR review automation.

### 40. OpenTelemetry Export Documentation (v0.2.52)
- **Area:** `docs/20-operations-and-telemetry.md`
- **Source:** https://x.ai/build/changelog
- **Quote:** *"Export usage metrics and events to your own OpenTelemetry collector."*

### 41. `GROK_PROXY_URL` Token-Shaping Integration
- **Area:** `docs/12-network-and-endpoints.md`, `docs/20-operations-and-telemetry.md`
- **Source:** https://github.com/headroomlabs-ai/headroom/issues/1291
- **Quote:** *"Grok Build users doing long sessions… leaving massive token savings on the table."*

### 42. Usage Block in `streaming-json` Tail Events
- **Area:** `docs/23-headless-mode.md`, `docs/20-operations-and-telemetry.md`
- **Source:** Competitive gap vs Codex JSONL `usage.cached_input_tokens`

---

## ACP & IDE Integration

### 43. ACP Registry `npx @xai-official/grok` Distribution
- **Area:** `docs/07-acp-protocol.md`, `docs/03-binary-and-installation.md`
- **Source:** https://github.com/agentclientprotocol/registry/issues/366
- **Quote:** Switch from per-arch binary URLs to npm auto-update.

### 44. Zed / OpenCode / JetBrains Certification Guide
- **Area:** `docs/07-acp-protocol.md`, `docs/02-cursor-harness.md`
- **Source:** https://news.ycombinator.com/item?id=48139115
- **Quote:** HN **giancarlostoro**: *"Wonder if they will ever add this to Zed."*

### 45. ACP Conformance Test Suite (beyond Cursor)
- **Area:** `docs/07-acp-protocol.md`
- **Source:** https://docs.factory.ai/ (ACP output format support)

---

## Platform, Pricing & Access

### 46. Developer-Only Grok Build Plan / Trial Quota
- **Area:** `docs/04-authentication.md`, `docs/05-models-and-api.md`
- **Source:** https://news.ycombinator.com/item?id=48139115
- **Quote:** **giancarlostoro**: *"Wonder if they offered a 'Grok Build only plan'."*

### 47. Credits Balance UI + Deep `/usage`
- **Area:** `docs/20-operations-and-telemetry.md`
- **Source:** https://www.testingcatalog.com/xai-prepares-credits-system-for-upcoming-grok-build-launch/
- **Quote:** Monthly credits allotment + on-demand top-up (hybrid model).

### 48. Native Windows Binary Parity (no WSL)
- **Area:** `docs/03-binary-and-installation.md`, `docs/22-interactive-tui.md`
- **Source:** https://news.ycombinator.com/item?id=48139115
- **Quote:** **skp1995** (xAI): Windows build *"not as heavily tested yet."* **ofek**: native binaries expected.

### 49. Plan Mode Controls UX (from @skcd42 shipped fixes)
- **Area:** `docs/22-interactive-tui.md`, `docs/24-external-topics-index.md`
- **Source:** https://x.com/skcd42/status/2055554272545362394 (x_keyword_search via x_search.py)
- **Quote:** *"plan mode controls should be more intuitive"* — xAI engineer shipping beta fixes from CLI feedback.

### 50. Concise / Anti-Verbosity Agent Preset
- **Area:** `docs/05-models-and-api.md`, `docs/17-config-schema.md`
- **Source:** https://news.ycombinator.com/item?id=48287379
- **Quote:** **nikolay**: *"Hallucination to the max, too chatty, too annoying!"*

### 51. Desktop ↔ CLI Session Portability
- **Area:** `docs/01-architecture.md`, `docs/08-session-persistence.md`
- **Source:** https://www.testingcatalog.com/spacexai-prepares-grok-build-desktop-app-to-rival-openai-codex/
- **Quote:** Desktop app with Plans, Files, Edits, built-in browser — feature parity with Codex/Claude Code desktop.

---

## Documentation & Onboarding

### 52. First-Run Onboarding Checklist in Harness
- **Area:** `reference/user-guide-index.md`, new `docs/27-onboarding-checklist.md` proposal
- **Source:** https://code.claude.com/docs/en/commands
- **Quote:** *"First session in a repo. Run `/init`… `/mcp` and `/agents`."*

### 53. `/docs` and `/help` Deep Links to Harness Topics
- **Area:** `docs/22-interactive-tui.md`, `docs/24-external-topics-index.md`
- **Source:** https://geminicli.com/docs/reference/commands/
- **Quote:** *"`/docs` — Open Gemini CLI documentation in your browser."*

### 54. Headless CI Cookbook with `streaming-json` Examples
- **Area:** `docs/23-headless-mode.md`
- **Source:** https://cursor.com/docs/cli/headless
- **Quote:** *"Use `--output-format stream-json` for message-level progress tracking."*

### 55. Auto Permission Classifier (production `auto` mode)
- **Area:** `docs/18-permissions-sandbox-hooks.md`
- **Source:** https://code.claude.com/docs/en/permission-modes
- **Quote:** Classifier reviews shell/network before execution; blocks destructive ops.

### 56. Enterprise Mission Governance (`missionPolicy`)
- **Area:** `docs/21-mission-mode-local.md`
- **Source:** https://docs.factory.ai/cli/features/missions
- **Quote:** Org-level policies for long-running orchestrations.