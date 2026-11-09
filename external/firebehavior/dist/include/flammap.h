//FlamMap DLL header file
//Exported routines for FlamMap.dll
#pragma once
#include <vector>

#ifdef _MSC_VER
#ifdef BUILD_FLAMMAPDLL 
#define FLAMMAPDLL_EXPORT __declspec(dllexport) 
#else 
#define FLAMMAPDLL_EXPORT __declspec(dllimport) 
#endif
#else
#define FLAMMAPDLL_EXPORT
#endif 

//#include <windows.h>
//#include <windef.h>
#ifndef BOOL
typedef int                 BOOL;
#endif

#ifndef COLORREF
typedef unsigned long   COLORREF;
#endif

const int MAX_FMP_PATH = 512;
#define NODATA_VAL -9999.0
#define MAX_CATS 100
//native FLamMap Layers
typedef enum LcpLayers{ELEV = 0, SLOPE = 1, ASPECT = 2, FUEL = 3, COVER = 4, HEIGHT = 5, BASE_HEIGHT = 6, BULK_DENSITY = 7, 
	DUFF = 8, WOODY = 9} LCP_LAYER;
typedef enum FlamMapRunState{Stopped = 0, Loading=1, WindNinja = 2, Conditioning = 3, FireBehavior = 4, Complete = 5} FLAMMAPRUNSTATE;

#define NUM_STATICOUTPUTS		20
//output layers available
#define FLAMELENGTH 	0
#define SPREADRATE 		1
#define INTENSITY 		2
#define HEATAREA		3
#define CROWNSTATE 		4
#define SOLARRADIATION 	5
#define FUELMOISTURE1	6
#define FUELMOISTURE10	7
#define MIDFLAME		8
#define HORIZRATE		9
#define MAXSPREADDIR	10
#define ELLIPSEDIM_A	11
#define ELLIPSEDIM_B	12
#define ELLIPSEDIM_C	13
#define MAXSPOT         14
#define FUELMOISTURE100 15
#define FUELMOISTURE1000 16
#define CROWNFRACTIONBURNED    17
#define TORCHINGINDEX    18
#define CROWNINGINDEX    19
#define MAXSPOT_DIR     20
#define MAXSPOT_DX      21
#define WINDDIRGRID      22
#define WINDSPEEDGRID    23

//forward declaration
class FlamMap;
class CLegendData;


class FLAMMAPDLL_EXPORT CFlamMap
{
public:
	CFlamMap();
	~CFlamMap();

/* FuelCondDLL <---- here to identify and search on any code changes */
/* for Conditioning DLL  */
/* Functions gets error message back when using the DLL */
   char * Get_CondDLLErrMes();


/*.....................................................*/
/* MCR - Moisture Conditioning Reuse and related stuff */
 // void MCR_Copy(CFlamMap *from);
  void  MCR_Init (); 
  
 int FSPRo_ConditionInputs (char cr_PthFN[]); 

 // bool   WindNinjaRun ( int *ai_Err); 
  char * WindNinjaError ( int i_Err); 


/* WNS WindNinja Save ......................... */
  float **Get_windDirGrid (); 
  float **Get_windSpdGrid ();    
  bool has_GriddedWinds (); 
  bool GridWindRowCol (int *Rows, int *Cols); 
 
   int CommandFileLoad(char cr_PthFN[]);
   char *CommandFileError(int i_ErrNum); 
	char *GetErrorMessage(int errNum);

	
  void GetWindCorners (double *X, double *Y);
  void AllocWindGrids(long wndRows, long wndCols, double wndRes, double wndXLL, double wndYLL);
  void SetWindGrids(long wndRows, long wndCols, double wndRes, double wndXLL, double wndYLL, float *pDirs, float *pSpeeds);


	//initialization, associate with a landscape file
	int SetLandscapeFile(char *_lcpFileName);
	char *GetLandscapeFileName();
	int SetUseDiskForLCP(int set);
	long GetNumCols();
	long GetNumRows();
	double GetWest();
	double GetSouth();
	double GetEast();
	double GetNorth();
	double GetCellSize();
	float GetLayerValue(int _layer, double east, double north);
	float GetLayerValueByCell(int _layer, int col, int row);
	int GetUnits(int _layer);
	bool IsFuelTimber(int fuel);
	//resample landscape at greater resolution for FSPro
	int ResampleLandscape(double NewRes);
	//write a resampled landscape at greater resolution
	int WriteResampledLandscape(char *trgName, double NewRes);
	//create a new treated landscape given this landscape, an Ideal landscape, and a treatment grid (mask)
	int CreateTreatedLandscape(char *idealLCP, char *treatGridName, char *treatedLandscapeName);
	int SetAnalysisArea(double tEast, double tWest, double tNorth, double tSouth);

