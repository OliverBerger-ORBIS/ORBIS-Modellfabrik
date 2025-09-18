# APS Mosquitto Analyse - Zwischenergebnis

## 📊 Analyse-Status

**Datum:** 18. September 2025  
**Zeitraum:** 15:59 - 16:24 (Docker-Zeit)  
**Log-Größe:** System-Log: 9.6MB, Payload-Log: 25MB → gefiltert: 2.4MB  

## 🔍 Zeitpunkt-Validierung

### System-Log Analyse
- **Erste Client-Verbindungen:** 1758205495 (15:54 Docker-Zeit)
- **Letzte Client-Verbindungen:** 1758209686 (16:28 Docker-Zeit)
- **Analyse-Zeitraum:** 1758206000 - 1758206640 (15:59 - 16:24)

### ✅ Zeitpunkt bestätigt
Der gewählte Zeitraum (15:59 - 16:24) erfasst die Hauptaktivität nach dem APS-Neustart.

## 🏷️ Client-ID → Komponente-Mapping

### Identifizierte Client-IDs (Analyse-Zeitraum)
```
Client auto-26CCDA7B-8E2D-78B4-57AE-7B794D976EFC
Client auto-4B3D121F-21DE-70DD-B9F7-B6A5B667BB0F  
Client auto-AC6F2CEE-130A-6A01-622A-AC3765A947A5
Client auto-D48B02CD-EC58-8CB4-9738-AFDC0D94C3A3
```

### IP-Adressen-Mapping (aus System-Log)
- **192.168.0.105:** auto-F6DFC829-567D-0985-C27D-262A31EC52D5
- **192.168.0.103:** auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4
- **192.168.0.104:** auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591
- **192.168.0.102:** auto-AC941349-4637-28AC-2662-E51FFA998712
- **172.18.0.5:** mqttjs_8e5c7d5a (Frontend)
- **172.18.0.4:** nodered_abe9e421b6fe3efd (Node-RED)

### IP-Adressen-Mapping (aus empirischer Analyse zum Testzeitpunkt)
- **192.168.0.105:** auto-F6DFC829-567D-0985-C27D-262A31EC52D5 -> FTS : TXT4.0-5i04 
- **192.168.0.103:** auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4 -> CGW :  TXT4.0-WjY4
- **192.168.0.104:** auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591 -> AIQS : TXT4.0-00Y4
- **192.168.0.102:** auto-AC941349-4637-28AC-2662-E51FFA998712 -> DPS : TXT4.0-p0F4
- **172.18.0.5:** mqttjs_8e5c7d5a (Frontend) -> APS-Dashboard
- **172.18.0.4:** nodered_abe9e421b6fe3efd (Node-RED) -> Node-RED


## 📡 PUB/SUB-Beziehungen

### Hauptkommunikationsmuster
```
auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4 → auto-AC941349-4637-28AC-2662-E51FFA998712
Topic: /j1/txt/1/i/cam (Kamera-Daten)
```

### Identifizierte Topics (Top 20)
1. **809x** `module/v1/ff/SVR4H73275/instantAction` - Instant Actions
2. **806x** `ccu/pairing/state` - Pairing-Status
3. **275x** `fts/v1/ff/5iO4/state` - FTS-Status
4. **83x** `module/v1/ff/*/connection` - Modul-Verbindungen
5. **50x** `ccu/order/active` - Aktive Bestellungen
6. **50x** `/j1/txt/1/f/i/order` - TXT-Controller Bestellungen

## 🏭 Komponenten-Identifikation

### Modul-IDs
- **SVR4H73275** - Hauptmodul (809 Instant Actions)
- **SVR4H76530** - Modul 2
- **SVR4H76449** - Modul 3  
- **SVR3QA2098** - Modul 4
- **SVR3QA0022** - Modul 5

### Modul-IDs (gesicherte Information)
- **SVR4H73275** - Modul DPS
- **SVR4H76530** - Modul AIQS
- **SVR4H76449** - Modul DRILL 
- **SVR3QA2098** - Modul MILL
- **SVR3QA0022** - Modul HBW

### Node-RED-Instanzen
- **Node-RED(SUB)** - `nodered_abe9e421b6fe3efd` - **Monitoring/Subscriber** (16:25:09)
  - **55 Subscriptions** auf direkte Modul-Topics (`module/v1/ff/<Modul-Id>/+`)
  - **Empfängt auch** NodeRed-vermittelte Topics (`module/v1/ff/NodeRed/<Modul-Id>/+`)
