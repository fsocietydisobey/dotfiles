-- mcphub.nvim — UI for browsing and debugging MCP servers from inside Neovim.
-- Reads the project-local .mcp.json (Claude Code format) so the same servers
-- registered for Claude Code show up here for inspection.
return {
  "ravitemer/mcphub.nvim",
  dependencies = {
    "nvim-lua/plenary.nvim",
  },
  build = "npm install -g mcp-hub@latest",
  cmd = { "MCPHub" }, -- lazy-load on :MCPHub
  keys = {
    { "<Leader>mh", "<cmd>MCPHub<cr>", desc = "MCP Hub (browse servers)" },
  },
  config = function()
    require("mcphub").setup({
      -- Point at the project-local .mcp.json when present.
      -- Falls back to the default location for other projects.
      config = (function()
        local project_config = vim.fn.getcwd() .. "/.mcp.json"
        if vim.fn.filereadable(project_config) == 1 then
          return project_config
        end
        return vim.fn.expand("~/.config/mcphub/servers.json")
      end)(),
    })
  end,
}
