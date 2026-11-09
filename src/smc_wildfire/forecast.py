# %%

import numpy as np

from .data import get_parameters_path, load_observation
from .farsite import farsite_step
from .geometry import get_max_vertices, normalize_perimeter

# %%

def forecast_particles(X_prev, k, idx_wildfire, landscape, crs, rng, std_state):
    """
    Boucle commune entre EnSF et BPF pour la transition X_k = FARSITE(X_{k-1}) + bruit
    """

    # on stacke les particules dans une liste après FARSITE car ils n'ont pas les mêmes dimensions
    list_X = []

    # paramètre k-1 pour FARSITE
    parameters = get_parameters_path(idx_wildfire, k - 1)

    for i in range(len(X_prev)):

        coords_particle = farsite_step(
            landscape_path=landscape, 
            parameters_path=parameters, 
            initial_perimeter=X_prev[i].reshape(-1,2),
            crs=crs
        )
        list_X.append(coords_particle)

    Y = load_observation(idx_wildfire, k)
    num_vertices = get_max_vertices(Y, list_X)

    X_pred = np.zeros((len(X_prev), 2 * num_vertices))
    Y = normalize_perimeter(Y, num_vertices)

    for i, part in enumerate(list_X): 
        X_pred[i] = normalize_perimeter(part, num_vertices).ravel() # équivalent à reshape(-1,1).squeeze(axis=1)
        X_pred[i] += rng.standard_normal(2 * num_vertices) * std_state

    return Y, X_pred