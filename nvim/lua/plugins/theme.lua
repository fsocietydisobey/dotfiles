-- Theme configuration
--
-- Active theme: vscode.nvim + Space Grey overrides
-- Matches kitty space grey palette — warm mid-dark bg, soft grey fg, desaturated syntax.
--
-- Key palette:
--   bg #252528  fg #B0B4BF  keywords #6AAAA0  functions #C0A870
--   strings #9A80B0  variables #7090B8  properties #8A70A0
--   numbers #A89060  comments #555560 italic
--
-- Toggle with `:colorscheme catppuccin-mocha` to switch back.
-- Also installed: catppuccin-mocha, tokyonight, rose-pine, kanagawa

local BG      = "#252528"
local BG_FLOAT= "#1E1E22"
local FG      = "#B0B4BF"
local SPLIT   = "#3A3A42"
local LINENR  = "#505058"

-- Syntax — desaturated to match space grey kitty colors
local KW      = "#6AAAA0"  -- dusty teal   (keywords)
local FN      = "#C0A870"  -- warm amber   (functions/types)
local STR     = "#9A80B0"  -- dusty violet (strings)
local NUM     = "#A89060"  -- muted amber  (numbers/constants)
local VAR     = "#7090B8"  -- steel blue   (variables)
local PROP    = "#8A70A0"  -- dusty purple (properties)
local CMT     = "#555560"  -- muted grey   (comments)

return {
  -- Tell LazyVim to use vscode instead of its default tokyonight
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "vscode",
    },
  },

  -- Space Grey — active
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
          Normal         = { fg = FG,  bg = BG },
          NormalNC       = { bg = BG },
          SignColumn     = { bg = BG },
          LineNr         = { bg = BG, fg = LINENR },
          CursorLineNr   = { bg = BG, fg = FG },
          EndOfBuffer    = { bg = BG },

          -- Floats / separators
          WinSeparator   = { fg = SPLIT, bg = BG },
          VertSplit      = { fg = SPLIT, bg = BG },
          NormalFloat    = { bg = BG_FLOAT },
          FloatBorder    = { bg = BG_FLOAT, fg = SPLIT },
          AvanteNormal   = { bg = BG_FLOAT },
          AvanteInput    = { bg = BG_FLOAT },

          -- Keywords → dusty teal
          Keyword        = { fg = KW },
          Statement      = { fg = KW },
          Conditional    = { fg = KW },
          Repeat         = { fg = KW },
          Exception      = { fg = KW },
          StorageClass   = { fg = KW },
          Include        = { fg = KW },
          Define         = { fg = KW },
          ["@keyword"]            = { fg = KW },
          ["@keyword.function"]   = { fg = KW },
          ["@keyword.operator"]   = { fg = KW },
          ["@keyword.import"]     = { fg = KW },
          ["@conditional"]        = { fg = KW },
          ["@repeat"]             = { fg = KW },
          ["@exception"]          = { fg = KW },
          ["@storageclass"]       = { fg = KW },
          ["@include"]            = { fg = KW },
          ["@type.builtin"]       = { fg = KW },
          ["@constant.builtin"]   = { fg = KW },
          ["@boolean"]            = { fg = KW },

          -- Functions / types → warm amber
          Function       = { fg = FN },
          ["@function"]       = { fg = FN },
          ["@function.call"]  = { fg = FN },
          ["@function.macro"] = { fg = FN },
          ["@method"]         = { fg = FN },
          ["@method.call"]    = { fg = FN },
          ["@constructor"]    = { fg = FN },
          Type           = { fg = FN },
          ["@type"]           = { fg = FN },
          ["@namespace"]      = { fg = FN },

          -- Strings → dusty violet
          String         = { fg = STR },
          Character      = { fg = STR },
          ["@string"]         = { fg = STR },
          ["@string.special"] = { fg = STR },
          ["@character"]      = { fg = STR },

          -- Numbers / constants → muted amber
          Number         = { fg = NUM },
          Float          = { fg = NUM },
          Constant       = { fg = NUM },
          ["@number"]     = { fg = NUM },
          ["@float"]      = { fg = NUM },
          ["@constant"]   = { fg = NUM },

          -- Comments → muted grey italic
          Comment        = { fg = CMT, italic = true },
          ["@comment"]    = { fg = CMT, italic = true },

          -- Variables → steel blue
          ["@variable"]   = { fg = VAR },

          -- Properties → dusty purple
          ["@property"]   = { fg = PROP },
          ["@field"]      = { fg = PROP },

          -- Parameters → soft fg
          ["@parameter"]  = { fg = FG },
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
        local nvim_bg = "#252528"
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

  -- File icon colors — mapped to Space Grey palette
  {
    "nvim-tree/nvim-web-devicons",
    lazy = true,
    config = function()
      -- Space Grey colors:
      --   teal    #6AAAA0  (keywords)
      --   amber   #C0A870  (functions/types)
      --   violet  #9A80B0  (strings)
      --   steel   #7090B8  (variables)
      --   purple  #8A70A0  (properties)
      --   muted   #555560  (comments)
      require("nvim-web-devicons").setup({
        override_by_extension = {
          -- TypeScript
          ts  = { icon = "", color = "#7090B8", name = "Ts" },
          tsx = { icon = "", color = "#7090B8", name = "Tsx" },
          -- JavaScript
          js  = { icon = "", color = "#C0A870", name = "Js" },
          jsx = { icon = "", color = "#C0A870", name = "Jsx" },
          mjs = { icon = "", color = "#C0A870", name = "Mjs" },
          cjs = { icon = "", color = "#C0A870", name = "Cjs" },
          -- Python
          py  = { icon = "", color = "#6AAAA0", name = "Py" },
          -- Lua
          lua = { icon = "", color = "#7090B8", name = "Lua" },
          -- JSON / YAML / TOML
          json = { icon = "", color = "#C0A870", name = "Json" },
          yml  = { icon = "", color = "#C0A870", name = "Yml" },
          yaml = { icon = "", color = "#C0A870", name = "Yaml" },
          toml = { icon = "", color = "#C0A870", name = "Toml" },
          -- Markdown / text
          md   = { icon = "", color = "#B0B4BF", name = "Md" },
          mdx  = { icon = "", color = "#B0B4BF", name = "Mdx" },
          txt  = { icon = "󰈙", color = "#555560", name = "Txt" },
          -- CSS / SCSS / HTML
          css  = { icon = "", color = "#9A80B0", name = "Css" },
          scss = { icon = "", color = "#9A80B0", name = "Scss" },
          html = { icon = "", color = "#C0A870", name = "Html" },
          -- Shell
          sh   = { icon = "", color = "#6A9870", name = "Sh" },
          bash = { icon = "", color = "#6A9870", name = "Bash" },
          zsh  = { icon = "", color = "#6A9870", name = "Zsh" },
          fish = { icon = "", color = "#6A9870", name = "Fish" },
          -- Rust / Go
          rs  = { icon = "", color = "#C0A870", name = "Rs" },
          go  = { icon = "", color = "#6AAAA0", name = "Go" },
          -- Config / env
          env     = { icon = "", color = "#A89060", name = "Env" },
          lock    = { icon = "󰌾", color = "#555560", name = "Lock" },
          gitignore = { icon = "", color = "#555560", name = "Gitignore" },
          -- Docker
          dockerfile = { icon = "", color = "#7090B8", name = "Dockerfile" },
          -- SQL
          sql = { icon = "", color = "#8A70A0", name = "Sql" },
        },
      })
    end,
  },
}
