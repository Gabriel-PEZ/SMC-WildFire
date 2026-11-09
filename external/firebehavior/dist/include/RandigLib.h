#pragma once

#ifdef _MSC_VER
#ifdef RANDIG_EXPORTS
#define RANDIGLIB_API __declspec(dllexport)
#else
#define RANDIGLIB_API __declspec(dllimport)
#endif
#else
#define RANDIGLIB_API
#endif

class CRandig;

#define RANDIG_BURN_PROBABILITY			70
#define RANDIG_FLP_CLASS_0_2			71
#define RANDIG_FLP_CLASS_2_4			72
#define RANDIG_FLP_CLASS_4_6			73
#define RANDIG_FLP_CLASS_6_8			74
#define RANDIG_FLP_CLASS_8_12			75
#define RANDIG_FLP_CLASS_12_PLUS		76
#define RANDIG_CONDITIONAL_FLAMELENGTH	77


class RANDIGLIB_API CRandigLib
{
public:
	CRandigLib();
	~CRandigLib();

	int SetLandscapeFile(char* trgName);
	//load the inputs
	int LoadInputsFile(char *trgName);
	int SetFireListFile(char* trgName);
	int SetGriddedWindsFiles(char* gwSpeed, char* gwDir);
	char *GetErrorMessage(int errNumber);
	//run Randig
	int LaunchRandig();
	int CancelRandig();
	double GetProgress();
	double GetProportionBurned();
	int GetNumFiresComplete();
	int GetNumFiresToDo();
	int GetNumMTTFailures();
	double GetTargetBurnProportion();
	//outputs
	int WriteFLP(char *trgName);
	int WritePerimeters(char *trgName);
	int WriteFireSizeList(char *trgName);
	int WriteEmbersCSV(char *trgName);
	int WriteEmbers(char *trgName);
	int WriteTimingsFile(char *trgName);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);
	//int WriteOutputLayerASCII(int _layer, char *name);
	int WriteWindVectorKML(char *fileNamePath, double resolution);
	double GetWindVectorKMLResolution();
private:
	CRandig *pRandig;
};