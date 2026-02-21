# AS-IS Doku vs. Fischertechnik-Referenz – Vergleich

**Datum:** 20.02.2026  
**Quellen:** AS-IS aus empirischer Analyse (Session-Logs, 00-REFERENCE). Mit [fischertechnik-official/](../06-integrations/fischertechnik-official/) abgeglichen – Übereinstimmung mit FT-Doku vorbehaltlich Verifizierung gegen reale Implementierung.  
**AS-IS Doku:** [aps-data-flow.md](../../02-architecture/aps-data-flow.md), [00-REFERENCE/](../06-integrations/00-REFERENCE/)

---

## 1. Übereinstimmungen ✅

| Aspekt | AS-IS Doku | Fischertechnik | Status |
|--------|------------|----------------|--------|
| **MQTT-Broker** | mosquitto, Port 1883 | Mosquitto, Port 1883, 9001 WebSocket | ✅ |
| **Topic-Namespaces** | `module/v1/ff/<serial>/...`, `fts/v1/ff/<serial>/...`, `ccu/...` | Identisch | ✅ |
| **VDA5050-Basis** | Erwähnt | Standard, mit Erweiterungen | ✅ |
| **CCU-Rolle** | Order Management, Orchestrierung | Order Management, Path Planning, State Monitoring | ✅ |
| **Node-RED Bridge** | OPC-UA ↔ MQTT | OPC-UA ↔ MQTT für Produktionsmodule | ✅ |
| **DPS/AIQS mit TXT** | TXT + OPC-UA (DPS, AIQS) | „Internal TXT“ für Kamera/NFC, PLC für Produktion | ✅ |
| **FTS** | TXT-only, MQTT | AGV = TXT 4.0, MQTT | ✅ |
| **Action States** | – | WAITING → INITIALIZING → RUNNING → FINISHED/FAILED | ✅ (implizit) |
| **CHECK_QUALITY Result** | – | PASSED, FAILED | ✅ |

---

## 2. Abweichungen & Korrekturen

### 2.1 Datenfluss-Diagramm (aps-data-flow.md)

| Aspekt | AS-IS Doku | Fischertechnik | Korrektur |
|--------|------------|----------------|-----------|
| **Cloud Gateway Rolle** | „Data Aggregation“, CAM/SENS/STATE → CG | CGW = MQTT-Forwarder (lokal ↔ Cloud), keine Aggregation | CGW-Beschreibung anpassen: „MQTT-Bridge“, nicht „Aggregation“ |
| **Datenfluss Cloud** | FTC → CG → MQTT (HTTPS) | Cloud ↔ CGW über MQTT (nicht HTTPS für Commands) | Prüfen: CGW nutzt MQTT zu Cloud-Broker |
| **QoS/Retain** | „QoS=0, Retain=False“ für State | State: QoS 1–2, **Retained** („UI persistence“) | State-Topics als retained dokumentieren |

### 2.2 State-Message-Verhalten

**Fischertechnik (02-architecture, 05-message-structure):**
- State **nur bei Änderung** (event-driven), kein periodischer 30s-Refresh
- Retained für UI-Persistenz
- „Reduces MQTT traffic by ~95%“

**AS-IS Doku:** Nicht explizit erwähnt.  
**Empfehlung:** In aps-data-flow oder 00-REFERENCE ergänzen.

### 2.3 Will-Message / Connection-Topics

**Fischertechnik (Standard):** `module/v1/ff/<serial>/connection`, `fts/v1/ff/<serial>/connection`  
**Interne Topics (Fischertechnik):** `module/v1/ff/NodeRed/cam/connection` (AIQS TXT-Kamera), `module/v1/ff/NodeRed/{DEVICEID}/...` (DPS intern)

**OSF-Umsetzung:**
- TXT-Controller publizieren Connection/Will wie in der Fischertechnik-Referenz – kein Unterschied zwischen APS und FMF.
- **OSF-UI:** Verwendet ausschließlich **Standard-Modul-Topics** (`module/v1/ff/<serial>/connection`) für Connection-Anzeige.
- **Module-Details-Sidebar:** NodeRed-Connection-Topics werden nicht angezeigt (nur Standard-Format).

### 2.4 AIQS-Hardware-Beschreibung

