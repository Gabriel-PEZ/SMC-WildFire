#include "CFireStream.h"
#include "CBinaryGrid.h"

//CDayType
void InitDayType(CDayType *dt);
void DestroyDayType(CDayType *dt);

//CFireStream
void InitFireStream(CFireStream *fs);
void DestroyFireStream(CFireStream *fs);
//void DisplayFireStream(CFireStream *fs);
void FreeFSDayTypes(CFireStream *fs);
int GetFSFireID(CFireStream *fs);
int GetFSNumBurnPeriods(CFireStream *fs);
int GetFSDayType(CFireStream *fs, int burnPeriod);
int SetFSFireID(CFireStream *fs, int id);
//int SetFSNumBurnPeriods(CFireStream *fs, int _numBurnPeriods);
//int SetFSDayType(CFireStream *fs, int burnPeriod, int dayTypeIndex);

//BinaryGrids
//void InitBinaryGrid(CBinaryGrid *bg);
//void CreateBinaryGrid(CBinaryGrid *bg, long rows, long cols, double cellRes, double llSouth, double llWest);
//CBinaryGrid *CopyBinaryGrid(CBinaryGrid *srcGrid);
//void SetBinaryGridCellValue(CBinaryGrid *bg, long row, long col, float val);
//void DestroyBinaryGrid(CBinaryGrid *bg);
//void FreeBGGrid(CBinaryGrid *bg);
//long GetBGNumRows(CBinaryGrid *bg);
//long GetBGNumCols(CBinaryGrid *bg);
//double GetBGWest(CBinaryGrid *bg);
//double GetBGSouth(CBinaryGrid *bg);
//double GetBGEast(CBinaryGrid *bg);
//double GetBGNorth(CBinaryGrid *bg);
//double GetBGRes(CBinaryGrid *bg);
//int WriteBGBinary(CBinaryGrid *bg, char *trgName, char *layerName, long layerType);
//int WriteBGAscii(CBinaryGrid *bg, char *trgName);

