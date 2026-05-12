# /chimera-configure — Re-sync this machine to your chimera profile

Brings the current machine into alignment with the chimera profile
declared in your dotfiles repo. Same operations as running `chimera
sync` from a terminal, but invokable from inside any Claude Code
session — useful when you've pushed a profile change from another
machine and want this one to pick it up without dropping out of chat.

## What it does

In order:

1. **Loads the profile.** Resolution order: `--profile` arg →
   `CHIMERA_PROFILE` env → `~/.config/chimera/profile.yaml` →
   chimera-shipped default.
2. **`git pull --ff-only`** the dotfiles repo declared in the profile.
3. **Re-applies symlinks** declared under `dotfiles.symlinks`. Existing
   correct symlinks are left alone (idempotent). Real files at a
   declared destination get backed up to `.bak.<ts>` rather than
   clobbered.
4. **Re-registers MCP servers** with Claude Code at user scope. Skips
   servers Claude already lists (use `force=True` to override).
5. **Re-writes `~/.claude/settings.json` hooks** (only if the profile
   has `install_claude_hooks: true`). Hook command paths are derived
   from the local chimera install — that's why this step runs
   per-machine instead of being symlinked.

## When to use

- After pushing a profile or dotfiles change from another machine.
- After Claude Code's settings.json drifts (e.g., you opened the
  settings UI and clicked something).
- After a chimera self-update that changed hook scripts.
- Periodically as a sanity check — it's idempotent, no-op when clean.

## Not for

- **First-run setup on a brand-new machine.** Chimera's MCP server
  needs to be installed locally for this slash command to exist. Use
  the CLI one-liner instead:
  ```
  uvx --from git+https://github.com/<you>/chimera chimera bootstrap \
      --profile https://raw.githubusercontent.com/<you>/dotfiles/main/chimera-profile.yaml
  ```

## Args

- `profile` (optional) — explicit path or URL to a profile YAML.
  Overrides the env/file/default resolution.
- `force` (default `false`) — re-register MCP servers even if Claude
  already lists them. Use when you've changed a server's `command`
  in the profile and want the new body to take effect.

## Invokes

`mcp__chimera__chimera_configure(profile, force)` — returns a report
with per-operation status (✨ created, 🔄 updated, · unchanged,
— skipped, ✗ failed) and a summary tail.
