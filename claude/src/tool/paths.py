"""Canonical filesystem paths used across the CLI."""

from __future__ import annotations

from pathlib import Path

HOME = Path.home()

# Dotfiles (source of truth)
DOTFILES = HOME / "dotfiles" / "claude"
RULES_SRC = DOTFILES / "rules"
RULES_PERSONAL = RULES_SRC / "personal"
RULES_ENGINEERING = RULES_SRC / "engineering"
RULES_MCP = RULES_SRC / "mcp"
MCP_SERVERS_TOML = DOTFILES / "mcp" / "servers.toml"
PROJECTS_BASE = DOTFILES / "projects" / "_base"
PROJECTS_OVERRIDES = DOTFILES / "projects" / "overrides"

# Targets (generated or symlinked)
CLAUDE_JSON = HOME / ".claude.json"
CLAUDE_DIR = HOME / ".claude"
CLAUDE_RULES = CLAUDE_DIR / "rules"  # symlink → RULES_SRC

CURSOR_DIR = HOME / ".cursor"
CURSOR_MCP_JSON = CURSOR_DIR / "mcp.json"
CURSOR_RULES = CURSOR_DIR / "rules"  # real directory — generated .mdc files
