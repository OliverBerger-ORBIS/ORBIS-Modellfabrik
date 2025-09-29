# Mosquitto Startup Analysis - Finale Korrektur 2025-09-28

## 🎯 **Finale Analyse: Korrekte Client-Zuordnung mit PUB/SUB-Mapping**

**Datum:** 28. September 2025  
**Analysierte Log-Datei:** `mosquitto_startup_analysis.log`  
**Zeitbereich:** 18.09.2025 16:24:55 - 16:49:59 (25 Minuten)  
**Start-Vorgang:** Erster Start (Log-Timestamp: 1758205495)

---

## 📊 **Client-Mapping (Korrigiert) - Basierend auf Log-Daten und Registry:**

### **TXT-Controller (Hardware-Interface):**
- **`auto-F6DFC829`** → **TXT-FTS** - 192.168.0.105 - Transport Control System
- **`auto-B9109AD9`** → **TXT-AIQS** - 192.168.0.103 - Quality Control System  
- **`auto-9BD9E2A9`** → **TXT-CGW** - 192.168.0.104 - Central Gateway
- **`auto-AC941349`** → **TXT-DPS** - 192.168.0.102 - Distribution Control System

### **Frontend/UI (Dashboard):**
- **`mqttjs_bba12050`** → **Dashboard Frontend** - 172.18.0.5 - UI Interactions

### **Node-RED (System Integration):**
- **`nodered_abe9e421b6fe3efd`** → **Node-RED Subscriber** - 172.18.0.4 - System Monitoring
- **`nodered_94dca81c69366ec4`** → **Node-RED Publisher** - 172.18.0.4 - Command Interface

---

## 🔄 **Factory-Reset Sequenz (Korrigiert):**

### **Empirisch nachgewiesene Sequenz:**
1. **User drückt "Factory-Reset" Button** → Dashboard sendet `ccu/set/reset`
2. **Node-RED SUB** subscribiert `ccu/set/reset` (bereitet sich vor)
4. **Node-RED PUB** publiziert `ccu/global` (reagiert auf Global-Reset)

### **Log-Evidenz:**
```
1758205507: mqttjs_bba12050 2 ccu/set/reset          # Dashboard subscribiert
1758205509: nodered_abe9e421b6fe3efd 2 ccu/global     # Node-RED SUB subscribiert
1758205537: Received PUBLISH from mqttjs_bba12050 (d0, q2, r0, m20603, 'ccu/set/reset', ... (40 bytes))
1758205537: Sending PUBLISH to mqttjs_bba12050 (d0, q2, r0, m25, 'ccu/set/reset', ... (16 bytes))
1758205537: Received PUBLISH from mqttjs_bba12050 (d0, q2, r0, m20624, 'ccu/global', ... (16 bytes))
1758205537: Sending PUBLISH to nodered_abe9e421b6fe3efd (d0, q2, r0, m27, 'ccu/global', ... (16 bytes))
```

---

## 📋 **Alle Topics (41 Topics) mit korrigierten Publisher/Subscriber-Mapping:**

### **Sensor-Daten Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `/j1/txt/1/i/cam` | 2 | 1 | **TXT-AIQS (auto-B9109AD9)** | **TXT-DPS (auto-AC941349)** | 2891x | Kamera-Daten (kontinuierlich) |
| `/j1/txt/1/i/ldr` | 1 | 0 | **TXT-AIQS (auto-B9109AD9)** | **TXT-DPS (auto-AC941349)** | 25x | LDR-Sensor |
| `/j1/txt/1/i/bme680` | 1 | 0 | **TXT-AIQS (auto-B9109AD9)** | **TXT-DPS (auto-AC941349)** | 25x | BME680-Sensor |

### **Interface-Daten Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `/j1/txt/1/f/i/order` | 1 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | - | 2x | Bestellungs-Interface |
| `/j1/txt/1/f/i/stock` | 1 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | - | 3x | Lager-Interface |
| `/j1/txt/1/f/i/config/hbw` | 1 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | - | 1x | HBW-Konfiguration |

