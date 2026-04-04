return {
  "xiyaowong/transparent.nvim",
  lazy = false,
  config = function()
    require("transparent").setup({
      extra_groups = {
        -- The big ones for explorers
        "NormalFloat",
        "NvimTreeNormal",
        "NvimTreeNormalNC",
        "NeoTreeNormal",
        "NeoTreeNormalNC",
        "NeoTreeWinSeparator",
        "NeoTreeEndOfBuffer",
        -- For the AI sidebar (Avante)
        "AvanteNormal",
        "AvanteInput",
      },
      exclude_groups = {}, -- Leave empty to ensure everything is cleared
    })
    
    -- Force clear the background just in case the theme reapplies it
    vim.api.nvim_set_hl(0, "NeoTreeNormal", { bg = "NONE", ctermbg = "NONE" })
    vim.api.nvim_set_hl(0, "NeoTreeNormalNC", { bg = "NONE", ctermbg = "NONE" })
  end,
}
