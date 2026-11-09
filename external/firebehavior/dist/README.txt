FireBehaviorModels 

Release date 9/21/2026

Product of the Missoula Fire Sciences Laboratory

Attribution: Any use of the data derived from FireBehaviorModels requires the following citation:

"Fire Behavior calculations produced with the command line applications developed by the Missoula Fire Sciences Laboratory, Missoula, MT"

NOTE: For proper running of any of the fire behavior models, please run the SetEnv.bat file in the same command window as running any of the models. This will ensure WINDNINJA_DATA, GDAL_DATA and PROJ_LIB environment variables are set correctly, and programs can read/write spatial reference system information correctly as well as find necessary data. 
Note that these environment variables are only valid for the command window session. You can also set these environment variables for your system. Please examine the SetENV.bat file to see what variables need to be set, and their appropriate values.

Documentation for each model's input file formats are located in the FireBehaviorModels\doc folder.

Sample data has been provided. The samples available are:

FlamMap\TestFlammap.bat
Farsite\TestFarsite.bat
MTT\testMTT.bat
Randig\TestRandig.bat
FSPro\TestFSPro.bat

Please note that the sample input files are set up to run regardless of extraction location, in a relative directory structure. In practice it is best to put complete paths to files referenced in the inputs files,
entering the arguments on the command line instead of running in a batch file.

To properly set up FireBehaviorModels, please open a command prompt, navigate to the root FireBehaviorModels directory, and run SetEnv.bat from the command prompt. Then any of the fire behavior models will be able to be run correctly from that command prompt.