# /tools — list everything khimaira exposes

Quick discoverability surface — surfaces all CLI subcommands, MCP tools, slash commands, web routes, and REST API endpoints in one catalog.

## Steps

1. Run `khimaira tools` via Bash. Optionally pass a substring filter as `$ARGUMENTS` (e.g. `/tools session` runs `khimaira tools session`).
2. Render the output verbatim — it's already formatted for terminal display.
3. If the user is looking for something specific they couldn't find, suggest they use `--category` to narrow (cli / mcp / slash / web / api).

## Notes

- Cheap and offline — just introspects local Python modules + `~/.claude/commands/`. No daemon call.
- For machine-readable output, append `--json`.
