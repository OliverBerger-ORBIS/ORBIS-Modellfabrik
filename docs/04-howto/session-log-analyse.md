# Session-Log-Analyse – Anleitung

**Zweck:** Empirische Verifizierung von MQTT-Topics, Topics-Struktur, und optional QoS/Retained-Strategie.

**Kontext (Warum QoS/Retained prüfen?):** Unsere Doku ([mqtt-topic-conventions](../06-integrations/00-REFERENCE/mqtt-topic-conventions.md)) übernimmt die Retained-Strategie aus der [Fischertechnik-Referenz](../06-integrations/fischertechnik-official/) – State/connection/factsheet als retained. Ob APS/FMF tatsächlich so publiziert, ist ungeprüft; relevant z.B. für UI-Persistenz und Reconnect-Verhalten. Vergleiche [AS-IS vs. Fischertechnik](../07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md).

---

## 1. Vorhandene Werkzeuge

### 1.1 Session Manager (Streamlit)

**Start:**
```bash
cd session_manager
streamlit run app.py
```

**Tab „Session Analysis“:**
- Session aus `data/omf-data/sessions/` auswählen (`.db`)
- Timeline-Visualisierung (Plotly)
- Topic-Statistiken
- Payload-Anzeige

**Dokumentation:** [session-manager/session-analysis.md](helper_apps/session-manager/session-analysis.md)

### 1.2 Modul-spezifische Python-Skripte

Für DPS, AIQS, FTS, HBW, DRILL, MILL:

```bash
# Beispiel DPS
python scripts/analyze_dps_sessions.py data/omf-data/sessions/auftrag-blau_1.log

# Beispiel AIQS
python scripts/analyze_aiqs_sessions.py data/omf-data/sessions/auftrag-rot_1.log

# Mit Ausgabeverzeichnis
python scripts/analyze_dps_sessions.py data/omf-data/sessions/auftrag-blau_1.log --output-dir data/omf-data/dps-analysis
```

**Ausgabe:** Topic-Verteilung, Commands, Kontext-Messages.

### 1.3 SQLite-Direktabfragen

```bash
sqlite3 data/omf-data/sessions/auftrag-blau_1.db
```

```sql
-- Alle Topics mit Häufigkeit
SELECT topic, COUNT(*) as cnt FROM mqtt_messages GROUP BY topic ORDER BY cnt DESC;

-- State-Topics
SELECT timestamp, topic, substr(payload, 1, 80) 
FROM mqtt_messages 
WHERE topic LIKE '%/state' 
ORDER BY timestamp;

-- Connection-Topics
SELECT timestamp, topic, payload 
FROM mqtt_messages 
WHERE topic LIKE '%/connection';

-- Factsheet-Topics
SELECT topic, substr(payload, 1, 200) 
FROM mqtt_messages 
WHERE topic LIKE '%/factsheet';
```

### 1.4 Session Replay (OSF-Tests)

```bash
npx tsx scripts/replay-sessions.ts --session data/omf-data/sessions/auftrag-blau_1.log
```

**Dokumentation:** [scripts/README-replay.md](../../scripts/README-replay.md)

---

## 2. Session-Formate und -Quellen

### Aufnahmepfad

| Quelle | Format | Felder | QoS/Retain |
|--------|--------|--------|------------|
| **Session Recorder** (Session Manager) | `.db` + `.log` | topic, payload, timestamp | ❌ nicht gespeichert |
| **Topic Recorder** (Session Manager) | JSON pro Topic | topic, payload, qos, retain, timestamp | ✅ |

### Log-Format (Session Recorder)

JSON-Lines (eine Zeile = ein Objekt):

```json
{"topic": "module/v1/ff/SVR4H73275/state", "payload": "{...}", "timestamp": "2025-08-14T16:14:45.240146"}
```

---

## 3. QoS/Retained prüfen (optional)

**Ziel:** Prüfen, ob State-/Connection-/Factsheet-Topics tatsächlich mit `retained=true` publiziert werden (Fischertechnik-Doku).

### 3.1 Einschränkung

Der **Session Recorder** speichert aktuell **kein** QoS und Retain. Daher:

- Keine QoS/Retain-Analyse aus bestehenden `.db`/`.log`-Sessions möglich.
- Alternativen siehe unten.

### 3.2 Option A: Session Recorder erweitern

Session Recorder so anpassen, dass der MQTT-Client-Callback `qos` und `retain` erhält und beide Felder mit speichert (analog Topic Recorder).

### 3.3 Option B: mosquitto_sub

Retain-Status ist im Broker gespeichert. Bei direktem Subscribe sichtbar:

```bash
# Alle retained Messages beim Connect
mosquitto_sub -h 192.168.0.100 -t '#' -v

# Nur State-Topics
mosquitto_sub -h 192.168.0.100 -t 'module/v1/ff/+/state' -v
```

Retain wird hier nicht explizit angezeigt; man kann aber prüfen, ob beim Reconnect sofort Messages ankommen (typisch für retained).

### 3.4 Option C: MQTT Traffic Logger (wenn verfügbar)

Falls `mqtt_bridge_logger` oder `comprehensive_mqtt_logger` (siehe [mqtt-traffic-logging.md](setup/mqtt-traffic-logging.md)) verwendet werden – diese können `qos` und `retained` loggen, sofern in der DB-Schema vorgesehen.

### 3.5 Option D: Topic Recorder nutzen

Der **Topic Recorder** speichert pro Topic-Datei `qos` und `retain`.  
Daten liegen in `data/omf-data/test_topics/` – dort können retained-Topics gezählt bzw. ausgewertet werden.

---

## 4. Typische Analyse-Abläufe

### Topic-Struktur prüfen

```bash
sqlite3 data/omf-data/sessions/auftrag-blau_1.db \
  "SELECT DISTINCT topic FROM mqtt_messages ORDER BY topic;"
```

### Connection-Topics (Standard vs. NodeRed)

```sql
SELECT topic, COUNT(*) 
FROM mqtt_messages 
WHERE topic LIKE '%/connection%' 
GROUP BY topic;
```

### State-Updates pro Modul

```bash
python scripts/analyze_dps_sessions.py data/omf-data/sessions/<session>.log
# Zeigt Topic-Verteilung inkl. module/v1/ff/.../state
```

---

## 5. Verweise

- [Session Manager README](../../session_manager/README.md)
- [Session Analysis Tab](helper_apps/session-manager/session-analysis.md)
- [MQTT Traffic Logging](setup/mqtt-traffic-logging.md)
- [AS-IS-FISCHERTECHNIK-COMPARISON](../../docs/07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md) – Kontext „Session-Log-Analyse“
