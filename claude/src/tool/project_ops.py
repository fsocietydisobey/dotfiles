"""Apply project .claude/ templates (base + per-project overrides) to a target project.

Layering (higher overwrites lower):
  1. projects/_base/.claude/
  2. projects/overrides/<project_name>/.claude/

Files NEVER touched in target:
  - .claude/settings.local.json (per-machine)
  - .claude/scratch/ (ephemeral)
  - Any path matching gitignored patterns in the target repo (if it's a git repo)
"""

from __future__ import annotations

import filecmp
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .paths import PROJECTS_BASE, PROJECTS_OVERRIDES

console = Console()

PROTECTED_PATHS = {
    ".claude/settings.local.json",
    ".claude/scratch",
}


@dataclass
class FileOp:
    """One operation during apply/diff."""

    kind: str  # "create" | "update" | "same" | "target_only" | "protected"
    rel_path: str
    source: Path | None = None
    target: Path | None = None


def _project_override_dir(project_name: str) -> Path:
    return PROJECTS_OVERRIDES / project_name / ".claude"


def _base_dir() -> Path:
    return PROJECTS_BASE / ".claude"


def _iter_template_files(project_name: str) -> list[tuple[Path, str]]:
    """Yield (source_path, rel_path_from_dot_claude) for every file the template would install.

    Later layers (overrides) take precedence over base. Uses a dict keyed by rel_path.
    """
    merged: dict[str, Path] = {}

    base = _base_dir()
    if base.exists():
        for p in base.rglob("*"):
            if p.is_file() and p.name != ".gitkeep":
                rel = p.relative_to(base).as_posix()
                merged[rel] = p

    override = _project_override_dir(project_name)
    if override.exists():
        for p in override.rglob("*"):
            if p.is_file() and p.name != ".gitkeep":
                rel = p.relative_to(override).as_posix()
                merged[rel] = p

    return [(src, rel) for rel, src in sorted(merged.items())]


def _is_protected(rel_path: str) -> bool:
    for p in PROTECTED_PATHS:
        if rel_path == p or rel_path.startswith(p + "/"):
            return True
    return False


def _plan(project_path: Path) -> list[FileOp]:
    """Compute what would happen if we apply the template to project_path."""
    project_name = project_path.name
    target_claude = project_path / ".claude"
    ops: list[FileOp] = []
    template_rels: set[str] = set()

    for src, rel in _iter_template_files(project_name):
        template_rels.add(rel)
        target = target_claude / rel

        if _is_protected(rel):
            ops.append(FileOp("protected", rel, src, target))
            continue

        if not target.exists():
            ops.append(FileOp("create", rel, src, target))
            continue

        if filecmp.cmp(src, target, shallow=False):
            ops.append(FileOp("same", rel, src, target))
        else:
            ops.append(FileOp("update", rel, src, target))

    # Files in target that aren't in the template — leave alone, but report
    if target_claude.exists():
        for p in target_claude.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(target_claude).as_posix()
            if _is_protected(rel) or rel in template_rels:
                continue
            ops.append(FileOp("target_only", rel, None, p))

    return ops


def _print_plan(ops: list[FileOp], title: str) -> None:
    counts = {"create": 0, "update": 0, "same": 0, "target_only": 0, "protected": 0}
    for op in ops:
        counts[op.kind] += 1

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Kind")
    table.add_column("Count")
    table.add_row("[green]create[/]", str(counts["create"]))
    table.add_row("[yellow]update[/]", str(counts["update"]))
    table.add_row("[dim]same[/]", str(counts["same"]))
    table.add_row("[cyan]target only[/]", str(counts["target_only"]))
    table.add_row("[magenta]protected[/]", str(counts["protected"]))
    console.print(table)

    for op in ops:
        if op.kind == "same":
            continue
        color = {
            "create": "green",
            "update": "yellow",
            "target_only": "cyan",
            "protected": "magenta",
        }.get(op.kind, "white")
        console.print(f"  [{color}]{op.kind:12s}[/] {op.rel_path}")


# ── Public entry points ───────────────────────────────────────────────────────


def apply(project_path: Path, write: bool = False) -> None:
    """Apply template to project. Dry-run unless write=True."""
    project_path = project_path.expanduser().resolve()
    if not project_path.is_dir():
        console.print(f"[red]error[/] not a directory: {project_path}")
        raise SystemExit(2)

    project_name = project_path.name
    override_dir = _project_override_dir(project_name)
    base = _base_dir()
    if not override_dir.exists() and not base.exists():
        console.print(
            f"[yellow]warning[/] no template for '{project_name}' "
            f"(checked {override_dir} and {base})"
        )
        raise SystemExit(1)

    ops = _plan(project_path)
    mode = "[green]WRITE[/]" if write else "[yellow]DRY RUN[/]"
    _print_plan(ops, title=f"{mode} — apply template to {project_path}")

    if not write:
        console.print("\n[dim]Re-run with --write to actually apply.[/]")
        return

    target_claude = project_path / ".claude"
    target_claude.mkdir(exist_ok=True)
    for op in ops:
        if op.kind not in ("create", "update"):
            continue
        op.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(op.source, op.target)
        # Preserve executable bit for hook scripts
        if op.source.suffix == ".sh":
            op.target.chmod(0o755)
    console.print(f"\n[green]✓[/] applied template to {target_claude}")


def diff(project_path: Path) -> None:
    """Show drift between project's .claude/ and template."""
    project_path = project_path.expanduser().resolve()
    if not project_path.is_dir():
        console.print(f"[red]error[/] not a directory: {project_path}")
        raise SystemExit(2)

    ops = _plan(project_path)
    _print_plan(ops, title=f"diff — {project_path} vs template")
