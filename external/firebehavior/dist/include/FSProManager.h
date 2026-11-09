//CFSProManager Class
//Class manages inputs and outputs to CFSProServer objects

#pragma once

#ifdef _MSC_VER
#ifdef FSPROMANAGER_EXPORTS 
#define FSPROMANAGERDLL_EXPORT __declspec(dllexport) 
#else 
#define FSPROMANAGERDLL_EXPORT __declspec(dllimport) 
#endif 
#else
#define FSPROMANAGERDLL_EXPORT
#endif 

//#include "GridItem.h"
#include "CFireStream.h"
#include <time.h>
#include <mutex>
#include <vector>
#include "gdal_priv.h"


#define FSPRO_BURN_PROBABILITY				90
#define FSPRO_AVERAGE_FLAMELENGTH			91
#define FSPRO_AVERAGE_ARRIVAL_TIME			92
#define FSPRO_SUPPRESSION_BURN_PROBABILITY	93
#define FSPRO_IGNITION						94
#define FSPRO_FLP_0_2						95
#define FSPRO_FLP_2_4						96
#define FSPRO_FLP_4_6						97
#define FSPRO_FLP_6_8						98
#define FSPRO_FLP_8_12						99
#define FSPRO_FLP_12						100
#define FSPRO_CONDITIONAL_FLAMELENGTH       101
//forward declarations
//class CDayType;
//struct CFireStream;
class CBinaryGrid;
class CFlamMap;
class FSPROInputs;
class IBG;
class TimeSeriesInputs;
class SeverityGroup;
class CContourPerim;
class CFire;
class StatRep;

class FSPROMANAGERDLL_EXPORT CFSProManager
{
public:
	CFSProManager();
	~CFSProManager();

	int SetLandscapeFile(char *lcpName);
	char *GetLandscapeFileName();
	int LoadInputsFile(char *inFile);//load the FSPro inputs file
	char *GetErrorMessage(int errNum);//Ge error message with error code
	int GetNumFires();//get Number of fires
	CFireStream* GetFireStream(int _fireID);//get an individual fire stream
	int GetNumDayTypes();//Get number of DayTypes
	CDayType GetDayType(int dtLoc);//Get a specific DayType
	//int GetDayTypes(int n, CDayType *_dayTypes); // Populate a previously allocated DayType array
	CBinaryGrid *GetIgnitionGrid();
	//int GetIgnitionGrid(CBinaryGrid *pGrid);
	double GetResolution();
	int AddArrivalTimeGrid(int fireID, long nRows, long nCols, double west, double south, double res, float *grid);
	int BuildPerimeters();
	int AddPerimeter(GDALRasterBand* pBand, OGRLayerH hLayer, int loc, int fireID);
	int AddPerimeter(int fireID, int numPoints, int numParts, int *partStarts, float *pXvals, float *pYvals);
	//int AddSuppressionGrid(int fireID, long nRows, long nCols, double west, double south, double res, float *grid);
	int AddFlameLengthGrid(int fireID, long nRows, long nCols, double west, double south, double res, float *grid);
	int WriteBurnProbabilityGrid(char *trgName);
	int WriteIgnitionGrid(char *trgName);
	int WriteAverageFlameLengthGrid(char *trgName);
	int GetNumServers();
	int GetServerName(int serverNum, char *serverName, char *port);
	bool ClaimFire(int fireID);
	int FinalizeResults();
	int GetNumFiresToDo();
	int GetNumFiresComplete();
	int GetSavePerimeters();
	//int WritePerimeters(char* tName);
	int WritePerimetersGDAL(char* tName);
	int WriteOutputPrjFile(char *tName);
	int WriteEventCoverageReport (char cr_FN[]); 
	FSPROInputs *GetFSProInputs();
	double GetWindNinjaResolution();
	TimeSeriesInputs *GetTimeSeriesInputs();
	int GetFiresDuration();
	double ApplyContainment(long fireNum, CBinaryGrid *bg, double *DailyAc, int *maxProbDay);
	int SetMaxContainProb(long FireNum, double val, int _day, double _acres);
	double GetContainGreaterThan50Percent();
	double GetContainAverageMaxProb();
	double GetFinalFireSize(long FireNum);
	double GetMaxContainProb(long FireNum);
	int CritiqueLCP(char *trgName);
	int CritiquePDF(char *trgName);
	int WriteDailyAcres(char *trgName);
	int WriteContainSummary(char *trgName);
	int WriteSuppressionGrid(char *trgName);
	int WriteAverageTimeGrid(char *trgName);
	int WriteArrivalDayDistribution(char *trgName);
	int DidAnythingBurn();
	void CancelFSPro();
	bool GetCancel();
	int WriteDayTypes(char *trgName);
	int WriteFireStreams(char *trgName);
	//int WriteFinalFireSizeHistogram(char *_fileName, int width, int height);
	int WriteProcessTimeFile(char *trgName);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);
	int WriteFlpLayers(char* trgName);
	std::string GetVersion();
	//stats support functions
	int GetNumWindDirs();
	int GetNumWindSpeeds();
	int GetWindDir(int windDirClass);
	int GetWindSpeed(int windSpeedClass);

	double GetFireDailyAcres(int fire, int day);
	int GetFireERC(int fire, int day);
	int GetFireErcClass(int fire, int day);
	int GetFireWindSpeed(int fire, int day);
	int GetFireWindDir(int fire, int day);
	int GetNumBurndays();
	//retuns number of DayTypes read
	int LoadDayTypesFile(char*);
	//returns number of fire streams read
	int LoadFireStreamsFile(char*);
	std::vector<CDayType> GetDayTypes();
	int SetIgnitionAndBarrier(char* ignitFileName, char* barrierFileName);
