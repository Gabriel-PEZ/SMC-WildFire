# %%

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from smc_wildfire.bpf import run_bpf
from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    load_observation,
)
from smc_wildfire.ensf import run_ensf
from smc_wildfire.farsite import run_farsite

# %%

idx_wildfire = 1819
landscape = get_landscape_path(idx_wildfire)
initial_perimeter = load_observation(idx_wildfire, idx_time=0)
crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

# %%

"""
Boucle de filtrage EnSF
"""
rng_ensf = np.random.default_rng(2003)
# paramètres de l'article : 
num_particles = 10
num_steps = 200
eps_a = 0.96
eps_b = 0.03
C = 1 
std_obs = 0.5
std_state = np.sqrt(0.5)
std_init = 0.1

observations_ensf, filtered_particles_ensf = run_ensf(idx_wildfire, num_particles, num_steps, eps_a, eps_b, C, std_obs, std_state, std_init, rng_ensf)

# %%

"""
Plot de l'évolution de l'EnSF avec moyenne des particules pour chaque pas de
temps
"""

fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.colormaps["viridis"]
norm = plt.Normalize(vmin=1, vmax=len(filtered_particles_ensf))

for k, particles in enumerate(filtered_particles_ensf, start=1):
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
norm = plt.Normalize(vmin=1, vmax=len(observations_ensf))

for k, obs in enumerate(observations_ensf, start=1):

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
idx_wildfire = 1819
farsite_predictions = run_farsite(idx_wildfire)

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

Y = observations_ensf[idx]
farsite_pred = farsite_predictions[idx]
X_filtered = filtered_particles_ensf[idx].mean(axis=0).reshape(-1, 2)

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


"""
Boucle de filtrage BPF
"""

rng_bpf = np.random.default_rng(2000)

observations_bpf, filtered_particles_bpf, log_W, log_ESS_hist = run_bpf(
    idx_wildfire=idx_wildfire,
    num_particles=num_particles,
    C=C,
    std_obs=std_obs,
    std_state=std_state,
    std_init=std_init,
    rng=rng_bpf
)