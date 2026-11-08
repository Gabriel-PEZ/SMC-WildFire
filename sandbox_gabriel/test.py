# %%

import time

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
from shapely.validation import explain_validity

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
"""
on crée X_0 à partir de Y_0 + bruit mais le pb est qu'en rajoutant un bruit à
Y_0 rien n'assure que la structure de polygone soit encore valide
"""

rng = np.random.default_rng(2003)
num_particles = 10
# test sur 10 particules : 
Y_0_stacked = coords.reshape(-1,1) # on concatène en un seul vecteur (h1,v1,h2,v2,..)
for _ in range(num_particles):
    X_0_stacked = Y_0_stacked + rng.standard_normal(Y_0_stacked.shape) * np.sqrt(0.01)
    X_0 = X_0_stacked.reshape(-1,2)
    X_0_polygon = Polygon(X_0)
    print(X_0_polygon.is_valid, explain_validity(X_0_polygon))

# %%

"""
Pour sampler X_0, on accepte uniquement si
Polygon(X_0).is_valid == True
"""

start = time.perf_counter()
nb_trials_max = 100 * num_particles
trial = 0
valid_particles = 0 
particles = np.zeros((num_particles, Y_0_stacked.shape[0]))
while (valid_particles < num_particles) and (trial < nb_trials_max):
    X_0_stacked = Y_0_stacked + rng.standard_normal(Y_0_stacked.shape) * np.sqrt(0.01)
    X_0 = X_0_stacked.reshape(-1,2)
    X_0_polygon = Polygon(X_0)
    trial += 1
    if X_0_polygon.is_valid:
        particles[valid_particles] = np.asarray(X_0_polygon.exterior.coords[:-1]).reshape(-1,1).squeeze(axis=1)
        valid_particles += 1
# assert len(valid_particles) == num_particles
acceptance_rate = 100 * valid_particles / trial
end = time.perf_counter()
print(f"{end-start:.2f} secs", acceptance_rate)

# %%

"""
X_1 = FARSITE(X_0) + bruit
Verif que les particules passées par FARSITE soient encore valide
"""
coords_particles = []
for i in range(len(particles)):

    coords_particle = farsite_prediction(
        landscape_path=landscape, 
        parameters_path=parameters, 
        initial_perimeter=particles[i].reshape(-1,2),
        crs=crs
    )
    coords_particles.append(coords_particle)
    print(Polygon(coords_particle).is_valid)

# %%
