-- Theme configuration
--
-- Active theme: vscode.nvim + Anysphere Dark overrides
-- Matches Cursor Dark "Anysphere Dark" (v0.0.3) exactly.
--
-- Key palette:
--   bg #181818  fg #E4E4E4  keywords #82D2CE  functions #efb080
--   strings #e394dc  variables #87C3FF  properties #AAA0FA
--   numbers #ebc88d  comments #636363 italic
--
-- Toggle with `:colorscheme catppuccin-mocha` to switch back.
-- Also installed: catppuccin-mocha, tokyonight, rose-pine, kanagawa

return {
  -- Tell LazyVim to use vscode instead of its default tokyonight
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "vscode",
    },
  },

  -- Anysphere Dark (Cursor Dark) — active
  {
    "Mofiqul/vscode.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      require("vscode").setup({
        style = "dark",
        transparent = false,
        italic_comments = true,
        underline_links = true,
        group_overrides = {
          -- Core backgrounds
          Normal         = { fg = "#E4E4E4", bg = "#181818" },
          NormalNC       = { bg = "#181818" },
          SignColumn     = { bg = "#181818" },
          LineNr         = { bg = "#181818", fg = "#636363" },
          CursorLineNr   = { bg = "#181818", fg = "#E4E4E4" },
          EndOfBuffer    = { bg = "#181818" },

          -- Floats / separators (sidebar is #141414 in Anysphere)
          WinSeparator   = { fg = "#3a3a3a", bg = "#181818" },
          VertSplit      = { fg = "#3a3a3a", bg = "#181818" },
          NormalFloat    = { bg = "#141414" },
          FloatBorder    = { bg = "#141414", fg = "#3a3a3a" },
          AvanteNormal   = { bg = "#141414" },
          AvanteInput    = { bg = "#141414" },

          -- Keywords → teal (#82D2CE)
          Keyword        = { fg = "#82D2CE" },
          Statement      = { fg = "#82D2CE" },
          Conditional    = { fg = "#82D2CE" },
          Repeat         = { fg = "#82D2CE" },
          Exception      = { fg = "#82D2CE" },
          StorageClass   = { fg = "#82D2CE" },
          Include        = { fg = "#82D2CE" },
          Define         = { fg = "#82D2CE" },
          ["@keyword"]            = { fg = "#82D2CE" },
          ["@keyword.function"]   = { fg = "#82D2CE" },
          ["@keyword.operator"]   = { fg = "#82D2CE" },
          ["@keyword.import"]     = { fg = "#82D2CE" },
          ["@conditional"]        = { fg = "#82D2CE" },
          ["@repeat"]             = { fg = "#82D2CE" },
          ["@exception"]          = { fg = "#82D2CE" },
          ["@storageclass"]       = { fg = "#82D2CE" },
          ["@include"]            = { fg = "#82D2CE" },
          ["@type.builtin"]       = { fg = "#82D2CE" },
          ["@constant.builtin"]   = { fg = "#82D2CE" },
          ["@boolean"]            = { fg = "#82D2CE" },

          -- Functions / types → orange (#efb080)
          Function       = { fg = "#efb080" },
          ["@function"]       = { fg = "#efb080" },
          ["@function.call"]  = { fg = "#efb080" },
          ["@function.macro"] = { fg = "#efb080" },
          ["@method"]         = { fg = "#efb080" },
          ["@method.call"]    = { fg = "#efb080" },
          ["@constructor"]    = { fg = "#efb080" },
          Type           = { fg = "#efb080" },
          ["@type"]           = { fg = "#efb080" },
          ["@namespace"]      = { fg = "#efb080" },

          -- Strings → pink/lavender (#e394dc)
          String         = { fg = "#e394dc" },
          Character      = { fg = "#e394dc" },
          ["@string"]         = { fg = "#e394dc" },
          ["@string.special"] = { fg = "#e394dc" },
          ["@character"]      = { fg = "#e394dc" },

          -- Numbers / constants → amber (#ebc88d)
          Number         = { fg = "#ebc88d" },
          Float          = { fg = "#ebc88d" },
          Constant       = { fg = "#ebc88d" },
          ["@number"]     = { fg = "#ebc88d" },
          ["@float"]      = { fg = "#ebc88d" },
          ["@constant"]   = { fg = "#ebc88d" },

          -- Comments → muted gray italic
          Comment        = { fg = "#636363", italic = true },
          ["@comment"]    = { fg = "#636363", italic = true },

          -- Variables → light blue (#87C3FF)
          ["@variable"]   = { fg = "#87C3FF" },

          -- Properties → lavender (#AAA0FA)
          ["@property"]   = { fg = "#AAA0FA" },
          ["@field"]      = { fg = "#AAA0FA" },

          -- Parameters → default fg
          ["@parameter"]  = { fg = "#d6d6dd" },
        },
      })
      vim.cmd.colorscheme("vscode")
    end,
  },

  -- Catppuccin Mocha (previous active — kept available)
  {
    "catppuccin/nvim",
    name = "catppuccin",
    lazy = true,
    priority = 900,
    opts = {
      flavour = "mocha",
      transparent_background = false,
      term_colors = true,
      no_italic = false,
      styles = {
        comments = { "italic" },
        conditionals = { "italic" },
      },
      integrations = {
        cmp = true,
        gitsigns = true,
        treesitter = true,
        telescope = { enabled = true },
        mason = true,
        neotree = true,
        notify = true,
        which_key = true,
        lsp_trouble = true,
        native_lsp = {
          enabled = true,
          virtual_text = {
            errors = { "italic" },
            hints = { "italic" },
            warnings = { "italic" },
            information = { "italic" },
          },
          underlines = {
            errors = { "underline" },
            hints = { "underline" },
            warnings = { "underline" },
            information = { "underline" },
          },
        },
      },
      custom_highlights = function(colors)
        local nvim_bg = "#222224"
        return {
          Normal = { bg = nvim_bg },
          NormalNC = { bg = nvim_bg },
          NormalFloat = { bg = nvim_bg },
          FloatBorder = { bg = nvim_bg, fg = "#3a3a4a" },
          NeoTreeNormal = { bg = nvim_bg },
          NeoTreeNormalNC = { bg = nvim_bg },
          NeoTreeEndOfBuffer = { bg = nvim_bg },
          NeoTreeWinSeparator = { bg = nvim_bg, fg = "#3a3a4a" },
          WinSeparator = { fg = "#3a3a4a", bg = nvim_bg },
          VertSplit = { fg = "#3a3a4a", bg = nvim_bg },
          AvanteNormal = { bg = nvim_bg },
          AvanteInput = { bg = nvim_bg },
          SignColumn = { bg = nvim_bg },
          LineNr = { bg = nvim_bg },
          EndOfBuffer = { bg = nvim_bg },
        }
      end,
    },
  },

  -- Tokyo Night (installed for testing)
  {
    "folke/tokyonight.nvim",
    lazy = true,
    opts = {
      style = "night",
      transparent = true,
      styles = {
        sidebars = "transparent",
        floats = "transparent",
      },
    },
  },

  -- Rose Pine (installed for testing)
  {
    "rose-pine/neovim",
    name = "rose-pine",
    lazy = true,
    opts = {
      variant = "main",
      styles = {
        transparency = true,
        italic = true,
      },
    },
  },

  -- Kanagawa (previous theme — kept available for fallback)
  {
    "rebelot/kanagawa.nvim",
    lazy = true,
    opts = {
      transparent = true,
      theme = "dragon",
    },
  },

  -- mini.icons — outlined style for default/fallback icons
  {
    "nvim-mini/mini.icons",
    opts = {
      default = {
        directory = { glyph = "󰉖", hl = "MiniIconsAzure" }, -- folder-outline
        file      = { glyph = "󰈤", hl = "MiniIconsGrey"  }, -- file-outline
        extension = { glyph = "󰈤", hl = "MiniIconsGrey"  }, -- file-outline
      },
    },
  },

  -- File icon colors — mapped to Anysphere Dark palette
  {
    "nvim-tree/nvim-web-devicons",
    lazy = true,
    config = function()
      -- Anysphere Dark colors:
      --   teal    #82D2CE  (keywords)
      --   orange  #efb080  (functions/types)
      --   pink    #e394dc  (strings)
      --   amber   #ebc88d  (numbers/constants)
      --   blue    #87C3FF  (variables)
      --   lavender #AAA0FA (properties)
      --   green   #a8cc7c  (directives/decorators)
      --   muted   #636363  (comments)
      require("nvim-web-devicons").setup({
        override_by_extension = {
          -- TypeScript
          ts  = { icon = "", color = "#87C3FF", name = "Ts" },
          tsx = { icon = "", color = "#87C3FF", name = "Tsx" },
          -- JavaScript
          js  = { icon = "", color = "#ebc88d", name = "Js" },
          jsx = { icon = "", color = "#ebc88d", name = "Jsx" },
          mjs = { icon = "", color = "#ebc88d", name = "Mjs" },
          cjs = { icon = "", color = "#ebc88d", name = "Cjs" },
          -- Python
          py  = { icon = "", color = "#82D2CE", name = "Py" },
          -- Lua
          lua = { icon = "", color = "#87C3FF", name = "Lua" },
          -- JSON / YAML / TOML
          json = { icon = "", color = "#ebc88d", name = "Json" },
          yml  = { icon = "", color = "#efb080", name = "Yml" },
          yaml = { icon = "", color = "#efb080", name = "Yaml" },
          toml = { icon = "", color = "#efb080", name = "Toml" },
          -- Markdown / text
          md   = { icon = "", color = "#E4E4E4", name = "Md" },
          mdx  = { icon = "", color = "#E4E4E4", name = "Mdx" },
          txt  = { icon = "󰈙", color = "#636363", name = "Txt" },
          -- CSS / SCSS / HTML
          css  = { icon = "", color = "#e394dc", name = "Css" },
          scss = { icon = "", color = "#e394dc", name = "Scss" },
          html = { icon = "", color = "#efb080", name = "Html" },
          -- Shell
          sh   = { icon = "", color = "#a8cc7c", name = "Sh" },
          bash = { icon = "", color = "#a8cc7c", name = "Bash" },
          zsh  = { icon = "", color = "#a8cc7c", name = "Zsh" },
          fish = { icon = "", color = "#a8cc7c", name = "Fish" },
          -- Rust / Go
          rs  = { icon = "", color = "#efb080", name = "Rs" },
          go  = { icon = "", color = "#82D2CE", name = "Go" },
          -- Config / env
          env     = { icon = "", color = "#ebc88d", name = "Env" },
          lock    = { icon = "󰌾", color = "#636363", name = "Lock" },
          gitignore = { icon = "", color = "#636363", name = "Gitignore" },
          -- Docker
          dockerfile = { icon = "", color = "#87C3FF", name = "Dockerfile" },
          -- SQL
          sql = { icon = "", color = "#AAA0FA", name = "Sql" },
        },
      })
    end,
  },
}
