# %%

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    get_parameters_path,
    load_observation,
)
from smc_wildfire.ensf import reverse_diffusion
from smc_wildfire.farsite import farsite_prediction
from smc_wildfire.geometry import get_max_vertices, normalize_perimeter

# from smc_wildfire.bpf import bpf_filer

# %%

idx_wildfire = 1819
landscape = get_landscape_path(idx_wildfire)
initial_perimeter = load_observation(idx_wildfire, idx_time=0)
crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

# %%

rng_ensf = np.random.default_rng(2003)
num_particles = 10
initial_perimeter = initial_perimeter.reshape(-1,1) # on concatène en un seul vecteur (h1,v1,h2,v2,..)
X_0 = initial_perimeter.ravel() + 0.1 * rng_ensf.standard_normal(
    (num_particles, initial_perimeter.shape[0])
)
X = X_0.copy() # shape num_particles x 2 * dimY

# %%

"""
Boucle de filtrage EnSF
"""

# pour stocker respectivement les obs, les X après transition et les X filtrés
observations = []
predictions = []
filtered_particles = []

# paramètres de l'article : 
num_steps = 200
eps_a = 0.96
eps_b = 0.03
C = 1 
std_obs = 0.5

for k in range(1,14): # 13 dossiers x/ dans 1819/
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
        X[i] += rng_ensf.standard_normal(2 * num_vertices) * np.sqrt(0.5)

    predictions.append(X)

    X = reverse_diffusion(
        num_steps=num_steps, 
        Y=Y.ravel(), 
        X_0=X, 
        C=C, 
        std_obs=std_obs, 
        eps_a=eps_a, 
        eps_b=eps_b, 
        rng=rng_ensf
    )

    filtered_particles.append(X)

# %%

"""
Plot de l'évolution de l'EnSF avec moyenne des particules pour chaque pas de
temps
"""

fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.colormaps["viridis"]
norm = plt.Normalize(vmin=1, vmax=len(filtered_particles))

for k, particles in enumerate(filtered_particles, start=1):
    mean_filtered = particles.mean(axis=0).reshape(-1, 2)

    # Fermer le périmètre
    closed = np.vstack([mean_filtered, mean_filtered[0]])

    ax.plot(
        closed[:, 0],
        closed[:, 1],
        color=cmap(norm(k)),
        linewidth=1.5,
        alpha=0.9
    )

sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
fig.colorbar(sm, ax=ax, label="Pas de temps k")

ax.set_aspect("equal")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Évolution du périmètre moyen filtré par EnSF")
ax.grid(alpha=0.2)

plt.show()

# %%

"""
Plot de l'évolution de l'observation
"""

fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.colormaps["viridis"]
norm = plt.Normalize(vmin=1, vmax=len(observations))

for k, obs in enumerate(observations, start=1):

    # Fermer le périmètre
    closed = np.vstack([obs, obs[0]])

    ax.plot(
        closed[:, 0],
        closed[:, 1],
        color=cmap(norm(k)),
        linewidth=1.5,
        alpha=0.9
    )

sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
fig.colorbar(sm, ax=ax, label="Pas de temps k")

ax.set_aspect("equal")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Évolution du périmètre observé par EnSF")
ax.grid(alpha=0.2)

plt.show()


# %%
"""
FARSITE UNIQUEMENT : X_{k+1} = FARSITE(X_k)
"""

X = initial_perimeter
farsite_predictions = []
# BOUCLE FARSITE UNIQUEMENT i.e. sans bruit et sans assimilation
for k in range(13): # 13 dossiers x/ dans 1819/

    parameters = get_parameters_path(idx_wildfire, k)
    X = farsite_prediction(
        landscape_path=landscape, 
        parameters_path=parameters, 
        initial_perimeter=X.reshape(-1,2),
        crs=crs
    )
    
    farsite_predictions.append(X)

fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.colormaps["viridis"]
norm = plt.Normalize(vmin=1, vmax=len(farsite_predictions))

