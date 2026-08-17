"""Portable, private per-project agent-context capture and restore.

The public dotfiles repository contains this mechanism, never the proprietary
payload.  Payloads live in an independent private Git repository (the context
store) and are selected by an explicit allowlist manifest.
"""

from __future__ import annotations

import filecmp
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml
from rich.console import Console
from rich.table import Table

console = Console()

MANIFEST_NAME = "manifest.yaml"
FILES_DIR = "files"
ARCHIVE_DIR = "archive"
EXCLUDE_BEGIN = "# BEGIN agent-context managed excludes"
EXCLUDE_END = "# END agent-context managed excludes"

DENIED_EXACT = {
    ".mcp.json",
    ".claude/settings.local.json",
    ".khimaira/context.auto.yaml",
}
DENIED_PREFIXES = {
    ".git",
    ".claude/scratch",
    ".claude/worktrees",
    ".claude/checkpoints",
    ".claude/mailbox",
    ".claude/routines/.state",
    ".claude/__pycache__",
}


class ContextError(RuntimeError):
    """Raised when a context operation would cross a safety boundary."""


@dataclass(frozen=True)
class Manifest:
    project: str
    managed: tuple[str, ...]
    archive: tuple[str, ...]
    excludes: tuple[str, ...]


@dataclass(frozen=True)
class FileOp:
    kind: str
    group: str
    rel_path: str
    source: Path | None
    target: Path | None


def default_store() -> Path:
    configured = os.environ.get("AGENT_CONTEXT_HOME", "~/agent-context")
    return Path(configured).expanduser()