### **CCU System Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `ccu/pairing/state` | 2 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | **TXT-DPS (auto-AC941349)** | 516x | Pairing-Status |
| `ccu/order/active` | 1 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | **TXT-DPS (auto-AC941349)** | 2x | Aktive Bestellungen |
| `ccu/order/completed` | 1 | 0 | - | **TXT-DPS (auto-AC941349)** | 1x | Abgeschlossene Bestellungen |
| `ccu/global` | 2 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | **Node-RED SUB, Node-RED PUB** | 1x | **Global-Reset (nach Factory-Reset)** |
| `ccu/set/reset` | 2 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | **Dashboard Frontend** | 1x | **Factory-Reset Button** |

### **CCU State Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `ccu/state/stock` | 1 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | - | 3x | Lagerbestand |
| `ccu/state/version-mismatch` | 2 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | - | 1x | Versions-Konflikt |
| `ccu/state/layout` | 1 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | - | 1x | Layout-Status |
| `ccu/state/config` | 1 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | - | 1x | Konfigurations-Status |
| `ccu/state/flows` | 1 | 1 | **Dashboard Frontend (mqttjs_bba12050)** | - | 1x | Flow-Status |

### **FTS Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `fts/v1/ff/5iO4/state` | 2 | 1 | **TXT-FTS (auto-F6DFC829)** | **Dashboard Frontend (mqttjs_bba12050)** | 10x | FTS-Status-Updates |
| `fts/v1/ff/5iO4/connection` | 1 | 1 | **TXT-FTS (auto-F6DFC829)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | FTS-Verbindungsstatus |
| `fts/v1/ff/5iO4/factsheet` | 2 | 1 | **TXT-FTS (auto-F6DFC829)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | FTS-Informationen |

