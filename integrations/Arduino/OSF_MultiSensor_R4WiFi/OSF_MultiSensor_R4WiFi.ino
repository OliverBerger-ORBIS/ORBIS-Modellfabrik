/*
 * Projekt: OSF Multi-Sensor – Arduino R4 WiFi
 * Sketch: OSF_MultiSensor_R4WiFi
 * Version: 1.1.0  (SemVer: MAJOR.MINOR.PATCH – bei Deployment anpassen)
 * Hardware: Arduino Uno R4 WiFi, MPU-6050 (I2C), SW-420 (D11), DHT11 (D12), Flamme (A1), MQ-2 Gas (A0), 4-Ch Relais, 12V Ampel
 * Quelle: docs/05-hardware/arduino-r4-multisensor.md
 *
 * Sensoren: MPU-6050 + SW-420 + DHT11 + Flammensensor + MQ-2 Gas. Gemeinsame Ampel (OR-Logik).
 * USE_MQTT: 0 = nur Serial, 1 = MQTT über WiFi
 */
#define SKETCH_VERSION "1.1.0"
#define USE_MQTT 1

/** Relais-Logik: 1 = aktiv-niedrig (LOW=ein, typisch). 0 = aktiv-hoch (HIGH=ein, manche Module). */
#define RELAY_ACTIVE_LOW 1
#define RELAY_ON  (RELAY_ACTIVE_LOW ? LOW : HIGH)
#define RELAY_OFF (RELAY_ACTIVE_LOW ? HIGH : LOW)
/** Relais-Test beim Start: 2s Grün, 2s Gelb, 2s Rot. 0 = deaktivieren. */
#define RELAY_STARTUP_TEST 1

#define SENSOR_ACTIVE_HIGH 1  // SW-420: 1 = HIGH bei Vibration, 0 = LOW bei Vibration

#include <Wire.h>
#include <math.h>
#include <MPU6050.h>
#include <DHT.h>

#if USE_MQTT
#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <PubSubClient.h>

// === WLAN-Konfiguration – Umschaltung daheim / ORBIS ===
#define WIFI_MODE_DAHEIM 0
#define WIFI_MODE_ORBIS  1
#define WIFI_MODE WIFI_MODE_DAHEIM  // <-- Nur diese Zeile ändern: DAHEIM oder ORBIS

#if WIFI_MODE == WIFI_MODE_DAHEIM
  // WLAN Daheim – Fritz!Box 192.168.178.x, Arduino .95 reserviert
  const char* WIFI_SSID = "daheim";
  const char* WIFI_PASS = "LillaVilla1";
  IPAddress arduinoIP(192, 168, 178, 95);         // Fritz!Box-Reservierung
  IPAddress gatewayIP(192, 168, 178, 1);
  IPAddress subnetIP(255, 255, 255, 0);
  const char* MQTT_BROKER = "192.168.178.65";     // Mac mit Mosquitto
#else
  // WLAN ORBIS – RPi/APS-Betrieb (credentials.md)
  const char* WIFI_SSID = "ORBIS-4711";
  const char* WIFI_PASS = "49117837";
  IPAddress arduinoIP(192, 168, 0, 95);
  IPAddress gatewayIP(192, 168, 0, 1);
  IPAddress subnetIP(255, 255, 255, 0);
  const char* MQTT_BROKER = "192.168.0.100";
