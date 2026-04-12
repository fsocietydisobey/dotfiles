return {
  "iamcco/markdown-preview.nvim",
  opts = function()
    vim.g.mkdp_preview_options = {
      disable_sync_scroll = 0,
      disable_filename = 0,
    }
    -- mkdp_highlight_css targets the full page (not just .markdown-body)
    vim.g.mkdp_highlight_css = vim.fn.stdpath("config") .. "/styles/markdown.css"

    -- Keep preview windows open when you leave the markdown buffer in nvim.
    -- Default is 1 (auto-close on buffer leave), which makes it impossible
    -- to have multiple previews open simultaneously or switch nvim tabs
    -- while a preview stays visible. Set to 0 so previews are only closed
    -- by closing the browser window or running :MarkdownPreviewStop.
    vim.g.mkdp_auto_close = 0

    -- Open all markdown previews in a DEDICATED Firefox profile named
    -- `markdown-preview`, which isolates them from your personal browsing.
    -- Behavior:
    --   - First <leader>mp:  Firefox spawns a new instance using the
    --                        markdown-preview profile → one window appears
    --                        with the first preview tab.
    --   - Subsequent <leader>mp:  Firefox sees the markdown-preview profile
    --                             is already running → sends the URL via the
    --                             remote protocol → it opens as a NEW TAB in
    --                             the existing markdown-preview window.
    --   - Your default profile (personal tabs) stays completely untouched.
    --
    -- Profile was created with: firefox -CreateProfile "markdown-preview"
    -- To delete it later: firefox -P (opens profile manager)
    vim.cmd([[
      function! OpenMarkdownPreviewInProfile(url)
        silent execute "!firefox -P markdown-preview " . shellescape(a:url) . " &"
        redraw!
      endfunction
    ]])
    vim.g.mkdp_browserfunc = "OpenMarkdownPreviewInProfile"
  end,
}
