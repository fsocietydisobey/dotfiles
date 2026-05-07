# /chimera-monitor — Local LangGraph monitor daemon

Manages the chimera-monitor daemon — a local FastAPI dashboard that
auto-discovers LangGraph projects from chimera's roots registry, surfaces
topology + threads + state, and serves a React UI on `127.0.0.1:8740`.

## Usage

`/chimera-monitor <subcommand>` where subcommand is one of:

- `start` — daemonize the server and open the dashboard. No-op if already running.
- `stop`  — SIGTERM the daemon (SIGKILL after 5s if needed).
- `status` — report PID + URL + log path.

Default port `8740`, override with `CHIMERA_MONITOR_PORT`.
Logs at `~/.local/state/chimera/monitor.log`.

## Steps

1. Run `uv run chimera monitor <subcommand>` from the chimera repo (or any directory if chimera is installed globally).
2. Surface the daemon's stdout verbatim — it's a one-liner per command. Don't summarize.
3. If `start` reports the daemon didn't stay alive, tail `~/.local/state/chimera/monitor.log` and surface the last 30 lines.

## Notes

- Backend deps live in the `chimera[monitor]` extra. If the user hasn't installed them, the daemon prints `Install monitor extras: uv pip install 'chimera[monitor]'` and exits — pass that hint through.
- Phase 1 only supports AsyncPostgresSaver checkpoints; SQLite + Qdrant land in Phase 2.
- The daemon survives Claude Code restarts — it's a real fork, not an MCP child.
- 127.0.0.1 binding is asserted at startup. Refuse any user request to bind elsewhere.
