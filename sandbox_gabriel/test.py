# %%

import time

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon
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

# FARSITE accepte les particules qui ne forment pas un polygone donc pour le moment 
# on peut oublier l'acceptation/rejet
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
"""

particles_0 = Y_0_stacked.ravel() + 0.1 * rng.standard_normal(
    (num_particles, Y_0_stacked.shape[0])
)

# %%

"""
X_1 = FARSITE(X_0) + bruit
Meme si les polygones ne sont pas bien définis cela FARSITE ne renvoie pas d'erreur
"""
coords_particles = []
for i in range(len(particles_0)):

    coords_particle = farsite_prediction(
        landscape_path=landscape, 
        parameters_path=parameters, 
        initial_perimeter=particles_0[i].reshape(-1,2),
        crs=crs
    )
    coords_particles.append(coords_particle)
    print(Polygon(coords_particle).is_valid)

# %%

# fonction pour trouver le nombre de sommets max des polygones parmi les particules et l'observation
def get_max_vertices(observed_perimeter, list_particles):
    """
    - observed_perimeter = obtenu depuis load_observatio de taille n_O * 2
    - list_particles = liste des particules (n_i * 2) passés dans FARSITE sans avoir ajouté le bruit 
    ie X_k = FARSITE(X_{k-1})

    - Renvoie max(n_O, n_1, ..., n_N)
    """
    max_vertices = []
    for particle in list_particles:
        max_vertices.append(len(particle))
    max_vertices.append(len(observed_perimeter))
    return max(max_vertices)


observed_perimeter_1 = load_observation(idx_wildfire, idx_time=1)
num_vertices = get_max_vertices(observed_perimeter_1, coords_particles)

# %%

def resample_perimeter(perimeter, num_vertices):
    """
    Fonction pour uniformiser la taille des particules et de l'observation 
    ie on ajoute artificiellement des sommets le long du périmètre du polygone

    - num_vertices = max des sommets entre (X_k^{(i)})_i et Y_k (les deux de taille x_j * 2)
    - perimeter = particule ou observation qu'on veut passer de (n_i * 2) à (max * 2)
    """

    diff = np.roll(perimeter, -1, axis=0) - perimeter
    segment_lengths = np.linalg.norm(diff, axis=1)

    length_perimeter = np.sum(segment_lengths)
    cumsum_dist = np.concatenate(([0], np.cumsum(segment_lengths)))

    # points réparti uniforfément sur le périmètre du polygone
    # on exclut dernier sommmet pour fermer le polygone
    new_vertices = np.linspace(0, length_perimeter, num_vertices, endpoint=False) 
    # pour chaque point on regarde sur quel segment il se trouve
    vertex_segments = np.searchsorted(cumsum_dist, new_vertices, side='right') - 1

    # alpha du papier
    alpha = (new_vertices - cumsum_dist[vertex_segments])/(cumsum_dist[vertex_segments + 1] - cumsum_dist[vertex_segments])
    new_perimeter = (1 - alpha[:, None]) * perimeter[vertex_segments] + alpha[:, None] * perimeter[(vertex_segments + 1) % len(perimeter)]
    return new_perimeter

# %%

new_perimeter_particle_0 = resample_perimeter(coords_particles[0], num_vertices)

# %%

def normalize_orientation(perimeter):

    """
    Permet de toujours représenter les sommets du polygone dans le sens horaire
    Pour ça on calcule l'aire signée : 
        - si A > 0, le polygone est parcouru dans le sens anti-horaire
        - si A < 0, sens horaire
    On retourne toujours les sommets qui décrivent le périmètre dans le sens horaire
    """

    # on ajoute comme dernier sommet le premier pour fermé le polygone pour calculer A
    closed_perimeter = np.concatenate((perimeter, perimeter[0:1]))
    signed_area = 0.5 * np.sum(
        closed_perimeter[:-1,0] * closed_perimeter[1:,1] - 
        closed_perimeter[1:,0] * closed_perimeter[:-1,1]
    )
    if signed_area > 0:
        return perimeter[::-1]
    return perimeter

# %%

perimeter_normed_particle_0 = normalize_orientation(new_perimeter_particle_0)

# %%

angle_rad = np.atan2(
    perimeter_normed_particle_0[:,1],
    perimeter_normed_particle_0[:,0]
)

idx_max_abs_angle_rad = np.argmin(np.abs(angle_rad))

# %%



# %%

def normalize_starting_vertex(perimeter):
    """
    atan2(y,x) calcule l'angle entre l'axe positif des x et le vecteur 
    allant de l'origine à (x,y)
    Pour être sur que dans la ligne i corresponde au même sommet entre toutes les 
    particules et l'observation, les auteurs décident de fixer le premier sommet comme étant 
    celui qui a la plus petite valeur absolue atan2(y,x)
    """

    angle_rad = np.atan2(
        perimeter[:,1],
        perimeter[:,0]
    )

    idx_max_abs_angle_rad = np.argmin(np.abs(angle_rad))
    return np.roll(perimeter, -idx_max_abs_angle_rad, axis=0)


def normalize_perimeter(perimeter, num_vertices):
    return normalize_starting_vertex(
        normalize_orientation(
            resample_perimeter(perimeter, num_vertices)
        )
    )


# %%

