-- Show dotfiles by default in file pickers and the snacks.explorer sidebar.
-- .env, .claude/, .cursor/, .gitignore, .mcp.json etc. should be visible.
return {
  -- Telescope: include hidden files in find_files and live_grep by default.
  {
    "nvim-telescope/telescope.nvim",
    opts = {
      defaults = {
        -- live_grep / grep_string: search inside hidden files too
        vimgrep_arguments = {
          "rg",
          "--color=never",
          "--no-heading",
          "--with-filename",
          "--line-number",
          "--column",
          "--smart-case",
          "--hidden",
          "--glob=!**/.git/*",
        },
      },
      pickers = {
        find_files = {
          hidden = true, -- show .env, .claude, etc.
          no_ignore = false, -- still respect .gitignore
          file_ignore_patterns = { "^.git/", "node_modules", "__pycache__" },
        },
      },
    },
  },

  -- Snacks picker / explorer: show hidden files by default.
  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          files = {
            hidden = true,
            ignored = false, -- respect .gitignore
          },
          explorer = {
            hidden = true,
            ignored = true, -- show git-ignored files (.env, .venv, etc.)
            -- Single-click to expand folders / open files.
            -- <LeftRelease> fires after vim has moved the cursor to the
            -- clicked row, so confirm acts on the right item.
            win = {
              list = {
                keys = {
                  ["<LeftRelease>"] = "confirm",
                },
              },
            },
          },
        },
      },
    },
  },
}
