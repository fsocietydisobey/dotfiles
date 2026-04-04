return {
  -- The "Magit" for Neovim (Better than Cursor's Git UI)
  {
    "NeogitOrg/neogit",
    dependencies = { "nvim-lua/plenary.nvim", "sindrets/diffview.nvim", "nvim-telescope/telescope.nvim" },
    config = true,
    keys = {
      { "<leader>gs", "<cmd>Neogit<cr>", desc = "Git Status (Full UI)" },
    },
  },
  -- The ultimate Diff & Conflict tool
  {
    "sindrets/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewFileHistory" },
    keys = {
      { "<leader>gd", "<cmd>DiffviewOpen<cr>", desc = "Git Diff (Project)" },
      { "<leader>gh", "<cmd>DiffviewFileHistory %<cr>", desc = "Git File History" },
    },
  },
}
