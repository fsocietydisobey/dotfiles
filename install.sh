#!/usr/bin/env bash
# Symlink dotfiles into place. Run from the dotfiles repo root.
# Usage: ./install.sh

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

link() {
    local src="$DOTFILES_DIR/$1"
    local dest="$2"

    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        echo "Backing up existing $dest → ${dest}.bak"
        mv "$dest" "${dest}.bak"
    fi

    mkdir -p "$(dirname "$dest")"
    ln -sf "$src" "$dest"
    echo "Linked $dest → $src"
}

link "nvim"  "$HOME/.config/nvim"
link "kitty" "$HOME/.config/kitty"

echo ""
echo "Done. Open a new terminal and run 'nvim' to install plugins."
