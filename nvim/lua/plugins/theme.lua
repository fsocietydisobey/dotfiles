-- Theme configuration
--
-- Active theme: Catppuccin Mocha
-- Also installed (try with `:colorscheme <name>`):
--   - tokyonight, tokyonight-night, tokyonight-storm, tokyonight-moon
--   - rose-pine, rose-pine-moon, rose-pine-main
--   - kanagawa, kanagawa-dragon (previous theme)
--
-- To revert to kanagawa-dragon: copy theme.lua.kanagawa.bak over this file.

return {
  -- Catppuccin (active)
  {
    "catppuccin/nvim",
    name = "catppuccin",
    lazy = false,
    priority = 1000,
    config = function()
      require("catppuccin").setup({
        flavour = "mocha",
        transparent_background = true,
        term_colors = true,
        no_italic = false,
        styles = {
          comments = { "italic" },
          conditionals = { "italic" },
        },
        integrations = {
          cmp = true,
          gitsigns = true,
          treesitter = true,
          telescope = { enabled = true },
          mason = true,
          neotree = true,
          notify = true,
          which_key = true,
          lsp_trouble = true,
          native_lsp = {
            enabled = true,
            virtual_text = {
              errors = { "italic" },
              hints = { "italic" },
              warnings = { "italic" },
              information = { "italic" },
            },
            underlines = {
              errors = { "underline" },
              hints = { "underline" },
              warnings = { "underline" },
              information = { "underline" },
            },
          },
        },
        custom_highlights = function(colors)
          return {
            -- Keep all floating/sidebar backgrounds transparent
            NormalFloat = { bg = "NONE" },
            FloatBorder = { bg = "NONE", fg = "#3a3a4a" },
            NeoTreeNormal = { bg = "NONE" },
            NeoTreeNormalNC = { bg = "NONE" },
            NeoTreeEndOfBuffer = { bg = "NONE" },
            NeoTreeWinSeparator = { bg = "NONE", fg = "#3a3a4a" },
            -- Lighter window borders
            WinSeparator = { fg = "#3a3a4a", bg = "NONE" },
            VertSplit = { fg = "#3a3a4a", bg = "NONE" },
            -- Avante
            AvanteNormal = { bg = "NONE" },
            AvanteInput = { bg = "NONE" },
            -- Gutter
            SignColumn = { bg = "NONE" },
            LineNr = { bg = "NONE" },
          }
        end,
      })

      vim.cmd.colorscheme("catppuccin-mocha")
    end,
  },

  -- Tokyo Night (installed for testing)
  {
    "folke/tokyonight.nvim",
    lazy = true,
    opts = {
      style = "night",
      transparent = true,
      styles = {
        sidebars = "transparent",
        floats = "transparent",
      },
    },
  },

  -- Rose Pine (installed for testing)
  {
    "rose-pine/neovim",
    name = "rose-pine",
    lazy = true,
    opts = {
      variant = "main",
      styles = {
        transparency = true,
        italic = true,
      },
    },
  },

  -- Kanagawa (previous theme — kept available for fallback)
  {
    "rebelot/kanagawa.nvim",
    lazy = true,
    opts = {
      transparent = true,
      theme = "dragon",
    },
  },
}
