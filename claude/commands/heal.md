# /heal — Auto-detect khimaira setup drift and apply fixes

Self-reflect, find what's broken, fix it. Equivalent of `khimaira doctor`
+ `khimaira bootstrap` in one shot, scoped to khimaira's own setup
health (not your project code).

## What it does

Three phases:

1. **Introspect** — runs the same checks `khimaira doctor` does. Loads
   the active khimaira profile, reports drift, checks daemon liveness.
2. **Plan** — prints each item that needs fixing.
3. **Apply** — runs `khimaira bootstrap` to resolve profile drift; with
   `--aggressive`, also starts the daemon if it's down.

Idempotent — re-running on a healthy machine is a no-op.

## When to use

- You feel like "something's off" with khimaira (MCP tools missing,
  hooks not firing, daemon flaky).
- You've pushed a profile change from another machine and want this
  one to catch up without thinking.
- Periodically as a maintenance hygiene step.
- After re-bootstrapping a venv or running `uv sync` and suspecting
  workspace entry-points got dropped.

## Args

- `profile` (optional) — path or URL to a khimaira profile YAML.
  Defaults to standard resolution: `KHIMAIRA_PROFILE` env →
  `~/.config/khimaira/profile.yaml` → khimaira-shipped baseline.
- `dry_run` — print the planned fixes without applying anything
  (alias for `khimaira doctor --profile <p>`).
- `aggressive` — also apply fixes with side effects beyond khimaira
  state: start the daemon if down, install supervisor if missing.
  Default is conservative.
- `force` — pass `--force` through to bootstrap (re-register MCPs,
  overwrite stale supervisor units).

## Invokes

`mcp__khimaira__khimaira_configure` for the bootstrap+sync application
under the hood, just like `/khimaira-configure`. The difference: heal
also restarts the daemon if it's down (with `--aggressive`) and
reports a clearer diagnosis-then-fix summary.

## When NOT to use

- To fix code in your project — heal only touches khimaira's own setup.
- To debug daemon crashes — use `khimaira monitor status` and
  `journalctl --user -u khimaira-monitor` instead.
- For "what would change?" without applying — use
  `khimaira bootstrap --check` (heal's `dry_run` mode does the same).