**AS-IS (aps-data-flow):** „AIQS[TXT-AIQS SPS S7-1200]“

**Fischertechnik:** AIQS = PLC (S7) + OPC-UA + optional internes TXT für Kamera.

**Bewertung:** Korrekt – AIQS hat S7-1200 (OPC-UA) und TXT (Kamera). Formulierung passt.

---

## 3. Lücken in unserer Doku

### 3.1 Fehlende Themen

| Thema | Fischertechnik | AS-IS | Priorität |
|-------|----------------|-------|-----------|
| **QoS-Strategie** | QoS 2 für Commands, QoS 1 für State | Nicht dokumentiert | Hoch |
| **Retained Messages** | State, connection, factsheet retained | Nicht dokumentiert | Hoch |
| **Order-Cancel** | Nur ENQUEUED, nicht IN_PROGRESS | Nicht dokumentiert | Mittel |
| **Instant Actions** | startCalibration, stopCalibration, setStatusLED, … | Teilweise (00-REFERENCE) | Mittel |
| **OVEN** | Modul dokumentiert | Nicht in unserer Hardware | – |
| **CGW Topic-Forwarding** | `/j1/txt/<id>/` Prefix | Nicht dokumentiert | Niedrig (wenn Cloud ungenutzt) |

### 3.2 CCU vs. Node-RED – Rollentrennung

**Fischertechnik:** CCU = Order Management, Path Planning. Node-RED = nur OPC-UA-Bridge, keine Order-Logik.

**AS-IS (component-overview):** Bereits korrekt – Node-RED „NICHT beteiligt an Order-Management“. ✅

---

## 4. Architektur-Diagramme – Anpassungsvorschläge

### 4.1 aps-data-flow.md

1. **Cloud Gateway-Box:** Text ändern von „Data Aggregation“ zu „MQTT-Bridge (lokal ↔ Cloud)“
2. **Legende / Hinweis:** QoS und Retained für State ergänzen
3. **Sequenzdiagramm:** FTC ↔ CGW über MQTT (nicht nur HTTPS), falls zutreffend

### 4.2 00-REFERENCE

1. **MQTT-Topic-Conventions:** Retained-Strategie ergänzen
2. **Message Examples:** QoS-Werte in Beispielen angeben
3. **Module-Serial-Mapping:** Hinweis auf `NodeRed/<serial>` bei DPS/AIQS als interne Topic-Variante

---

## 5. Zusammenfassung

| Kategorie | Anzahl |
|-----------|--------|
| Übereinstimmungen | 9+ |
| Abweichungen (korrigierbar) | 4 |
| Lücken (ergänzbar) | 6 |
| Kritische Fehler | 0 |

**Fazit:** Die AS-IS-Doku ist weitgehend konsistent mit der Fischertechnik-Referenz. Hauptkorrekturen: CGW-Rolle präzisieren, QoS/Retained dokumentieren, State-Verhalten (event-driven) ergänzen. Keine gravierenden inhaltlichen Fehler.

---

## 6. Nächste Schritte

1. ~~**aps-data-flow.md** – CGW-Beschreibung und QoS/Retained anpassen~~ ✅
2. ~~**00-REFERENCE/MQTT-Topic-Conventions** – Retained-Strategie ergänzen~~ ✅
3. ~~**OSF-UI Module-Details-Sidebar** – Connection-Anzeige auf Standard-Topics umstellen~~ ✅
4. ~~**module-serial-mapping.md** – Connection Topics Standard vs. NodeRed dokumentieren~~ ✅
5. **Optional:** [Session-Log-Analyse](../04-howto/session-log-analyse.md) – verifizieren, ob State-Topics tatsächlich retained publiziert werden (Doku-Stand aus FT-Referenz; empirische Verifizierung gegen reale APS/FMF-Implementierung fehlt)

---

**Referenzen:**
- [Fischertechnik 02-architecture](../06-integrations/fischertechnik-official/02-architecture.md)
- [Fischertechnik 05-message-structure](../06-integrations/fischertechnik-official/05-message-structure.md)
- [Fischertechnik 04-opcua-relationship](../06-integrations/fischertechnik-official/04-opcua-relationship.md)
- [FISCHERTECHNIK-OFFICIAL](../06-integrations/FISCHERTECHNIK-OFFICIAL.md)
