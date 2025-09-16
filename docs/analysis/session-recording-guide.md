# 📹 Session-Recording Guide

## 🎯 **Praktische Anleitung für MQTT-Session-Aufnahme**

### **Vorbereitung**

1. **APS-System vorbereiten**
   - Alle Module einschalten
   - MQTT-Broker läuft (192.168.0.100:1883)
   - Werkstücke bereitstellen (Rot, Weiß, Blau)

2. **Session-Logger vorbereiten**
   ```bash
   cd /Users/oliver/Projects/ORBIS-Modellfabrik
   ```

### **Session-Recording Workflow**

#### **Schritt 1: Session starten**
```bash
# Session-Logger starten
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-rot_1 --auto-start
```

#### **Schritt 2: Workflow durchführen**
- **Werkstück Rot** in Wareneingang platzieren
- **Gesamten Prozess** beobachten
- **Auf Fehler achten** und notieren

#### **Schritt 3: Session beenden**
- **"q" drücken** um Session zu stoppen
- **Session-DB prüfen** in `data/mqtt-data/sessions/`

### **📋 Session-Plan (Flexibel - Basis + Varianz bei Bedarf)**

#### **Phase 1: Wareneingang (Basis + Varianz bei Bedarf)**
```bash
# Basis-Sessions (1x pro Szenario)
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-rot --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-weiss --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-blau --auto-start

# Varianz-Sessions (nur bei Bedarf - z.B. wenn erste Session unklar war)
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-rot_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-weiss_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label wareneingang-blau_2 --auto-start
```

#### **Phase 2: Auftrag (9 Sessions)**
```bash
# Rot (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-rot_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-rot_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-rot_3 --auto-start

# Weiß (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-weiss_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-weiss_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-weiss_3 --auto-start

# Blau (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-blau_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-blau_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label auftrag-blau_3 --auto-start
```

#### **Phase 3: AI-Error (9 Sessions)**
```bash
# Rot (3x) - Qualitätsprüfung nicht bestanden
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-rot_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-rot_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-rot_3 --auto-start

# Weiß (3x) - Qualitätsprüfung nicht bestanden
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-weiss_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-weiss_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-weiss_3 --auto-start

# Blau (3x) - Qualitätsprüfung nicht bestanden
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-blau_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-blau_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label ai-not-ok-blau_3 --auto-start
```

#### **Phase 4: FTS (9 Sessions)**
```bash
# Laden (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden_3 --auto-start

# Dock an DPS (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-dock-dps_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-dock-dps_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-dock-dps_3 --auto-start

# Laden beenden (3x)
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden-beenden_1 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden-beenden_2 --auto-start
python omf/mqtt/loggers/aps_session_logger.py --session-label fts-laden-beenden_3 --auto-start
```

### **📊 Session-Überwachung**

#### **Session-Status prüfen**
```bash
# Verfügbare Sessions anzeigen
ls -la data/mqtt-data/sessions/

# Session-DB Größe prüfen
du -h data/mqtt-data/sessions/*.db
```

#### **Session-Analyse**
```bash
# Einzelne Session analysieren
python omf/mqtt/tools/mqtt_session_analyzer.py data/mqtt-data/sessions/wareneingang-rot.db

# Varianz-Analyse (optional - nur bei Bedarf)
python omf/mqtt/tools/mqtt_session_analyzer.py data/mqtt-data/sessions/wareneingang-rot.db --compare data/mqtt-data/sessions/wareneingang-rot_2.db

# Alle Sessions einer Phase analysieren
for db in data/mqtt-data/sessions/wareneingang-*.db; do
    echo "Analysiere: $db"
    python omf/mqtt/tools/mqtt_session_analyzer.py "$db"
done
```

### **⚠️ Wichtige Hinweise**

#### **Session-Recording Best Practices**
1. **Konsistente Workflows**: Immer gleiche Schritte für identische Sessions
2. **Fehler dokumentieren**: Notieren wenn etwas schief geht
3. **Timing beachten**: Zwischen Sessions Pausen einlegen
4. **System-Reset**: Bei Fehlern System zurücksetzen

#### **Troubleshooting**
- **Session startet nicht**: MQTT-Broker-Verbindung prüfen
- **Keine Daten**: Topic-Subscription prüfen
- **Session stoppt nicht**: "q" drücken oder Ctrl+C

### **📈 Erwartete Ergebnisse**

#### **Nach Phase 1 (Wareneingang)**
- 3-6 Session-DBs mit je ~100-500 MQTT-Nachrichten
- ORDER-ID Muster für Wareneingang
- Status-Transitions der beteiligten Module

#### **Nach Phase 2 (Auftrag)**
- 6-12 Session-DBs total
- Workflow-Sequenzen identifiziert
- Command-Timing-Patterns

#### **Nach Phase 3 (AI-Error)**
- 9-18 Session-DBs total
- Error-Handling Muster
- Recovery-Strategien

#### **Nach Phase 4 (FTS)**
- 12-24 Session-DBs total
- VDA5050 Standard Muster
- FTS-Kommunikation verstanden

### **🎯 Nächste Schritte**

1. **Phase 1 starten**: Wareneingang Sessions aufnehmen
2. **Erste Analyse**: ORDER-ID Muster identifizieren
3. **Weitere Phasen**: Systematisch durchführen
4. **Varianz-Analyse**: Unterschiede zwischen Sessions erkennen

---

**Status**: 📋 **BEREIT FÜR SESSION-RECORDING** - Flexibel: Basis + Varianz bei Bedarf
**Nächster Schritt**: Phase 1 - Wareneingang Sessions beginnen
