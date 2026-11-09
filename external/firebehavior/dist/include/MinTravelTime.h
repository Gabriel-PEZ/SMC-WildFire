//MinTravelTime.h
//defines exported class for MinTravelTime.dll
#pragma once
#include <vector>
#include <string>

#ifdef _MSC_VER
#ifdef BUILD_MTTDLL 
#define MTTDLL_EXPORT __declspec(dllexport) 
#else 
#define MTTDLL_EXPORT __declspec(dllimport) 
#endif 
#else
#define MTTDLL_EXPORT
#endif

class CMTT;
class CFlamMap;
class CBurnDay;
//class TileStack;
//#include <list>

//MTT Output Raster Layer Identifiers
#define MTT_ARRIVAL_TIME		50
#define MTT_SPREAD_RATE			51
#define MTT_INFLUENCE			52
#define MTT_INTENSITY			53
#define MTT_FLAME_LENGTH		54
#define MTT_IGNITION			55
//end MTT output layer identifiers

class MTTDLL_EXPORT CPerimeterLine
{
public:
	CPerimeterLine();
	CPerimeterLine(const CPerimeterLine& rhs);
	~CPerimeterLine();
	int SetNumPoints(int _numPoints);
	int GetNumPoints();
	bool GetPoint(int pointNum, float *x, float *y);
	bool SetPoint(int pointNum, float x, float y);
private:
	int numPoints;
	float *xVals;
	float *yVals;
};

class MTTDLL_EXPORT CPerimeter
{
public:
	CPerimeter();
	CPerimeter(const CPerimeter& rhs);
	~CPerimeter();
	int SetNumLines(int _numLines);
	int GetNumLines();
	CPerimeterLine *GetLine(int lineNum);
private:
	int numLines;
	CPerimeterLine *lines;
};

class MTTDLL_EXPORT CMTTSpot
{
public:
	CMTTSpot();
	~CMTTSpot();
	void SetData(double _launchX, double _launchY, double _landX, double _landY, double _launchTime, double _landTime);
	void SetLaunchX(double val);
	void SetLaunchY(double val);
	void SetLandX(double val);
	void SetLandY(double val);
	void SetLaunchTime(double ltime);
	void SetLandTime(double ltime);
	double GetLaunchX();
	double GetLaunchY();
	double GetLandX();
	double GetLandY();
	double GetLaunchTime();
	double GetLandTime();
private:
	double launchX;
	double launchY;
	double landX;
	double landY;
	double launchTime;
	double landTime;
};

class MTTDLL_EXPORT CMTTSpots
{
public:
	CMTTSpots();
	~CMTTSpots();
	int SetNumSpots(int _numSpots);
	int GetNumSpots();
	void SetSpot(int spotNum, double launchX, double launchY, double landX, double landY, double launchTime, double landTime);
	CMTTSpot *GetSpot(int spotNum);
private:
	int numSpots;
	CMTTSpot *spots;
};

class MTTDLL_EXPORT CMinTravelTime
{
public:
	static const int RATEOFSPREAD = 0;
	static const int INFLUENCE = 1;
	static const int ARRIVALTIME = 2;
	static const int INTENSITYMAP = 3;
	static const int FLOWPATHS = 4;
	static const int MAJORPATHS = 5;
	//static const int ARRIVALCONTOUR = 6;
	CMinTravelTime();
	~CMinTravelTime();
	int ResetMTT();
	CMTT *mtt;
	int SetLandscapeFile(char *_lcpFileName);
	double SetResolution(double res);
	int SetAnalysisArea(double tEast, double tWest, double tNorth, double tSouth);
	int SetIgnitionPoint(double x, double y);
	int SetIgnition(char *shapeFileName);
	int SetBarriers(char *shapeFileName);
	int SetFillBarriers(int set);
	long SetMaxSimTime(long minutes = 0);
	long SetPathInterval(long interval = 500);
	int SetNumProcessors(int numThreads = 1);
	int SetStartProcessor(int _procNum);
	int GetStartProcessor();
	int SetNumLat(int _numLat);
	int GetNumLat();
	int SetNumVert(int _numVert);
	int GetNumVert();
	bool SetTrackSpots(bool _track);
	bool GetTrackSpots();
	double SetSpotProbability(double _spotProb);
	double GetSpotProbability();
	int SetSpotDelay(int minutes);
	int GetSpotDelay();
	int SetSpottingSeed(int seed);
	int GetSpottingSeed();
	double GetResolution();
	long GetNumCols();
	long GetNumRows();
	double GetWest();
	double GetSouth();
	double GetEast();
	double GetNorth();
	int SetGriddedWindsFiles(char* gwSpeed, char* gwDir);

