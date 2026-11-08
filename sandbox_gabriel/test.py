# %%

from smc_wildfire.data import (
    load_observation,
    get_landscape_path,
    get_parameters_path
)

# %%

idx_wildfire = 1819
idx_time = 0 

# %%

Y_0 = load_observation(idx_wildfire, idx_time)
landscape = get_landscape_path(idx_wildfire)
parameters = get_parameters_path(idx_wildfire, idx_time)

# %%