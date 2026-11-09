#pragma once
#include "icf_def.h"
#include <time.h>
#include "flammap.h"
#include "gdal_priv.h"
#include <unordered_map>

#ifndef LONG_64
#ifdef _MSC_VER
#define LONG_64 __int64
#else
#define LONG_64 long
#endif
#endif

#define MAX_PATH 260

//class CPerimeter;
class CMTTSpots;
class CMinTravelTime;
class CBinaryGrid;

class fireItem
{
public:
	fireItem();
	~fireItem();
	int fireNum;
	double x;
	double y;
	double acres;
	//CPerimeter *fireperim;
	CMTTSpots *embers;
};

typedef struct
{
	long ncols;
	long nrows;
	double xll;
	double yll;
	double cellsize;
}HeadData;

class CRandig
{
public:
	CRandig();
	~CRandig();
	//load the inputs
	int SetLandscapeFile(char* trgName);
	int LoadInputsFile(char *trgName);
	int SetFireListFile(char* trgName);
	int SetGriddedWindsFiles(char* gwSpeed, char* gwDir);
	bool ReadIgProbFile(char *FileName, CMinTravelTime *pMTT);
	bool CheckIgProb(double xpt, double ypt, float prob);
	char *GetErrorMessage(int errNumber);
	//run Randig
	int LaunchRandig();
	int CancelRandig();
	int RunRandigOpenMP();
	int RunRandigStd();
	double GetProgress();
	double GetProportionBurned();
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
	char *GetOutputLayerName32char(long layer, char *textBuf);
	char *GetOutputLayerUnits(int _layer, char *_unitsStr);
	ICF icf;
	fireItem *m_firelist;
//private:
	char inputsFileName[MAX_PATH];
	clock_t tStart;
	clock_t tEnd;
	timespec tsStart;
	timespec tsEnd;
	CFlamMap masterFlamMap;
	LONG_64 nRows;
	LONG_64 nCols;
	double res;
	double north, south, east, west;
	int m_NumFires;
	int m_NumMTTDone;
	int m_NumMTTFailure;
	int *m_burnCountGrid;
	int **m_FLFreqs;
	int m_numFLP;
	bool cancelRequest;
	LONG_64 m_burnableCells;
	LONG_64 m_targetCells;
	LONG_64 m_cellsBurned;
	HeadData m_ighead;
	float *m_igProbGrid = 0;
	GDALDataset* m_pPerimDS;
	//std::unordered_map<int, CBinaryGrid*> mpArrivalGrids;
	CBinaryGrid **m_pFlamelengthGrids;
	//std::unordered_map<int, double> mpRuntimes;
	//std::unordered_map<int, CMTTSpots*> mpEmbers;
	void AddFLGrid(int fireID, CMinTravelTime* pMTT);
	int BuildPerimeters();
	int AddPerimeter(OGRLayerH hLayer, int loc, int fireID);
	void CreateFlameLengthGrids();
	void DestroyFlameLengthGrids();
};