	int TrimLandscape();
	int SetNoBurnMask(int *noBurnMask);
	//calculation resolution
	double SetCalculationResolution(double _resolution);
	double GetCalculationResolution();

	int SetStartProcessor(int _procNum);
	int GetStartProcessor();
	//number of threads
	int SetNumberThreads(int _numThreads);
	int GetNumberThreads();
	int GetNumberMTTThreads();//get MTT Threads from Inputs file...
	double GetMTT_SpotProbability();//get MTT Spot Probability from Inputs file...
	int GetMTT_SpotDelay();//get MTT Spot Delay from Inputs file...
	bool GetMTT_CapFlamelength();
	//fuel moistures
	int GetSpottingSeed();
	int SetFuelMoistureFile(char *_fuelMoistureFileName);
	char *GetFuelMoistureFile();
	int SetMoistures(int fuelModel, int _fm1, int _fm10, int _fm100,
		int _fmHerb, int _fmWoody, int _fm1000);
	int SetAllMoistures(int _fm1, int _fm10, int _fm100,
		int _fmHerb, int _fmWoody, int _fm1000);
	//custom fuels file name/url
	int SetCustomFuelsFile(char *_customFuelsFileName);
	char *GetCustomFuelsFile();

	//wind inputs
	int SetWindType(int _windType);
	int GetWindType();
	int SetConstWind(double _windSpeed, double _windDir);
	int SetWindDirection(double _windDir);
	double GetWindDirection();
	int SetWindSpeed(double _windSpeed);
	double GetWindSpeed();
	int SetWindVectorThemes(char *_speedFileName, char *_dirFileName);
	char *GetWindVectorSpeedFileName();
	char *GetWindVectorDirectionFileName();
	int SetWindNinjaOn(int res, int speed, int dir);
	//constant canopy height
	int SetCanopyHeight(double _height);
	double GetCanopyHeight();

	//constant canopy base height
	int SetCanopyBaseHeight(double _baseHeight);
	double GetCanopyBaseHeight();

	//constant bulk density
	int SetBulkDensity(double _bulkDensity);
	double GetBulkDensity();

	//foliar moisture content
	int SetFoliarMoistureContent(long _moisturePercent);
	double GetFoliarMoistureContent();

	//fuel moisture conditioning
	int SetUseFixedFuelMoistures(int _useFixedFuels);
	int GetUseFixedFuelMoistures();
	int SetWeatherFile(char *_wtrFileName);
	char *GetWeatherFile();
	int SetWindsFile(char *_wndFileName);
	char *GetWindsFile();
	int SetConditioningPeriod (int _startMonth, int _startDay, 
	                          	int _startHour, int _startMinute,
	                          	int _endMonth, int _endDay, 
	                          	int _endHour, int _endMinute);


	int GetConditioningStartMonth();
	int GetConditioningStartDay();
	int GetConditioningStartHour();
	int GetConditioningStartMinute();
	int GetConditioningEndMonth();
	int GetConditioningEndDay();
	int GetConditioningEndHour();
	int GetConditioningEndMinute();

	//crown fire calc type (default = Finney)
	int SetUseScottReinhardt(int _select);
	int GetUseScottReinhardt();

	//spread direction adjustments
	int SetSpreadDirectionFromNorth(int _select, double _degrees);
	int GetUseSpreadDirectionFromNorth();
	double GetSpreadDirectionFromNorth();

	//output memory or file based
	int SelectOutputReturnType(int _returnType); //0 = memory, 1 = files

	//outputs to calculate
	int SelectOutputLayer(int _layer, int _select);

	long GetTheme_DistanceUnits();

