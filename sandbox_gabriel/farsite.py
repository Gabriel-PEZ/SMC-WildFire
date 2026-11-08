# %%

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np

from smc_wildfire.data import (
    get_landscape_path,
    get_observation_path,
    get_parameters_path,
    get_project_root,
)

# %%

root = get_project_root()
farsite_dir = root / "external" / "firebehavior" / "dist"
farsite_exe = farsite_dir / "bin" / "runfarsite.exe"
assert farsite_exe.is_file()

# %%
idx_wildfire = 1819
idx_time = 0

landscape = get_landscape_path(idx_wildfire)
parameters = get_parameters_path(idx_wildfire, idx_time)
initial_perimeter = get_observation_path(idx_wildfire, idx_time)

# %%

def farsite_prediction(landscape_path, parameters_path, initial_perimeter_path):

    # on crée un dossier temporaire propre à chaque simulation 
    # pour éviter que si on run farsite avec 30 particules, chaque nouvelle particule 
    # écrase celle d'avant
    with TemporaryDirectory(prefix="farsite_") as tmp_dir:
        work_dir = Path(tmp_dir)

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

coords = farsite_prediction(
    landscape_path=landscape, 
    parameters_path=parameters, 
    initial_perimeter_path=initial_perimeter
)

# %%

coords

# %%
