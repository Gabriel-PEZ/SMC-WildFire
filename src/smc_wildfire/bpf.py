# %%

import geopandas as gpd
import numpy as np

from .data import (
    get_landscape_path,
    get_max_timestep,
    get_observation_path,
    load_observation,
)
from .forecast import forecast_particles

# %%
"""
fonctions pour filters bpf (avec systematic resampling basé sur ESS)
"""

def systematic_resampling(W, rng, num_particles):

    W_cumsum = np.cumsum(W)
    W_cumsum[-1] = 1.0 # pour sécuriser le cumsum à cause des flottants
    U = np.zeros(num_particles)
    U[0] = rng.uniform(low=0.0, high=1/num_particles)
    for i in range(1,num_particles):
        U[i] = U[0] + i/num_particles
    return np.searchsorted(W_cumsum, U)


def log_ESS(log_W):
    """
    On utilise directement les log poids normalisés pour l'ESS et
    """
    max_log_W = np.max(2 * log_W)
    return - max_log_W - np.log(np.exp(2 * log_W - max_log_W).sum())

def run_bpf(idx_wildfire, num_particles, C, std_obs, std_state, std_init, rng):

    landscape = get_landscape_path(idx_wildfire)
    initial_perimeter = load_observation(idx_wildfire, idx_time=0)
    crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

    T = get_max_timestep(idx_wildfire)
    log_W = np.zeros((T+1, num_particles))
    log_ESS_hist = np.zeros(T+1)

    # pour éviter de le calculer plusieurs fois
    log_N = np.log(num_particles)
    log_W[0] = -log_N
    log_ESS_hist[0] = log_N

    # propagation ie X_1|X_0 
    X_0 = initial_perimeter.ravel() + std_init * rng.standard_normal(
        (num_particles, initial_perimeter.size)
    )

    X = X_0.copy()

    observations = [initial_perimeter]
    filtered_particles = [X_0.copy()]

    for k in range(1, T + 1): 
        
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

        # C = 1 pour les auteurs
        log_w = log_W[k-1] + (-1/(2 * std_obs**2) * ((Y.ravel() - C * X)**2).sum(axis=1))
        max_log_w = np.max(log_w)
        log_W[k] = log_w - max_log_w - np.log((np.exp(log_w - max_log_w)).sum())

        log_ESS_curr = log_ESS(log_W[k])
        log_ESS_hist[k] = log_ESS_curr

        # systematic resampling si ESS <= N/2
        if log_ESS_curr <= log_N - np.log(2):
            idx_resampling = systematic_resampling(np.exp(log_W[k]), rng, num_particles)
            X = X[idx_resampling]
            log_W[k] = -log_N

        filtered_particles.append(X)

    return observations, filtered_particles, log_W, log_ESS_hist