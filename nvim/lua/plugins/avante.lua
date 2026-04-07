return {
  "yetone/avante.nvim",
  event = "VeryLazy",
  lazy = false,
  version = false, -- Set this to false to always pull the latest changes
  opts = {
    provider = "claude",
    providers = {
      claude = {
      	endpoint = "https://api.anthropic.com",
      	model = "claude-opus-4-6",
      	enable_caching = true,
	extra_request_body = {
      	  max_tokens = 8192,
	  temperature = 0,
	}
      },
    },
    -- This is the "Cursor" magic: it builds a map of your repo
    repo_map = {
      enabled = true,
      depth = 4, -- Deeper = better awareness of nested feature modules (jeevy_portal has deeply nested domains)
    },
    behaviour = {
      auto_suggestions = false, -- Set to true if you want Copilot-style ghost text
      support_paste_from_clipboard = true,
    },
    mappings = {
      diff = {
        ours = "co",
        theirs = "ct",
        all_theirs = "ca",
        both = "cb",
        cursor = "cc",
        next = "]x",
        prev = "[x",
      },
      suggestion = {
        accept = "<M-l>",
        confirm = "<M-j>",
        undo = "<M-h>",
        next = "<M-]>",
        prev = "<M-[>",
      },
      jump = {
        next = "]]",
        prev = "[[",
      },
      submit = {
        normal = "<CR>",
        insert = "<C-s>",
      },
    },
  },
  -- These are the "Engine" parts Avante needs to run
  build = "make",
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
    "stevearc/dressing.nvim",
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    "nvim-tree/nvim-web-devicons", 
    {
      -- Support for image pasting (handy for debugging UI)
      "HakonHarnes/img-clip.nvim",
      event = "VeryLazy",
      opts = {
        default = {
          embed_image_as_base64 = false,
          prompt_for_file_name = false,
          drag_and_drop = { insert_mode = true },
        },
      },
    },
  },
}
