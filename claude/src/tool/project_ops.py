"""Apply project .claude/ templates (base + per-project overrides) to a target project.

Layering (higher overwrites lower):
  1. projects/_base/.claude/
  2. projects/overrides/<project_name>/.claude/

Files NEVER touched in target:
  - .claude/settings.json (owned by the active Khimaira installer)
  - .claude/settings.local.json (per-machine)
  - Claude runtime state such as scratch/, worktrees/, checkpoints/, and mailbox/
"""

from __future__ import annotations

import filecmp
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .paths import PROJECTS_BASE, PROJECTS_OVERRIDES

console = Console()

# Paths passed to _is_protected are relative to the target .claude directory.
# Keep this list in that namespace.  The former entries included a leading
# ``.claude/`` and therefore protected nothing.
PROTECTED_PATHS = {
    "settings.json",
    "settings.local.json",
    "scratch",
    "worktrees",
    "checkpoints",
    "mailbox",
    "routines/.state",
    "agent-registry.json",
    "agent-memory-local",
    "first-run",
    "assistant-daemon-state.json",
}
PRIVATE_CONTEXT_MARKER = ".private-context"


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


def _refuse_private_context_project(project_path: Path) -> None:
    marker = PROJECTS_OVERRIDES / project_path.name / PRIVATE_CONTEXT_MARKER
    if not marker.is_file():
        return
    console.print(
        f"[red]error[/] {project_path.name!r} uses the private context store; "
        "legacy public-template apply/diff is disabled. Use "
        f"`tool project context-diff {project_path}` or `context-apply` instead."
    )
    raise SystemExit(2)


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
    if "__pycache__" in Path(rel_path).parts or rel_path.startswith(
        "settings.json.bak-"
    ):
        return True
    return any(
        rel_path == path or rel_path.startswith(path + "/") for path in PROTECTED_PATHS
    )


def _iter_target_files(target_claude: Path):
    """Yield target files without descending into protected runtime trees."""

    for root, dirs, files in os.walk(target_claude):
        root_path = Path(root)
        root_rel = root_path.relative_to(target_claude)
        kept_dirs: list[str] = []
        for dirname in dirs:
            rel = (root_rel / dirname).as_posix()
            if not _is_protected(rel):
                kept_dirs.append(dirname)
        dirs[:] = kept_dirs
        for filename in files:
            path = root_path / filename
            rel = path.relative_to(target_claude).as_posix()
            if not _is_protected(rel):
                yield path, rel


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
        for p, rel in _iter_target_files(target_claude):
            if rel in template_rels:
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
    _refuse_private_context_project(project_path)

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
    _refuse_private_context_project(project_path)

    ops = _plan(project_path)
    _print_plan(ops, title=f"diff — {project_path} vs template")
