return {
  "datsfilipe/vesper.nvim",
  lazy = false,
  priority = 1000, -- Load this first
  config = function()
    require("vesper").setup({
      transparent = true,
      italics = {
        comments = true,
        keywords = true,
        functions = true,
        strings = false,
        variables = true,
      },
      variant = "main", -- The deep charcoal variant
    })

    -- Load the colorscheme
    vim.cmd.colorscheme("vesper")

    -- FORCE TRANSPARENCY (The Fix for Neo-tree & Avante)
    -- This autocmd ensures that every time the theme loads, we strip the bg
    vim.api.nvim_create_autocmd("ColorScheme", {
      pattern = "vesper",
      callback = function()
        local hl_groups = {
          "Normal", "NormalNC", "SignColumn", "StatusLine", "StatusLineNC",
          "WinSeparator", "VertSplit", "EndOfBuffer",
          "NeoTreeNormal", "NeoTreeNormalNC", "NeoTreeWinSeparator", "NeoTreeEndOfBuffer",
          "NvimTreeNormal", "NvimTreeNormalNC",
          "TabLine", "TabLineFill", "TabLineSel",
          "Pmenu", "FloatBorder", "NormalFloat",
          "AvanteNormal", "AvanteInput", -- Transparency for your AI sidebar
        }
        for _, group in ipairs(hl_groups) do
          vim.api.nvim_set_hl(0, group, { bg = "NONE", ctermbg = "NONE" })
        end
        -- Restore visible backgrounds for markdown code blocks
        vim.api.nvim_set_hl(0, "RenderMarkdownCode", { bg = "#1e1e2e" })
        vim.api.nvim_set_hl(0, "RenderMarkdownCodeInline", { bg = "#1e1e2e" })
      end,
    })
    
    -- Give markdown code blocks a visible background despite transparency
    vim.api.nvim_set_hl(0, "RenderMarkdownCode", { bg = "#1e1e2e" })
    vim.api.nvim_set_hl(0, "RenderMarkdownCodeInline", { bg = "#1e1e2e" })

    -- Trigger the autocmd immediately for the current session
    vim.cmd("doautocmd ColorScheme vesper")
  end,
}
