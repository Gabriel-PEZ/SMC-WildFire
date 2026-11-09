@echo off

set FBM_BIN=%~dp0\bin
set FBM_BIN=%FBM_BIN:\\=\%

@echo FBM_BIN set to %FBM_BIN%

set FBM_ROOT=%~dp0
set FBM_ROOT=%FBM_ROOT:\\=\%

SET "PATH=%FBM_BIN%;%PATH%"
@echo Path set to %PATH%
SET "GDAL_DATA=%FBM_ROOT%share\gdal"
@echo GDAL_DATA set to %GDAL_DATA%
SET "PROJ_LIB=%FBM_ROOT%share\proj"
@echo PROJ_LIB set to %PROJ_LIB%
SET "WINDNINJA_DATA=%FBM_ROOT%share\windninja"
@echo WINDNINJA_DATA set to %WINDNINJA_DATA%
