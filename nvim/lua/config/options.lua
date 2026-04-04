-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua

-- CursorHold fires after this many ms of inactivity. Default is 4000ms.
-- Lower = faster external file detection + LSP diagnostic refresh.
vim.opt.updatetime = 1000

-- Ensure terminal focus events are enabled (needed for FocusGained to fire)
vim.opt.termsync = true