- **Node-RED(PUB)** - `nodered_94dca81c69366ec4` - **Command/Publisher** (16:25:47, 32min aktiv)
  - **645 Publications** auf direkte Modul-Topics (`module/v1/ff/<Modul-Id>/+`)
  - **Nur 3 Publications** mit NodeRed-Präfix (`module/v1/ff/NodeRed/<Modul-Id>/+`)
  - **NodeRed-Präfix nur für:** DPS (SVR4H73275) und AIQS (SVR4H76530) `instantAction`
  - **Module mit eigenem TXT Controller** verwenden NodeRed-Präfix für spezielle Kommunikation
  - **Module ohne TXT Controller** (HBW, MILL, DRILL) ohne NodeRed-Präfix
  - **Fungiert als Direkt-Publisher** für Module

## 🔄 Kommunikationsfluss

### Publisher-Subscriber-Muster
1. **TXT-Controller (192.168.0.103)** → **FTS (192.168.0.102)**
   - Topic: `/j1/txt/1/i/cam` (Kamera-Daten)
   
2. **Module** → **CCU/Node-RED**
   - Topics: `module/v1/ff/*/instantAction`, `module/v1/ff/*/state`

3. **FTS** → **System**
   - Topics: `fts/v1/ff/5iO4/state`, `fts/v1/ff/5iO4/instantAction`

## 🎮 APS-Dashboard-Befehle (Analyse-Zeitraum)

**Manuell ausgelöste Befehle:**
1. **Docke an** - FTS-Docking-Befehl
2. **Rohware-RED Eingang** - Automatisch durch DPS-Modul (SVR4H73275)
3. **Bestellung-BLUE** - Produktionsauftrag
4. **Rohware RED Eingang (Aussortierung)** - Automatisch durch DPS-Modul , da kein Platz im Lager, DPS-Modul sortiert aus
5. **FTS-Laden** - FTS fährt zur Ladestation (CHRG0) und ist danach "BLOCKED"
6. **FTS-Laden beenden** - FTS verlässt Ladestation und ist danach "READY"
7. **Kamera-Justierung** - 4x 10° (hoch, rechts, runter, links)
8. **NFC-Lesen** - NFC-Code auslesen (NFC-READER über TXT der DPS-Station)
9. **NFC-Löschen** - NFC-Code löschen (s.o.)
10. **Kalibrierung AIQS** - SVR4H76530 (abgebrochen durch User)
11. **Bestellung-WHITE** - Mit Quality-Check durch AIQS → Quality-Not-OK → Neuer Produktionsauftrag
12. **Factory-Reset** - System-Reset (ohne Storage-Reset)

**Automatische Prozesse:**
- **DPS-Modul** löst Rohware-Eingang automatisch aus
- **AIQS-Modul** führt Quality-Check durch
- **HBW-Modul** sendet Lagerinformationen (Lagerverwaltung vermutlich in CCU)
- **CHRG0-Modul** passiv (keine aktive Kommunikation/Ansteuerung)

## 🔗 Command-Correlation (Dashboard ↔ MQTT)

### **Bestellungen (WHITE, RED, BLUE)**
- **Alle Module** unterstützen **alle Load-Types** (WHITE, RED, BLUE)
- **DPS-Modul** `loadSpecification`: `{"WHITES", "REDS", "BLUES"}`
- **Pattern ist Load-Type-unabhängig** - universelles System
- **HBW-Modul** zeigt WHITE-Workpieces in Lagerpositionen (A1, A2, C1)

### **Factory-Reset**
- **Alle Module** haben `resetCalibration` Action mit `factory` Parameter
- **DPS-Modul** hat zusätzlich `reset` Action
- **Keine direkten Reset-Nachrichten** in den Logs sichtbar

### **FTS-Laden**
- **CHRG0-Modul** als Ladestation identifiziert
- **FTS-Status** zeigt `charging: false`, `batteryPercentage: 92`
- **FTS** fährt zu `lastNodeId: "UNKNOWN"` (vermutlich CHRG0)
- **FTS-Status:** "BLOCKED" wenn an CHRG0, "READY" wenn frei

### **Kamera-Systeme & NFC-Operationen**
- **DPS-Kamera** (192.168.0.102) - **Überwachungskamera** der gesamten APS-Fabrik-Anlage
  - **Kamera-Justierung** (hoch, rechts, runter, links) geht an DPS-Kamera
