from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tool.context_ops import (
    ContextError,
    apply,
    capture,
    capture_plan,
    excludes,
    load_manifest,
)
from tool.project_ops import _is_protected, _iter_target_files


def _write_manifest(store: Path, body: str) -> Path:
    project_store = store / "projects" / "jeevy_portal"
    project_store.mkdir(parents=True)
    (project_store / "manifest.yaml").write_text(body)
    return project_store


def test_project_runtime_paths_are_actually_protected(tmp_path: Path) -> None:
    claude = tmp_path / ".claude"
    (claude / "scratch").mkdir(parents=True)
    (claude / "scratch" / "state").write_text("runtime")
    (claude / "rules").mkdir()
    (claude / "rules" / "context.md").write_text("durable")

    assert _is_protected("settings.json")
    assert _is_protected("settings.local.json")
    assert _is_protected("worktrees/agent/.git")
    assert _is_protected("scratch/state")
    assert _is_protected("hooks/__pycache__/hook.cpython-313.pyc")
    assert _is_protected("settings.json.bak-123")
    assert not _is_protected("rules/context.md")
    assert [rel for _, rel in _iter_target_files(claude)] == ["rules/context.md"]


def test_capture_restore_and_archive_boundary(tmp_path: Path) -> None:
    store = tmp_path / "context-store"
    project = tmp_path / "jeevy_portal"
    (project / ".khimaira").mkdir(parents=True)
    (project / ".khimaira" / "context.yaml").write_text("project: jeevy\n")
    (project / "shared-docs" / "agent-context").mkdir(parents=True)
    (project / "shared-docs" / "agent-context" / "architecture.md").write_text("v1\n")
    (project / ".agents").mkdir()
    (project / ".agents" / "handoff.md").write_text("historical\n")
    _write_manifest(
        store,
        """\
version: 1
project: jeevy_portal
managed:
  - .khimaira/context.yaml
  - shared-docs/agent-context/
archive:
  - .agents/
excludes:
  - /.khimaira/
  - /shared-docs/agent-context/
  - /.agents/
""",
    )

    capture(project, store, write=True)
    assert (
        store / "projects/jeevy_portal/files/.khimaira/context.yaml"
    ).read_text() == ("project: jeevy\n")
    assert (
        store / "projects/jeevy_portal/archive/.agents/handoff.md"
    ).read_text() == "historical\n"

    (project / ".khimaira" / "context.yaml").unlink()
    (project / "shared-docs" / "agent-context" / "architecture.md").unlink()
    (project / ".agents" / "handoff.md").unlink()
    apply(project, store, write=True)

    assert (project / ".khimaira/context.yaml").read_text() == "project: jeevy\n"
    assert (project / "shared-docs/agent-context/architecture.md").read_text() == "v1\n"
    assert not (project / ".agents/handoff.md").exists()


def test_capture_fails_before_partial_write_when_source_missing(tmp_path: Path) -> None:
    store = tmp_path / "context-store"
    project = tmp_path / "jeevy_portal"
    project.mkdir()
    (project / "present.md").write_text("present")
    project_store = _write_manifest(
        store,
        """\
version: 1
project: jeevy_portal
managed: [present.md, missing.md]
archive: []
excludes: []
""",
    )

    with pytest.raises(ContextError, match="required source paths are missing"):
        capture(project, store, write=True)
    assert not (project_store / "files/present.md").exists()


@pytest.mark.parametrize(
    "managed",
    [
        "../escape.md",
        "/absolute.md",
        ".claude/settings.local.json",
        ".khimaira/context.auto.yaml",
    ],
)
def test_manifest_rejects_unsafe_or_generated_paths(
    tmp_path: Path, managed: str
) -> None:
    store = tmp_path / "context-store"
    _write_manifest(
        store,
        f"version: 1\nproject: jeevy_portal\nmanaged: [{managed!r}]\narchive: []\nexcludes: []\n",
    )
    with pytest.raises(ContextError):
        load_manifest(store, "jeevy_portal")


def test_managed_exclude_block_is_idempotent_and_preserves_user_lines(
    tmp_path: Path,
) -> None:
    store = tmp_path / "context-store"
    project = tmp_path / "jeevy_portal"
    exclude_file = project / ".git/info/exclude"
    exclude_file.parent.mkdir(parents=True)
    exclude_file.write_text("# user-owned\n*.local\n")
    _write_manifest(
        store,
        """\
version: 1
project: jeevy_portal
managed: []
archive: []
excludes: [/.claude/, /.khimaira/]
""",
    )

    excludes(project, store, write=True)
    first = exclude_file.read_text()
    excludes(project, store, write=True)
    second = exclude_file.read_text()

    assert first == second
    assert "# user-owned\n*.local" in first
    assert first.count("# BEGIN agent-context managed excludes") == 1
    assert "/.claude/" in first


def test_capture_plan_refuses_symlinks(tmp_path: Path) -> None:
    store = tmp_path / "context-store"
    project = tmp_path / "jeevy_portal"
    project.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    (project / "linked.md").symlink_to(outside)
    _write_manifest(
        store,
        """\
version: 1
project: jeevy_portal
managed: [linked.md]
archive: []
excludes: []
""",
    )

    with pytest.raises(ContextError, match="symlink"):
        capture_plan(project, store)


def test_private_context_marker_refuses_legacy_project_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tool import project_ops

    overrides = tmp_path / "overrides"
    project = tmp_path / "jeevy_portal"
    project.mkdir()
    marker = overrides / "jeevy_portal" / project_ops.PRIVATE_CONTEXT_MARKER
    marker.parent.mkdir(parents=True)
    marker.write_text("private\n")
    monkeypatch.setattr(project_ops, "PROJECTS_OVERRIDES", overrides)

    with pytest.raises(SystemExit) as raised:
        project_ops.apply(project, write=False)
    assert raised.value.code == 2
