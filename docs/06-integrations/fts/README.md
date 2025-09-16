# FTS Steuerung in Node-Red

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Dokumentation basiert auf einer Hypothese und wurde noch nicht verifiziert. Die beschriebenen FTS-Steuerungslogik und VDA 5050-Implementierung müssen noch getestet und validiert werden.
Die Steuerung des fahrerlosen Transportsystems (FTS) bzw. Automated Guided Vehicle (AGV) nach dem VDA 5050 Standard ist in der Datei implizit enthalten, insbesondere durch die Verarbeitung von Aufträgen (Orders) und deren Weiterleitung über OPC UA Nodes. Hier sind die wesentlichen Punkte zusammengefasst: 

 
 

## 🚗 FTS-Steuerung nach VDA 5050 – Überblick 

1. Auftragsverarbeitung 

Aufträge werden über ein Node-RED-Flow verarbeitet. 

Die Funktion Write Order (z. B. Node e7e0014dac56a4d5) schreibt Befehle an das FTS über OPC UA. 

Die Aufträge enthalten Informationen wie: 

Zielpositionen (TO_CAMERA, TO_NIO_BIN, TO_PICKUP, etc.) 

Bewegungsbefehle (PICK, DROP, etc.) 

Metadaten wie duration, position, references. 

2. VDA 5050-konforme Kommunikation 

Die Struktur der Nachrichten und Zustände folgt dem VDA 5050-Standard: 

Order: enthält orderId, orderUpdateId, actionState, loads, errors. 

State: wird regelmäßig über MQTT publiziert (z. B. msg.topic = MQTT_topic + "/state"). 

InstantActions: wie startCalibration, stopCalibration, resetCalibration. 

3. Zustandsüberwachung 

Zustände wie PICKBUSY, DROPBUSY, WAITING_AFTER_PICK, etc. werden im Flow gespeichert. 

Erfolgreiche oder fehlerhafte Ausführungen führen zu Statusänderungen (FINISHED, FAILED). 

Diese Zustände werden über MQTT veröffentlicht und können vom VDA 5050 Master interpretiert werden. 

4. Kalibrierung und Referenzdaten 

Es gibt spezielle Funktionen zur Kalibrierung (startCalibration, setCalibrationValues, etc.). 

Diese Aktionen werden ebenfalls als InstantActions im VDA 5050-Format verarbeitet. 

 
 

## 🔄 Beispielhafter Ablauf 

Order empfangen (z. B. PICK an Position TO_PICKUP) 

Order schreiben via OPC UA 

FTS fährt zur Position 

Statusänderung auf PICKBUSY 

Nach erfolgreichem Abschluss: WAITING_AFTER_PICK → FINISHED 

State wird über MQTT publiziert 

 
 

## 📡 Technologien im Einsatz 

OPC UA: zur Kommunikation mit dem FTS 

MQTT: zur Statusübertragung im VDA 5050-Format 

Node-RED: zur Orchestrierung der Logik 

VDA 5050: als Kommunikationsstandard für AGV-Integration 

 
 

Hier ist das grafische Flussdiagramm, das den Ablauf der FTS-Steuerung nach dem VDA 5050 Standard im Node-RED-Flow darstellt: 

graph TD
    subgraph "Auftragsverarbeitung"
        A[MQTT: Auftrag empfangen<br/>(command: PICK, DROP, etc.)] -->|bei Auftragseingang| B{Verarbeite Auftrag<br/>(Flow prüft mobileState & command)}
    
        B -->|command == DROP| C[OPC UA Write: DROP<br/>ns=4;i=6 = true]
        B -->|command == PICK| D[OPC UA Write: PICK<br/>ns=4;i=5 = true]
        B -->|command == FIRE| E[OPC UA Write: FIRE<br/>ns=4;i=7 = duration]
        B -->|command == MILL| F[OPC UA Write: MILL<br/>ns=4;i=11 = duration]
    
        C --> G((Status: DROPBUSY))
        D --> H((Status: PICKBUSY))
        E --> I((Status: FIREBUSY))
        F --> J((Status: MILLBUSY))
    
        G --> K[OPC UA Read: DROP abgeschlossen]
        H --> L[OPC UA Read: PICK abgeschlossen]
        I --> M[OPC UA Read: FIRE abgeschlossen]
        J --> N[OPC UA Read: MILL abgeschlossen]
    
        K -->|ns=4;i=9 = true| O((Status: IDLE<br/>MQTT: {state: FINISHED}))
        
        L -->|ns=4;i=12 = true| P((Status: WAITING_AFTER_PICK<br/>MQTT: {state: FINISHED}))
        L -->|ns=4;i=8 = true<br/>ns=4;i=15 = true| Q((Fehlerfall<br/>- actionState: FAILED<br/>- MQTT: {state: ...}))
        
        M -->|ns=4;i=10 = true| R((Status: WAITING_AFTER_FIRE<br/>MQTT: {state: FINISHED}))
        M -->|ns=4;i=3 = true| Q
        
        N -->|ns=4;i=14 = true| S((Status: WAITING_AFTER_MILL<br/>MQTT: {state: FINISHED}))
        N -->|ns=4;i=13 = true| Q
    end

    style Q fill:#ffcccc,stroke:#cc0000,stroke-width:2px

