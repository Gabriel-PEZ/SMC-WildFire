#pragma once
#ifndef LONG_64
#ifdef _MSC_VER
#define LONG_64 __int64
#else
#define LONG_64 long
#endif
#endif


class CBinaryGrid
{
	const float BG_NODATA_VAL = -9999.0;
public:
	CBinaryGrid();
	CBinaryGrid(const CBinaryGrid& rhs);
	~CBinaryGrid();
	void CreateBinaryGrid(LONG_64 rows, LONG_64 cols, double cellRes, double llY, double llX);
	LONG_64 GetNumRows();
	LONG_64 GetNumCols();
	double GetWest();
	double GetSouth();
	double GetEast();
	double GetNorth();
	double GetRes();
	bool SetCellValue(LONG_64 row, LONG_64 col, float val);
	float GetCellValue(LONG_64 row, LONG_64 col);
	float* GetGrid();
private:
	LONG_64 nRows;
	LONG_64 nCols;
	double west;
	double south;
	double res;
	float* grid;

};

