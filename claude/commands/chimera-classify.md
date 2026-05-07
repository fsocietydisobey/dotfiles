# /chimera-classify — Tier-check a task before committing to a chain

Quick, cheap classification of a task — returns tier (research / architect / implement) + recommended pipeline. Use this when unsure whether a task is worth a full `chain_pipeline` run.

## Steps

1. Call `mcp__chimera__classify` with:
   - `task_description`: $ARGUMENTS
2. Report the tier, confidence, recommended pipeline, and one-line reasoning.
3. If the user wants to act on the recommendation, suggest the matching slash command (`/chimera-research`, `/chimera-architect`, `/chimera-chain`).

## Notes

- This call uses a fast, cheap API model — under $0.001 and ~2s.
- Always run before any expensive chain to avoid burning tokens on a misclassified task.
