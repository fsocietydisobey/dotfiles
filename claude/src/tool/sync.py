"""Generate Claude/Cursor config files from source of truth in dotfiles.

`sync` reads:
  - mcp/servers.toml (MCP server registry)
  - rules/engineering/*.md (Cursor-synced rules)

`sync` writes:
  - ~/.claude.json mcpServers block (surgical patch — other keys preserved)
  - ~/.cursor/mcp.json (fully regenerated)
  - ~/.cursor/rules/*.mdc (generated from rules/engineering/*.md with frontmatter)
"""

from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from .config import ServerEntry, global_servers, load_servers
from .paths import (
    CLAUDE_JSON,
    CURSOR_MCP_JSON,
    CURSOR_RULES,
    RULES_ENGINEERING,
)

console = Console()


@dataclass
class SyncResult:
    """Summary of changes `sync` intends to make (dry-run) or has made."""

    claude_json_changed: bool = False
    cursor_mcp_changed: bool = False
    mdc_created: list[str] = None
    mdc_updated: list[str] = None
    mdc_removed: list[str] = None

    def __post_init__(self):
        if self.mdc_created is None:
            self.mdc_created = []
        if self.mdc_updated is None:
            self.mdc_updated = []
        if self.mdc_removed is None:
            self.mdc_removed = []

    @property
    def any_changes(self) -> bool:
        return (
            self.claude_json_changed
            or self.cursor_mcp_changed
            or bool(self.mdc_created or self.mdc_updated or self.mdc_removed)
        )


# ── ~/.claude.json surgical patch ─────────────────────────────────────────────


def _render_claude_mcp_block(servers: dict[str, ServerEntry]) -> dict[str, Any]:
    """Render the `mcpServers` block for ~/.claude.json."""
    return {name: s.to_mcp_dict() for name, s in servers.items()}


def sync_claude_json(
    servers: dict[str, ServerEntry], write: bool = True
) -> bool:
    """Patch ~/.claude.json's mcpServers block in place. Returns True if changed.

    Critical: this file contains OAuth state, migration flags, session refs.
    We ONLY touch the `mcpServers` key. Everything else is preserved byte-for-byte.
    """
    if not CLAUDE_JSON.exists():
        console.print(f"[yellow]warning[/] {CLAUDE_JSON} does not exist — skipping")
        return False

    data = json.loads(CLAUDE_JSON.read_text())
    current = data.get("mcpServers", {})
    desired = _render_claude_mcp_block(global_servers(servers))

    if current == desired:
        return False

    if write:
        backup = CLAUDE_JSON.with_suffix(f".json.bak-{int(time.time())}")
        shutil.copy2(CLAUDE_JSON, backup)
        console.print(f"[dim]backup:[/] {backup}")
        data["mcpServers"] = desired
        CLAUDE_JSON.write_text(json.dumps(data, indent=2))

    return True


# ── ~/.cursor/mcp.json full regeneration ──────────────────────────────────────


def _render_cursor_mcp_json(servers: dict[str, ServerEntry]) -> dict[str, Any]:
    """Render ~/.cursor/mcp.json content. Cursor uses a slightly different shape
    — no "type" field, just command/args/env."""
    out: dict[str, Any] = {"mcpServers": {}}
    for name, s in global_servers(servers).items():
        entry: dict[str, Any] = {
            "command": s.launcher,
            "args": s.resolve_args(),
        }
        if s.env:
            entry["env"] = dict(s.env)
        out["mcpServers"][name] = entry
    return out


def sync_cursor_mcp_json(
    servers: dict[str, ServerEntry], write: bool = True
) -> bool:
    """Regenerate ~/.cursor/mcp.json. Returns True if content changed."""
    desired = _render_cursor_mcp_json(servers)
    current = json.loads(CURSOR_MCP_JSON.read_text()) if CURSOR_MCP_JSON.exists() else None

    if current == desired:
        return False

    if write:
        CURSOR_MCP_JSON.parent.mkdir(parents=True, exist_ok=True)
        if CURSOR_MCP_JSON.exists():
            backup = CURSOR_MCP_JSON.with_suffix(f".json.bak-{int(time.time())}")
            shutil.copy2(CURSOR_MCP_JSON, backup)
            console.print(f"[dim]backup:[/] {backup}")
        CURSOR_MCP_JSON.write_text(json.dumps(desired, indent=2) + "\n")
        # Keep 600 perms since Cursor may consume secrets via env
        CURSOR_MCP_JSON.chmod(0o600)

    return True


