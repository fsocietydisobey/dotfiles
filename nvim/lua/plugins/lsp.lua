return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        -- Python / FastAPI Optimization
        pyright = {
          settings = {
            python = {
              analysis = {
                autoSearchPaths = true,
                useLibraryCodeForTypes = true,
                diagnosticMode = "workspace",
              },
            },
          },
        },
        -- TypeScript / React / Redux Optimization
        vtsls = {
          settings = {
            typescript = {
              suggest = { completeFunctionCalls = true },
              inlayHints = {
                parameterNames = { enabled = "all" },
                variableTypes = { enabled = true },
              },
            },
          },
        },
      },
    },
  },
}