	//output retrieval
	const char *GetOutputLayerName32char(long layer, char *textBuf);
	const char *GetOutputLayerUnits(int _layer, char *_unitsStr);
	float GetOutputLayerVal(int Layer, int row, int col);
	float GetWindGridSpeedByCoord(double xCoord, double yCoord);
	float GetWindGridDirByCoord(double xCoord, double yCoord);
	float *GetOutputLayer(int _layer);
	char *GetOutputGridFileName(int _layer, char *buf, int bufLen);
	int WriteOutputLayerToDisk(int _layer, char *name);
	int WriteOutputLayerBinary(int _layer, char *name);
	int WriteOutputLayerGeoTiff(int _layer, char *name);
	int WriteAllOutputLayersGeoTiff(char *name);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);
	int WriteProjection(char *name);
	int WriteTimingsFile(char* name);
	//Process control
	int CanLaunchFlamMap();
	int LaunchFlamMap(int _runAsync);
	double QueryFlamMapProgress();
	double GetConditioningProgress();
	double GetWindNinjaProgress();
	double GetFireBehaviorProgress();
	bool ResetFlamMapProgress();
	int CancelFlamMap();
	void ResetBurn();
	void ResetAll();
	FLAMMAPRUNSTATE GetRunState();
	double GetTotalRunTime();
	int CritiqueTXT(char *FileName);
	int CritiquePDF(char *FileName);
	int CritiqueHTML(char *FileName);

	int GenerateImage(int _layer, char *_fileName);
	int GenerateLegendImage(int _layer, char *_fileName);
	int LoadFlamMapTextSettingsFile(char *FileName);
	int LoadFuelConversionFile(char *_fileName);  // returns the number of fuels models converted

	//MTT input helpers (Loaded from a FlamMap inputs file
	double GetMttResolution();
	int GetMttSimTime();
	int GetMttPathInterval();
	char *GetMttIgnitionFile();
	char *GetMttBarriersFile();
	int GetMttFillBarriers();
	double GetSuppressionFactor();
	//TOM input helpers  (Loaded from a FlamMap inputs file
	char *GetIdealLcpName();
	char *GetTOMIgnitionFileName();
	int GetTreatIterations();
	float GetTreatDimension();
	float GetTreatFraction();
	float GetTreatResolution();
	int GetTreatOpportunitiesOnly();

	//NODESPREAD additions
	int GetNodeSpreadNumLat();
	int GetNodeSpreadNumVert();
	//nodespread addtion for MemTile
	int GetNumTilesX();
	int GetNumTilesY();

	int GetTileSizeX();
	int GetTileSizeY();

	float GetMaxSpreadDistanceMultiplier();
 
	//Header Access helpers....
	long GetLayerHi(int layer);
	long GetLayerLo(int layer);
	int GetLayerHeaderValCount(int layer);
	long GetLayerHeaderVal(int layer, int loc);
	short GetLayerUnits(int layer);
	long GetNumWindRows();
	long GetNumWindCols();
	long GetWindsResolution();
	char * GetProjectionString();

	int WriteWindGeoTiff(char *fileName);
	//	int WriteWindNetCDF(char *fileName);
	// new wind vector -> kml   2011/09
	int WriteWindVectorKML(char *fileName, double resolution);
	double GetWindVectorKMLResolution();
	void  GWN_Set_SpeedDir (long WindSpeed, long WindDir);
	void  GWN_Set_NoSw (); 
	void  GWN_Set_YesSw (); 

	int SetGriddedWindsFiles(char *gwSpeed, char *gwDir);

	void   GWN_Set_Yes(
		float f_Resolution,
		float f_WindHeight,
		long l_procs,
		bool Diurnal,
		int i_Month, int i_Day, int i_Year,
		int i_Second, int i_Minute, int i_Hour, int i_TimeZone,
		float f_Temp, float f_CloudCover,
		float f_Longitude);
	void   GWN_Set_Yes(
		float f_Resolution,
		float f_WindHeight,
		long l_procs,
		bool Diurnal,
		int i_Month, int i_Day, int i_Year,
		int i_Second, int i_Minute, int i_Hour, char * str_TimeZone,
		float f_Temp, float f_CloudCover,
		float f_Longitude);

	 
	int ExportMoistureDataText(char *trgName);
	//calculates convergence angles at West Edge, Center, and East Edge of landscape
	std::vector<double> CalcLandscapeConvergenceAngles();
	bool GetConvergenceAngles(double angles[3]);
	const char* GetConvergenceRating();
	//returns vector of haversine distances (top (north), bottom(south), left(west), right(east)
	std::vector<double> GetEdgeHaversineDistances(); 
	int GetLatitude();

private:
	double ConvertWindSpeed(double windSpeed, int srcUnits, int destUnits);
	char m_strLCPName[MAX_FMP_PATH];
	char m_strCustFuelFileName[MAX_FMP_PATH];
	int m_outputsType;//0 = memory, 1 = files
	FlamMap *pFlamMap;
	bool m_runningFlamMap;
	bool m_moisturesSet;
	float *maxSpotDirLayer;
	float *maxSpotDxLayer;
	float *windNinjaDirLayer;
	float *windNinjaSpeedLayer;
	static const int nConvergenceClasses = 4;
	const char* convergenceRatings[nConvergenceClasses] = { "Excellent", "Fair", "Poor", "Invalid" };
};