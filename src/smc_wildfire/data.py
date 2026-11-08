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

def load_observation(idx_wildfire, idx_time):
    path = get_project_root() / "data" / f"{idx_wildfire}" / f"{idx_time}" / "fire_boundary.shp" 
    gdf = gpd.read_file(path)
    return np.asarray(gdf.geometry.iloc[0].exterior.coords)[:-1,:]