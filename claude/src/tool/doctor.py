"""Read-only diagnostic — check config for drift, stale paths, exposed secrets, orphans."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .config import global_servers, load_servers
from .paths import (
    CLAUDE_JSON,
    CLAUDE_RULES,
    CURSOR_MCP_JSON,
    CURSOR_RULES,
    HOME,
    RULES_ENGINEERING,
    RULES_MCP,
    RULES_PERSONAL,
    RULES_SRC,
)
from .sync import _render_claude_mcp_block, _render_cursor_mcp_json, _render_mdc

console = Console()

# Regexes for common secret formats — used to detect literal keys in config files.
SECRET_PATTERNS = [
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{20,})\b"), "OpenAI/Anthropic-style key"),
    (re.compile(r"\b(lin_api_[A-Za-z0-9]{20,})\b"), "Linear API key"),
    (re.compile(r"\b(ghp_[A-Za-z0-9]{20,})\b"), "GitHub personal access token"),
    (re.compile(r"\b(gho_[A-Za-z0-9]{20,})\b"), "GitHub OAuth token"),
    (re.compile(r"\b(AIza[A-Za-z0-9_-]{20,})\b"), "Google API key"),
    (re.compile(r"\b(xox[a-z]-[A-Za-z0-9-]{20,})\b"), "Slack token"),
    (re.compile(r"(?i)\b(aws_secret_access_key)\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})"), "AWS secret"),
]


@dataclass
class Issue:
    """One diagnostic finding."""

    severity: str  # "error" | "warning" | "info"
    code: str
    message: str
    location: str = ""

    def render(self) -> str:
        symbol = {"error": "[red]✗[/]", "warning": "[yellow]⚠[/]", "info": "[cyan]ℹ[/]"}[self.severity]
        loc = f" [dim]({self.location})[/]" if self.location else ""
        return f"  {symbol} [{self.code}] {self.message}{loc}"


# ── Individual checks ─────────────────────────────────────────────────────────


def check_stale_paths(issues: list[Issue]) -> None:
    """Scan MCP config files for paths that don't exist or point outside $HOME."""
    targets = [CLAUDE_JSON, CURSOR_MCP_JSON]
    path_re = re.compile(r"/home/[a-zA-Z0-9_-]+(?:/[^\s\"']*)?")

    for target in targets:
        if not target.exists():
            continue
        text = target.read_text()
        found = set(path_re.findall(text))
        for p in found:
            # Only look at absolute /home paths
            if not p.startswith(str(HOME)):
                issues.append(
                    Issue(
                        "error",
                        "stale_path",
                        f"Path outside $HOME: {p}",
                        location=str(target),
                    )
                )
                continue
            if not Path(p).exists():
                issues.append(
                    Issue(
                        "warning",
                        "missing_path",
                        f"Path does not exist: {p}",
                        location=str(target),
                    )
                )


def check_exposed_secrets(issues: list[Issue]) -> None:
    """Scan MCP config files for literal API keys / secrets."""
    targets = [CLAUDE_JSON, CURSOR_MCP_JSON]
    for target in targets:
        if not target.exists():
            continue
        text = target.read_text()
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(
                    Issue(
                        "error",
                        "exposed_secret",
                        f"Literal {label} found — use ${{VAR}} env reference",
                        location=str(target),
                    )
                )


def check_mcp_drift(issues: list[Issue]) -> None:
    """Compare ~/.claude.json mcpServers and ~/.cursor/mcp.json against servers.toml."""
    servers = load_servers()

    # Claude drift
    if CLAUDE_JSON.exists():
        try:
            current_claude = json.loads(CLAUDE_JSON.read_text()).get("mcpServers", {})
            desired_claude = _render_claude_mcp_block(global_servers(servers))
            if current_claude != desired_claude:
                only_current = set(current_claude) - set(desired_claude)
                only_desired = set(desired_claude) - set(current_claude)
                differing = {
                    k for k in set(current_claude) & set(desired_claude) if current_claude[k] != desired_claude[k]
                }
                detail_parts = []
                if only_current:
                    detail_parts.append(f"in ~/.claude.json only: {', '.join(sorted(only_current))}")
                if only_desired:
                    detail_parts.append(f"in servers.toml only: {', '.join(sorted(only_desired))}")
                if differing:
                    detail_parts.append(f"content differs: {', '.join(sorted(differing))}")
                issues.append(
                    Issue(
                        "warning",
                        "claude_mcp_drift",
                        "~/.claude.json mcpServers differs from servers.toml — run `tool sync`. "
                        + " | ".join(detail_parts),
                        location=str(CLAUDE_JSON),
                    )
                )
        except json.JSONDecodeError as e:
            issues.append(Issue("error", "claude_json_invalid", f"Invalid JSON: {e}", str(CLAUDE_JSON)))

    # Cursor drift
    if CURSOR_MCP_JSON.exists():
        try:
            current_cursor = json.loads(CURSOR_MCP_JSON.read_text())
            desired_cursor = _render_cursor_mcp_json(servers)
            if current_cursor != desired_cursor:
                issues.append(
                    Issue(
                        "warning",
                        "cursor_mcp_drift",
                        "~/.cursor/mcp.json differs from servers.toml — run `tool sync`",
                        location=str(CURSOR_MCP_JSON),
                    )
                )
        except json.JSONDecodeError as e:
            issues.append(Issue("error", "cursor_json_invalid", f"Invalid JSON: {e}", str(CURSOR_MCP_JSON)))


