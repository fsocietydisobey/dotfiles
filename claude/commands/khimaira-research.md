# /khimaira-research — Deep research via khimaira (Gemini)

Spawn khimaira's research tool (Gemini CLI) to investigate a topic before planning. Use for domain exploration, technology evaluation, or understanding unknowns.

## Steps

1. Call `mcp__khimaira__research` with:
   - `question`: $ARGUMENTS
   - `cwd`: the absolute path of the current working directory
2. Pass the question verbatim. If the user already gave context (file paths, prior findings), include those in the `context` arg; otherwise leave it empty.
3. Report Gemini's findings as a tight summary, then offer the full output if the user wants depth.

## Notes

- Gemini is faster and cheaper than Claude — good for "what should I read about X?" before committing to architect.
- For known territory or tight scope, just ask Claude (me) directly — research is for genuine unknowns.
