# /chimera-swarm — Parallel batch ops via chimera (PDE)

Decomposes a goal into N independent tasks and dispatches them concurrently. Best for batch ops: "fix all pyright errors", "add tests to 10 modules", "convert all CSS files to use theme variables".

## Steps

1. Call `mcp__chimera__swarm` with:
   - `goal`: $ARGUMENTS
   - `budget`: 2.0 (USD; override only if the user specified)
   - `max_agents`: 10 (override only if the user specified)
2. Capture the returned `job_id` + `thread_id`.
3. Tell the user: "Started swarm `<job_id>` with budget $2.00 / max 10 workers. Track via `mcp__chimera__status('<job_id>')`."
4. Don't poll automatically.

## Notes

- The decomposer chooses how many workers to actually spawn — `max_agents` is a ceiling.
- Budget is conservative by default. Bump to $5+ if the goal is genuinely big.
- For single, complex tasks → `/chimera-chain`. For autonomous loops → `/chimera-refiner`.