- **AIQS-Kamera** (192.168.0.103) - **Produktkamera** für Qualitätskontrolle
  - **Macht Bilder von produzierten Werkstücken**
  - **AI-Bilderkennung** analysiert Produktqualität
  - **Entscheidung:** Produktion erfolgreich → weiter im Prozess
  - **Entscheidung:** Produktion nicht erfolgreich → Aussortierung + neuer Produktionsauftrag
- **NFC-READER** über DPS-TXT Controller (192.168.0.102)

## 🔍 Detaillierte Client-Zuordnung

### **TXT Controller (auto-* Client-IDs)**
- **192.168.0.102** = **DPS TXT Controller** (`auto-AC941349-4637-28AC-2662-E51FFA998712`)
- **192.168.0.103** = **AIQS TXT Controller** (`auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4`)
- **192.168.0.104** = **CGW TXT Controller** (`auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591`)
- **192.168.0.105** = **FTS TXT Controller** (`auto-F6DFC829-567D-0985-C27D-262A31EC52D5`)
- **192.168.0.106** = **MacBook (User)** (`auto-AF5C15BD-F2F5-5B20-7C51-E02B7FE97A2E`) - DHCP nach APS-Start

### **Node-RED Instanzen (nodered_* Client-IDs)**
- **`nodered_abe9e421b6fe3efd`** = **Node-RED(SUB)** - Monitoring/Subscriber (16:25:09)
- **`nodered_94dca81c69366ec4`** = **Node-RED(PUB)** - Command/Publisher (16:25:47, 32min aktiv)
- **`nodered_2767ab1e285b62e0`** = **Node-RED(SUB)** - Monitoring (später, 16:30:12)

### **Frontend (mqttjs_* Client-IDs)**
- **`mqttjs_17ecbee3`** = **APS-Dashboard Frontend** (Web-Interface)

## 📊 Topic-Hierarchie

### **1. Module Topics (`module/v1/ff/`)**
- **`SVR4H73275`** (DPS) - **913 Nachrichten** - Hauptaktivität
- **`SVR4H76530`** (AIQS) - **118 Nachrichten** - Qualitätskontrolle
- **`SVR4H76449`** (HBW) - **114 Nachrichten** - Lagerverwaltung
- **`SVR3QA0022`** (MILL) - **99 Nachrichten** - Fräsen
- **`SVR3QA2098`** (DRILL) - **96 Nachrichten** - Bohren
- **`NodeRed`** - **66 Nachrichten** - Node-RED-vermittelte Topics

### **2. FTS Topics (`fts/v1/ff/`)**
- **`5iO4`** (FTS) - **317 Nachrichten** - Transport-System

### **3. CCU Topics (`ccu/`)**
- **`pairing`** - **807 Nachrichten** - Modul-Pairing
- **`order`** - **63 Nachrichten** - Bestellungen
- **`state`** - **24 Nachrichten** - System-Status
- **`set`** - **7 Nachrichten** - Konfiguration
- **`global`** - **1 Nachricht** - Global-Reset

### **4. TXT Topics (`/j1/txt/1/`)**
- **`f/i/order`** - **50 Nachrichten** - Bestellungen
- **`f/i/stock`** - **17 Nachrichten** - Lager-Status

## 📋 Nächste Schritte

1. **Vollständige Dokumentation** erstellen

## ⚠️ Erkenntnisse

- **Zeitpunkt korrekt:** 15:59-16:24 erfasst die Hauptaktivität
- **Filtering erfolgreich:** 90% Reduktion der Log-Größe
- **Client-IDs identifiziert:** 4 Haupt-Client-IDs im Analyse-Zeitraum
- **Kommunikationsmuster erkennbar:** TXT→FTS, Module→CCU, FTS→System
- **Node-RED-Architektur komplexer:** SUB empfängt beide Topic-Typen, PUB publiziert hauptsächlich direkt
- **NodeRed-Präfix selektiv:** Nur Module mit eigenem TXT Controller (DPS, AIQS) verwenden NodeRed-Präfix
- **Modul-Architektur erkennbar:** TXT Controller → NodeRed-Präfix, zentrale Module → direkte Kommunikation

---
*Erstellt: 18. September 2025*  
*Status: Zwischenergebnis - Analyse läuft*