def _safe_relative(raw: str) -> str:
    normalized = raw.strip().rstrip("/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ContextError(f"unsafe context path: {raw!r}")
    return path.as_posix()


def _is_denied(rel_path: str) -> bool:
    if rel_path in DENIED_EXACT:
        return True
    if any(
        rel_path == prefix or rel_path.startswith(prefix + "/")
        for prefix in DENIED_PREFIXES
    ):
        return True
    return any(
        part == "__pycache__" or part == ".env"
        for part in PurePosixPath(rel_path).parts
    )


def _project_store(store: Path, project: str) -> Path:
    return store.expanduser().resolve() / "projects" / project


def load_manifest(store: Path, project: str) -> Manifest:
    path = _project_store(store, project) / MANIFEST_NAME
    if not path.is_file():
        raise ContextError(f"context manifest not found: {path}")
    payload = yaml.safe_load(path.read_text()) or {}
    if payload.get("version") != 1:
        raise ContextError(f"unsupported context manifest version in {path}")
    declared_project = payload.get("project")
    if declared_project != project:
        raise ContextError(
            f"manifest project mismatch: expected {project!r}, found {declared_project!r}"
        )

    def paths_for(key: str, *, permit_archive: bool = False) -> tuple[str, ...]:
        values = payload.get(key, [])
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise ContextError(f"manifest {key!r} must be a list of paths")
        paths = tuple(_safe_relative(value) for value in values)
        if len(paths) != len(set(paths)):
            raise ContextError(f"manifest {key!r} contains duplicate paths")
        if not permit_archive:
            denied = [value for value in paths if _is_denied(value)]
            if denied:
                raise ContextError(f"manifest {key!r} contains denied paths: {denied}")
        return paths

    managed = paths_for("managed")
    archive = paths_for("archive", permit_archive=True)
    overlap = sorted(set(managed) & set(archive))
    if overlap:
        raise ContextError(f"paths cannot be both managed and archived: {overlap}")

    excludes = payload.get("excludes", [])
    if not isinstance(excludes, list) or not all(
        isinstance(value, str) for value in excludes
    ):
        raise ContextError("manifest 'excludes' must be a list of Git exclude patterns")
    excludes_tuple = tuple(value.strip() for value in excludes if value.strip())
    return Manifest(project, managed, archive, excludes_tuple)


def _assert_contained(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ContextError(f"path escapes its root: {path} (root {root})") from exc


def _files_under(root: Path, rel_path: str) -> dict[str, Path]:
    entry = root / rel_path
    if entry.is_symlink():
        raise ContextError(f"symlink context entries are not supported: {entry}")
    _assert_contained(entry, root)
    if not entry.exists():
        return {}
    if entry.is_file():
        return {rel_path: entry}

    found: dict[str, Path] = {}
    for path in entry.rglob("*"):
        if path.is_symlink():
            raise ContextError(f"symlink context entries are not supported: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if _is_denied(relative):
            continue
        found[relative] = path
    return found


def _plan_group(
    source_root: Path, target_root: Path, entries: tuple[str, ...], group: str
) -> list[FileOp]:
    ops: list[FileOp] = []
    for entry in entries:
        source_files = _files_under(source_root, entry)
        target_files = _files_under(target_root, entry)
        if not source_files:
            ops.append(
                FileOp("missing_source", group, entry, source_root / entry, None)
            )
            continue
        for rel_path, source in sorted(source_files.items()):
            target = target_root / rel_path
            if rel_path not in target_files:
                kind = "create"
            elif filecmp.cmp(source, target, shallow=False):
                kind = "same"
            else:
                kind = "update"
            ops.append(FileOp(kind, group, rel_path, source, target))
        for rel_path, target in sorted(target_files.items()):
            if rel_path not in source_files:
                ops.append(FileOp("target_only", group, rel_path, None, target))
    return ops


def capture_plan(project_path: Path, store: Path) -> list[FileOp]:
    project = project_path.expanduser().resolve()
    manifest = load_manifest(store, project.name)
    project_store = _project_store(store, project.name)
    return _plan_group(
        project, project_store / FILES_DIR, manifest.managed, "managed"
    ) + _plan_group(project, project_store / ARCHIVE_DIR, manifest.archive, "archive")


def apply_plan(project_path: Path, store: Path) -> list[FileOp]:
    project = project_path.expanduser().resolve()
    manifest = load_manifest(store, project.name)
    project_store = _project_store(store, project.name)
    return _plan_group(project_store / FILES_DIR, project, manifest.managed, "managed")


def _print_plan(ops: list[FileOp], title: str) -> None:
    kinds = ("create", "update", "same", "target_only", "missing_source")
    counts = {kind: sum(op.kind == kind for op in ops) for kind in kinds}
    table = Table(title=title, show_header=True)
    table.add_column("Kind")
    table.add_column("Count", justify="right")
    for kind in kinds:
        table.add_row(kind, str(counts[kind]))
    console.print(table)
    for op in ops:
        if op.kind != "same":
            console.print(f"  {op.kind:14s} [{op.group}] {op.rel_path}")


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{target.name}.", dir=target.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _execute(ops: list[FileOp]) -> None:
    missing = [op.rel_path for op in ops if op.kind == "missing_source"]
    if missing:
        raise ContextError(
            f"refusing partial operation; required source paths are missing: {missing}"
        )
    for op in ops:
        if op.kind in {"create", "update"}:
            assert op.source is not None and op.target is not None
            _atomic_copy(op.source, op.target)


def capture(project_path: Path, store: Path, *, write: bool = False) -> None:
    ops = capture_plan(project_path, store)
    _print_plan(ops, f"{'WRITE' if write else 'DRY RUN'} — capture private context")
    if write:
        _execute(ops)
        console.print("[green]✓[/] private context captured")


def apply(project_path: Path, store: Path, *, write: bool = False) -> None:
    ops = apply_plan(project_path, store)
    _print_plan(ops, f"{'WRITE' if write else 'DRY RUN'} — restore private context")
    if write:
        _execute(ops)
        console.print("[green]✓[/] private context restored")


def diff(project_path: Path, store: Path) -> None:
    ops = apply_plan(project_path, store)
    _print_plan(ops, "private context drift")


def _replace_exclude_block(existing: str, patterns: tuple[str, ...]) -> str:
    lines = existing.splitlines()
    retained: list[str] = []
    inside = False
    found_begin = False
    for line in lines:
        if line == EXCLUDE_BEGIN:
            if inside or found_begin:
                raise ContextError("duplicate managed exclude begin marker")
            inside = True
            found_begin = True
            continue
        if line == EXCLUDE_END:
            if not inside:
                raise ContextError("managed exclude end marker without begin marker")
            inside = False
            continue
        if not inside:
            retained.append(line)
    if inside:
        raise ContextError("unterminated managed exclude block")
    while retained and not retained[-1].strip():
        retained.pop()
    block = [EXCLUDE_BEGIN, *patterns, EXCLUDE_END]
    return "\n".join([*retained, "", *block]).lstrip("\n") + "\n"


def excludes(project_path: Path, store: Path, *, write: bool = False) -> None:
    project = project_path.expanduser().resolve()
    manifest = load_manifest(store, project.name)
    exclude_file = project / ".git" / "info" / "exclude"
    if not exclude_file.parent.is_dir():
        raise ContextError(f"project has no writable .git/info directory: {project}")
    current = exclude_file.read_text() if exclude_file.exists() else ""
    rendered = _replace_exclude_block(current, manifest.excludes)
    if rendered == current:
        console.print("[green]✓[/] managed Git excludes are current")
        return
    console.print(f"{'would update' if not write else 'updating'} {exclude_file}")
    if write:
        exclude_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", prefix=".exclude.", dir=exclude_file.parent, delete=False
        ) as handle:
            handle.write(rendered)
            temporary = Path(handle.name)
        os.replace(temporary, exclude_file)
        console.print("[green]✓[/] managed Git excludes updated")
