# /khimaira-refiner — Autonomous codebase refinement loop (CLR)

Runs continuously: assess health → triage → execute → validate → commit/revert → loop. Reads `SPEC.md` from the project root for feature goals. Stops on convergence, budget exhaustion, or spec completion.

## Steps

1. Parse $ARGUMENTS for optional overrides — formats accepted: `<max_cycles>`, `budget=<usd>`, or `<max_cycles> budget=<usd>`. Default: `max_cycles=50, budget=5.0`.
2. Call `mcp__khimaira__chain_refiner` with the parsed (or default) values.
3. Capture the returned `job_id`.
4. Tell the user: "Refiner started — job `<job_id>`, max cycles X, budget $Y. It will loop autonomously until convergence/budget exhaustion. Track via `mcp__khimaira__status('<job_id>')`."
5. Warn if `SPEC.md` doesn't exist in the current project root — refiner needs it.

## Notes

- "Leave it running" mode. Designed for codebase convergence, not single tasks.
- Reverts its own commits if validation fails — git history will show a revert pattern.
- Bounded by both `max_cycles` AND `budget`. Whichever hits first stops the loop.
