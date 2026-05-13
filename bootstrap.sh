#!/usr/bin/env bash
# bootstrap.sh — one-command setup for the khimaira portable agent ecosystem.
#
# Usage on a fresh machine:
#
#   1. Cloned-first:
#        git clone git@github.com:fsocietydisobey/dotfiles.git ~/dotfiles
#        cd ~/dotfiles && ./bootstrap.sh
#
#   2. One-liner (clones dotfiles itself):
#        curl -fsSL https://raw.githubusercontent.com/fsocietydisobey/dotfiles/main/bootstrap.sh | bash
#
# What it does, in order:
#   - verify prereqs (git, uv, optionally claude + npm)
#   - clone ~/dotfiles if not already present (curl-piped flow)
#   - clone ~/dev/khimaira if not already present
#   - uv sync --all-packages inside khimaira (load-bearing — keeps
#     .venv/bin/khimaira in place, the workspace-member entry script
#     that bare `uv sync` drops)
#   - add the khimaira workspace venv to PATH in the right shell rc
#   - exec `khimaira bootstrap` with the profile (does everything else:
#     dotfiles symlinks, sibling repo clones, MCP server registration,
#     hooks setup, supervisor install, SPA build).
#
# Idempotent — safe to re-run after a partial failure. Each step skips
# itself when already complete.

set -euo pipefail

# Platform check up front — Windows-native is unsupported (symlink
# permissions, no POSIX shell). WSL2 falls through as Linux.
case "$(uname -s 2>/dev/null)" in
    Linux|Darwin) ;;
    MINGW*|CYGWIN*|MSYS*)
        printf "\033[31m[bootstrap] Windows-native isn't supported.\033[0m\n"
        printf "[bootstrap] Run this inside WSL2 instead: the script + khimaira + profile\n"
        printf "[bootstrap] all work transparently in a WSL Ubuntu/Debian environment.\n"
        exit 1
        ;;
esac

note() { printf "\033[34m[bootstrap]\033[0m %s\n" "$*"; }
warn() { printf "\033[33m[bootstrap] ⚠ %s\033[0m\n" "$*" >&2; }
fail() { printf "\033[31m[bootstrap] ✗ %s\033[0m\n" "$*" >&2; exit 1; }

# Configurable defaults — override via env if you want a non-standard layout
DOTFILES_REPO="${DOTFILES_REPO:-git@github.com:fsocietydisobey/dotfiles.git}"
KHIMAIRA_REPO="${KHIMAIRA_REPO:-git@github.com:fsocietydisobey/khimaira.git}"
DOTFILES_DEFAULT="$HOME/dotfiles"
KHIMAIRA_DEV_PATH="$HOME/dev/khimaira"

# ---------------------------------------------------------------------------
# 1. Prereqs
# ---------------------------------------------------------------------------
note "checking prereqs"

command -v git >/dev/null 2>&1 \
    || fail "git not on PATH. Install it and re-run."

if ! command -v uv >/dev/null 2>&1; then
    fail "uv not on PATH. Install it:
  curl -LsSf https://astral.sh/uv/install.sh | sh
then open a new shell and re-run this script."
fi

# claude CLI is needed for `claude mcp add` (registering MCP servers).
# Soft-warn instead of fail — bootstrap will skip MCP registration
# gracefully if claude isn't installed.
if ! command -v claude >/dev/null 2>&1; then
    warn "claude CLI not on PATH — MCP server registration will be skipped."
    warn "Install Claude Code first, then re-run this script to register MCPs."
fi

# npm is needed for the khimaira-monitor SPA build. Soft-warn — dashboard
# UI won't be available without it but the daemon's JSON API still works.
command -v npm >/dev/null 2>&1 \
    || warn "npm not on PATH — khimaira monitor dashboard SPA won't build (API still works)."

# ---------------------------------------------------------------------------
# 2. Find or clone dotfiles
# ---------------------------------------------------------------------------
# Detect whether we're being run from inside an existing dotfiles checkout
# vs. piped via curl. The script's own location is the strongest signal.
if [ -n "${BASH_SOURCE[0]:-}" ] && \
   [ -f "$(dirname "${BASH_SOURCE[0]}")/khimaira-profile.yaml" ]
then
    DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    note "running from existing dotfiles checkout: $DOTFILES_DIR"