def check_cursor_rules_drift(issues: list[Issue]) -> None:
    """Compare generated ~/.cursor/rules/*.mdc against what sync would produce."""
    sources = {p.stem: p for p in RULES_ENGINEERING.glob("*.md") if p.is_file()}
    existing = {p.stem: p for p in CURSOR_RULES.glob("*.mdc") if p.is_file()}

    for name, src in sources.items():
        target = CURSOR_RULES / f"{name}.mdc"
        if not target.exists():
            issues.append(
                Issue("warning", "missing_mdc", f"Missing Cursor rule: {name}.mdc", str(target))
            )
            continue
        desired = _render_mdc(src.read_text(), name)
        if target.read_text() != desired:
            issues.append(
                Issue("warning", "stale_mdc", f"Stale Cursor rule: {name}.mdc", str(target))
            )

    for name in existing.keys() - sources.keys():
        issues.append(
            Issue(
                "warning",
                "orphan_mdc",
                f"Orphan Cursor rule (no source .md): {name}.mdc",
                str(CURSOR_RULES / f"{name}.mdc"),
            )
        )


def check_rules_symlink(issues: list[Issue]) -> None:
    """Verify ~/.claude/rules is a symlink pointing to dotfiles."""
    if not CLAUDE_RULES.exists():
        issues.append(Issue("error", "missing_rules_symlink", "~/.claude/rules does not exist"))
        return
    if not CLAUDE_RULES.is_symlink():
        issues.append(
            Issue(
                "warning",
                "rules_not_symlink",
                "~/.claude/rules is not a symlink — run ~/dotfiles/install.sh",
            )
        )
        return
    resolved = CLAUDE_RULES.resolve()
    expected = RULES_SRC.resolve()
    if resolved != expected:
        issues.append(
            Issue(
                "warning",
                "rules_symlink_misaligned",
                f"~/.claude/rules → {resolved} (expected {expected})",
            )
        )


def check_mcp_sources(issues: list[Issue]) -> None:
    """For local: MCP sources, verify the directory exists."""
    servers = load_servers()
    for name, s in servers.items():
        if s.source_path and not Path(s.source_path).exists():
            issues.append(
                Issue(
                    "error",
                    "mcp_source_missing",
                    f"MCP '{name}' source does not exist: {s.source_path}",
                    location=str(MCP_SERVERS_TOML_IF_AVAILABLE),
                )
            )


# Module-level reference used in check_mcp_sources (defined here to allow patching/test)
from .paths import MCP_SERVERS_TOML as MCP_SERVERS_TOML_IF_AVAILABLE  # noqa: E402


def check_launchers(issues: list[Issue]) -> None:
    """Verify each server's launcher is on PATH."""
    import shutil

    servers = load_servers()
    missing_launchers: set[str] = set()
    for name, s in servers.items():
        if shutil.which(s.launcher) is None:
            missing_launchers.add(s.launcher)

    for launcher in sorted(missing_launchers):
        issues.append(
            Issue(
                "error",
                "launcher_missing",
                f"Launcher '{launcher}' not found on PATH",
            )
        )


# ── Orchestrator ──────────────────────────────────────────────────────────────


def run_doctor() -> int:
    """Run all checks, print report, return nonzero exit code if any errors."""
    issues: list[Issue] = []

    check_rules_symlink(issues)
    check_stale_paths(issues)
    check_exposed_secrets(issues)
    check_mcp_drift(issues)
    check_cursor_rules_drift(issues)
    check_mcp_sources(issues)
    check_launchers(issues)

    # Summary
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    if not issues:
        console.print("[green]✓[/] all checks passed")
        return 0

    table = Table(show_header=True, header_style="bold", title="doctor report")
    table.add_column("Severity")
    table.add_column("Count")
    table.add_row("[red]errors[/]", str(len(errors)))
    table.add_row("[yellow]warnings[/]", str(len(warnings)))
    table.add_row("[cyan]info[/]", str(len(infos)))
    console.print(table)

    for group, label in [(errors, "errors"), (warnings, "warnings"), (infos, "info")]:
        if not group:
            continue
        console.print(f"\n[bold]{label}:[/]")
        for issue in group:
            console.print(issue.render())

    return 1 if errors else 0
