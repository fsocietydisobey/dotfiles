"""Typer CLI entry point. Composes subcommands for sync, doctor, mcp, project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .sync import print_sync_report, run_sync

app = typer.Typer(
    help="Personal Claude/Cursor workstation orchestration.",
    no_args_is_help=True,
    add_completion=False,
)

mcp_app = typer.Typer(help="MCP server lifecycle and introspection.", no_args_is_help=True)
project_app = typer.Typer(help="Apply base + override templates to project .claude/ dirs.", no_args_is_help=True)

app.add_typer(mcp_app, name="mcp")
app.add_typer(project_app, name="project")

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"tool v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True, help="Show version."
    ),
) -> None:
    """Root callback — handles --version."""
    pass


# ── sync ──────────────────────────────────────────────────────────────────────


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview changes without writing."
    ),
) -> None:
    """Regenerate ~/.claude.json mcpServers, ~/.cursor/mcp.json, ~/.cursor/rules/*.mdc from sources."""
    result = run_sync(write=not dry_run)
    print_sync_report(result, dry_run=dry_run)


# ── doctor (Phase 4) ──────────────────────────────────────────────────────────


@app.command()
def doctor() -> None:
    """Lint for drift, stale paths, exposed secrets. Read-only."""
    from .doctor import run_doctor
    run_doctor()


# ── mcp (Phase 6) ─────────────────────────────────────────────────────────────


@mcp_app.command("list")
def mcp_list() -> None:
    """List registered MCP servers with reachability check."""
    from .mcp_ops import list_servers
    list_servers()


@mcp_app.command("reindex")
def mcp_reindex(
    project: str = typer.Argument(None, help="Project name or 'all' (default)."),
) -> None:
    """Run Séance reindex_changed on indexed projects."""
    from .mcp_ops import reindex
    reindex(project)


@mcp_app.command("reload-config")
def mcp_reload_config() -> None:
    """Re-sync config and remind to restart Claude/Cursor."""
    result = run_sync(write=True)
    print_sync_report(result, dry_run=False)
    console.print(
        "\n[yellow]Reminder:[/] restart Claude Code and Cursor to pick up MCP server changes."
    )


# ── project (Phase 5) ─────────────────────────────────────────────────────────


@project_app.command("apply")
def project_apply(
    path: Path = typer.Argument(..., help="Project root."),
    write: bool = typer.Option(False, "--write", help="Actually write (default is dry-run)."),
) -> None:
    """Apply _base + overrides to <path>/.claude/. Dry-run unless --write."""
    from .project_ops import apply as _apply
    _apply(path, write=write)


@project_app.command("diff")
def project_diff(
    path: Path = typer.Argument(..., help="Project root."),
) -> None:
    """Show drift between <path>/.claude/ and the template (_base + overrides)."""
    from .project_ops import diff as _diff
    _diff(path)
