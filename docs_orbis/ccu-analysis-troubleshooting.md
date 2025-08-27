# 🔧 CCU Analysis Troubleshooting

## 📋 Problem

**"0 Templates wurden analysiert"** - Die CCU-Analyse findet keine CCU Topics.

## 🔍 Diagnose

### **1. Datenbank-Prüfung:**
```bash
# Prüfe welche Session-Datenbanken verfügbar sind
find mqtt-data/sessions -name "*.db"

# Prüfe CCU Topics in einer spezifischen Datenbank
sqlite3 mqtt-data/sessions/aps_persistent_traffic_auftrag-rot_1.db \
  "SELECT DISTINCT topic FROM mqtt_messages WHERE topic LIKE 'ccu/%' LIMIT 10;"
```

### **2. Erwartete CCU Topics:**
- `ccu/order/active`
- `ccu/order/completed`
- `ccu/order/request`
- `ccu/order/response`
- `ccu/pairing/state`
- `ccu/state/config`
- `ccu/state/flows`
- `ccu/state/layout`
- `ccu/state/stock`
- `ccu/state/version-mismatch`

## ✅ Lösungen

### **1. Session-Datenbank wechseln:**
- **Dashboard:** `⚙️ Einstellungen` → Session-Datenbank auswählen
- **Wähle eine Datenbank** mit CCU-Nachrichten (z.B. `auftrag-*` Sessions)

### **2. SQL-Query erweitern:**
```sql
-- Erweiterte Suche nach CCU-ähnlichen Topics
WHERE topic LIKE 'ccu/%' 
   OR topic LIKE 'order/%' 
   OR topic LIKE 'workflow/%'
   OR topic LIKE 'state/%'
   OR topic LIKE 'pairing/%'
```

### **3. Debug-Informationen:**
Das Dashboard zeigt jetzt:
- **Datenbank-Pfad** der verwendet wird
- **Verfügbare Topics** in der Datenbank
- **Hilfreiche Tipps** für die Lösung

## 🎯 Häufige Ursachen

### **❌ Falsche Session-Datenbank:**
- **Problem:** Dashboard verwendet eine Session ohne CCU-Nachrichten
- **Lösung:** Wechsle zu einer Session mit Auftrags-Daten

### **❌ Leere Session:**
- **Problem:** Session enthält keine MQTT-Nachrichten
- **Lösung:** Verwende eine Session mit tatsächlichen Daten

### **❌ Datenbank-Fehler:**
- **Problem:** SQLite-Verbindung fehlschlägt
- **Lösung:** Prüfe Datenbank-Integrität

## 🔗 Verwandte Dokumentation

- **[CCU Analysis Integration](ccu-analysis-integration.md)**
- **[MQTT Control Dashboard](mqtt-control-summary.md)**
- **[Template Message Manager](template-message-manager-implementation.md)**
