# %%

import time

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    get_parameters_path,
    load_observation,
)
from smc_wildfire.farsite import farsite_prediction
from smc_wildfire.geometry import get_max_vertices, normalize_perimeter

# %%

idx_wildfire = 1819
idx_time = 0 

landscape = get_landscape_path(idx_wildfire)
parameters = get_parameters_path(idx_wildfire, idx_time)
initial_perimeter = load_observation(idx_wildfire, idx_time)
crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time)).crs

# %%

rng = np.random.default_rng(2003)
num_particles = 10
Y_0_stacked = initial_perimeter.reshape(-1,1) # on concatène en un seul vecteur (h1,v1,h2,v2,..)
particles_T0 = Y_0_stacked.ravel() + 0.1 * rng.standard_normal(
    (num_particles, Y_0_stacked.shape[0])
)

# %%

"""
X_1 = FARSITE(X_0) + bruit
Meme si les polygones ne sont pas bien définis cela FARSITE ne renvoie pas d'erreur
"""

# on passe las particules X_0 dans FARSITE qu'on stacke dans une liste 
# sans ajouter le bruit, qu'on ajoutera une fois que toutes les particules
# auront été normalisées
list_particles_T1 = []
for i in range(len(particles_T0)):

    coords_particle = farsite_prediction(
        landscape_path=landscape, 
        parameters_path=parameters, 
        initial_perimeter=particles_T0[i].reshape(-1,2),
        crs=crs
    )
    print(Polygon(coords_particle).is_valid)
    list_particles_T1.append(coords_particle)
    

# %%

Y_1 = load_observation(idx_wildfire, 1)
num_vertices = get_max_vertices(Y_1, list_particles_T1)

# %%

X_1 = np.zeros((num_particles, 2 * num_vertices))
Y_1 = normalize_perimeter(Y_1, num_vertices)
for i, part in enumerate(list_particles_T1): 
    X_1[i] = normalize_perimeter(part, num_vertices).reshape(-1,1).squeeze(axis=1)
    X_1[i] += rng.standard_normal(2 * num_vertices) * np.sqrt(0.5)

# %%



# %%