#endif
const int MQTT_PORT = 1883;
const char* MQTT_USER = "default";
const char* MQTT_PASS = "default";
const char* MQTT_CLIENT_ID = "arduino_sensors_1";
const char* TOPIC_MPU_STATE = "osf/arduino/vibration/mpu6050-1/state";
const char* TOPIC_MPU_CONNECTION = "osf/arduino/vibration/mpu6050-1/connection";
const char* TOPIC_SW420_STATE = "osf/arduino/vibration/sw420-1/state";
const char* TOPIC_SW420_CONNECTION = "osf/arduino/vibration/sw420-1/connection";
const char* TOPIC_DHT11_STATE = "osf/arduino/temperature/dht11-1/state";
const char* TOPIC_DHT11_CONNECTION = "osf/arduino/temperature/dht11-1/connection";
const char* TOPIC_FLAME_STATE = "osf/arduino/flame/flame-1/state";
const char* TOPIC_FLAME_CONNECTION = "osf/arduino/flame/flame-1/connection";
const char* TOPIC_GAS_STATE = "osf/arduino/gas/mq2-1/state";
const char* TOPIC_GAS_CONNECTION = "osf/arduino/gas/mq2-1/connection";
const char* TOPIC_ALARM_ENABLED = "osf/arduino/alarm/enabled";  // true/false – Sirene nur bei aktivem Toggle

/** MQTT Publish-Interval: Jedes Topic wird bei Zustandsänderung sofort gesendet; bei Idle alle 5s als Heartbeat. */
const unsigned long MQTT_HEARTBEAT_INTERVAL = 5000;
const float DHT_TEMP_WARN = 30.0;   // °C – Gelb
const float DHT_TEMP_DANGER = 35.0; // °C – Rot
const float DHT_HUM_WARN = 80.0;    // % – Gelb
const float DHT_HUM_DANGER = 90.0;  // % – Rot

WiFiUDP udp;
NTPClient timeClient(udp, "pool.ntp.org", 0, 60000);

unsigned long lastReconnectAttempt = 0;
const unsigned long RECONNECT_INTERVAL = 5000;
unsigned long lastNtpUpdate = 0;  // NTP nur alle 2 s – update() blockiert sonst Sensor-Loop
const unsigned long NTP_UPDATE_INTERVAL = 2000;
int lastPublishedLevel = -1;
unsigned long lastPublishTime = 0;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
#endif

const int SW420_PIN = 11;
const int DHT_PIN = 12;  // DHT11 Data. Sensor links→rechts: − GND, Mitte VCC, S Data
const int FLAME_PIN = A1;  // Flammensensor AO (analog)
const int FLAME_THRESHOLD = 25;  // raw < 25 → Flamme. Ruhe ~38, Feuerzeug nah ~10–15. Poti beeinflusst nur DO, nicht A0!
const int GAS_PIN = A0;  // MQ-2 Gas-Sensor AO (analog). Hoch = Gefahr (Rauch/CO)
const int GAS_THRESHOLD_WARN = 500;   // Gelb: raw > 500 (erhöhte Konzentration)
const int GAS_THRESHOLD_DANGER = 750; // Rot: raw > 750 (Alarm, starke Rauch/Gas-Belastung)
const int FLAME_CONFIRM_SAMPLES = 20;  // N Messungen unter Schwellenwert nötig (20×10ms = 200ms) – filtert Licht-Spitzen
#define FLAME_INVERTED 1  // 1 = niedrig=Flamme (KY-026). 0 = hoch=Flamme.
const int RELAY_GRUEN = 7;

MPU6050 mpu;
DHT dht(DHT_PIN, DHT11);
const int RELAY_GELB = 8;
const int RELAY_ROT = 9;
const int RELAY_SIRENE = 10;  // Relais 4 – Sirene nur wenn Alarm-Toggle in osf-ui aktiv

const int sampleInterval = 10;
const unsigned long DEBUG_INTERVAL = 500;
/** Minimum time (ms) red light stays on after any alarm (flame, gas, vibration). Ensures visibility even for brief sensor pulses. */
const unsigned long ROT_MIN_DURATION = 2500;
const unsigned long GELB_MIN_DURATION = 2000;

const long MAG_THRESHOLD_GELB = 18500;
const long MAG_THRESHOLD_ROT = 26500;

