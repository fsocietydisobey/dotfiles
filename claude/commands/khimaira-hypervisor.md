# /khimaira-hypervisor — Meta-orchestrator (HVD)

Monitors the repository, decides which khimaira pattern to spawn (refiner for incremental improvement, swarm for batch fixes, pipeline for single tasks), enforces directives, and controls a daily $ budget. The "set a budget and walk away" mode.

## Steps

1. Parse $ARGUMENTS for optional `budget=<usd>` override. Default: `budget=10.0` (daily ceiling).
2. Call `mcp__khimaira__chain_hypervisor` with the parsed (or default) budget.
3. Capture the returned `job_id`.
4. Tell the user: "Hypervisor started — job `<job_id>`, daily budget $X. It will dispatch sub-patterns autonomously. Track via `mcp__khimaira__status('<job_id>')`."
5. Note that hypervisor jobs survive across MCP restarts only if khimaira's checkpointer is persistent — so for a true daemon, run khimaira outside of Claude Code (not currently set up).

## Notes

- The most autonomous of the khimaira tools. Use deliberately.
- Hypervisor enforces its own directives (no `--no-verify`, no force-pushes, etc.) — these are configured in khimaira's config, not here.
- For bounded one-shot work, prefer `/khimaira-chain` or `/khimaira-swarm`.
