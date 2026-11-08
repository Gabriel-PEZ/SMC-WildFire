# %%

import geopandas as gpd

from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    get_parameters_path,
    load_observation,
)
from smc_wildfire.farsite import farsite_prediction

# %%

idx_wildfire = 1819
idx_time = 0 

landscape = get_landscape_path(idx_wildfire)
parameters = get_parameters_path(idx_wildfire, idx_time)
initial_perimeter = load_observation(idx_wildfire, idx_time)
crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time)).crs

coords = farsite_prediction(
    landscape_path=landscape, 
    parameters_path=parameters, 
    initial_perimeter=initial_perimeter,
    crs=crs
)

print(coords)

# %%