unsigned long impulseCount = 0;
unsigned long sw420ImpulseCount = 0;
unsigned long lastSample = 0;
unsigned long lastSw420PublishTime = 0;
int lastSw420Level = -1;
int lastPublishedSw420Level = -1;
bool lastSw420Triggered = false;
unsigned long lastDhtRead = 0;
const unsigned long DHT_READ_INTERVAL = 2000;
const unsigned long DHT_BACKOFF_AFTER_FAILS = 30000;  // 30 s Pause nach Fehlern
const int DHT_MAX_CONSECUTIVE_FAILS = 3;
int dhtConsecutiveFails = 0;
bool dhtSuspended = false;
unsigned long dhtSuspendUntil = 0;
float lastTemp = 0;
float lastHum = 0;
unsigned long lastDhtPublish = 0;
int lastPublishedDhtLevel = -1;
unsigned long lastFlamePublish = 0;
bool lastFlameDetected = false;
int flameConfirmCount = 0;  // Debounce: nur Alarm nach N aufeinanderfolgenden Low-Werten
unsigned long lastGasPublish = 0;
bool lastGasDetected = false;
bool alarmEnabled = false;  // Sirene nur wenn true – von osf/arduino/alarm/enabled
unsigned long lastDebugPrint = 0;
unsigned long redStartedAt = 0;
unsigned long yellowStartedAt = 0;

#if USE_MQTT
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, TOPIC_ALARM_ENABLED) == 0 && length >= 4) {
    if (payload[0] == 't' && payload[1] == 'r' && payload[2] == 'u' && payload[3] == 'e') {
      alarmEnabled = true;
      Serial.println("Alarm-Toggle: Sirene EIN");
    } else {
      alarmEnabled = false;
      Serial.println("Alarm-Toggle: Sirene AUS");
    }
  }
}

void mqttReconnect() {
  if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS, TOPIC_MPU_CONNECTION, 1, true, "{\"connectionState\":\"OFFLINE\"}")) {
    mqttClient.subscribe(TOPIC_ALARM_ENABLED);
    IPAddress ip = WiFi.localIP();
    char payload[120];
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"mpu6050-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_MPU_CONNECTION, payload, true);
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"sw420-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_SW420_CONNECTION, payload, true);
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"dht11-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_DHT11_CONNECTION, payload, true);
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"flame-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_FLAME_CONNECTION, payload, true);
    snprintf(payload, sizeof(payload), "{\"connectionState\":\"ONLINE\",\"ip\":\"%d.%d.%d.%d\",\"serialNumber\":\"mq2-1\"}",
             ip[0], ip[1], ip[2], ip[3]);
    mqttClient.publish(TOPIC_GAS_CONNECTION, payload, true);
    Serial.print("MQTT verbunden. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.print("MQTT fehlgeschlagen, rc=");
    Serial.println(mqttClient.state());
  }
}

const unsigned long NTP_SYNC_THRESHOLD = 1000000000;

/** Epoch (sec seit 1970) → Jahr, Monat, Tag (UTC). */
void epochToYMD(unsigned long epoch, int& y, int& m, int& d) {
  long z = (long)(epoch / 86400) + 719468;
  int era = (int)(z / 146097);
  unsigned int doe = (unsigned int)(z - (long)era * 146097);
  unsigned int yoe = (doe - doe/1460 + doe/36524 - doe/146096) / 365;
  y = (int)yoe + era * 400;
  unsigned int doy = doe - (365*yoe + yoe/4 - yoe/100);
  unsigned int mp = (5*doy + 2) / 153;
  d = (int)(doy - (153*mp+2)/5) + 1;
  m = (int)mp + (mp < 10 ? 3 : -9);
  y += (m <= 2 ? 1 : 0);
}

void getTimestamp(char* buf, size_t len) {
  unsigned long epoch = timeClient.getEpochTime();
  if (epoch > NTP_SYNC_THRESHOLD) {
    int y, m, d;
    epochToYMD(epoch, y, m, d);
    snprintf(buf, len, "\"%04d-%02d-%02dT%02d:%02d:%02dZ\"",
             y, m, d,
             timeClient.getHours(), timeClient.getMinutes(), timeClient.getSeconds());
  } else {
    snprintf(buf, len, "\"\"");
  }
}