Pseudocode der Auftragsverarbeitung
Dieser Code beschreibt eine Funktion, die aufgerufen wird, wenn ein neuer MQTT-Auftrag eintrifft.

// Funktion wird bei Eingang einer neuen MQTT-Nachricht aufgerufen
FUNKTION handle_mqtt_command(command, duration):

  // Schritt 1: Prüfe den eingegangenen Befehl
  FALLS command == "DROP":
    // Prozess für "DROP" starten
    OPC_UA_Write(ns=4, i=6, wert=true)
    Set_Status("DROPBUSY")

    // Warten auf Abschlussmeldung
    ergebnis_drop = OPC_UA_Read(ns=4, i=9)
    WENN ergebnis_drop == true:
      Set_Status("IDLE")
      MQTT_Publish(state="FINISHED")
    SONST:
      // Fehlerbehandlung für DROP (im Diagramm nicht spezifiziert)
      Set_Status("Fehlerfall")
      MQTT_Publish(state="FAILED")
    ENDE WENN

  SONST FALLS command == "PICK":
    // Prozess für "PICK" starten
    OPC_UA_Write(ns=4, i=5, wert=true)
    Set_Status("PICKBUSY")

    // Warten auf Abschlussmeldung und Fehler prüfen
    ergebnis_pick_ok = OPC_UA_Read(ns=4, i=12)
    ergebnis_pick_fehler1 = OPC_UA_Read(ns=4, i=8)
    ergebnis_pick_fehler2 = OPC_UA_Read(ns=4, i=15)

    WENN ergebnis_pick_ok == true:
      Set_Status("WAITING_AFTER_PICK")
      MQTT_Publish(state="FINISHED")
    SONST WENN ergebnis_pick_fehler1 == true ODER ergebnis_pick_fehler2 == true:
      Set_Status("Fehlerfall")
      MQTT_Publish(state="FAILED", actionState="FAILED")
    ENDE WENN

  SONST FALLS command == "FIRE":
    // Prozess für "FIRE" starten
    OPC_UA_Write(ns=4, i=7, wert=duration)
    Set_Status("FIREBUSY")

    // Warten auf Abschlussmeldung und Fehler prüfen
    ergebnis_fire_ok = OPC_UA_Read(ns=4, i=10)
    ergebnis_fire_fehler = OPC_UA_Read(ns=4, i=3)

    WENN ergebnis_fire_ok == true:
      Set_Status("WAITING_AFTER_FIRE")
      MQTT_Publish(state="FINISHED")
    SONST WENN ergebnis_fire_fehler == true:
      Set_Status("Fehlerfall")
      MQTT_Publish(state="FAILED", actionState="FAILED")
    ENDE WENN

  SONST FALLS command == "MILL":
    // Prozess für "MILL" starten
    OPC_UA_Write(ns=4, i=11, wert=duration)
    Set_Status("MILLBUSY")

    // Warten auf Abschlussmeldung und Fehler prüfen
    ergebnis_mill_ok = OPC_UA_Read(ns=4, i=14)
    ergebnis_mill_fehler = OPC_UA_Read(ns=4, i=13)

    WENN ergebnis_mill_ok == true:
      Set_Status("WAITING_AFTER_MILL")
      MQTT_Publish(state="FINISHED")
    SONST WENN ergebnis_mill_fehler == true:
      Set_Status("Fehlerfall")
      MQTT_Publish(state="FAILED", actionState="FAILED")
    ENDE WENN

ENDE FUNKTION

## 🧭 Ablaufbeschreibung 

MQTT-Eingang: Ein Auftrag mit einem command (z. B. PICK, DROP, MILL, FIRE) wird empfangen. 

Verarbeitung: Der Flow prüft den aktuellen moduleState und entscheidet, ob der Auftrag ausgeführt werden kann. 

OPC UA Write: Der entsprechende Befehl wird an das FTS gesendet (z. B. ns=4;i=5 = true für PICK). 

BUSY-Zustand: Das Modul wechselt in einen BUSY-Zustand (z. B. PICKBUSY). 

OPC UA Read: Das System überwacht den Abschluss der Aktion über bestimmte Nodes. 

Statuswechsel: 

Bei Erfolg: z. B. WAITING_AFTER_PICK, IDLE, WAITING_AFTER_MILL, WAITING_AFTER_FIRE 

Bei Fehler: actionState.state = FAILED 

MQTT-Statusmeldung: Der neue Zustand wird über MQTT veröffentlicht (/state). 
