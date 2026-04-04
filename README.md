# dotfiles

Neovim (LazyVim) + Kitty terminal configs. Vesper theme, transparent, Ghostly Teal accents.

## What's Included

```
nvim/           # LazyVim config — Avante (Claude), Neogit, Diffview, DAP, Pyright, vtsls
kitty/          # Kitty terminal config
install.sh      # Symlink script
```

## New Machine Setup

### 1. Prerequisites

Install these first:

```bash
# Arch
sudo pacman -S neovim kitty git nodejs npm
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ubuntu/Debian
sudo apt install neovim kitty git nodejs npm
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS
brew install neovim kitty git node uv
```

Python is managed by `uv`, not system packages. `uv` handles Python installation, virtual environments, and dependencies.

### 2. Clone & Install

```bash
git clone git@github.com:fsocietydisobey/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

This backs up any existing configs (→ `.bak`) and symlinks the dotfiles into `~/.config/`.

### 3. First Launch

```bash
nvim
```

On first launch, Lazy.nvim will auto-install all plugins. Wait for it to finish, then quit and reopen.

After plugins install:
- `:Mason` — install LSP servers (pyright, vtsls, etc.)
- `:Lazy update` — ensure everything is current
- `:checkhealth` — verify no issues

### 4. Avante (Claude AI)

Avante needs your Anthropic API key. Set it in your shell profile:

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Claude Code CLI

```bash
# Arch (AUR)
yay -S claude-code

# npm (any platform)
npm install -g @anthropic-ai/claude-code
```

The `lazyvim.plugins.extras.ai.claudecode` extra is already enabled — it bridges Claude Code into Neovim automatically.

## Keeping Configs in Sync

After changing a config on any machine:

```bash
cd ~/dotfiles
git add -A
git commit -m "update: description of change"
git push
```

On other machines:

```bash
cd ~/dotfiles
git pull
```

Since configs are symlinked, pulling updates them everywhere instantly — no re-install needed.

## Neovim Extras Enabled

These LazyVim extras are pre-configured in `lazyvim.json`:

- **AI:** claudecode
- **Editor:** mini-diff
- **Formatting:** black, prettier
- **Languages:** docker, json, markdown, python, sql, tailwind, typescript, yaml
- **Linting:** eslint
- **Utilities:** dot, gh, gitui

## Key Bindings Reference

See `~/dev/nvim-notes/COMMANDS.md` and `~/dev/nvim-notes/CURSOR-FLOW.md` for the full reference (not included in this repo — those are local working notes).
