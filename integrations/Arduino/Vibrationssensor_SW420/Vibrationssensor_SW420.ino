/*
 * Projekt: Vibrationsüberwachung der FMF (Fischertechnik-Modellfabrik der APS) für das OSF-Projekt (ORBIS SmartFactory)
 * Hardware: Arduino Uno, Ethernet Shield 2, SW-420, 4-Ch Relais, 12V Ampel
 * Quelle: integrations/Arduino – siehe docs/05-hardware/arduino-vibrationssensor.md
 *
 * LAN/MQTT: 0 = nur Serial (ohne Ethernet Shield). 1 = MQTT aktiv (Shield + LAN verbunden).
 */
#define USE_MQTT 0

// Pin Definitionen
const int SENSOR_PIN = 2;   // SW-420 Digital Out
const int RELAY_GRUEN = 5;   // Relais für grüne Lampe
const int RELAY_ROT = 6;    // Relais für rote Lampe + Sirene

// Einstellungen
int alarmDauer = 2000;       // Wie lange der Alarm nach Erschütterung aktiv bleibt (ms)
unsigned long impulseCount = 0;

#if USE_MQTT
#include <Ethernet2.h>
#include <PubSubClient.h>

// Netzwerk (DR-18: 192.168.0.91–99)
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0x01 };
IPAddress ip(192, 168, 0, 95);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

const char* MQTT_BROKER = "192.168.0.100";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "arduino_sw420_1";
const char* TOPIC_STATE = "osf/arduino/vibration/sw420-1/state";
const char* TOPIC_CONNECTION = "osf/arduino/vibration/sw420-1/connection";

EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

void mqttReconnect() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect(MQTT_CLIENT_ID, TOPIC_CONNECTION, 1, true, "{\"online\":false}")) {
      char payload[64];
      snprintf(payload, sizeof(payload), "{\"online\":true,\"ip\":\"%d.%d.%d.%d\"}",
               ip[0], ip[1], ip[2], ip[3]);
      mqttClient.publish(TOPIC_CONNECTION, payload, true);
    } else {
      delay(3000);
    }
  }
}

void publishState(const char* ampel) {
  if (!mqttClient.connected()) return;
  char payload[80];
  snprintf(payload, sizeof(payload), "{\"ampel\":\"%s\",\"impulseCount\":%lu,\"ts\":\"\"}",
           ampel, impulseCount);
  mqttClient.publish(TOPIC_STATE, payload, true);
}
#endif

void setup() {
  Serial.begin(9600);

  pinMode(SENSOR_PIN, INPUT);
  pinMode(RELAY_GRUEN, OUTPUT);
  pinMode(RELAY_ROT, OUTPUT);
  digitalWrite(RELAY_GRUEN, LOW);
  digitalWrite(RELAY_ROT, HIGH);

#if USE_MQTT
  Ethernet.begin(mac, ip, gateway, subnet);
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(256);
  mqttReconnect();
  publishState("GRUEN");
#endif

  Serial.println("System bereit. Warte auf Vibration...");
}

void loop() {
#if USE_MQTT
  if (!mqttClient.connected()) mqttReconnect();
  mqttClient.loop();
#endif

  int vibration = digitalRead(SENSOR_PIN);

  if (vibration == HIGH) {
    impulseCount++;
    Serial.println("!!! VIBRATION ERKANNT !!!");

    digitalWrite(RELAY_GRUEN, HIGH);
    digitalWrite(RELAY_ROT, LOW);
#if USE_MQTT
    publishState("ROT");
#endif

    delay(alarmDauer);

    digitalWrite(RELAY_GRUEN, LOW);
    digitalWrite(RELAY_ROT, HIGH);
#if USE_MQTT
    publishState("GRUEN");
#endif
    Serial.println("System beruhigt. Überwachung läuft...");
  }
}
