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

This legacy public template is disabled by `.private-context`. It is retained
temporarily for history while the private-store migration is reviewed, but
`tool project apply` and `tool project diff` refuse to apply it. The active
source of truth is the private context store managed with `tool project
context-*`; the dotfiles repository is public.

```bash
tool project context-diff  ~/work/jeevy_portal
tool project context-apply ~/work/jeevy_portal --write
```

The generic public-template apply path remains available for projects without
the marker. It never touches Khimaira-generated `settings.json`, machine-local
`settings.local.json`, or ephemeral Claude runtime state in the target.
