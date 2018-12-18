#include "ACS712IEMSCurSensor.h"
/*
==============================================
	IEMS ACS712 Current Messuring Arduino
	by Rammuni Ravidu Suien Silva
	IIT No - 2016314
	UoW No - 16267097
============================================== 
*/

/*
	These methods helps to messure the AC current of a device
	All the calculations which needs in order to calculate the
	current usage which passes by our device will happen here. 
*/
ACS712IEMSCurSensor::ACS712IEMSCurSensor(int model, uint8_t inPin) {
	pinUsing = inPin;
	// Switching to different models of the ohms
	switch (model) {
		case 5:
			ohms = 0.185;
			break;
		case 20:
			ohms = 0.100;
			break;
		case 30:
			ohms = 0.066;
			break;
	}
}

//This method calibrates the sensor to make sure that no current is measured when the sensor is in idle
int ACS712IEMSCurSensor::calibrateSensor() {
	uint16_t read = 0;
	for (int i = 0; i < 10; i++) {
		read += analogRead(pinUsing);
	}
	adjustedNeutralPoint = read / 10; //getting the avg
	return adjustedNeutralPoint;
}

//Setting above mentioned calibration
void ACS712IEMSCurSensor::setadjustedNeutralPointPoint(int adjustedNeutral) {
	adjustedNeutralPoint = adjustedNeutral;
}

//Messuring the electricity
float ACS712IEMSCurSensor::getElectricity() {
	uint16_t fr = 52; //frequency of the current
	uint32_t time_dif = 1000000 / fr; //calculating time for one rotation
	uint32_t I_all = 0;
	uint32_t cnt = 0;
	int32_t I_cur;

	uint32_t time_start = micros(); //Messures the time periods
	while (micros() - time_start < time_dif) {
		I_cur = analogRead(pinUsing) - adjustedNeutralPoint; //adjusting messurment
		I_all += I_cur * I_cur;
		cnt++;
	}

	//Equation for finding root mean squared current
	float I_root_mean_square = sqrt(I_all / cnt) / 1023.0 * 5.0 / ohms;
	return I_root_mean_square;
}

