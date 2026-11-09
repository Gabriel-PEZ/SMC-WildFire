//FARSITE.h
//Defines exported class for FARSITE.dll

#ifdef _MSC_VER
#ifdef BUILD_FARSITEDLL 
#define FARSITEDLL_EXPORT __declspec(dllexport) 
#else 
#define FARSITEDLL_EXPORT __declspec(dllimport) 
#endif 
#else
#define FARSITEDLL_EXPORT
#endif

class Farsite5;

enum FARSITE_GRID_OUTPUTS  
{
	FARSITE_ARRIVAL_TIME,
	FARSITE_CROWNFIRE,
	FARSITE_FLAMELENGTH,
	FARSITE_HEAT_PER_UNIT_AREA,
	FARSITE_IGNITION_GRID,
	FARSITE_INTENSITY,
	FARSITE_REACTION_INTENSITY,
	FARSITE_SPREAD_DIRECTION,
	FARSITE_SPREAD_RATE
};

class FARSITEDLL_EXPORT CFarsiteSpot
{
public:
	CFarsiteSpot();
	~CFarsiteSpot();
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

class FARSITEDLL_EXPORT CFarsiteSpots
{
public:
	CFarsiteSpots();
	~CFarsiteSpots();
	int SetNumSpots(int _numSpots);
	int GetNumSpots();
	void SetSpot(int spotNum, double launchX, double launchY, double landX, double landY, double launchTime, double landTime);
	CFarsiteSpot *GetSpot(int spotNum);
private:
	int numSpots;
	CFarsiteSpot *spots;
};

class FARSITEDLL_EXPORT CFarsite
{
public:
	CFarsite();
	~CFarsite();
	int SetLandscapeFile(char *_lcpFileName);
	int SetIgnition(char *shapeFileName);
	int SetBarriers(char *shapeFileName);
	int SetNumProcessors(int numThreads = 1);
	int SetStartProcessor(int _procNum);
	int GetStartProcessor();
	int GetNumIgnitionCells();
	int GetNumEdgeHits();
	char * GetProjectionString();
	int GetSpottingSeedUsed();
	int LoadFarsiteInputs(char *_inputFile);
	char *CommandFileError(int i_ErrNum); 
	char *GetErrorMessage(int errNum);
	
	double GetResolution();
	long GetNumCols();
	long GetNumRows();
	double GetWest();
	double GetSouth();
	double GetEast();
	double GetNorth();

	int CanLaunchFarsite(void);
	int LaunchFarsite(void);
  double GetFarsiteProgress();
  const char* GetFarsiteProgressText();
  int GetNumCurrentFires();
  int GetNumSpotFiresCreated();
  int GetNumSpotFires();
  CFarsiteSpots *GetFireSpots();
  // double GetFarsiteProgress(int *ai_RunStatus, char cr[]);
// int  GetFarsiteStatus (char cr[]); 
	int GetTotalVertices();
	bool GetSimTimes(int *yr, int *month, int *day, int *hour, int *min);
	int CancelFarsite(void);

	//output functions
	int WriteArrivalTimeGrid(char *trgName);
	int WriteIntensityGrid(char *trgName);
	int WriteFlameLengthGrid(char *trgName);
	int WriteSpreadRateGrid(char *trgName);
	int WriteSpreadDirectionGrid(char *trgName);
	int WriteHeatPerUnitAreaGrid(char *trgName);
	int WriteReactionIntensityGrid(char *trgName);
	int WriteCrownFireGrid(char *trgName);
	int WriteArrivalTimeGridBinary(char *trgName);
	int WriteIntensityGridBinary(char *trgName);
	int WriteFlameLengthGridBinary(char *trgName);
	int WriteSpreadRateGridBinary(char *trgName);
	int WriteSpreadDirectionGridBinary(char *trgName);
	int WriteHeatPerUnitAreaGridBinary(char *trgName);
	int WriteReactionIntensityGridBinary(char *trgName);
	int WriteCrownFireGridBinary(char *trgName);
	int WriteIgnitionGrid(char *trgName);
	int WritePerimetersShapeFile(char *trgName);
	int WriteTimingsFile(char *trgName);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);
	int WriteProjection(char *trgName);
	int WriteOneHours(char *trgName);
	int WriteTenHours(char *trgName);
	int WriteHundredHours(char *trgName);
	int WriteMoistData(char *trgName);
	int WriteSpotDataFile(char *trgName);
	int WriteSpotShapeFile(char *trgName); 
	int WriteSpotGrid(char *trgName);

	//memory output functions, FARSITE will handle cleaning memory
	double *GetArrivalTimeGrid();
	double *GetFlameLengthGrid();
	double *GetRateOfSpreadGrid();
	double *GetFireLineIntensityGrid();
	double *GetHeatPerUnitAreaGrid();
	double *GetSpreadDirectionGrid();
	double *GetCrownFireActivityGrid();
	double *GetReactionIntensityGrid();
	double *GetIgnitionGrid();

#ifdef FARSITE_USE_WINDNINJA
	int GetNumWindNinjaCols();
	int GetNumWindNinjaRows();
	double GetWindNinjaResolution();
	double GetWindNinjaXLLCorner();
	double GetWindNinjaYLLCorner();
	int GetNumWindNinjaGrids();
	float **GetWindNinjaSpeedGrid(int gridNum);
	short **GetWindNinjaDirGrid(int gridNum);
	int GetWindNinjaGridEndTimes(int nGrids, double *endTimeVals);
	int GetWindNinjaGridDateTimes(int nGrids, char **dateTimeStrings);
	int GetWindNinjaInput(int nGrids, float* speeds, short* dirs, int* tmps, int* ccs);
	int WriteWindSpeedGrid(int gridNum, char *fileName);
	int WriteWindDirGrid(int gridNum, char *fileName);
	int WriteWindGrids(char* fileName);
#endif
	int MergeShapes(char *shpName1, char *shpName2, char *outName);
	int MergeCSVs(char *csvName1, char *csvName2, char *outName);
	char *GetOutputLayerName(int _layer, char *output);
	char *GetOutputLayerUnits(int _layer, char *output);
private:
	Farsite5 *m_pFarsite;
	double *arrivalTimeGrid;
	double *flameLengthGrid;
	double *rateOfSpreadGrid;
	double *fireLineIntensityGrid;
	double *heatPerUnitAreaGrid;
	double *spreadDirectionGrid;
	double *crownFireActivityGrid;
	double *reactionIntensityGrid;
	double *ignitionGrid;
	CFarsiteSpots *pFarsiteSpots;

};