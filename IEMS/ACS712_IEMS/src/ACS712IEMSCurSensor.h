#ifndef ACS712IEMSCurSensor_h
#define ACS712IEMSCurSensor_h

#include <Arduino.h>

class ACS712IEMSCurSensor {
public:
	ACS712IEMSCurSensor(int model, uint8_t inPin);
	int calibrateSensor();
	void setadjustedNeutralPointPoint(int adjustedNeutral);
	float getElectricity();

private:
	uint8_t pinUsing;
	int adjustedNeutralPoint = 512;
	float ohms;
};

#endif