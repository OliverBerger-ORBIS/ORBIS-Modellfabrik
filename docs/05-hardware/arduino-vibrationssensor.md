# Projektplan: Vibrationsüberwachung APS-Modellfabrik

Dieses Dokument beschreibt den Aufbau eines Überwachungssystems mit Arduino, Ethernet Shield 2 und einer 12V-Signalampel zur Detektion von Vibrationen (z. B. mittels Stimmgabel).

## 1. Vorbereitung & Hardware-Check

Bevor du startest, stelle sicher, dass folgende Komponenten bereitliegen:

* [ ] Arduino Uno & Ethernet Shield 2
* [ ] SW-420 Vibrationssensor
* [ ] 4-Kanal Relais Modul (5V)
* [ ] 12V Signalampel & 12V Netzteil
* [ ] Jumperkabel (M/M, M/F) & USB-Kabel
* [ ] DC-Adapter für das Netzteil

---

## 2. Schritt-für-Schritt Aufbau

### Schritt 1: Controller-Stack

Stecke das **Ethernet Shield 2** vorsichtig auf den **Arduino Uno**. Achte darauf, dass alle Pins deckungsgleich sind und keine Pins verbogen werden.

### Schritt 2: Sensor-Anschluss (5V Welt)

Verbinde den SW-420 Sensor mit dem Ethernet Shield (Nutze die Buchsenleisten oben auf dem Shield):

* **VCC** an **5V**
* **GND** an **GND**
* **DO (Digital Out)** an **Pin 2**

### Schritt 3: Relais & Ampel (12V Welt)

1. Verbinde das Relais-Modul mit dem Arduino (Steuerseite):
* **VCC** an **5V** | **GND** an **GND**
* **IN1** (Grüne Lampe) an **Pin 5**
* **IN2** (Rote Lampe + Sirene) an **Pin 6**


2. Verkabelung der 12V-Seite (Lastseite):
* Verbinde den **Minuspol (GND)** des 12V Netzteils direkt mit dem gemeinsamen Minusleiter der Ampel.
* Führe den **Pluspol (12V)** zum **COM** (Common) Anschluss des Relais.
* Verbinde den **NO** (Normally Open) Anschluss des Relais mit dem Pluskabel der jeweiligen Ampelfarbe.



---

## 3. Test-Software (Basis-Logik)

Dieser Code prüft den Sensor und schaltet die Ampel bei Vibration von Grün auf Rot/Alarm um.

```cpp
/*
 * Projekt: Vibrationsüberwachung APS-Modellfabrik
 * Hardware: Arduino Uno, Ethernet Shield 2, SW-420, 4-Ch Relais, 12V Ampel
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
    digitalWrite(RELAY_GRUEN, HIGH); // Grün AUS
    digitalWrite(RELAY_ROT, LOW);    // Rot/Alarm AN
    
    delay(alarmDauer);               // Alarmzeit abwarten
    
    // Zurück in Normalzustand
    digitalWrite(RELAY_GRUEN, LOW);  // Grün AN
    digitalWrite(RELAY_ROT, HIGH);   // Rot/Alarm AUS
    Serial.println("System beruhigt. Überwachung läuft...");
  }
}
```

---

## 4. Nächste Schritte nach dem Hardware-Test

1. **Kalibrierung:** Drehe am blauen Potentiometer des SW-420, bis die Status-LED gerade so erlischt. Teste die Empfindlichkeit mit der Stimmgabel.
2. **Netzwerk-Einbindung:** Sobald die lokale Logik läuft, ergänzen wir den Code um die `Ethernet.h` Library, um die Alarme per LAN zu senden.
3. **Integration:** Mechanische Befestigung des Sensors an den fischertechnik-U-Profilen der Modellfabrik.
