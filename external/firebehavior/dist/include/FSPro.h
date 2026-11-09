#pragma once
#ifdef _MSC_VER
#ifdef FSPRO_EXPORTS
#define FSPRO_API __declspec(dllexport)
#else
#define FSPRO_API __declspec(dllimport)
#endif
#else
#define FSPRO_API
#endif
#include <string>

class CFSProManager;
class CFSProServer;

class FSPRO_API CFSPro
{
public:
	CFSPro();
	~CFSPro();

	std::string GetVersion();
	int SetLandscapeFile(char * trgName);
	int LoadInputsFile(char * trgName);
	int SetIgnitionAndBarrier(char* ignitFileName, char* barrierFileName);
	char *GetErrorMessage(int errNumber);
	int LaunchFSPro();
	int CancelFSPro();
	int GetNumFiresToDo();
	int GetNumFiresComplete();
	int GetFinalFireSize(int fireNum);
	double GetContainGreaterThan50Percent();
	double GetContainAverageMaxProb();
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
	double GetResolution();


	int WriteBurnProbabilityGrid(char *trgName);
	int WriteAverageFlameLengthGrid(char *trgName);
	int WriteIgnitionGrid(char *trgName);
	int WriteSuppressionGrid(char *trgName);
	int WriteAverageTimeGrid(char *trgName);
	int WriteOutputLayersGeoTiff(int _nLayers, int *_layers, char *name);

	int WritePerimeters(char *tName);
	int WriteArrivalDayDistribution(char *trgName);

	int WriteDailyAcres(char *trgName);
	int WriteContainSummary(char *trgName);
	int WriteProcessTimeFile(char *trgName);
	int WriteFireStreams(char *trgName);
	int WriteDayTypes(char *trgName);
	int WriteEventCoverageReport(char *trgName);
private:
	CFSProManager *manager;
	CFSProServer *server;
};