-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua

-- Auto-reload ALL open buffers when files change externally (Claude Code, git, etc.)
-- checktime on the current buffer alone isn't enough — stale buffers mean stale LSP diagnostics.
vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter", "CursorHold", "CursorHoldI" }, {
  group = vim.api.nvim_create_augroup("auto_reload", { clear = true }),
  callback = function()
    -- Reload every loaded buffer, not just the current one
    for _, buf in ipairs(vim.api.nvim_list_bufs()) do
      if vim.api.nvim_buf_is_loaded(buf) and vim.bo[buf].buftype == "" then
        vim.api.nvim_buf_call(buf, function()
          vim.cmd("silent! checktime")
        end)
      end
    end
  end,
})