else
    DOTFILES_DIR="$DOTFILES_DEFAULT"
    if [ ! -d "$DOTFILES_DIR/.git" ]; then
        note "cloning dotfiles → $DOTFILES_DIR"
        git clone "$DOTFILES_REPO" "$DOTFILES_DIR"
    else
        note "dotfiles already cloned at $DOTFILES_DIR — pulling latest"
        git -C "$DOTFILES_DIR" pull --ff-only
    fi
fi

PROFILE="$DOTFILES_DIR/khimaira-profile.yaml"
[ -f "$PROFILE" ] || fail "profile not found at $PROFILE — does your dotfiles repo ship it?"

# ---------------------------------------------------------------------------
# 3. Clone + sync khimaira
# ---------------------------------------------------------------------------
if [ ! -d "$KHIMAIRA_DEV_PATH/.git" ]; then
    note "cloning khimaira → $KHIMAIRA_DEV_PATH"
    mkdir -p "$(dirname "$KHIMAIRA_DEV_PATH")"
    git clone "$KHIMAIRA_REPO" "$KHIMAIRA_DEV_PATH"
fi

# --all-packages is load-bearing on uv workspaces: a bare `uv sync` only
# installs the root project's deps and drops member entry-point scripts.
# Specifically that's where .venv/bin/khimaira comes from — without
# --all-packages, the khimaira binary disappears and the rest of this
# script can't shell out to it.
note "syncing khimaira workspace (--all-packages)"
(cd "$KHIMAIRA_DEV_PATH" && uv sync --all-packages)

[ -x "$KHIMAIRA_DEV_PATH/.venv/bin/khimaira" ] \
    || fail "uv sync didn't produce $KHIMAIRA_DEV_PATH/.venv/bin/khimaira. Bailing — please investigate before retrying."

# ---------------------------------------------------------------------------
# 4. Put workspace venv on PATH for this shell and persist for new ones
# ---------------------------------------------------------------------------
export PATH="$KHIMAIRA_DEV_PATH/.venv/bin:$PATH"

# Pick the right shell rc file. Falls back to a printed instruction if we
# can't infer the user's shell (e.g. nix-darwin with $SHELL unset).
SHELL_NAME="$(basename "${SHELL:-$0}")"
case "$SHELL_NAME" in
    zsh)   RCFILE="$HOME/.zshrc" ;;
    bash)  RCFILE="$HOME/.bashrc" ;;
    fish)  RCFILE="$HOME/.config/fish/config.fish" ;;
    *)     RCFILE="" ;;
esac

PATH_EXPORT='export PATH="$HOME/dev/khimaira/.venv/bin:$PATH"'
PATH_MARKER='dev/khimaira/.venv/bin'

if [ -z "$RCFILE" ]; then
    warn "unrecognized shell '$SHELL_NAME' — add this to your shell rc manually:"
    warn "  $PATH_EXPORT"
elif [ "$SHELL_NAME" = "fish" ]; then
    # fish uses different syntax + can be appended idempotently via grep
    mkdir -p "$(dirname "$RCFILE")"
    if ! grep -q "$PATH_MARKER" "$RCFILE" 2>/dev/null; then
        note "appending PATH to $RCFILE"
        {
            echo ''
            echo '# khimaira workspace venv (added by dotfiles bootstrap)'
            echo 'set -gx PATH $HOME/dev/khimaira/.venv/bin $PATH'
        } >> "$RCFILE"
    fi
else
    if ! grep -q "$PATH_MARKER" "$RCFILE" 2>/dev/null; then
        note "appending PATH to $RCFILE"
        {
            echo ''
            echo '# khimaira workspace venv (added by dotfiles bootstrap)'
            echo "$PATH_EXPORT"
        } >> "$RCFILE"
    fi
fi

# ---------------------------------------------------------------------------
# 5. Run khimaira bootstrap with the profile
# ---------------------------------------------------------------------------
# --force handles the case where this is a re-bootstrap and a previous
# partial run left a systemd unit / launchd plist whose contents drifted
# from the current template.
note "running khimaira bootstrap (--force, profile=$PROFILE)"
"$KHIMAIRA_DEV_PATH/.venv/bin/khimaira" bootstrap --force --profile "$PROFILE"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
note "bootstrap complete."
note ""
note "next steps:"
note "  1. Open a new terminal (so PATH update is picked up)"
note "  2. Run \`claude\` to verify the MCP servers are connected"
note "  3. \`khimaira sync\` or /khimaira-configure to pull profile updates later"
