# Node-Red Flows der Fischertechnik APS

> ⚠️ **VERIFIKATION AUSSTEHEND**: Diese Dokumentation basiert auf einer Hypothese und wurde noch nicht verifiziert. Die beschriebenen Node-RED-Flows und Zustandsdiagramme müssen noch getestet und validiert werden.



🧱 1. Struktur der Node-RED Flows 

📁 Tabs (Maschinen-Module) 

Jede Maschine oder Station ist als eigener Flow-Tab organisiert: 

MILL #1–5 
DRILL #1–5 
OVEN #1–5 
AIQS #1–5 
HBW #1–3 
DPS 

Jeder Tab enthält: 

OPC UA Connector mit spezifischem Endpoint (z. B. opc.tcp://192.168.0.x:4840) 
Listener, Reader, Writer für OPC UA 
MQTT-Kommunikation 

 
 

🔄 2. Subflows (Wiederverwendbare Logik) 

| Subflow | Funktion |
|---------|----------|
| handle-actions | Verarbeitung von Aufträgen und InstantActions |
| load-factsheet | Lädt Factsheets von der Festplatte |
| get-opcua-address | Holt OPC UA-Adresse aus Umgebungsvariablen |
| update-rack-position | Aktualisiert Positionen im Rack |
| update-calibration | Verarbeitet Kalibrierwerte |
| vda-status-finished | Meldet abgeschlossene Aktionen |
| vda-status-running | Meldet laufende Aktionen |
| check-nodeValue-is-true | Prüft OPC UA-Boolesche Werte |
| check-opcua-connection | Überwacht Verbindungsstatus |

📡 3. MQTT-Kommunikation 

Broker: 192.168.2.189:1883 
Topics: z. B. module/v1/ff/NodeRed/status, /state, /connection 
Verwendung: 
Statusmeldungen 
Auftragsannahme 
InstantActions 
Fehlerberichte 

🧠 4. Funktionale Knoten (JavaScript) 

Verbindungsaufbau: connection state, dynamic Connection 
Auftragslogik: sub order, isOrder?, isSupportedOrder? 
InstantActions: expand-instant-action-payload, isInstantAction? 
Zustandsverwaltung: createState, updateActionState 
Fehlerbehandlung: catch, debug, error logging 

🧪 5. Kalibrierung & Rack-Management 

Kalibrierdaten: setup-listen, setup-dictionary, writeNodeValue 
Rack-Positionen: getRackPositionNodeId, writeNodeValue, update-loads 
Visualisierung: Statusanzeigen und Debug-Ausgaben 

🧰 6. System-Setup & Initialisierung 

Inject-Nodes: zum Initialisieren von Variablen und Verbindungen 
HTTP-Requests: zur Steuerung von Flow-Reloads 
Environment-Handling: z. B. FACTSHEET_FILE, OPCUA_ADDRESS 


🛡️ 7. Fehler- und Statusmanagement 

Catch-Nodes: für globale und lokale Fehlerbehandlung 
Status-Nodes: zeigen Zustand von Verbindungen, Aktionen, Kalibrierung 
Debug-Nodes: zur Laufzeitüberwachung 
 

📦 Zusammenfassung 

Diese Node-RED-Konfiguration ist ein modulares, skalierbares Steuerungssystem für eine Produktionsanlage. Sie integriert: 

Maschinenkommunikation über OPC UA 
Daten- und Steuerkommunikation über MQTT 
Zustands- und Fehlermanagement 
Kalibrierung und Rack-Verwaltung 
Wiederverwendbare Subflows für zentrale Logik 

 
 graph TD
    subgraph "Beispiel-Diagramm eines Node-RED Flows"
        style Start fill:#90EE90,stroke:#008000
        style VerarbeiteAuftrag fill:#ADD8E6,stroke:#87CEEB
        style WandleWert fill:#ADD8E6,stroke:#87CEEB
        style EmpfangeMQTT fill:#FFC107,stroke:#FF8C00
        style SendeMQTT fill:#FFA500,stroke:#FF8C00
        style DebugAusgabe fill:#808080,stroke:#555555
        style LeseOPCUA fill:#DA70D6,stroke:#9400D3

        Start(Start) --> VerarbeiteAuftrag(Verarbeite Auftrag)
        Start --> WandleWert(Wandle Wert)

        LeseOPCUA(Lese OPC UA) --> VerarbeiteAuftrag
        LeseOPCUA --> WandleWert

        VerarbeiteAuftrag --> DebugAusgabe(Debug-Ausgabe)
        VerarbeiteAuftrag --> SendeMQTT(Sende MQTT)

        WandleWert --> EmpfangeMQTT(Empfange MQTT)
        WandleWert --> SendeMQTT

        EmpfangeMQTT --> WandleWert

        %% Legende (kann in Mermaid nicht direkt als interaktive Legende gerendert werden,
        %% aber hier zur Verdeutlichung der Farbcodes im Code)
        %% classDef inject fill:#90EE90,stroke:#008000
        %% classDef function fill:#ADD8E6,stroke:#87CEEB
        %% classDef mqtthttpout fill:#FFA500,stroke:#FF8C00
        %% classDef mqtthttpin fill:#FFC107,stroke:#FF8C00
        %% classDef debug fill:#808080,stroke:#555555
        %% classDef opcuaiiotread fill:#DA70D6,stroke:#9400D3
    end

🧩 Enthaltene Elemente: 

Inject-Node („Start“) triggert den Flow 

Function-Nodes verarbeiten Daten 

MQTT in/out für Kommunikation 
OPC UA Read liest Maschinendaten 
Debug zeigt Ausgaben zur Laufzeit     

## Beispiel Verarbeite Auftrag

Mermaid:

graph TD
    %% Node Definitions
    A1[Start]
    A2[Start]
    B[Verarbeite Auftrag]
    C[Wandle Wert]
    D[Empfange MQTT]
    E[Sende MQTT]
    F[Debug-Ausgabe]
    G[Lese OPC UA]

    %% Connections
    A1 --> B
    A2 --> C
    G --> B
    G --> C
    B --> F
    B --> E
    C --> D
    C --> E
    D --> C

    %% Styling to match Node-RED colors
    style A1 fill:#90EE90,stroke:#008000
    style A2 fill:#90EE90,stroke:#008000
    style B fill:#ADD8E6,stroke:#87CEEB
    style C fill:#ADD8E6,stroke:#87CEEB
    style D fill:#FFC107,stroke:#FF8C00
    style E fill:#FFA500,stroke:#FF8C00
    style F fill:#808080,stroke:#555555
    style G fill:#DA70D6,stroke:#9400D3


graph TD
    %% Node Definitions
    A(Start: Auftrag empfangen)
    B{command == "PICK"<br/>&& moduleState == "WAITING"}
    C{command == "DROP"<br/>&& moduleState == "WAITING_AFTER_MILL"}
    D{command == "MILL"<br/>&& moduleState == "WAITING_AFTER_PICK"}
    E(Setze moduleState = PICKBUSY<br/>Schreibe true auf ns=4;i=5)
    F(Setze moduleState = DROPBUSY<br/>Schreibe true auf ns=4;i=6)
    G(Setze moduleState = MILLBUSY<br/>Lese duration<br/>Schreibe duration auf ns=4;i=11)
    H[Fehler: Command not supported<br/>Speichere Fehlerobjekt]
    I[Speichere actionState, loads, orderUpdateId<br/>Setze payload für OPC UA Write]
    J(return [msg, null] oder [null, msg])

    %% Connections
    A -->|prüfe| B
    B -->|ja| E
    B -->|nein| C
    C -->|ja| F
    C -->|nein| D
    D -->|ja| G
    D -->|nein| H
    E --> I
    F --> I
    G --> I
    I --> J
    H --> J

 Hier ist die Logik aus dem zweiten Flussdiagramm als detaillierter Pseudocode. Dieser Code kann als Vorlage für eine Funktion, zum Beispiel in Node-RED, dienen.

Pseudocode der Logik
// Funktion, die eine eingehende Nachricht (msg) verarbeitet
FUNKTION verarbeite_auftrag(msg):

  // Lese die aktuellen Werte aus der Nachricht
  command = msg.command
  moduleState = msg.moduleState

  // Prüfe die erste Bedingung
  WENN (command == "PICK" UND moduleState == "WAITING"):
    msg.moduleState = "PICKBUSY"
    
    // Bereite die OPC UA Nachricht vor
    msg.payload = {
      actionState: "...", 
      loads: "...", 
      orderUpdateId: "...",
      opcua_variable: "ns=4;i=5",
      opcua_wert: true
    }
    
    // Sende die Nachricht an den ersten Ausgang (Erfolg)
    return [msg, null]

  // Prüfe die zweite Bedingung
  SONST WENN (command == "DROP" UND moduleState == "WAITING_AFTER_MILL"):
    msg.moduleState = "DROPBUSY"

    // Bereite die OPC UA Nachricht vor
    msg.payload = {
      actionState: "...", 
      loads: "...", 
      orderUpdateId: "...",
      opcua_variable: "ns=4;i=6",
      opcua_wert: true
    }

    // Sende die Nachricht an den ersten Ausgang (Erfolg)
    return [msg, null]

  // Prüfe die dritte Bedingung
  SONST WENN (command == "MILL" UND moduleState == "WAITING_AFTER_PICK"):
    msg.moduleState = "MILLBUSY"
    duration = msg.duration // Annahme: duration kommt in der Nachricht an

    // Bereite die OPC UA Nachricht vor
    msg.payload = {
      actionState: "...", 
      loads: "...", 
      orderUpdateId: "...",
      opcua_variable: "ns=4;i=11",
      opcua_wert: duration
    }

    // Sende die Nachricht an den ersten Ausgang (Erfolg)
    return [msg, null]

  // Wenn keine der Bedingungen zutrifft
  SONST:
    // Erstelle ein Fehlerobjekt
    fehler_msg = {
      payload: "Command not supported for the current moduleState",
      original_command: command,
      original_state: moduleState
    }
    
    // Sende die Fehlernachricht an den zweiten Ausgang
    return [null, fehler_msg]
  
ENDE FUNKTION

## ZUstandsdiagramm
Hier ist das Zustandsdiagramm für die Variable moduleState, das die Übergänge zwischen Maschinenzuständen im Node-RED Flow visualisiert: 
🔄 Zustände & Übergänge: 

IDLE → WAITING: Initialisierung 

WAITING → PICKBUSY: Auftrag „PICK“ 

PICKBUSY → WAITING_AFTER_PICK: PICK abgeschlossen 

WAITING_AFTER_PICK → MILLBUSY: Auftrag „MILL“ 

MILLBUSY → WAITING_AFTER_MILL: MILL abgeschlossen 

WAITING_AFTER_MILL → DROPBUSY: Auftrag „DROP“ 

DROPBUSY → WAITING_AFTER_DROP: DROP abgeschlossen 

WAITING_AFTER_PICK → FIREBUSY: Auftrag „FIRE“ 

FIREBUSY → WAITING_AFTER_FIRE: FIRE abgeschlossen 

WAITING_AFTER_FIRE → DROPBUSY: Folgeauftrag „DROP“ 

DROPBUSY → IDLE: Abschluss 

IDLE ↔ CALIBRATION: Kalibrierungsmodus 

Mermaid Code
Code-Snippet

stateDiagram-v2
    direction LR
    [*] --> IDLE

    IDLE --> WAITING : Initialisierung
    IDLE --> CALIBRATION : Kalibrierung starten

    CALIBRATION --> CALIBRATION : Kalibrierung aktiv

    WAITING --> PICKBUSY : PICK
    PICKBUSY --> WAITING_AFTER_PICK : PICK abgeschlossen

    state WAITING_AFTER_PICK {
        direction LR
        [*] --> fork_point
        fork_point --> MILLBUSY : MILL
        fork_point --> FIREBUSY : FIRE
    }

    MILLBUSY --> WAITING_AFTER_MILL : MILL abgeschlossen
    FIREBUSY --> WAITING_AFTER_FIRE : FIRE abgeschlossen

    WAITING_AFTER_MILL --> DROPBUSY : DROP
    WAITING_AFTER_FIRE --> DROPBUSY : DROP

    state DROPBUSY {
        direction LR
        [*] --> fork_point_drop
        fork_point_drop --> IDLE : DROP abgeschlossen
        fork_point_drop --> WAITING_AFTER_DROP : DROP abgeschlossen
    }