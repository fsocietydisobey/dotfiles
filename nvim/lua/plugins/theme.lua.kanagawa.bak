return {
  "rebelot/kanagawa.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    require("kanagawa").setup({
      transparent = true,
      theme = "dragon", -- dark, warm variant
      colors = {
        theme = {
          all = {
            ui = {
              bg_gutter = "NONE",
            },
          },
        },
      },
      overrides = function(colors)
        return {
          -- Make all floating/sidebar backgrounds transparent
          NormalFloat = { bg = "NONE" },
          FloatBorder = { bg = "NONE" },
          NormalDark = { bg = "NONE" },
          LazyNormal = { bg = "NONE" },
          NeoTreeNormal = { bg = "NONE" },
          NeoTreeNormalNC = { bg = "NONE" },
          NeoTreeEndOfBuffer = { bg = "NONE" },
          NeoTreeWinSeparator = { bg = "NONE", fg = "#3a3a4a" },
          -- Lighter window borders (dark but visible)
          WinSeparator = { fg = "#3a3a4a", bg = "NONE" },
          VertSplit = { fg = "#3a3a4a", bg = "NONE" },
          FloatBorder = { bg = "NONE", fg = "#3a3a4a" },
          AvanteNormal = { bg = "NONE" },
          AvanteInput = { bg = "NONE" },
          -- Markdown code blocks
          RenderMarkdownCode = { bg = colors.theme.ui.bg_p1 },
          RenderMarkdownCodeInline = { bg = colors.theme.ui.bg_p1 },
        }
      end,
    })

    vim.cmd.colorscheme("kanagawa")
  end,
}