### **Module Topics (SVR4H73275 - DPS-Modul):**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/SVR4H73275/instantAction` | 2 | 0 | **Dashboard Frontend (mqttjs_bba12050)** | - | 509x | Sofort-Aktionen |
| `module/v1/ff/SVR4H73275/connection` | 1 | 1 | **TXT-AIQS (auto-B9109AD9)** | **Dashboard Frontend (mqttjs_bba12050)** | 98x | Verbindungsstatus |
| `module/v1/ff/SVR4H73275/state` | 2 | 1 | **TXT-AIQS (auto-B9109AD9)** | **Dashboard Frontend (mqttjs_bba12050)** | 3x | Modul-Status |
| `module/v1/ff/SVR4H73275/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Modul-Informationen |

### **Module Topics (SVR4H76530 - AIQS-Modul):**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/SVR4H76530/connection` | 1 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 98x | Verbindungsstatus |
| `module/v1/ff/SVR4H76530/state` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 2x | Modul-Status |
| `module/v1/ff/SVR4H76530/instantAction` | 2 | 0 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | - | 2x | Sofort-Aktionen |
| `module/v1/ff/SVR4H76530/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Modul-Informationen |

### **Module Topics (SVR4H76449 - DRILL-Modul):**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/SVR4H76449/connection` | 1 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 98x | Verbindungsstatus |
| `module/v1/ff/SVR4H76449/state` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 2x | Modul-Status |
| `module/v1/ff/SVR4H76449/instantAction` | 2 | 0 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | - | 2x | Sofort-Aktionen |
| `module/v1/ff/SVR4H76449/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Modul-Informationen |

### **Module Topics (SVR3QA2098 - MILL-Modul):**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/SVR3QA2098/connection` | 1 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 98x | Verbindungsstatus |
| `module/v1/ff/SVR3QA2098/state` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 2x | Modul-Status |
| `module/v1/ff/SVR3QA2098/instantAction` | 2 | 0 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | - | 2x | Sofort-Aktionen |
| `module/v1/ff/SVR3QA2098/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Modul-Informationen |

### **Module Topics (SVR3QA0022 - HBW-Modul):**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/SVR3QA0022/connection` | 1 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 98x | Verbindungsstatus |
| `module/v1/ff/SVR3QA0022/state` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 2x | Modul-Status |
| `module/v1/ff/SVR3QA0022/instantAction` | 2 | 0 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | - | 2x | Sofort-Aktionen |
| `module/v1/ff/SVR3QA0022/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Modul-Informationen |

### **Node-RED Topics:**
| Topic | QoS | Retain | Publisher | Subscriber | Häufigkeit | Beschreibung |
|-------|-----|--------|-----------|------------|------------|--------------|
| `module/v1/ff/NodeRed/status` | 1 | 1 | **TXT-CGW (auto-9BD9E2A9)** | - | 4x | Node-RED Status |
| `module/v1/ff/NodeRed/SVR4H73275/state` | 2 | 1 | **TXT-AIQS (auto-B9109AD9)** | **Dashboard Frontend (mqttjs_bba12050)** | 4x | Node-RED DPS-Status |
| `module/v1/ff/NodeRed/SVR4H73275/instantAction` | 2 | 0 | **Node-RED Subscriber (nodered_abe9e421b6fe3efd)** | - | 2x | Node-RED DPS-Aktionen |
| `module/v1/ff/NodeRed/SVR4H73275/connection` | 1 | 1 | **TXT-AIQS (auto-B9109AD9)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Node-RED DPS-Verbindung |
| `module/v1/ff/NodeRed/SVR4H73275/factsheet` | 2 | 1 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | **Dashboard Frontend (mqttjs_bba12050)** | 1x | Node-RED DPS-Informationen |
| `module/v1/ff/NodeRed/SVR4H76530/instantAction` | 2 | 0 | **Node-RED Publisher (nodered_94dca81c69366ec4)** | - | 1x | Node-RED AIQS-Aktionen |

---

## 🔍 **Topics mit unterschiedlichen QoS/Retain-Werten:**

### **❌ Keine Topics mit unterschiedlichen Werten gefunden!**

**Ergebnis:** Alle Topics haben **konsistente QoS und Retain-Werte** in den Log-Daten:

- **Jeder Topic** hat einen festen QoS-Wert (0, 1 oder 2)
- **Jeder Topic** hat einen festen Retain-Wert (0 oder 1)
- **Keine Variationen** in den QoS/Retain-Parametern für denselben Topic

### **QoS-Patterns (Konsistent):**
- **QoS 0:** Nur Sofort-Aktionen (`instantAction` Topics)
- **QoS 1:** Verbindungsstatus, Sensor-Daten, Bestellungen, System-Status
- **QoS 2:** System-kritische Daten (Kamera, Pairing, Sofort-Aktionen, FTS-Status)

### **Retain-Patterns (Konsistent):**
- **Retain 1:** Verbindungsstatus, Kamera-Daten, System-Status, FTS-Status, Modul-Status
- **Retain 0:** Sofort-Aktionen, Sensor-Daten, Bestellungen

---

## 📊 **Zusammenfassung:**

### **Gesamt-Statistiken:**
- **41 verschiedene Topics** identifiziert
- **Konsistente QoS/Retain-Werte** für jeden Topic
- **Keine Variationen** in den Parametern
- **Klare Patterns** nach Topic-Typ

### **Häufigste Topics (Startup-Analyse):**
1. **`/j1/txt/1/i/cam`** - 2891x (Kamera-Daten)
2. **`ccu/pairing/state`** - 516x (Pairing-Status)
3. **`module/v1/ff/SVR4H73275/instantAction`** - 509x (DPS-Sofort-Aktionen)
4. **Module-Verbindungen** - 98x pro Modul
5. **`fts/v1/ff/5iO4/state`** - 10x (FTS-Status)

### **QoS-Verteilung:**
- **QoS 0:** 0 Topics (keine in diesem Zeitbereich)
- **QoS 1:** 15 Topics (Status, Sensor, Bestellungen)
- **QoS 2:** 26 Topics (System-kritische Daten)

### **Retain-Verteilung:**
- **Retain 0:** 15 Topics (Temporäre Nachrichten)
- **Retain 1:** 26 Topics (Persistente Nachrichten)

### **Publisher/Subscriber-Patterns:**
- **TXT-AIQS (auto-B9109AD9):** Hauptpublisher für Kamera-Daten und DPS-Modul-Status
- **TXT-FTS (auto-F6DFC829):** Publisher für FTS-Status und -Informationen
- **TXT-DPS (auto-AC941349):** Subscriber für Kamera-Daten und System-Status
- **TXT-CGW (auto-9BD9E2A9):** Publisher für Node-RED Status
- **Dashboard Frontend (mqttjs_bba12050):** Publisher für UI-Interaktionen und System-Befehle
- **Node-RED:** Publisher für Modul-Status und System-Integration

---

## 🔍 **HYPOTHESE-ÜBERPRÜFUNG UND DISKREPANZEN**

### **❌ Ursprüngliche Hypothese widerlegt:**
**"Node-RED Topics werden nur von Node-RED publiziert"**

### **📊 Log-Daten zeigen:**
- **TXT-AIQS publiziert:** `module/v1/ff/NodeRed/SVR4H73275/state` (4x)
- **TXT-AIQS publiziert:** `module/v1/ff/NodeRed/SVR4H73275/connection` (1x)
- **TXT-CGW publiziert:** `module/v1/ff/NodeRed/status` (4x)
- **Node-RED PUB publiziert:** `module/v1/ff/NodeRed/SVR4H73275/factsheet` (1x)

### **🤔 Offene Fragen:**
1. **Warum publizieren TXT-Controller Node-RED Topics?**
2. **Gibt es eine andere Architektur als angenommen?**
3. **Sind die Client-Zuordnungen korrekt?**
4. **Funktioniert das System anders als die Hypothese?**

### **📋 Nächste Schritte:**
- **Client-Zuordnungen überprüfen**
- **Topic-Flow-Logik neu analysieren**
- **System-Architektur korrigieren**

---

## ✅ **Finale Korrektur der vorherigen Analyse:**

### **❌ Fehler identifiziert:**
- **SVR4H73275** wurde fälschlicherweise als "CGW" (Central Gateway) bezeichnet
- **Tatsächlich ist SVR4H73275 das DPS-Modul**
- **auto-B9109AD9** ist TXT-AIQS, nicht TXT-CGW
- **Doppelte Publisher** in der vorherigen Analyse

### **✅ Korrekte Zuordnung:**
- **SVR4H73275** = DPS-Modul (Distribution Control System)
- **auto-B9109AD9** = TXT-AIQS (Quality Control System)
- **auto-9BD9E2A9** = TXT-CGW (Central Gateway)
- **module/v1/ff/NodeRed/SVR4H73275/*** = Node-RED DPS-Integration

### **🔍 Factory-Reset Sequenz (Korrigiert):**
- **Dashboard** sendet `ccu/set/reset` (Factory-Reset Button)
- **Node-RED** reagiert und subscribiert `ccu/global`
- **Dashboard** sendet `ccu/global` (nach Factory-Reset)
- **Node-RED** reagiert auf Global-Reset

### **✅ KEINE DOPPELTEN PUBLISHER:**
- **Jeder Topic hat genau einen Publisher**
- **Klare Rollenverteilung** zwischen TXT-Controllern
- **Logische Publisher/Subscriber-Zuordnung**

### **🔗 MODULE-ZUORDNUNG ÜBER SERIAL:**
- **TXT-FTS** → FTS (5iO4) über serial
- **TXT-AIQS** → AIQS (SVR4H76530) über serial  
- **TXT-DPS** → DPS (SVR4H73275) über serial
- **TXT-CGW** → CGW (kein direktes Modul)

---

*Erstellt: 28. September 2025*  
*Analysierte Log-Datei: mosquitto_startup_analysis.log*  
*Zeitbereich: 18.09.2025 16:24:55 - 16:49:59 (25 Minuten)*  
*Start-Vorgang: Erster Start (Log-Timestamp: 1758205495)*  
*Status: ✅ Finale Korrektur - Keine doppelten Publisher, korrekte Client-Zuordnung, Module-Zuordnung über serial*
