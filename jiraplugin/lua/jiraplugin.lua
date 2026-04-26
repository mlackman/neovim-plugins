local config = {}

local function setup(c)
    config = c
end

local function getConfig()
    return config
end

return {setup = setup, getConfig = getConfig}
