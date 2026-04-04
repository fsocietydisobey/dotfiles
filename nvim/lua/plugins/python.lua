return {
  {
    "mfussenegger/nvim-dap",
    dependencies = {
      "rcarriga/nvim-dap-ui",
      "nvim-neotest/nvim-nio",
      "mfussenegger/nvim-dap-python",
    },
    -- DO NOT USE 'opts = {}' here, it triggers the fake .setup() call
    config = function()
      local dap = require("dap")
      local dapui = require("dapui")

      dapui.setup()

      -- Automatically open/close DAP UI
      dap.listeners.after.event_initialized["dapui_config"] = function()
        dapui.open()
      end
      dap.listeners.before.event_terminated["dapui_config"] = function()
        dapui.close()
      end
      dap.listeners.before.event_exited["dapui_config"] = function()
        dapui.close()
      end
    end,
  },
  {
    "mfussenegger/nvim-dap-python",
    ft = "python",
    config = function()
      -- This points to your uv-managed python or system python
      -- it helps find the 'debugpy' module
      require("dap-python").setup("python") 
    end,
  },
}
