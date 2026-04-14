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
      -- Solid nvim background (independent of kitty's color).
      -- Kitty terminals show their space gray; nvim keeps this dark color.
      local nvim_bg = "#181818"

      require("catppuccin").setup({
        flavour = "mocha",
        transparent_background = false,
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
            -- Force the dark nvim background everywhere the editor renders,
            -- so kitty's space gray shows only in actual terminal panes.
            Normal = { bg = nvim_bg },
            NormalNC = { bg = nvim_bg },
            NormalFloat = { bg = nvim_bg },
            FloatBorder = { bg = nvim_bg, fg = "#3a3a4a" },
            NeoTreeNormal = { bg = nvim_bg },
            NeoTreeNormalNC = { bg = nvim_bg },
            NeoTreeEndOfBuffer = { bg = nvim_bg },
            NeoTreeWinSeparator = { bg = nvim_bg, fg = "#3a3a4a" },
            -- Window borders
            WinSeparator = { fg = "#3a3a4a", bg = nvim_bg },
            VertSplit = { fg = "#3a3a4a", bg = nvim_bg },
            -- Avante
            AvanteNormal = { bg = nvim_bg },
            AvanteInput = { bg = nvim_bg },
            -- Gutter
            SignColumn = { bg = nvim_bg },
            LineNr = { bg = nvim_bg },
            EndOfBuffer = { bg = nvim_bg },
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
