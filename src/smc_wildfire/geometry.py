# %%

import numpy as np

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

# %%

def resample_perimeter(perimeter, num_vertices):
    """
    Fonction pour uniformiser la taille des particules et de l'observation 
    ie on redistribue uniformément des sommets le long du périmètre du polygone

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

    idx_min_abs_angle_rad = np.argmin(np.abs(angle_rad))
    return np.roll(perimeter, -idx_min_abs_angle_rad, axis=0)


def normalize_perimeter(perimeter, num_vertices):
    return normalize_starting_vertex(
        normalize_orientation(
            resample_perimeter(perimeter, num_vertices)
        )
    )

# %%
