/*
 * Projekt: Vibrationsüberwachung APS-Modellfabrik (MPU-6050) – OSF
 * Hardware: Arduino Uno, Ethernet Shield 2, MPU-6050 (I2C), 4-Ch Relais, 12V Ampel
 * Quelle: docs/05-hardware/arduino-r4-multisensor.md
 *
 * Bibliothek: MPU6050 (Library Manager: "MPU6050" by ElectronicCats)
 * I2C: SDA=A4, SCL=A5
 *
 * USE_MQTT: 0 = nur Serial, 1 = MQTT aktiv
 */
#define USE_MQTT 0   // 0 = stand-alone; 1 = MQTT (morgen mit LAN)

#include <Wire.h>
#include <math.h>
#include <MPU6050.h>

MPU6050 mpu;

// Verdrahtung: D7→IN1 (Grün), D8→IN2 (Gelb), D9→IN3 (Rot+Sirene) – D5/D6 vermeiden
// Relais aktiv-niedrig: LOW schaltet ein, HIGH schaltet aus
const int RELAY_GRUEN = 7;   // D7 → IN1 → NO1 → Grün
const int RELAY_GELB = 8;    // D8 → IN2 → NO2 → Gelb
const int RELAY_ROT = 9;     // D9 → IN3 → NO3 → Rot+Sirene

const int sampleInterval = 10;  // Abtastintervall ms (kurze Impulse erfassen)
const unsigned long DEBUG_INTERVAL = 500;  // Magnitude-Debug alle 500 ms
const unsigned long ROT_MIN_DURATION = 2000;   // Rot+Sirene mind. 2 s (kein Flackern)
const unsigned long GELB_MIN_DURATION = 2000;  // Gelb mind. 2 s (wie Rot, kein Flackern)

// Schwellen: Ruhe ~16,5k–17,5k. Leicht (Stimmgabel/klopfen) ~20k. Stark (Finger auf Sensor) ~30k.
const long MAG_THRESHOLD_GELB = 18500;  // Darüber: Gelb
const long MAG_THRESHOLD_ROT = 26500;   // Darüber: Rot+Sirene

unsigned long impulseCount = 0;
unsigned long lastSample = 0;
unsigned long lastDebugPrint = 0;
unsigned long redStartedAt = 0;    // Wann Rot zuletzt aktiviert (für Mindestdauer)
unsigned long yellowStartedAt = 0; // Wann Gelb zuletzt aktiviert (für Mindestdauer)
int lastLoggedLevel = -1;         // Für MQTT-Serial-Ausgabe (auch ohne USE_MQTT)
unsigned long lastLogTime = 0;

#if USE_MQTT
#include <Ethernet2.h>
#include <EthernetUdp.h>
#include <NTPClient.h>
#include <PubSubClient.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0x02 };  // Andere MAC als SW-420!
IPAddress ip(192, 168, 0, 96);  // Andere IP als SW-420 (95)
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

const char* MQTT_BROKER = "192.168.0.100";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "default";
const char* MQTT_PASS = "default";
const char* MQTT_CLIENT_ID = "arduino_mpu6050_1";
const char* TOPIC_STATE = "osf/arduino/vibration/mpu6050-1/state";
const char* TOPIC_CONNECTION = "osf/arduino/vibration/mpu6050-1/connection";

// MQTT: Publish bei Zustandsänderung + Heartbeat alle 15 s (Grün stabil)
const unsigned long MQTT_HEARTBEAT_INTERVAL = 15000;

// NTP: ISO 8601 timestamp (analog Fischertechnik/DSP)
EthernetUDP udp;
NTPClient timeClient(udp, "pool.ntp.org", 0, 60000);  // UTC, Update alle 60 s
const unsigned long NTP_SYNC_THRESHOLD = 1000000000;  // Unix epoch > Sept 2001 = sinnvoll synchronisiert

unsigned long lastReconnectAttempt = 0;
const unsigned long RECONNECT_INTERVAL = 5000;
int lastPublishedLevel = -1;   // 0=green, 1=yellow, 2=red, -1=nie
unsigned long lastPublishTime = 0;

EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

void mqttReconnect() {
  if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS, TOPIC_CONNECTION, 1, true, "{\"connectionState\":\"OFFLINE\"}")) {
    char payload[100];
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"mpu6050-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_CONNECTION, payload, true);
  }
}

/** ISO 8601 timestamp (analog Fischertechnik/DSP: "timestamp") – bei NTP-Sync, sonst "". */
void getTimestamp(char* buf, size_t len) {
  if (timeClient.getEpochTime() > NTP_SYNC_THRESHOLD) {
    String d = timeClient.getFormattedDate();
    String t = timeClient.getFormattedTime();
    snprintf(buf, len, "\"%sT%sZ\"", d.c_str(), t.c_str());
  } else {
    snprintf(buf, len, "\"\"");
  }
}

void publishState(const char* level, long magnitude) {
  Serial.print("MQTT: ");
  Serial.print(level);
  Serial.print(" mag=");
  Serial.print(magnitude);
  if (!mqttClient.connected()) {
    Serial.println(" (nicht verbunden, uebersprungen)");
    return;
  }
  Serial.println();
  bool detected = (level[0] != 'g');  // vibrationDetected: true bei yellow/red
  char tsBuf[32];
  getTimestamp(tsBuf, sizeof(tsBuf));
  char payload[200];
  snprintf(payload, sizeof(payload),
           "{\"vibrationLevel\":\"%s\",\"vibrationDetected\":%s,\"impulseCount\":%lu,\"magnitude\":%ld,\"timestamp\":%s}",
           level, detected ? "true" : "false", impulseCount, magnitude, tsBuf);
  mqttClient.publish(TOPIC_STATE, payload, true);
}
#endif

