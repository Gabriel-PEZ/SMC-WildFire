#ifdef _MSC_VER
#ifdef FSPROSERVER_EXPORTS
#define FSPROSERVER_API __declspec(dllexport)
#else
#define FSPROSERVER_API __declspec(dllimport)
#endif
#else
#define FSPROSERVER_API
#endif

#ifndef LONG_64
#ifdef _MSC_VER
#define LONG_64 __int64
#else
#define LONG_64 long
#endif
#endif

#include <vector>

//forward declarations
class CDayType;
class CFireStream;
class CBinaryGrid;
class CFlamMap;
class CMinTravelTime;
class CPerimeter;

/*struct PerimeterItem
{
	int id;
	CPerimeter *perim;
};*/

class Perimeter4RPC
{
public:
	Perimeter4RPC();
	~Perimeter4RPC();
	int nPoints;
	int nLines;
	int *partStarts;
	float *pXvals;
	float *pYvals;
};

//typedef list<PerimeterItem *> PerimeterList;


// This class is exported from the FSProServer.dll
class FSPROSERVER_API CFSProServer 
{
public:
	CFSProServer();
	~CFSProServer();
	
	int SetLandscapeFile(char *lcpName, double newRes = 0.0);
	int SetIgnition(CBinaryGrid *ignitGrid);
	//int SetNumDaytypes(int n); // Set number of DayTypes
	//int SetDayType(int dtLoc, CDayType *_dayType);//Set an individual DayType
	//int SetDayTypes(int n, CDayType *_dayTypes);//Set all DayTypes
	int SetDayTypes(std::vector<CDayType> vDayTypes);
	int GetNumDayTypes();//Get number of DayTypes
	CDayType GetDayType(int dtLoc);//Get a specific DayType
	bool SetCalcPerims(bool set);
	bool GetCalcPerims();
	bool SetCalcFLI(bool set);
	bool GetCalcFLI();
	//Process Control
	//int RunFires();
	void SetMaxFires(int maxFires);
	void SetSpottingSeed(int seed);
//run the fire, returns an fireID for future use
	int RunFire(int loc, CFireStream *fireStream, int procNum);
	//int GetNumArrivalGrids();
	int CancelAllFires();
	int CancelFire(int fireID);

	//output functions
	long GetOutputRows();
	long GetOutputCols();
	long GetOutputWest();
	long GetOutputSouth();
	long GetOutputRes();
	//getFireGrid, populates a pre-allocated grid of fire (0 = Barrier/Ignition, 1 = burned cell, -9999 = NODATA)
	int GetFireGrid(int loc, long nRows, long nCols, double west, double south, double res, int **grid);
	int GetSuppressionFireGrid(int loc, long nRows, long nCols, double west, double south, double res, int **grid);
	int GetFireArrivalTimeGrid(int loc, long nRows, long nCols, double west, double south, double res, float *grid);
	int GetFireFlamelengthGrid(int loc, long nRows, long nCols, double west, double south, double res, float *grid);
	//CPerimeter * GetFirePerimeter(int fireID);
	Perimeter4RPC *GetFirePerimeter4RPC(int loc);
	void DestroyPerim4RPC(Perimeter4RPC *trg);
	int SetWindNinjaResolution(double wnRes);
	int RunFlamMap();
	double CellSize;
	long NumRows;
	long NumCols;
	double West;
	double East;
	double North;
	double South;
private:
	//int RunFlamMapDayType(int dayType);
	bool Risk_ReadFlamMapData(long Number, CFlamMap *pFlamMap);
	bool Risk_RotateGrid(long Number, double angledeg, double resolution, bool LastOne);
	void AddArrivalTimeGrid(int loc, CMinTravelTime *pMTT);
	void AddFLIGrid(int loc, CFireStream *fireStream, CMinTravelTime *pMTT);
	void AddPerimeter(int loc, CMinTravelTime *pMTT);
	CFlamMap *pFlamMap;
	CBinaryGrid *pIgnitionGrid;
	float **Intensity;
	float **Grid;
    double *SpotProbability;//=0;
    double *SpotIgnitionDelay;//=0;
	bool ShouldCancel;
	bool AllocGrid(long Number);
	void FreeDayTypes();
	//int numDayTypes;
	//CDayType *dayTypes;
	std::vector<CDayType> m_vDayTypes;
	double OldNorth;
	double OldSouth;
	double OldEast;
	double OldWest;
	long OldNumRows;
	long OldNumCols;
	double RotationAngle;
	double OldCellSize;
	//GridList arrivalGrids;
	//PerimeterList perimList;
	int m_MaxFires;
	CBinaryGrid **arrivalGridArray;
	CBinaryGrid **flGridArray;
	CPerimeter **perimArray;
	bool bWantPerims;
	bool bWantFLI;
	double windNinjaRes;
	int spottingSeed;
};