# ── Cursor .mdc rule generation ───────────────────────────────────────────────


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _derive_description(md_text: str, fallback_name: str) -> str:
    """Pull a one-liner description from the source .md.

    Priority:
      1. Explicit `description:` in existing frontmatter
      2. First H1 heading
      3. Filename (title-cased)
    """
    m = _FRONTMATTER_RE.match(md_text)
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("description:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")

    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return fallback_name.replace("-", " ").replace("_", " ").title()


def _rewrite_md_links(content: str) -> str:
    """Rewrite inline references like `error-handling.md` → `error-handling.mdc`
    so cross-rule references work in Cursor."""
    return re.sub(r"\b([a-z0-9_-]+)\.md\b", r"\1.mdc", content)


def _strip_existing_frontmatter(md_text: str) -> str:
    """Remove an existing YAML frontmatter block (if present) before wrapping."""
    m = _FRONTMATTER_RE.match(md_text)
    if m:
        return md_text[m.end() :]
    return md_text


def _render_mdc(md_text: str, name: str) -> str:
    """Transform an engineering .md into a Cursor .mdc."""
    description = _derive_description(md_text, name)
    body = _strip_existing_frontmatter(md_text)
    body = _rewrite_md_links(body)
    return (
        f"---\n"
        f"description: {description}\n"
        f"alwaysApply: true\n"
        f"---\n\n"
        f"{body.lstrip()}"
    )


def sync_cursor_rules(
    write: bool = True,
) -> tuple[list[str], list[str], list[str]]:
    """Regenerate ~/.cursor/rules/*.mdc from rules/engineering/*.md.

    Returns (created, updated, removed) filename lists.
    """
    sources = {p.stem: p for p in RULES_ENGINEERING.glob("*.md") if p.is_file()}
    CURSOR_RULES.mkdir(parents=True, exist_ok=True)
    existing = {p.stem: p for p in CURSOR_RULES.glob("*.mdc") if p.is_file()}

    created: list[str] = []
    updated: list[str] = []
    removed: list[str] = []

    for name, src in sources.items():
        target = CURSOR_RULES / f"{name}.mdc"
        desired = _render_mdc(src.read_text(), name)
        current = target.read_text() if target.exists() else None

        if current == desired:
            continue

        if target.exists():
            updated.append(f"{name}.mdc")
        else:
            created.append(f"{name}.mdc")

        if write:
            target.write_text(desired)

    # Remove orphans — .mdc files whose source .md no longer exists
    for name, target in existing.items():
        if name not in sources:
            removed.append(f"{name}.mdc")
            if write:
                target.unlink()

    return created, updated, removed


# ── Orchestrator ──────────────────────────────────────────────────────────────


def run_sync(write: bool = True) -> SyncResult:
    servers = load_servers()

    result = SyncResult()
    result.claude_json_changed = sync_claude_json(servers, write=write)
    result.cursor_mcp_changed = sync_cursor_mcp_json(servers, write=write)
    created, updated, removed = sync_cursor_rules(write=write)
    result.mdc_created = created
    result.mdc_updated = updated
    result.mdc_removed = removed
    return result


def print_sync_report(result: SyncResult, dry_run: bool) -> None:
    mode = "[yellow]DRY RUN[/]" if dry_run else "[green]WRITE[/]"
    console.print(f"\n{mode} — sync report\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Target")
    table.add_column("Change")
    table.add_row(
        "~/.claude.json (mcpServers)",
        "[yellow]would update[/]" if result.claude_json_changed and dry_run
        else ("[green]updated[/]" if result.claude_json_changed else "[dim]unchanged[/]"),
    )
    table.add_row(
        "~/.cursor/mcp.json",
        "[yellow]would update[/]" if result.cursor_mcp_changed and dry_run
        else ("[green]updated[/]" if result.cursor_mcp_changed else "[dim]unchanged[/]"),
    )
    mdc_summary = (
        f"[green]+{len(result.mdc_created)}[/] / "
        f"[yellow]~{len(result.mdc_updated)}[/] / "
        f"[red]-{len(result.mdc_removed)}[/]"
    )
    table.add_row("~/.cursor/rules/*.mdc", mdc_summary)
    console.print(table)

    for label, items in (
        ("created", result.mdc_created),
        ("updated", result.mdc_updated),
        ("removed", result.mdc_removed),
    ):
        for item in items:
            color = {"created": "green", "updated": "yellow", "removed": "red"}[label]
            console.print(f"  [{color}]{label:8s}[/] {item}")

    if not result.any_changes:
        console.print("\n[green]✓[/] everything already in sync")
