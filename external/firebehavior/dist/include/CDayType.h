#pragma once

class CDayType
{
public:
	CDayType();
	CDayType(const CDayType& rhs);
	~CDayType();
	//private:
	static const int nFuelModels = 257;
	int index;
	double fm1[nFuelModels];
	double fm10[nFuelModels];
	double fm100[nFuelModels];
	double fmHerb[nFuelModels];
	double fmWood[nFuelModels];
	double spotProbability;
	double spotDelay;
	double burnPeriod;
	double windSpeed;
	double windDir;
	int ercMin;
	int ercMax;
	int crownFireMethod; //0=Finney,1 = SR
private:
};