void publishMpuState(const char* level, long magnitude) {
  if (!mqttClient.connected()) return;
  bool detected = (level[0] != 'g');
  char tsBuf[32];
  getTimestamp(tsBuf, sizeof(tsBuf));
  char payload[200];
  snprintf(payload, sizeof(payload),
           "{\"vibrationLevel\":\"%s\",\"vibrationDetected\":%s,\"impulseCount\":%lu,\"magnitude\":%ld,\"timestamp\":%s}",
           level, detected ? "true" : "false", impulseCount, magnitude, tsBuf);
  mqttClient.publish(TOPIC_MPU_STATE, payload, true);
}

void publishSw420State(bool vibrationDetected) {
  if (!mqttClient.connected()) return;
  char payload[96];
  snprintf(payload, sizeof(payload), "{\"vibrationDetected\":%s,\"impulseCount\":%lu,\"timestamp\":\"\"}",
           vibrationDetected ? "true" : "false", sw420ImpulseCount);
  mqttClient.publish(TOPIC_SW420_STATE, payload, true);
}

void publishDht11State(float temp, float hum) {
  if (!mqttClient.connected()) return;
  char payload[120];
  snprintf(payload, sizeof(payload), "{\"temperature\":%.1f,\"humidity\":%.1f,\"temperatureUnit\":\"C\",\"humidityUnit\":\"%%\"}",
           temp, hum);
  mqttClient.publish(TOPIC_DHT11_STATE, payload, true);
}

void publishFlameState(int rawValue, bool flameDetected) {
  if (!mqttClient.connected()) return;
  char payload[96];
  snprintf(payload, sizeof(payload), "{\"flameDetected\":%s,\"rawValue\":%d,\"timestamp\":\"\"}",
           flameDetected ? "true" : "false", rawValue);
  mqttClient.publish(TOPIC_FLAME_STATE, payload, true);
}

void publishGasState(int rawValue, bool gasDetected, int gasLevel) {
  if (!mqttClient.connected()) return;
  char payload[96];
  char tsBuf[32];
  getTimestamp(tsBuf, sizeof(tsBuf));
  snprintf(payload, sizeof(payload), "{\"gasDetected\":%s,\"gasLevel\":%d,\"rawValue\":%d,\"timestamp\":%s}",
           gasDetected ? "true" : "false", gasLevel, rawValue, tsBuf);
  mqttClient.publish(TOPIC_GAS_STATE, payload, true);
}
#endif

