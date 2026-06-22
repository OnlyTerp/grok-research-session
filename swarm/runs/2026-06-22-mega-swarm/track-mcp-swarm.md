# Track: MCP / Swarm / Orchestration Patterns

**Subagent:** 019ef0ee-7434-7ff1-b320-d62a058ded9a

## Key sources
- https://modelcontextprotocol.io/specification/2025-11-25
- https://www.anthropic.com/engineering/code-execution-with-mcp
- https://www.anthropic.com/engineering/built-multi-agent-research-system
- https://cognition.com/blog/dont-build-multi-agents
- https://cursor.com/blog/agent-best-practices
- https://agentic-patterns.com/patterns/stop-hook-auto-continue-pattern/
- https://foojay.io/today/best-practices-for-working-with-ai-agents-subagents-skills-and-mcp/

## Improvement ideas (10+)
1. MCP progressive disclosure + code-execution bridge
2. Unified plugin trust + MCP allowlist per role
3. Structured HandoffV1 protocol
4. Plan ↔ Mission unification
5. Verifier plugin + stop-hook loops
6. Read-parallel / write-serialized topology
7. ACP mission control plane
8. Skills-as-orchestration packages (spec.yaml)
9. LSP-backed verification in subagent loop
10. Durable mission checkpoints + session fork

## Synthesis tension
Industry split: parallelize reads, serialize writes (Anthropic/LangChain) vs. full-trace handoffs (Cognition) vs. parallel worktrees (Cursor). **Recommendation:** Mission Mode gated parallelism + explore/best-of-n for reads.