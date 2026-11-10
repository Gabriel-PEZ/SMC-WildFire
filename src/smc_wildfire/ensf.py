# %%

import geopandas as gpd

from .data import (
    get_landscape_path,
    get_max_timestep,
    get_observation_path,
    load_observation,
)
from .diffusion import reverse_diffusion
from .forecast import forecast_particles

# %%

def run_ensf(idx_wildfire, num_particles, num_steps, eps_a, eps_b, C, std_obs, std_state, std_init, rng):

    landscape = get_landscape_path(idx_wildfire)
    initial_perimeter = load_observation(idx_wildfire, idx_time=0)
    crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

    X_0 = initial_perimeter.ravel() + std_init * rng.standard_normal(
        (num_particles, initial_perimeter.size)
    )
    X = X_0 # shape num_particles x 2 * dimY

    # pour stocker les obs normalisés et les X filtrés
    observations = [initial_perimeter]
    filtered_particles = [X_0.copy()]

    for k in range(1, get_max_timestep(idx_wildfire)+1): 

        # propagation des particules X_k = FARSITE(X_{k-1}) + bruit
        Y, X = forecast_particles(
            X_prev=X,
            k=k,
            idx_wildfire=idx_wildfire,
            landscape=landscape,
            crs=crs,
            rng=rng,
            std_state=std_state
        )

        # observation k normalisé (normalisation sommets + orientation)
        observations.append(Y)

        # p(X_{k} | Y_{0:k}) via diffusion
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

    return observations, filtered_particles