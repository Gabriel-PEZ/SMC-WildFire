# %%

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon

from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    get_parameters_path,
    load_observation,
)
from smc_wildfire.ensf import reverse_diffusion
from smc_wildfire.farsite import farsite_prediction
from smc_wildfire.geometry import get_max_vertices, normalize_perimeter

# %%

idx_wildfire = 1819
landscape = get_landscape_path(idx_wildfire)
initial_perimeter = load_observation(idx_wildfire, idx_time=0)
crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

# %%

rng = np.random.default_rng(2003)
num_particles = 10
Y_0_stacked = initial_perimeter.reshape(-1,1) # on concatène en un seul vecteur (h1,v1,h2,v2,..)
X_0 = Y_0_stacked.ravel() + 0.1 * rng.standard_normal(
    (num_particles, Y_0_stacked.shape[0])
)
X = X_0.copy() # shape num_particles x 2 * dimY

observations = []
predictions = []
filtered_particles = []

for k in range(3):
    # on passe las particules X_0 dans FARSITE qu'on stacke dans une liste 
    # sans ajouter le bruit, qu'on ajoutera une fois que toutes les particules
    # auront été normalisées
    list_X = []
    parameters = get_parameters_path(idx_wildfire, k - 1)
    for i in range(len(X)):

        coords_particle = farsite_prediction(
            landscape_path=landscape, 
            parameters_path=parameters, 
            initial_perimeter=X[i].reshape(-1,2),
            crs=crs
        )
        list_X.append(coords_particle)
    
    Y = load_observation(idx_wildfire, k)
    num_vertices = get_max_vertices(Y, list_X)

    X = np.zeros((num_particles, 2 * num_vertices))
    Y = normalize_perimeter(Y, num_vertices)
    observations.append(Y)

    for i, part in enumerate(list_X): 
        X[i] = normalize_perimeter(part, num_vertices).reshape(-1,1).squeeze(axis=1)
        X[i] += rng.standard_normal(2 * num_vertices) * np.sqrt(0.5)

    predictions.append(X)

    # paramètres de l'article : 
    num_steps = 200
    eps_a = 0.96
    eps_b = 0.03
    C = 1 
    std_obs = 0.5

    X = reverse_diffusion(
        num_steps=num_steps, 
        Y=Y.ravel(), 
        X_0=X, 
        C=C, 
        std_obs=std_obs, 
        eps_a=eps_a, 
        eps_b=eps_b, 
        rng=rng
    )

    filtered_particles.append(X)
    
# %%

fig, ax = plt.subplots()
plot_polygon(Polygon(X[0].reshape(-1,2)), ax=ax)
plot_polygon(Polygon(Y), ax=ax)

# %%
