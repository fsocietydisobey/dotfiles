# jeevy_portal — project override

Canonical `.claude/` contents for `~/work/jeevy_portal`.

## Contents

- `.claude/settings.json` — session-start hook registration
- `.claude/hooks/session-start-context.sh` — loads architecture context at session start
- `.claude/commands/` — project-specific slash commands (`/find`, `/review`, `/test`, `/trace`, `/sync-all-feature-claude-md`, `/update-architecture`, `/update-feature-claude-md`)
- `.claude/rules/` — project-specific rules (frontend, backend, agents, context, environment, guardrails, styling)

## What's NOT here (intentionally)

- `settings.local.json` — per-machine (permissions, enabled MCP servers). Stays in the working project only.
- `session-log.md`, `tasks.md` — ephemeral scratch. Stays in the working project.

## Sync model

Source of truth is *this directory*. Working copy is `~/work/jeevy_portal/.claude/`.

```bash
tool project diff  ~/work/jeevy_portal    # see drift
tool project apply ~/work/jeevy_portal --write   # template → project
```

`apply` never touches `settings.local.json` or ephemeral scratch files in the target.
