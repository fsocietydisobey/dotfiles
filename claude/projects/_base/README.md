# _base — common project `.claude/` skeleton

Everything here is overlaid into every project when `tool project apply <path>` runs, **before** any project-specific overrides.

Right now `_base/` is empty — there's only one project (jeevy_portal) so there's nothing generic to factor out. When a second project exists and a pattern emerges (shared settings.json hook, a common command, etc.), move it here.

## Precedence

```
<project>/.claude/ ← overrides/<project>/.claude/ ← _base/.claude/
                                (higher precedence)
```

`tool project apply` merges top-down; later layers overwrite earlier ones. Khimaira-owned
`settings.json`, machine-local `settings.local.json`, and Claude runtime state
(`scratch/`, `worktrees/`, `checkpoints/`, `mailbox/`, and related registries) are
never touched.