void setup() {
  Serial.begin(9600);
  Serial.println("Setup start...");
  Serial.print("Sketch v");
  Serial.println(SKETCH_VERSION);
  Serial.flush();

  Wire.begin();
  if (!mpu.testConnection()) {
    Serial.println("FEHLER: MPU-6050 nicht gefunden! I2C prüfen (SDA=A4, SCL=A5).");
    while (1) { delay(1000); }
  }
  mpu.initialize();
  mpu.setDLPFMode(MPU6050_DLPF_BW_256);
  Serial.println("MPU-6050 OK.");

  dht.begin();
  delay(2000);  // DHT braucht nach Power-up bis zu 2 s
  Serial.println("DHT11 init OK.");

  pinMode(SW420_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RELAY_GRUEN, OUTPUT);
  pinMode(RELAY_GELB, OUTPUT);
  pinMode(RELAY_ROT, OUTPUT);
  pinMode(RELAY_SIRENE, OUTPUT);
  digitalWrite(RELAY_GRUEN, RELAY_ON);
  digitalWrite(RELAY_GELB, RELAY_OFF);
  digitalWrite(RELAY_ROT, RELAY_OFF);
  digitalWrite(RELAY_SIRENE, RELAY_OFF);

#if RELAY_STARTUP_TEST
  /* Relais-Test: 2s Grün, 2s Gelb, 2s Rot – prüft Verdrahtung/COM-Kette */
  Serial.println("Relais-Test: Gruen 2s...");
  digitalWrite(RELAY_GRUEN, RELAY_ON);
  digitalWrite(RELAY_GELB, RELAY_OFF);
  digitalWrite(RELAY_ROT, RELAY_OFF);
  delay(2000);
  Serial.println("Relais-Test: Gelb 2s...");
  digitalWrite(RELAY_GRUEN, RELAY_OFF);
  digitalWrite(RELAY_GELB, RELAY_ON);
  digitalWrite(RELAY_ROT, RELAY_OFF);
  delay(2000);
  Serial.println("Relais-Test: Rot 2s...");
  digitalWrite(RELAY_GRUEN, RELAY_OFF);
  digitalWrite(RELAY_GELB, RELAY_OFF);
  digitalWrite(RELAY_ROT, RELAY_ON);
  delay(2000);
  digitalWrite(RELAY_GRUEN, RELAY_ON);
  digitalWrite(RELAY_GELB, RELAY_OFF);
  digitalWrite(RELAY_ROT, RELAY_OFF);
  Serial.println("Relais-Test Ende.");
#endif

#if USE_MQTT
  Serial.print("WLAN-Modus: ");
  Serial.println(WIFI_MODE == WIFI_MODE_DAHEIM ? "DAHEIM" : "ORBIS");
  Serial.print("WiFi verbinde ");
  Serial.println(WIFI_SSID);
  WiFi.config(arduinoIP, gatewayIP, subnetIP);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 30) {
    delay(500);
    Serial.print(".");
    wifiAttempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi OK. IP: ");
    Serial.println(WiFi.localIP());
    uint8_t mac[6];
    WiFi.macAddress(mac);
    Serial.print("MAC: ");
    for (int i = 0; i < 6; i++) {
      if (i > 0) Serial.print(':');
      if (mac[i] < 16) Serial.print('0');
      Serial.print(mac[i], HEX);
    }
    Serial.println();
  } else {
    Serial.println();
    Serial.println("WiFi fehlgeschlagen. MQTT deaktiviert.");
  }

  timeClient.begin();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(256);
  mqttClient.setSocketTimeout(3);
  mqttClient.setCallback(mqttCallback);
  if (WiFi.status() == WL_CONNECTED) {
    mqttReconnect();
    publishMpuState("green", 0);
    publishSw420State(false);
    publishDht11State(0, 0);
    publishFlameState(1023, false);
    publishGasState(0, false, 0);
    lastPublishedLevel = 0;
    lastPublishTime = millis();
    lastSw420Level = 0;
    lastSw420PublishTime = millis();
    lastPublishedSw420Level = 0;
    lastDhtPublish = millis();
    lastPublishedDhtLevel = 0;
    lastFlamePublish = millis();
    lastFlameDetected = false;
    lastGasPublish = millis();
    lastGasDetected = false;
  }
#endif

  Serial.println("System bereit. Warte auf Vibration/Flamme...");
  Serial.flush();
}

long getAccelMagnitude() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  return (long)sqrt((long)ax * ax + (long)ay * ay + (long)az * az);
}

