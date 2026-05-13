# /khimaira-architect — Plan an implementation via khimaira

Spawn khimaira's architect (Claude Code under the hood) to design an implementation plan and write `IMPLEMENTATION.md` + `TODO.md` into the current project.

## Steps

1. **Resolve goal + context.**
   - **If $ARGUMENTS is non-empty:** use $ARGUMENTS verbatim as the `goal`. Bundle relevant prior conversation into `context` — err on the side of MORE, not less.
   - **If $ARGUMENTS is empty: just go.** Synthesize a `goal` from the conversation's overall direction (typically a one-sentence "design / plan / revise X based on the discussion above"). The user invoked the slash command — that's the green light, no clarification dialogue.
   - **Bundling rule for `context`:** dump *everything relevant* — prior decisions, locked constraints, review feedback to apply, existing files to read, framing the user gave. The whole point of khimaira-architect is to off-load substantive design work; don't keep it in chat. Truncate only if you'd exceed ~50KB. Concrete shape: a concise summary of the conversation's arc + verbatim quotes of decisions, constraints, or review concerns. If the conversation references existing spec files (e.g. "revise tasks/<slug>/IMPLEMENTATION.md against this review"), include the path so architect can read and update them in place.
   - **Pass `constraints`** when the conversation has an explicit "do this, not that" set (e.g. "shadcn locked, no Next.js, port 8740"). Verbatim quotes are best.
2. Call `mcp__khimaira__architect` with the resolved `goal` / `context` / `constraints` plus `cwd` = the current working directory.
3. Report the path of written files and a one-paragraph summary of what was planned (or revised).

## Notes

- Architect prefers `shared-docs/<user>/todo/<slug>/` if `shared-docs/` exists; otherwise falls back to `tasks/<slug>/`.
- For length-bounded asks ("≤200 words, ranked table only"), include that in the goal — architect will respect it and skip file writes.
- Default model: claude-opus-4-6, ~30–90s per call. Cost ~$0.05–0.30.
