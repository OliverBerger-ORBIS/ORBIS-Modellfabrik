# 🏭 CCU Analysis Integration

## 📋 Übersicht

Die **CCU-Analyse** ist jetzt direkt in das APS Dashboard integriert und funktioniert ohne externe Dateien.

## 🎯 Verwendung

### **1. Dashboard öffnen:**
- **URL:** `http://localhost:8501`
- **Tab:** `⚙️ Einstellungen`
- **Untertab:** `📋 MQTT Templates`

### **2. CCU-Analyse starten:**
- **Button:** `🏭 CCU Templates analysieren`
- **Automatische Analyse** der Session-Daten
- **Echtzeit-Ergebnisse** werden angezeigt

## 📊 Analyse-Ergebnisse

### **🏭 CCU Topics werden automatisch erkannt:**
- `ccu/*` - Alle CCU Topics
- `order/*` - Order-bezogene Topics  
- `workflow/*` - Workflow-bezogene Topics

### **📋 Kategorisierte Anzeige:**
1. **📋 Order Management Topics** - Auftragsverwaltung
2. **🏭 State Management Topics** - Systemstatus
3. **🔧 Andere CCU Topics** - Sonstige CCU-Nachrichten

### **📊 Für jedes Topic:**
- **Nachrichtenanzahl** und **Sessions**
- **Template-Struktur** mit JSON-Format
- **Variable Felder** identifiziert
- **Beispiel-Nachrichten** angezeigt
- **Beschreibung** automatisch generiert

## 🔧 Technische Details

### **📁 Integration:**
- **Methode:** `analyze_ccu_topics()` in APSDashboard-Klasse
- **Datenquelle:** Aktuelle Session-Datenbank
- **SQL-Queries:** Automatische Topic-Erkennung
- **Template-Generierung:** Aus echten Nachrichten

### **🎯 Automatische Erkennung:**
```sql
WHERE topic LIKE 'ccu/%' 
   OR topic LIKE 'order/%' 
   OR topic LIKE 'workflow/%'
```

### **📋 Template-Struktur:**
- **Variable Felder** werden automatisch erkannt
- **JSON-Templates** aus echten Nachrichten
- **Beschreibungen** basierend auf Topic-Namen

## ✅ Status

**✅ Vollständig implementiert und funktionsfähig**

- **Button funktioniert** ohne externe Abhängigkeiten
- **Echtzeit-Analyse** der Session-Daten
- **Kategorisierte Anzeige** der CCU Topics
- **Template-Generierung** automatisch

## 🔗 Verwandte Dokumentation

- **[MQTT Control Dashboard](mqtt-control-summary.md)**
- **[Template Message Manager](template-message-manager-implementation.md)**
- **[Project Status](project-status.md)**
