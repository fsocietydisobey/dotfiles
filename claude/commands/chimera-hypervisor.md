# /chimera-hypervisor — Meta-orchestrator (HVD)

Monitors the repository, decides which chimera pattern to spawn (refiner for incremental improvement, swarm for batch fixes, pipeline for single tasks), enforces directives, and controls a daily $ budget. The "set a budget and walk away" mode.

## Steps

1. Parse $ARGUMENTS for optional `budget=<usd>` override. Default: `budget=10.0` (daily ceiling).
2. Call `mcp__chimera__chain_hypervisor` with the parsed (or default) budget.
3. Capture the returned `job_id`.
4. Tell the user: "Hypervisor started — job `<job_id>`, daily budget $X. It will dispatch sub-patterns autonomously. Track via `mcp__chimera__status('<job_id>')`."
5. Note that hypervisor jobs survive across MCP restarts only if chimera's checkpointer is persistent — so for a true daemon, run chimera outside of Claude Code (not currently set up).

## Notes

- The most autonomous of the chimera tools. Use deliberately.
- Hypervisor enforces its own directives (no `--no-verify`, no force-pushes, etc.) — these are configured in chimera's config, not here.
- For bounded one-shot work, prefer `/chimera-chain` or `/chimera-swarm`.
