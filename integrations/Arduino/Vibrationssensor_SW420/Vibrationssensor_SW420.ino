/*
 * Projekt: Vibrationsüberwachung der FMF (Fischertechnik-Modellfabrik der APS) für das OSF-Projekt (ORBIS SmartFactory)
 * Hardware: Arduino Uno, Ethernet Shield 2, SW-420, 4-Ch Relais, 12V Ampel
 * Quelle: integrations/Arduino – siehe docs/05-hardware/arduino-vibrationssensor.md
 */

// Pin Definitionen
const int SENSOR_PIN = 2;   // SW-420 Digital Out
const int RELAY_GRUEN = 5;  // Relais für grüne Lampe
const int RELAY_ROT = 6;    // Relais für rote Lampe + Sirene

// Einstellungen
int alarmDauer = 2000;      // Wie lange der Alarm nach Erschütterung aktiv bleibt (ms)

void setup() {
  Serial.begin(9600);

  // Pin Modi festlegen
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RELAY_GRUEN, OUTPUT);
  pinMode(RELAY_ROT, OUTPUT);

  // Initialzustand: Grün an, Rot aus
  // Hinweis: Viele Relais-Module sind "Low-Level Triggered" (LOW = AN)
  digitalWrite(RELAY_GRUEN, LOW);
  digitalWrite(RELAY_ROT, HIGH);

  Serial.println("System bereit. Warte auf Vibration...");
}

void loop() {
  // Sensor auslesen
  int vibration = digitalRead(SENSOR_PIN);

  if (vibration == HIGH) {
    Serial.println("!!! VIBRATION ERKANNT !!!");

    // Ampel umschalten
    digitalWrite(RELAY_GRUEN, HIGH);  // Grün AUS
    digitalWrite(RELAY_ROT, LOW);     // Rot/Alarm AN

    delay(alarmDauer);  // Alarmzeit abwarten

    // Zurück in Normalzustand
    digitalWrite(RELAY_GRUEN, LOW);   // Grün AN
    digitalWrite(RELAY_ROT, HIGH);    // Rot/Alarm AUS
    Serial.println("System beruhigt. Überwachung läuft...");
  }
}
