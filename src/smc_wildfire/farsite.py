# %%

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
import shapely

from .data import (
    get_landscape_path,
    get_max_timestep,
    get_observation_path,
    get_parameters_path,
    get_project_root,
    load_observation,
)

# %%

root = get_project_root()
farsite_dir = root / "external" / "firebehavior" / "dist"
farsite_exe = farsite_dir / "bin" / "runfarsite.exe"
assert farsite_exe.is_file()

# %%

def farsite_step(
        landscape_path, 
        parameters_path, 
        initial_perimeter, # numpy
        crs # système de coordonnées des obs
    ):
    """
    initial_perimeter = np.ndarray d*2
    """

    # on crée un dossier temporaire propre à chaque simulation 
    # pour éviter que si on run farsite avec 30 particules, chaque nouvelle particule 
    # écrase celle d'avant
    with TemporaryDirectory(prefix="farsite_") as tmp_dir:
        work_dir = Path(tmp_dir)

        # permet de créer l'objet Polygon que reçoit FARSITE
        # utiliser pour transformer une particule en objet Polygon
        polygon = shapely.geometry.Polygon(initial_perimeter)
        # on crée le gdf qu'on transforme ensuite en .shp pour FARSITE
        gdf_new = gpd.GeoDataFrame(
            geometry=[polygon],
            crs=crs,
        )
        initial_perimeter_path = work_dir / "initial_perimeter.shp"
        gdf_new.to_file(initial_perimeter_path, index=False)

        # farsite se lance avec le fichier FarsiteCmd.txt
        # qui contient landscape_path parameters_path ignition_path 0 output_prefix 2
        # cela indique au .exe quels fichiers utiliser et où stocker les résultats
        output_prefix = work_dir / "test"
        cmd_path = work_dir / "FarsiteCmd.txt"
        command = f"{landscape_path} {parameters_path} {initial_perimeter_path} 0 {output_prefix} 2"
        cmd_path.write_text(command, encoding="ascii")

        # variables d'environnement qu'on transmet à FARSITE
        env = os.environ.copy()

        # on ajoute les dossiers nécessaires à FARSITE
        env["PATH"] = str(farsite_dir / "bin") + os.pathsep + env["PATH"]
        # données géographiques 
        env["GDAL_DATA"] = str(farsite_dir / "share" / "gdal")
        # système de coordonnées
        env["PROJ_LIB"] = str(farsite_dir / "share" / "proj")
        # WindNinja = outil de simulation du vent sur des terrains complexes
        env["WINDNINJA_DATA"] = str(farsite_dir / "share" / "windninja")

        _ = subprocess.run(
            # liste = [fonction, argument1, argument2, etc...]
            [str(farsite_exe), str(cmd_path)],
            cwd=work_dir,
            env=env,
            check=True,
        )

        farsite_perimeters = work_dir / "test_Perimeters.shp"
        gdf = gpd.read_file(farsite_perimeters)
        # différents type de feu 
        # expanding fire = contour du feu qui se propage
        # enclave fire = contour d'une zone intérieure non brûlée entourée par le feu)
    
        expanding = gdf.loc[gdf["Fire_Type"] == "Expanding Fire"]
        final_time = expanding["Elapsed_Mi"].max()

        final_perimeter = expanding.loc[
            expanding["Elapsed_Mi"] == final_time, "geometry"
        ]

        # comme expliqué dans explications_data.txt para.input comporte les infos pour la simulation
        # FARSITE_START_TIME: 06 18 0000 = début 18 juin à 00h
        # FARSITE_END_TIME: 06 18 1200 = fin 18 juin à 12h
        # donc la durée de la simulation devrait être 12 * 60 = 720
        expected_duration = 720.0
        assert final_time == expected_duration
        # les auteurs ont travaillé sur des feux avec un seul polygone uniquement 
        # donc on vérifie si la sortie à H+12 de FARSITE est bien un seul polygone
        assert len(final_perimeter) == 1

        coords = np.asarray(final_perimeter.iloc[0].exterior.coords)
        return coords[:-1]
    
# %%

def run_farsite(idx_wildfire):
    """
    fonction run X_{k+1} = FARSITE(X_k) pour l'ensemble des données d'un feu et retourne 
    l'évolution du périmètre
    """

    landscape = get_landscape_path(idx_wildfire)
    initial_perimeter = load_observation(idx_wildfire, idx_time=0)
    crs = gpd.read_file(get_observation_path(idx_wildfire, idx_time=0)).crs

    X = initial_perimeter
    farsite_predictions = []

    k_max = get_max_timestep(idx_wildfire)

    # BOUCLE FARSITE UNIQUEMENT i.e. sans bruit et sans assimilation
    for k in range(k_max): 

        parameters = get_parameters_path(idx_wildfire, k)
        X = farsite_step(
            landscape_path=landscape, 
            parameters_path=parameters, 
            initial_perimeter=X.reshape(-1,2),
            crs=crs
        )
        
        farsite_predictions.append(X)
    return farsite_predictions