private:
	std::mutex mutexClaimFire;
	std::mutex mutexCompleteFire;

	//CRITICAL_SECTION claimFireCS;
	//CRITICAL_SECTION completeFireCS;
	int GenerateFireStreams();//generates all the streams of DayTypes for numFires fires
	int GenerateDayTypes();//generates all the DayTypes for inputs
	CDayType GetDayType(int ERC, double WDir, double WSpd);
    int GetDayTypeLoc(int ERC, double WDir, double WSpd);
    int GetErcClass(int ERC);
	int GetBurnMinutesForERC(long ERC);
	//int SetNumDayTypes(int n); // Set number of DayTypes
	//int SetDayType(int dtLoc, CDayType *_dayType);//Set an individual DayType
	//int SetDayTypes(int n, CDayType *_dayTypes);//Set all DayTypes
	int CreateSeverityTable();
	int SetNumFiresToDo(int nSimsRequested);
	long numFiresToDo;
	long numFiresComplete;
	int numDayTypes;
	//CDayType *dayTypes;
	std::vector< CDayType> m_vDayTypes;
	long numFires;
	//CFireStream *fireStreams;
	std::vector<CFireStream> m_vFireStreams;
	std::string m_strInputsFile;
	void FreeDayTypes();
	void FreeFireStreams();
	CBinaryGrid *pIgnitionGrid;
	char m_lcpFileName[512];
	CFlamMap  *pFlamMap; 
	FSPROInputs *fsp;
	IBG *pIBG;
	TimeSeriesInputs *tsInputs;
	SeverityGroup **severityTable;
	//evc grid 
	int nEVCrows;
	int nEVCcols;
	double evcRes;
	double evcNorth;
	double evcSouth;
	double evcEast;
	double evcWest;
	int evcNODATA; 
	int **evcGrid;
	//watershed grid 
	int nWSrows;
	int nWScols;
	double wsRes;
	double wsNorth;
	double wsSouth;
	double wsEast;
	double wsWest;
	int wsNODATA; 
	int **wsGrid;
	CBinaryGrid **pArrivalGrids;
	//GridList arrivalGrids;
	CBinaryGrid **pFlameLengthGrids;
	//GridList flameLengthGrids;
	//GridList suppressionGrids;
	//CBinaryGrid **pSuppressionGrids;
	int numFiresClaimed;
	int *claimFireArray;
	double *finalFireSizes;
    CFire **firePerims;
	CContourPerim *ContourFinalPerim( CBinaryGrid *grid);
     StatRep  *pStatRep;    /* Output Fire Stat Report */
	float **outTimeFreq;
	float *outGrid;
	float *ContainFreq;
	int** flpCounts;
	long outTimeFreqDays;
	double *maxContainProbs;
	float **DailyAcres;
	int **ErcStreams;
	long nDAfires;
	long nDAdays;
	bool timberIgnition;
	double initialAcres;
	int NumFireSizes;
	int GetCurrentDay(CFireStream *fs, double CurTime);
	double GetEndTime(CFireStream *fs, int day);
	void AllocErcStreams(long _NumFires, long _numDays);
	void AllocDailyAcres(long _NumFires, long _numDays);
	void AccumulateDailyAcres(long FireNum, long day, float acres);
	void AllocFinalFireSizes(long _NumFires);
	void AllocMaxContainProbs(long _NumFires);
	void AllocFirePerims(bool doSave);

 	void CleanGrid(float *_grid);

	GDALDataset* m_pPerimDS;

	bool shouldCancel;
	clock_t startTime;
	clock_t endFiresTime;
	clock_t endTime;
	timespec tsStart;
	timespec tsFires;
	timespec tsEnd;
	std::chrono::duration<double> runTime;
	std::string m_strVersion;


};