void setup() {
  Serial.begin(9600);
  Serial.println("Setup start...");  // Erste Ausgabe – prüft ob Serial funktioniert
  Serial.flush();

  Wire.begin();
  if (!mpu.testConnection()) {
    Serial.println("FEHLER: MPU-6050 nicht gefunden! I2C prüfen (SDA=A4, SCL=A5).");
    while (1) { delay(1000); }
  }
  mpu.initialize();
  mpu.setDLPFMode(MPU6050_DLPF_BW_256);  // Max. Bandbreite – Standard-DLPF dämpft Vibrationen
  Serial.println("MPU-6050 OK.");

  pinMode(LED_BUILTIN, OUTPUT);  // Pin 13 – Blink bei Serial-Ausgabe (Diagnose)
  pinMode(RELAY_GRUEN, OUTPUT);
  pinMode(RELAY_GELB, OUTPUT);
  pinMode(RELAY_ROT, OUTPUT);
  // Relais aktiv-niedrig: LOW=ein, HIGH=aus
  digitalWrite(RELAY_GRUEN, LOW);   // Grün ein = Ruhezustand
  digitalWrite(RELAY_GELB, HIGH);   // Gelb aus
  digitalWrite(RELAY_ROT, HIGH);    // Rot+Sirene aus

#if USE_MQTT
  Ethernet.begin(mac, ip, gateway, subnet);
  timeClient.begin();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(256);
  mqttClient.setSocketTimeout(3);  // 3 s statt 15 s – schneller Abbruch ohne LAN
  mqttReconnect();
  publishState("green", 0);
  lastPublishedLevel = 0;
  lastPublishTime = millis();
#endif

  Serial.println("System bereit. Warte auf Vibration...");
  Serial.flush();
}

long getAccelMagnitude() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  return (long)sqrt((long)ax * ax + (long)ay * ay + (long)az * az);
}

void loop() {
#if USE_MQTT
  timeClient.update();
  if (!mqttClient.connected()) {
    unsigned long now = millis();
    if (lastReconnectAttempt == 0 || now - lastReconnectAttempt >= RECONNECT_INTERVAL) {
      lastReconnectAttempt = now;
      mqttReconnect();
    }
  }
  mqttClient.loop();
#endif

  unsigned long now = millis();
  if (now - lastSample < sampleInterval) {
    delay(5);
    return;
  }
  lastSample = now;

  long mag = getAccelMagnitude();

  // Debug: Magnitude alle 500 ms ausgeben (Schwellenwert-Tuning)
  if (now - lastDebugPrint >= DEBUG_INTERVAL) {
    lastDebugPrint = now;
    digitalWrite(LED_BUILTIN, HIGH);  // LED an = Serial-Ausgabe sollte kommen
    Serial.print("mag=");
    Serial.print(mag);
    Serial.print(" (Gelb>");
    Serial.print(MAG_THRESHOLD_GELB);
    Serial.print(", Rot>");
    Serial.print(MAG_THRESHOLD_ROT);
    Serial.println(")");
    Serial.flush();
    digitalWrite(LED_BUILTIN, LOW);
  }

  // 3-Stufen-Ampel: Grün / Gelb / Rot+Sirene
  bool forceRed = (redStartedAt != 0 && (now - redStartedAt) < ROT_MIN_DURATION);
  bool forceYellow = (yellowStartedAt != 0 && (now - yellowStartedAt) < GELB_MIN_DURATION);

  int currentLevel;  // 0=green, 1=yellow, 2=red
  const char* levelStr;
  if (forceRed || mag >= MAG_THRESHOLD_ROT) {
    if (redStartedAt == 0) redStartedAt = now;
    yellowStartedAt = 0;  // Rot überschreibt Gelb
    impulseCount++;
    digitalWrite(RELAY_GRUEN, HIGH);
    digitalWrite(RELAY_GELB, HIGH);
    digitalWrite(RELAY_ROT, LOW);
    if (!forceRed) Serial.print("!!! ROT+SIRENE !!! mag=");
    if (!forceRed) Serial.println(mag);
    currentLevel = 2;
    levelStr = "red";
  } else if (forceYellow || mag >= MAG_THRESHOLD_GELB) {
    if (yellowStartedAt == 0) yellowStartedAt = now;
    redStartedAt = 0;
    digitalWrite(RELAY_GRUEN, HIGH);
    digitalWrite(RELAY_GELB, LOW);
    digitalWrite(RELAY_ROT, HIGH);
    currentLevel = 1;
    levelStr = "yellow";
  } else {
    redStartedAt = 0;
    yellowStartedAt = 0;
    digitalWrite(RELAY_GRUEN, LOW);
    digitalWrite(RELAY_GELB, HIGH);
    digitalWrite(RELAY_ROT, HIGH);
    currentLevel = 0;
    levelStr = "green";
  }

  // Serial: MQTT-Topic bei Zustandsänderung oder Heartbeat (Grün alle 15 s) – immer
  bool wouldPublish = (currentLevel != lastLoggedLevel) ||
      (currentLevel == 0 && (now - lastLogTime) >= 15000);
  if (wouldPublish) {
    Serial.print("MQTT wuerde: osf/arduino/vibration/mpu6050-1/state ");
    Serial.print(levelStr);
    Serial.print(" mag=");
    Serial.println(mag);
    lastLoggedLevel = currentLevel;
    lastLogTime = now;
  }

#if USE_MQTT
  bool shouldPublish = (currentLevel != lastPublishedLevel) ||
      (currentLevel == 0 && (now - lastPublishTime) >= MQTT_HEARTBEAT_INTERVAL);
  if (shouldPublish) {
    publishState(levelStr, mag);
    lastPublishedLevel = currentLevel;
    lastPublishTime = now;
  }
#endif
}
