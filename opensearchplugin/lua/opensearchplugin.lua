local config = {}

local function setup(cfg)
    config = cfg
    vim.keymap.set('n', '<Leader>os', ':SearchCommand<CR>', { silent = true })
end

-- Used in Python to get config
local function getConfig()
    return config
end

return { setup=setup, getConfig=getConfig }
