#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define TRIG_PIN 4
#define ECHO_PIN 2
#define RAIN_SENSOR_PIN 32
#define RELAY_PIN 14

#define RAIN_THRESHOLD 2000

const char* ssid = "ssid";
const char* password = "pswd";

String serverName = "http://10.191.250.20:5000/sensor";

long duration;
float distance;

bool pumpState = false;

void setup() {

Serial.begin(115200);

pinMode(TRIG_PIN, OUTPUT);
pinMode(ECHO_PIN, INPUT);
pinMode(RELAY_PIN, OUTPUT);

digitalWrite(RELAY_PIN, HIGH);

WiFi.begin(ssid, password);

Serial.print("Connecting to WiFi");

while (WiFi.status() != WL_CONNECTED) {
delay(1000);
Serial.print(".");
}

Serial.println();
Serial.println("WiFi Connected");
}


void loop() {

digitalWrite(TRIG_PIN, LOW);
delayMicroseconds(2);

digitalWrite(TRIG_PIN, HIGH);
delayMicroseconds(10);
digitalWrite(TRIG_PIN, LOW);

duration = pulseIn(ECHO_PIN, HIGH, 30000);

if(duration == 0){
Serial.println("Ultrasonic error");
return;
}

distance = duration * 0.0343 / 2;

int rainValue = analogRead(RAIN_SENSOR_PIN);

Serial.print("Water Distance: ");
Serial.println(distance);

Serial.print("Rain Sensor: ");
Serial.println(rainValue);


if(WiFi.status() == WL_CONNECTED){

WiFiClient client;
HTTPClient http;

http.begin(client, serverName);
http.addHeader("Content-Type", "application/json");

String jsonData = "{";
jsonData += "\"rain\":" + String(rainValue) + ",";
jsonData += "\"water\":" + String(distance);
jsonData += "}";

int httpResponseCode = http.POST(jsonData);

if(httpResponseCode > 0){

String payload = http.getString();

DynamicJsonDocument doc(1024);
deserializeJson(doc, payload);

float temperature = doc["temperature"];
float humidity = doc["humidity"];
float pressure = doc["pressure"];

Serial.print("Temperature: ");
Serial.println(temperature);

Serial.print("Pressure: ");
Serial.println(pressure);


float waterFactor = 0;
float rainFactor = 0;
float pressureFactor = 0;


if(distance <= 3) waterFactor = 100;
else if(distance <= 6) waterFactor = 60;
else waterFactor = 20;


if(rainValue < RAIN_THRESHOLD) rainFactor = 80;
else rainFactor = 10;


pressureFactor = (1015 - pressure) * 5;

if(pressureFactor < 0) pressureFactor = 0;
if(pressureFactor > 100) pressureFactor = 100;


float riskScore =
0.5 * waterFactor +
0.3 * rainFactor +
0.2 * pressureFactor;

Serial.print("Flood Risk Score: ");
Serial.println(riskScore);


if(riskScore >= 70){

Serial.println("🚨 FLOOD DANGER");

digitalWrite(RELAY_PIN, LOW);
pumpState = true;

}

else if(riskScore >= 40){

Serial.println("⚠ FLOOD WARNING");

digitalWrite(RELAY_PIN, HIGH);
pumpState = false;

}

else{

Serial.println("SAFE");

digitalWrite(RELAY_PIN, HIGH);
pumpState = false;

}

}

http.end();

}

Serial.println("------------------------");

delay(8000);

}
