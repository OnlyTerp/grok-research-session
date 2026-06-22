# Track: Competitive Agent Analysis

**Subagent:** 019ef0ee-7434-7ff1-b320-d61838b9aac1

## Competitors analyzed
Claude Code, Cursor Agent/Composer, OpenAI Codex CLI, Aider, Windsurf/Devin Cascade, Factory Droid Missions, Devin CLI

## Key sources
- https://code.claude.com/docs/en/agent-teams
- https://code.claude.com/docs/en/sub-agents
- https://cursor.com/blog/composer-2-5
- https://cursor.com/blog/plan-mode
- https://developers.openai.com/codex/noninteractive
- https://factory.ai/news/missions
- https://docs.devin.ai/release-notes/2026
- https://aider.chat/docs/usage/modes.html

## Feature gaps (12)
1. Agent teams with inter-agent messaging
2. First-party Mission Mode + dashboard
3. Skills marketplace + record/replay
4. Headless JSONL + `--output-schema`
5. `xai/grok-action` GitHub Action
6. Auto permission classifier
7. Persistent plan artifact
8. Local→cloud handoff
9. `/agents` UI + agent memory
10. TUI queue + checkpoints
11. Architect/editor dual-model
12. Usage/cache metrics in stdout

## Grok strengths to preserve
Cursor ACP harness, compat matrix, sandbox, hooks, headless flags (`--best-of-n`, `--worktree`), harness-docs transparency.