	CFlamMap *GetFlamMap();
	int LoadMTTInputs(char *_inputFile);
	int LoadTOMInputs(char *_inputFile);
	const char *CommandFileError(int i_ErrNum); 
	const char *GetErrorMessage(int errNum);
	void SetDisableFlows(int disable);
	void SetDisableMajorPaths(int disable);
	int CanLaunchMTT(void);
	int CanLaunchTOM(void);
	int LaunchMTT(void);
	int LaunchTOM(void);
	//int LaunchVariableWeatherMTT(BurnDay* _burndays, int _nBurnDays);
	int LaunchVariableWeatherMTT(std::vector<CBurnDay> vbd);
	int SetFlamMap(CFlamMap *tFlamMap);
	bool SetRiskGrids(float **_grid, float **_intensity, double  *_spotProbability, double *_spotIgnitionDelay, int _NumGrids);
//	bool SetTileStack(TileStack* _pTileStack);
	//bool SetNetworkFlowGrid(int *grid, int nRows, int nCols);
	//bool SetBurnDays(BurnDay *_bd, int _nBD);
	int LaunchMTTQuick();
	double GetMTTProgress(void);
	int CancelMTT(void);
	int SetSuppressionFactor(double factor);

	int WriteROSGrid(char *trgName);
	int WriteArrivalTimeGrid(char *trgName);
	int WriteFlameLengthGrid(char *trgName);
	int WriteFliMapGrid(char *trgName);
	int WriteInfluenceGrid(char *trgName);
	int WriteROSGridBinary(char *trgName);
	int WriteArrivalTimeGridBinary(char *trgName);
	int WriteFliMapGridBinary(char *trgName);
	int WriteInfluenceGridBinary(char *trgName);
	int WriteFlamMapOutputLayerBinary(int Layer, char *trgName);
	int WriteFlamMapOutputLayerAscii(int Layer, char *trgName);
	int WriteIgnitionGrid(char *trgName);
	int WritePerimeter(char* trgName);
	int WritePerimeterShapeFile(char* trgName);
	int WritePerimeterSpatialite(char* trgName);
	int WriteFlowPathsShapeFile(char *trgName);
	int WriteMajorPathsShapeFile(char *trgName);
	int WriteEmberCSV( char *trgName);
	int WriteEmberShapeFile( char *trgName);
	int WriteWindVectorKML(char *fileNamePath, double resolution);
	double GetWindVectorKMLResolution();
	double GetTotalRunTime();
	int WriteTimingsFile(char *trgName);
	int WriteTreatOpportunitiesGrid(char *trgName);
	int WriteTreatmentGrid(char *trgName);
	int WriteTreatROSGrid(char *trgName);
	int WriteTreatInfluenceGrid(char *trgName);
	int WriteTreatArrivalTimeGrid(char *trgName);
	int WriteTreatFliMap(char *trgName);
	int WriteTreatFlowPaths(char *trgName);
	int WriteTreatMajorPaths(char *trgName);
	int WriteTreatArrivalTimeContour(char *trgName);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);

	//grid based output
	float *GetFlamMapOutputLayer(int Layer);
	double *GetROSGrid();
	double *GetArrivalTimeGrid();
	//float *GetROSGrid();
	//float *GetArrivalTimeGrid();
	float *GetFliMapGrid();
	double *GetInfluenceGrid();
	double *GetFlameLengthGrid();
	//float *GetInfluenceGrid();
	float *GetIgnitionGrid();
	int SetIgnitionGrid(float *grid, int nRows, int nCols);
	//TOM output Grids
	float *GetTreatOpportunitiesGrid();
	double *GetTreatmentGrid();
	double *GetTreatROSGrid();
	double *GetTreatInfluenceGrid();
	double *GetTreatArrivalTimeGrid();
	float *GetTreatFliMap();
	//float *GetTreatmentsGrid();
	//float *GetTreatOpportunitiesGrid();

	//vector based output
	long GetNumFlowVecs();
	long GetNumFlowVecPoints(long vecNum);
	float GetFlowVecPointX(long vecNum, long pointNum);
	float GetFlowVecPointY(long vecNum, long pointNum);
	long GetNumMajorVecs();
	long GetNumMajorVecPoints(long vecNum);
	float GetMajorVecPointX(long vecNum, long pointNum);
	float GetMajorVecPointY(long vecNum, long pointNum);
	//vector based TOM output
	long GetNumTreatFlowVecs();
	long GetNumTreatFlowVecPoints(long vecNum);
	float GetTreatFlowVecPointX(long vecNum, long pointNum);
	float GetTreatFlowVecPointY(long vecNum, long pointNum);
	long GetNumTreatMajorVecs();
	long GetNumTreatMajorVecPoints(long vecNum);
	float GetTreatMajorVecPointX(long vecNum, long pointNum);
	float GetTreatMajorVecPointY(long vecNum, long pointNum);
	CPerimeter *GetFirePerimeter(int newNum = -1);
	CMTTSpots *GetFireSpots(); //mtt owns them, caller must copy
	CMTTSpots* GetEmbers();//caller owns them and must delete them

private:
	//double *rosGrid;
	//double *arrivalTimeGrid;
	//float *rosGrid;
	//float *arrivalTimeGrid;
	float *fliMapGrid;
	double *influenceGrid;
	double *flameLengthGrid;
	//float *influenceGrid;
	float *ignitionGrid;
	double *treatmentGrid;
	float *treatOpportunitiesGrid;
	CPerimeter *perimeter;
	CMTTSpots *mttSpots;
	std::string m_inputsFileName;

};