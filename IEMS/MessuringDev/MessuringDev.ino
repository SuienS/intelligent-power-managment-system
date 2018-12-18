
#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include "ACS712IEMSCurSensor.h"
/*
==========================================================
    Current Measuring Code for IEMS Current Measurer
    by Rammuni Ravidu Suien Silva
    IIT No - 2016134
    UoW No - 16267097
==========================================================
*/

/*
-----------------------------------------------------------
    This Arduino code calculates using methods in 
    ACS712IEMSCurSensor.cpp .
    This also sends, revtrieve, update, and manipulate
    data from and to Firebase. Turning devices on and off
    will also happens here. This connects to WiFi in order
    to achieve mentioned tasks
-----------------------------------------------------------

*/
const String dID = "D000";              // This is the unique device ID
const String uID = "devices/D000/user"; // In this path in the firebase device will be able to find its user
//Setting up pins
static const uint8_t D0 = 16;
const int relay = D0;

//Variables needed for calculations
float seconds[300]; // Array to save usage second by second
float mins5[12];    // Array to save 5-mins sets for an hour
float hours[12];    // Array to save hours for 12 hours
int secCount = 0;   // Index for seconds array
int min5Count = 0;  // Index for 5-min array
int hourCount = 0; // Index for hours array
int hours12Count = 0;
int ONstate = 0;       // For saving on off state
String ONstatePath = "devices/D000/power";   // Path for saving on off state in firebase
String totPath = "usage/" + dID + "/watts";   // Path for saving current usage in firebase
String allDevPath = "users/" + uID + "/home/allDeviceUsage/"; // Path for saving all current usage in firebase
String hoursPath;
String hours12Path;

// Variables need for calculating time periods
unsigned long startTime5min = 0;
unsigned long startTimeHour = 0;

// Firebase and wifi authentications
#define FIREBASE_HOST "swatt-d1414.firebaseio.com"
#define FIREBASE_AUTH "ZYYUtBV7OMH9biCZ6K0hghkEx1XIj1G56qdgHQQn"
#define WLAN_SSID "Connection Failed..."
#define WLAN_PASSWORD "Suien0772175682"

// Setting up the sensor using our library
ACS712IEMSCurSensor IEMSsensor(20, A0);

void setup()
{
  Serial.begin(9600);
  pinMode(relay, OUTPUT);
  digitalWrite(relay, HIGH); // 
  Serial.println("Calibrating the IEMSSensor");
  // This line caliberates sensor to make sure no current meassures while the sensor is in idle
  // It helpto improve the accuracy
  IEMSsensor.calibrateSensor();
  Serial.println("Done!");

  //Starting up the WiFi Connection
  WiFi.begin(WLAN_SSID, WLAN_PASSWORD);
  Serial.print("Connecting to the WiFi");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print("|");
    delay(500);
  }
  Serial.println();
  Serial.print("Successfully Connected: ");
  Serial.println(WiFi.localIP());
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  digitalWrite(relay, HIGH);
  Firebase.setInt(ONstatePath, 0);
  // Setting firebase paths 
  hoursPath = "usage/" + dID + "/hours/";
  hours12Path = "usage/" + dID + "/12hourSet/";

  startTime5min = millis();
  startTimeHour = millis();
}

void loop()
{
  if (String(Firebase.getString(String("devices/") + dID + String("/user"))) == "")
  {
    Serial.println(String("Non-Registered"));
    delay(2000);
    return;
  }

  // Setting the volatage of our current 
  // As in Sri Lanka this is set to 230V
  float AC_Voltage = 230;

  // Here it calculates the current flowing through the sensor
  // The Frequency of the AC Current is set to 52Hz as it is the average in Sri Lanka
  float I = (IEMSsensor.getElectricity() / 1.08);

  // Below is the equation to calculate the power   
  // Power(Watts) = Voltage(Volts) x Current(Amperes)
  float Power = AC_Voltage * I;

  Serial.println(String("I = ") + I + " A");
  Serial.println(String("P = ") + Power + " Watts");

  // Updating Value
  Firebase.setFloat(totPath, Power);

  seconds[secCount] = Power;
  Serial.println(secCount);
  secCount++;
  // Updating 5-min usage values to the firebase Device-vice
  if ((millis() - startTime5min) > 300050)
  {
    startTime5min = millis();
    for (int i = 0; i < 300; i++)
    {
      mins5[min5Count] += seconds[i];
    }
    mins5[min5Count] = (mins5[min5Count]/secCount) * (300/3600); //Calculating usage for 5mins in watt hours
    secCount = 0;
    min5Count++;
    // Updating Hour usage values to the firebase Device-vice
    if ((millis() - startTimeHour) > 3600000)
    {
      startTimeHour = millis();
      float hourTot = 0;
      for (int k = 0; k < 12; k++)
      {
        hourTot += mins5[k];
      }
      min5Count = 0;
      Firebase.setFloat(hoursPath + hourCount, hourTot);
      Firebase.setFloat(allDevPath + hourCount, hourTot);      
      hourCount++;
      // Updating 12-Hour usage values to the firebase Device-vice
      if (hourCount == 12)
      {
        hourCount = 0;
        Firebase.setFloat(hours12Path + hours12Count, hourTot);
        hours12Count++;
      }
    }
  }
  // Hndling Firebase Errors
  if (Firebase.failed())
  {
    Serial.print("Setting data failed:");
    Serial.println("Error : " + Firebase.error());
    return;
  }

  // Getting on/off state from firebase
  if (Firebase.getInt(ONstatePath) == 1)
  {
    Serial.println("Bulb On");
    digitalWrite(relay, LOW); // Setting the device on
  }
  else if (Firebase.getInt(ONstatePath) == 0)
  {
    Serial.println("Bulb Off");
    digitalWrite(relay, HIGH); // Setting the device off
  }
  // Getting on/off state from the firebase
  ONstate = Firebase.getInt(ONstatePath);
}
