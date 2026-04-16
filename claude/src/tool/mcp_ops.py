"""MCP server lifecycle and introspection.

`tool mcp list`     — show all registered servers + reachability check.
`tool mcp reindex`  — run Séance reindex_changed on one or all indexed projects.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .config import load_seance_indexed_projects, load_servers

console = Console()


# ── `tool mcp list` ───────────────────────────────────────────────────────────


def _server_status(launcher: str, source_path: str | None) -> tuple[str, str]:
    """Return (status_color, status_text) for a server."""
    if shutil.which(launcher) is None:
        return "red", f"launcher '{launcher}' not on PATH"
    if source_path:
        if not Path(source_path).exists():
            return "red", f"source missing: {source_path}"
        return "green", "local source OK"
    return "cyan", "remote / no local source"


def list_servers() -> None:
    servers = load_servers()
    if not servers:
        console.print("[yellow]no servers registered[/]")
        return

    table = Table(title="MCP servers", show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Scope")
    table.add_column("Launcher")
    table.add_column("Source")
    table.add_column("Status")

    for name, s in sorted(servers.items()):
        color, status = _server_status(s.launcher, s.source_path)
        source_display = s.source or "—"
        if len(source_display) > 50:
            source_display = source_display[:47] + "..."
        table.add_row(
            f"[bold]{name}[/]",
            s.scope,
            s.launcher,
            source_display,
            f"[{color}]{status}[/]",
        )

    console.print(table)


# ── `tool mcp reindex` ────────────────────────────────────────────────────────


def _run_seance_reindex(project_name: str, project_path: str) -> tuple[bool, str]:
    """Invoke seance reindex on one project. Returns (success, output)."""
    seance_dir = Path.home() / "dev" / "seance"
    if not seance_dir.exists():
        return False, f"seance source not at {seance_dir}"

    try:
        result = subprocess.run(
            [
                "uv",
                "--directory",
                str(seance_dir),
                "run",
                "seance",
                "reindex",
                project_path,
                "--name",
                project_name,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout).strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout after 5 minutes"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def reindex(project: str | None = None) -> None:
    """Run seance reindex on one project (by name) or all (if project is None/'all')."""
    indexed = load_seance_indexed_projects()
    if not indexed:
        console.print("[yellow]no indexed projects declared in servers.toml[/]")
        return

    targets: dict[str, str]
    if project is None or project == "all":
        targets = indexed
    else:
        if project not in indexed:
            console.print(
                f"[red]error[/] '{project}' not in seance_indexed_projects. "
                f"Known: {', '.join(sorted(indexed))}"
            )
            raise SystemExit(2)
        targets = {project: indexed[project]}

    for name, path in targets.items():
        if not Path(path).exists():
            console.print(f"[yellow]skip[/] {name}: path missing ({path})")
            continue
        console.print(f"[bold cyan]→[/] {name} ({path})")
        ok, output = _run_seance_reindex(name, path)
        if ok:
            console.print(f"  [green]✓[/] {output or 'reindexed'}")
        else:
            console.print(f"  [red]✗[/] {output}")
