# %%

from pathlib import Path

import geopandas as gpd
import numpy as np


def get_project_root():
    """
    fonction pour trouver root du projet peu importe ou on lance le script
    """
    for p in Path(__file__).resolve().parents:
        if (p / "pyproject.toml").is_file():
            return p
        
def get_landscape_path(idx_wildfire):
    return get_project_root() / "data" / f"{idx_wildfire}" / f"{idx_wildfire}.lcp"

def get_parameters_path(idx_wildfire, idx_time):
    return get_project_root() / "data" / f"{idx_wildfire}" / f"{idx_time}" / "para.input"

def get_observation_path(idx_wildfire, idx_time):
    return get_project_root() / "data" / f"{idx_wildfire}" / f"{idx_time}" / "fire_boundary.shp" 

def load_observation(idx_wildfire, idx_time):
    path = get_observation_path(idx_wildfire, idx_time)
    gdf = gpd.read_file(path)
    return np.asarray(gdf.geometry.iloc[0].exterior.coords)[:-1,:]

def get_max_timestep(idx_wildfire):

    """
    fonction qui retourne le plus grand k parmi les sous dossiers 
    dans un dossier wildfire 
    """

    root = get_project_root()
    wildfire_dir = root / "data" / str(idx_wildfire)

    k_max = max(
        int(path.name)
        for path in wildfire_dir.iterdir()
        if path.is_dir() and path.name.isdigit()
    )

    return k_max