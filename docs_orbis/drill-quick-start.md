# 🚀 DRILL Quick Start - W1 Pick-Drill-Drop

## ⚡ Schnellstart (5 Minuten)

### **1. Session Logger starten**
```bash
source .venv/bin/activate
python src_orbis/mqtt/loggers/aps_session_logger.py --session drill-test-w1
```

### **2. Dashboard öffnen**
- URL: `http://localhost:8501`
- **Hauptmenü:** "🎮 MQTT Module Control" wählen
- **Steuerungsmethode:** "Template Message" auswählen
- **Tab:** "🧪 Template Testing" wählen

### **3. Sequenz ausführen**
1. **DRILL_PICK_WHITE** → Senden
2. **Warten** bis PICK abgeschlossen (~10s)
3. **DRILL_PROCESS_WHITE** → Senden  
4. **Warten** bis DRILL abgeschlossen (~30s)
5. **DRILL_DROP_WHITE** → Senden

### **4. Monitoring**
- **MQTT Analysis** Tab öffnen
- **Session:** `drill-test-w1` auswählen
- **Module:** DRILL filtern
- **Status** verfolgen

## 📋 Checkliste

- [ ] Werkstück W1 verfügbar (NFC: `04798eca341290`)
- [ ] DRILL-Station erreichbar (192.168.0.50)
- [ ] MQTT-Broker aktiv (192.168.0.100)
- [ ] Session Logger läuft
- [ ] Dashboard geöffnet
- [ ] Sequenz erfolgreich ausgeführt

## 🎯 Erwartetes Ergebnis

**Status-Sequenz:**
1. **PICK:** `IDLE` → `RUNNING` → `IDLE`
2. **DRILL:** `IDLE` → `RUNNING` → `IDLE` (30s)
3. **DROP:** `IDLE` → `RUNNING` → `IDLE`

**Werkstück W1:** Gebohrt und bereit für nächsten Schritt
