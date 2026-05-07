# /chimera-chain — Kick off chimera's SPR-4 pipeline

Runs the structured 4-phase pipeline (research → plan → implement → review) with critic loops at each phase. Pauses for human approval before commit. Returns immediately with a `job_id`.

## Steps

1. Call `mcp__chimera__chain_pipeline` with:
   - `task_description`: $ARGUMENTS
   - `context`: empty unless the user provided extra context
2. Capture the returned `job_id` and `thread_id`.
3. Tell the user: "Started job `<job_id>`. Track progress with `mcp__chimera__status('<job_id>')`. When the pipeline pauses for review, run `mcp__chimera__approve('<job_id>')` to continue."
4. Don't poll status automatically — the chain runs in the background. Wait for the user to ask.

## Notes

- This is the structured variant — bounded steps, persistent memory across runs, phase-tagged progress events. Prefer this over the legacy supervisor `chain` tool.
- For batch ops (fix all X, add Y to N modules), use `/chimera-swarm` instead.
- Approval is non-skippable. The pipeline will sit paused until you run `approve()`.
