return {
  "iamcco/markdown-preview.nvim",
  opts = function()
    vim.g.mkdp_preview_options = {
      disable_sync_scroll = 0,
      disable_filename = 0,
    }
    -- mkdp_highlight_css targets the full page (not just .markdown-body)
    vim.g.mkdp_highlight_css = vim.fn.stdpath("config") .. "/styles/markdown.css"
  end,
}