void loop() {
#if USE_MQTT
  {
    unsigned long now = millis();
    if (lastNtpUpdate == 0 || now - lastNtpUpdate >= NTP_UPDATE_INTERVAL) {
      lastNtpUpdate = now;
      timeClient.update();  // Kann blockieren – nur alle 2 s ausführen
    }
  }
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
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
  bool sw420Triggered = (digitalRead(SW420_PIN) == (SENSOR_ACTIVE_HIGH ? HIGH : LOW));

  int flameRaw = analogRead(FLAME_PIN);
  bool rawBelowThreshold = FLAME_INVERTED ? (flameRaw < FLAME_THRESHOLD) : (flameRaw > FLAME_THRESHOLD);
  if (rawBelowThreshold) {
    flameConfirmCount++;
    if (flameConfirmCount > FLAME_CONFIRM_SAMPLES) flameConfirmCount = FLAME_CONFIRM_SAMPLES;
  } else {
    flameConfirmCount = 0;
  }
  bool flameDetected = (flameConfirmCount >= FLAME_CONFIRM_SAMPLES);
  int flameLevel = flameDetected ? 2 : 0;

  int gasRaw = analogRead(GAS_PIN);
  int gasLevel = 0;
  if (gasRaw > GAS_THRESHOLD_DANGER) gasLevel = 2;
  else if (gasRaw > GAS_THRESHOLD_WARN) gasLevel = 1;
  bool gasDetected = (gasLevel >= 1);

  float temp = lastTemp;
  float hum = lastHum;
  int dhtLevel = 0;

  if (dhtSuspended) {
    if (now >= dhtSuspendUntil) {
      dhtSuspended = false;
      dhtConsecutiveFails = 0;
    }
  } else if (now - lastDhtRead >= DHT_READ_INTERVAL) {
    lastDhtRead = now;
    temp = dht.readTemperature();
    hum = dht.readHumidity();
    if (!isnan(temp) && !isnan(hum)) {
      dhtConsecutiveFails = 0;
      lastTemp = temp;
      lastHum = hum;
    } else {
      dhtConsecutiveFails++;
      if (dhtConsecutiveFails >= DHT_MAX_CONSECUTIVE_FAILS) {
        dhtSuspended = true;
        dhtSuspendUntil = now + DHT_BACKOFF_AFTER_FAILS;
        Serial.println("DHT11 suspendiert (Fehler), 30s Pause.");
      }
    }
    if (lastTemp >= DHT_TEMP_DANGER || lastHum >= DHT_HUM_DANGER) dhtLevel = 2;
    else if (lastTemp >= DHT_TEMP_WARN || lastHum >= DHT_HUM_WARN) dhtLevel = 1;
  }

  if (sw420Triggered) {
    if (!lastSw420Triggered) {
      sw420ImpulseCount++;
      Serial.println("!!! SW-420 VIBRATION !!!");
    }
    lastSw420Triggered = true;
    lastSw420Level = 1;
  } else {
    lastSw420Triggered = false;
    lastSw420Level = 0;
  }

  if (now - lastDebugPrint >= DEBUG_INTERVAL) {
    lastDebugPrint = now;
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print("mag=");
    Serial.print(mag);
    Serial.print(" sw420=");
    Serial.print(sw420Triggered ? "TRIG" : "ok");
    Serial.print(" T=");
    Serial.print(lastTemp);
    Serial.print(" H=");
    Serial.print(lastHum);
    Serial.print(" flame=");
    Serial.print(flameRaw);
    Serial.print(" gas=");
    Serial.print(gasRaw);
    Serial.println();
    Serial.flush();
    digitalWrite(LED_BUILTIN, LOW);
  }

  bool forceRed = (redStartedAt != 0 && (now - redStartedAt) < ROT_MIN_DURATION);
  bool forceYellow = (yellowStartedAt != 0 && (now - yellowStartedAt) < GELB_MIN_DURATION);

  int mpuLevel = 0;
  if (mag >= MAG_THRESHOLD_ROT) mpuLevel = 2;
  else if (mag >= MAG_THRESHOLD_GELB) mpuLevel = 1;
  int sw420Level = sw420Triggered ? 2 : 0;
  int combinedLevel = mpuLevel;
  if (sw420Level > combinedLevel) combinedLevel = sw420Level;
  if (dhtLevel > combinedLevel) combinedLevel = dhtLevel;
  if (flameLevel > combinedLevel) combinedLevel = flameLevel;
  if (gasLevel > combinedLevel) combinedLevel = gasLevel;

  int currentLevel;
  const char* levelStr;
  if (forceRed || combinedLevel >= 2) {
    if (redStartedAt == 0) redStartedAt = now;
    yellowStartedAt = 0;
    if (mpuLevel >= 2) impulseCount++;
    digitalWrite(RELAY_GRUEN, RELAY_OFF);
    digitalWrite(RELAY_GELB, RELAY_OFF);
    digitalWrite(RELAY_ROT, RELAY_ON);
    digitalWrite(RELAY_SIRENE, alarmEnabled ? RELAY_ON : RELAY_OFF);
    if (!forceRed && mpuLevel >= 2) Serial.print("!!! ROT ");
    if (!forceRed && mpuLevel >= 2) Serial.print(alarmEnabled ? "+SIRENE " : "");
    if (!forceRed && mpuLevel >= 2) Serial.print("!!! mag=");
    if (!forceRed && mpuLevel >= 2) Serial.println(mag);
    if (!forceRed && flameLevel >= 2) Serial.println("!!! FLAMME ROT !!!");
    if (!forceRed && gasLevel >= 2) Serial.println("!!! GAS ROT !!!");
    currentLevel = 2;
    levelStr = "red";
  } else if (forceYellow || combinedLevel >= 1) {
    if (yellowStartedAt == 0) yellowStartedAt = now;
    redStartedAt = 0;
    digitalWrite(RELAY_GRUEN, RELAY_OFF);
    digitalWrite(RELAY_GELB, RELAY_ON);
    digitalWrite(RELAY_ROT, RELAY_OFF);
    digitalWrite(RELAY_SIRENE, RELAY_OFF);
    currentLevel = 1;
    levelStr = "yellow";
  } else {
    redStartedAt = 0;
    yellowStartedAt = 0;
    digitalWrite(RELAY_GRUEN, RELAY_ON);
    digitalWrite(RELAY_GELB, RELAY_OFF);
    digitalWrite(RELAY_ROT, RELAY_OFF);
    digitalWrite(RELAY_SIRENE, RELAY_OFF);
    currentLevel = 0;
    levelStr = "green";
  }

#if USE_MQTT
  if (WiFi.status() == WL_CONNECTED) {
    bool shouldPublishMpu = (currentLevel != lastPublishedLevel) ||
        (currentLevel == 0 && (now - lastPublishTime) >= MQTT_HEARTBEAT_INTERVAL);
    if (shouldPublishMpu) {
      publishMpuState(levelStr, mag);
      lastPublishedLevel = currentLevel;
      lastPublishTime = now;
    }
    bool shouldPublishSw420 = (lastSw420Level != lastPublishedSw420Level) ||
        (lastSw420Level == 0 && (now - lastSw420PublishTime) >= MQTT_HEARTBEAT_INTERVAL);
    if (shouldPublishSw420) {
      publishSw420State(sw420Triggered);
      lastPublishedSw420Level = lastSw420Level;
      lastSw420PublishTime = now;
    }
    bool shouldPublishDht = (dhtLevel != lastPublishedDhtLevel) ||
        (dhtLevel == 0 && (now - lastDhtPublish) >= MQTT_HEARTBEAT_INTERVAL);
    if (shouldPublishDht) {
      publishDht11State(lastTemp, lastHum);
      lastPublishedDhtLevel = dhtLevel;
      lastDhtPublish = now;
    }
    bool shouldPublishFlame = (flameDetected != lastFlameDetected) ||
        (!flameDetected && (now - lastFlamePublish) >= MQTT_HEARTBEAT_INTERVAL);
    if (shouldPublishFlame) {
      publishFlameState(flameRaw, flameDetected);
      lastFlameDetected = flameDetected;
      lastFlamePublish = now;
    }
    bool shouldPublishGas = (gasDetected != lastGasDetected) ||
        (!gasDetected && (now - lastGasPublish) >= MQTT_HEARTBEAT_INTERVAL);
    if (shouldPublishGas) {
      publishGasState(gasRaw, gasDetected, gasLevel);
      lastGasDetected = gasDetected;
      lastGasPublish = now;
    }
  }
#endif
}
