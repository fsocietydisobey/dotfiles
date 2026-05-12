# /heal — Auto-detect chimera setup drift and apply fixes

Self-reflect, find what's broken, fix it. Equivalent of `chimera doctor`
+ `chimera bootstrap` in one shot, scoped to chimera's own setup
health (not your project code).

## What it does

Three phases:

1. **Introspect** — runs the same checks `chimera doctor` does. Loads
   the active chimera profile, reports drift, checks daemon liveness.
2. **Plan** — prints each item that needs fixing.
3. **Apply** — runs `chimera bootstrap` to resolve profile drift; with
   `--aggressive`, also starts the daemon if it's down.

Idempotent — re-running on a healthy machine is a no-op.

## When to use

- You feel like "something's off" with chimera (MCP tools missing,
  hooks not firing, daemon flaky).
- You've pushed a profile change from another machine and want this
  one to catch up without thinking.
- Periodically as a maintenance hygiene step.
- After re-bootstrapping a venv or running `uv sync` and suspecting
  workspace entry-points got dropped.

## Args

- `profile` (optional) — path or URL to a chimera profile YAML.
  Defaults to standard resolution: `CHIMERA_PROFILE` env →
  `~/.config/chimera/profile.yaml` → chimera-shipped baseline.
- `dry_run` — print the planned fixes without applying anything
  (alias for `chimera doctor --profile <p>`).
- `aggressive` — also apply fixes with side effects beyond chimera
  state: start the daemon if down, install supervisor if missing.
  Default is conservative.
- `force` — pass `--force` through to bootstrap (re-register MCPs,
  overwrite stale supervisor units).

## Invokes

`mcp__chimera__chimera_configure` for the bootstrap+sync application
under the hood, just like `/chimera-configure`. The difference: heal
also restarts the daemon if it's down (with `--aggressive`) and
reports a clearer diagnosis-then-fix summary.

## When NOT to use

- To fix code in your project — heal only touches chimera's own setup.
- To debug daemon crashes — use `chimera monitor status` and
  `journalctl --user -u chimera-monitor` instead.
- For "what would change?" without applying — use
  `chimera bootstrap --check` (heal's `dry_run` mode does the same).
