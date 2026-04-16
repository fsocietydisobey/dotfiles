"""Load and resolve mcp/servers.toml into concrete MCP server entries."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from .paths import MCP_SERVERS_TOML


@dataclass
class ServerEntry:
    """One MCP server definition resolved from servers.toml."""

    name: str
    scope: str  # "global" | "project"
    launcher: str
    args: list[str]
    env: dict[str, str] = field(default_factory=dict)
    transport: str = "stdio"
    source: str | None = None  # "local:/path", "git+https://...", etc.
    projects: list[str] = field(default_factory=list)  # for project-scope servers

    @property
    def source_path(self) -> str | None:
        """Filesystem path for local: sources."""
        if self.source and self.source.startswith("local:"):
            return self.source.removeprefix("local:")
        return None

    @property
    def source_url(self) -> str | None:
        """Git URL for git+ sources."""
        if self.source and self.source.startswith("git+"):
            return self.source.removeprefix("git+")
        return None

    def resolve_args(self, project_dir: str | None = None) -> list[str]:
        """Substitute {source_path}, {source_url}, {project_dir} placeholders in args."""
        substitutions = {
            "source_path": self.source_path or "",
            "source_url": self.source_url or "",
            "project_dir": project_dir or "",
        }
        return [arg.format(**substitutions) for arg in self.args]

    def to_mcp_dict(self, project_dir: str | None = None) -> dict[str, Any]:
        """Render as an MCP server JSON object (the format Claude/Cursor consume)."""
        out: dict[str, Any] = {
            "type": self.transport,
            "command": self.launcher,
            "args": self.resolve_args(project_dir=project_dir),
        }
        # Only include env if non-empty — matches Claude Code's serialization
        if self.env:
            out["env"] = dict(self.env)
        return out


# Reserved top-level keys in servers.toml that are not MCP server definitions.
_RESERVED_KEYS = {"seance_indexed_projects"}


def load_servers(path: Path = MCP_SERVERS_TOML) -> dict[str, ServerEntry]:
    """Parse servers.toml and return {name: ServerEntry}."""
    with path.open("rb") as f:
        data = tomllib.load(f)

    servers: dict[str, ServerEntry] = {}
    for name, spec in data.items():
        if name in _RESERVED_KEYS:
            continue
        servers[name] = ServerEntry(
            name=name,
            scope=spec.get("scope", "global"),
            launcher=spec["launcher"],
            args=list(spec.get("args", [])),
            env=dict(spec.get("env", {})),
            transport=spec.get("transport", "stdio"),
            source=spec.get("source"),
            projects=list(spec.get("projects", [])),
        )
    return servers


def load_seance_indexed_projects(
    path: Path = MCP_SERVERS_TOML,
) -> dict[str, str]:
    """Return the seance_indexed_projects mapping (name → path)."""
    with path.open("rb") as f:
        data = tomllib.load(f)
    return dict(data.get("seance_indexed_projects", {}))


def global_servers(servers: dict[str, ServerEntry]) -> dict[str, ServerEntry]:
    return {name: s for name, s in servers.items() if s.scope == "global"}


def project_servers_for(
    servers: dict[str, ServerEntry], project_dir: str
) -> dict[str, ServerEntry]:
    return {
        name: s
        for name, s in servers.items()
        if s.scope == "project" and project_dir in s.projects
    }
