# 🚀 MQTT-Template Testing - Schnellstart

## ⚡ **Sofort starten (5 Minuten)**

### **1. Dashboard öffnen**
```
http://localhost:8501
```

### **2. MQTT verbinden**
- **Sidebar** → **🔗 Connect** Button klicken
- **Status:** ✅ Connected (grün)

### **3. Session auswählen**
- **APS Analyse Tab** → **Session-Verwaltung**
- **Dropdown:** `default_test_session` auswählen

### **4. Template testen**
- **MQTT Control Tab** öffnen
- **Steuerungsmethode:** "Template Message"
- **Template:** `DRILL_PICK_WHITE` auswählen
- **"Senden" Button** klicken

### **5. Ergebnis beobachten**
- **Erfolg:** ✅ Module reagiert
- **Fehler:** ❌ Fehlermeldung dokumentieren

---

## 📊 **6 Templates zum Testen**

### **DRILL Module (3x):**
1. `DRILL_PICK_WHITE` - Weißes Werkstück aufnehmen
2. `DRILL_PICK_BLUE` - Blaues Werkstück aufnehmen  
3. `DRILL_PICK_RED` - Rotes Werkstück aufnehmen

### **Andere Module (3x):**
4. `MILL_PICK_WHITE` - MILL weißes Werkstück
5. `HBW_STORE_WHITE` - HBW Werkstück lagern
6. `AIQS_CHECK_QUALITY_WHITE` - AIQS Qualitätsprüfung

---

## 📝 **Ergebnis-Dokumentation**

### **Für jedes Template:**
```
Template: DRILL_PICK_WHITE
Status: ✅ Erfolg / ❌ Fehler
Fehlermeldung: ________
Beobachtung: ________
```

### **Ergebnisse in Datei speichern:**
```
docs_orbis/analysis/mqtt-template-testing-ergebnisse.md
```

---

## 🎯 **Erwartete Ergebnisse**

### **Wahrscheinlich:**
- ⚠️ **ORDER-ID Probleme** (Eindeutigkeit)
- ⚠️ **Timing-Issues** (Module nicht bereit)
- ⚠️ **Error-Nachrichten** (Fehlerbehandlung)

### **Hoffentlich:**
- ✅ **Template-Struktur** funktioniert
- ✅ **MQTT-Verbindung** funktioniert
- ✅ **Einige Templates** funktionieren

---

## 🔧 **Troubleshooting**

### **MQTT nicht verbunden:**
- **Broker:** 192.168.0.100:1883
- **Credentials:** default/default
- **Firewall:** Port 1883 freigeben

### **Keine Templates verfügbar:**
- **Message Library** prüfen
- **Dashboard neu laden**
- **Logs** überprüfen

### **Template-Fehler:**
- **ORDER-ID** manuell eingeben
- **Module-Status** prüfen
- **Timing** anpassen

---

## 📈 **Nächste Schritte**

### **Nach Testing:**
1. **Ergebnisse dokumentieren**
2. **ORDER-ID Management** implementieren
3. **Modul-Status-Monitoring** verbessern
4. **Template-Optimierung** basierend auf Erkenntnissen

### **Parallel:**
- **Node-RED Tracking** implementieren
- **Error-Handling** verbessern
- **Workflow-Engine** entwickeln

---

**Status:** 🚀 **BEREIT FÜR TESTING** - Dashboard läuft, Templates verfügbar
