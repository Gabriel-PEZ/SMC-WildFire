#include <vector>
#include "CDayType.h"
#pragma once

class CFireStream
{
public:
	CFireStream();
	CFireStream(const CFireStream& rhs);
	~CFireStream();
	int fireID;
	std::vector<CDayType> vDayTypes;
	double GetBurnMinutes();
	double burnMinutes;
	double acres;
	double runTime;
	int spottingSeedUsed;

  private:
	bool operator > (const CFireStream& rhs) const
	{
		return (burnMinutes > rhs.burnMinutes);
	}
};
