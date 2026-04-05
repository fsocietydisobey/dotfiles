return {
  {
    "nvim-lualine/lualine.nvim",
    event = "VeryLazy",
    opts = {
      options = {
        theme = "auto",
        component_separators = "|",
        section_separators = "",
      },
      sections = {
        lualine_a = { { "mode", color = { bg = "#1e4a60", fg = "#e5e5ea", gui = "bold" } } },
      },
    },
  },
}
