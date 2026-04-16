# ~/dotfiles/claude/ — Personal Claude + Cursor workstation config

Source of truth for Claude Code and Cursor configuration. See `~/dev/WORKSTATION_TOOLING.md` for the full design plan.

## Layout

```
claude/
├── CLAUDE.md              # symlinked to ~/.claude/CLAUDE.md by ~/dotfiles/install.sh
├── commands/              # symlinked to ~/.claude/commands
├── rules/                 # symlinked to ~/.claude/rules
│   ├── personal/          # not synced to Cursor — personal working style
│   ├── engineering/       # synced to Cursor as .mdc by `tool sync`
│   └── mcp/               # MCP tool usage guides (transitional — will move into server instructions)
├── mcp/
│   └── servers.toml       # declarative MCP server registry (both Claude and Cursor generated from here)
├── projects/
│   ├── _base/             # common .claude/ skeleton for any project
│   └── overrides/         # per-project additions (jeevy_portal, etc.)
├── scripts/
│   ├── sync.sh            # wrapper around `tool sync`
│   └── doctor.sh          # wrapper around `tool doctor`
├── src/tool/              # Python CLI source
├── bin/tool               # CLI entry point
└── pyproject.toml
```

## The `tool` CLI

Install in editable mode (once):

```bash
cd ~/dotfiles/claude
uv pip install -e .
```

Then:

```bash
tool sync              # regenerate ~/.claude.json, ~/.cursor/mcp.json, ~/.cursor/rules/*.mdc from sources
tool sync --dry-run    # preview changes without writing
tool doctor            # lint for drift, stale paths, exposed secrets
tool mcp list          # list registered MCP servers + reachability
tool mcp reindex       # run Séance reindex_changed on all indexed projects
tool project apply <path>    # apply _base + overrides to a project's .claude/
tool project diff  <path>    # show drift between project's .claude/ and template
```

## How generated files work

| File | Source of truth | Written by |
|---|---|---|
| `~/.claude/CLAUDE.md` | `~/dotfiles/claude/CLAUDE.md` | symlink (install.sh) |
| `~/.claude/rules/**/*.md` | `~/dotfiles/claude/rules/**` | symlink (install.sh) — directory symlink |
| `~/.claude/commands/**` | `~/dotfiles/claude/commands/**` | symlink (install.sh) |
| `~/.claude.json` `mcpServers` block | `mcp/servers.toml` | `tool sync` (surgical patch, never touches other fields) |
| `~/.cursor/mcp.json` | `mcp/servers.toml` | `tool sync` |
| `~/.cursor/rules/*.mdc` | `rules/engineering/*.md` | `tool sync` (adds frontmatter, rewrites .md links to .mdc) |

## First-time setup on a new machine

```bash
git clone <your-dotfiles-repo> ~/dotfiles
cd ~/dotfiles
./install.sh             # creates ~/.claude/{CLAUDE.md,rules,commands} symlinks
cd claude
uv pip install -e .      # installs the `tool` CLI
tool sync                # populates ~/.claude.json mcpServers + ~/.cursor/{mcp.json,rules/}
tool doctor              # verify no drift
```