for k, f_pred in enumerate(farsite_predictions, start=1):

    if k%2 == 0:
        closed = np.vstack([f_pred, f_pred[0]])

        ax.plot(
            closed[:, 0],
            closed[:, 1],
            color=cmap(norm(k)),
            linewidth=1.5,
            alpha=0.9
        )

sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
fig.colorbar(sm, ax=ax, label="Pas de temps k")

ax.set_aspect("equal")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Évolution du périmètre prédit par FARSITE")
ax.grid(alpha=0.2)

plt.show()

# %%

"""
Comparaison de X filtré via EnSF, FARSITE uniquement et l'OBS
"""

k = 13
idx = k - 1

Y = observations[idx]
farsite_pred = farsite_predictions[idx]
X_filtered = filtered_particles[idx].mean(axis=0).reshape(-1, 2)

fig, ax = plt.subplots(figsize=(10, 8))

for perimeter, label, color in [
    (Y, "Observation", "black"),
    (farsite_pred, "FARSITE", "red"),
    (X_filtered, "EnSF", "blue"),
]:
    closed = np.vstack([perimeter, perimeter[0]])
    ax.plot(
        closed[:, 0],
        closed[:, 1],
        label=label,
        color=color,
        linewidth=2,
    )

ax.set_aspect("equal")
ax.set_title(f"Comparaison des périmètres à k={k}")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
ax.grid(alpha=0.2)

plt.show()

# %%


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

"""
def bpf_filer(Y, num_particles, d, rng_pf, phi, std_obs, std_state, C):

    Filtre bootstrap avec resampling systématique selon ESS
    
"""

rng_pf = np.random.default_rng(2000)

T = 13
log_W = np.zeros((T+1, num_particles))
log_ESS_hist = np.zeros(T+1)

# pour éviter de le calculer plusieurs fois
log_N = np.log(num_particles)
log_W[0] = -log_N

# propagation ie X_1|X_0 
X_0 = initial_perimeter.ravel() + 0.1 * rng_pf.standard_normal(
    (num_particles, initial_perimeter.shape[0])
)

X = X_0.copy()

observations_bpf = []
predictions_bpf = []
filtered_particles_bpf = []

for t in range(1,14): # 13 dossiers x/ dans 1819/
    # on passe las particules X_0 dans FARSITE qu'on stacke dans une liste 
    # sans ajouter le bruit, qu'on ajoutera une fois que toutes les particules
    # auront été normalisées
    list_X = []
    parameters = get_parameters_path(idx_wildfire, t - 1)
    for i in range(len(X)):

        coords_particle = farsite_prediction(
            landscape_path=landscape, 
            parameters_path=parameters, 
            initial_perimeter=X[i].reshape(-1,2),
            crs=crs
        )
        list_X.append(coords_particle)
    
    Y = load_observation(idx_wildfire, t)
    num_vertices = get_max_vertices(Y, list_X)

    X = np.zeros((num_particles, 2 * num_vertices))
    Y = normalize_perimeter(Y, num_vertices)
    observations_bpf.append(Y)

    for i, part in enumerate(list_X): 
        X[i] = normalize_perimeter(part, num_vertices).reshape(-1,1).squeeze(axis=1)
        X[i] += rng_pf.standard_normal(2 * num_vertices) * np.sqrt(0.5)

    predictions_bpf.append(X)
    # C = 1 pour les auteurs
    log_w = log_W[t-1] + (-1/(2 * std_obs**2) * ((Y.ravel() - C * X)**2).sum(axis=1))
    max_log_w = np.max(log_w)
    log_W[t] = log_w - max_log_w - np.log((np.exp(log_w - max_log_w)).sum())

    log_ESS_curr = log_ESS(log_W[t])
    log_ESS_hist[t] = log_ESS_curr

    # systematic resampling si ESS <= N/2
    if log_ESS_curr <= log_N - np.log(2):
        idx_resampling = systematic_resampling(np.exp(log_W[t]), rng_pf, num_particles)
        X = X[idx_resampling]
        log_W[t] = -log_N

    filtered_particles_bpf.append(X)

# %%