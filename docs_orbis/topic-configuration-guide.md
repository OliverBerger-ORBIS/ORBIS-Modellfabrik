# Topic-Konfiguration Guide

## **Übersicht**

Die Topic-Konfiguration ist eine zentrale Verwaltung aller MQTT-Topics für die ORBIS Modellfabrik. Sie ersetzt verstreute Topic-Mappings und bietet eine einheitliche Struktur für alle Topic-bezogenen Informationen.

## **Dateien**

### **Konfigurationsdatei:**
- **Pfad**: `src_orbis/mqtt/config/topic_config.yml`
- **Zweck**: Zentrale YAML-Konfiguration aller MQTT-Topics

### **Manager-Klasse:**
- **Pfad**: `src_orbis/mqtt/tools/topic_manager.py`
- **Zweck**: Python-Klasse für Topic-Verwaltung und -Abfragen

## **Struktur**

### **Topic-Kategorien:**

#### **1. CCU (Central Control Unit)**
- **Icon**: 🏭
- **Beschreibung**: Zentrale Steuerungseinheit - Koordiniert alle Module und Workflows
- **Topics**: 10 Topics für Status, Steuerung und Verbindung
- **Sub-Kategorien**: State, Control, Status

#### **2. TXT (TXT 4.0 Controller)**
- **Icon**: 🎛️
- **Beschreibung**: Fischertechnik Controller für Sensorik und Aktorik
- **Topics**: 17 Topics für Input/Output, Sensoren und Broadcast
- **Sub-Kategorien**: Function Input, Function Output, Control, Input, Output

#### **3. MODULE (APS-Module)**
- **Icon**: ⚙️
- **Beschreibung**: Einzelne Produktionsmodule (MILL, DRILL, AIQS, DPS, HBW, FTS)
- **Topics**: 24 Topics mit Sub-Kategorien
- **Sub-Kategorien**: Connection, State, Order, Factsheet

#### **4. Node-RED (Gateway)**
- **Icon**: 🔄
- **Beschreibung**: Übersetzt zwischen OPC-UA und MQTT Protokollen
- **Topics**: 16 Topics für Gateway-Funktionalität
- **Sub-Kategorien**: Connection, State, Factsheet, Status (wie Module)

### **Sub-Kategorien (alle Kategorien):**

#### **CCU Sub-Kategorien:**
- **State** 📊: CCU-Status und Workflow-Informationen (4 Topics)
- **Control** 🎮: CCU-Steuerungsbefehle (3 Topics)
- **Status** 📡: CCU-Verbindungsstatus und Gesundheit (3 Topics)

#### **TXT Sub-Kategorien:**
- **Function Input** 📥: TXT Function Input-Nachrichten (5 Topics)
- **Function Output** 📤: TXT Function Output-Nachrichten (4 Topics)
- **Control** 🎮: TXT Control-Befehle (3 Topics)
- **Input** 📥: TXT Input-Sensordaten (4 Topics)
- **Output** 📤: TXT Output-Nachrichten (1 Topic)

#### **Module Sub-Kategorien:**
- **Connection** 🔗: Verbindungsstatus zwischen Modul und CCU (6 Topics)
- **State** 📊: Aktueller Modul-Status und Betriebszustand (6 Topics)
- **Order** 📋: Befehle und Aufträge an das Modul (6 Topics)
- **Factsheet** 📄: Modul-Konfiguration und Metadaten (6 Topics)

#### **Node-RED Sub-Kategorien:**
- **Connection** 🔗: Node-RED Gateway-Verbindungen (5 Topics)
- **State** 📊: Node-RED Gateway-Status (5 Topics)
- **Factsheet** 📄: Node-RED Gateway-Konfiguration (5 Topics)
- **Status** 📡: Node-RED Gateway-Status (1 Topic)

## **TopicManager Klasse**

### **Hauptfunktionen:**

```python
# Initialisierung
topic_manager = get_topic_manager()

# Topic-Informationen abrufen
friendly_name = topic_manager.get_friendly_name("ccu/state")
topic_info = topic_manager.get_topic_info("ccu/state")
category = topic_manager.get_topic_category("ccu/state")

# Kategorien abrufen
categories = topic_manager.get_categories()
ccu_topics = topic_manager.get_topics_by_category("CCU")
module_topics = topic_manager.get_topics_by_module("MILL")

# Statistiken
stats = topic_manager.get_statistics()
```

### **Backward Compatibility:**

```python
# Alte Funktionen funktionieren weiterhin
friendly_name = topic_manager.get_friendly_topic_name("ccu/state")
all_mappings = topic_manager.get_all_mapped_topics()
unmapped = topic_manager.get_unmapped_topics(topic_list)
```

## **Dashboard-Integration**

### **Neuer Tab: "Topic-Konfiguration"**
- **Ort**: Einstellungen → Topic-Konfiguration (Tab 4 von 5)
- **Anzeige**: Pro Kategorie collapsible Sektionen
- **Inhalt**: Tabellarische Darstellung aller Topics
- **Tab-Reihenfolge**: 1) Dashboard, 2) Module, 3) NFC-Codes, 4) Topic-Konfiguration, 5) MQTT-Templates

### **Features:**
- ✅ **Kategorien-Übersicht**: Alle 4 Kategorien mit Icons und Beschreibungen (kollabiert)
- ✅ **Topic-Tabellen**: Pro Kategorie mit Topic, Friendly-Name, Sub-Kategorie, Modul
- ✅ **Universelle Filterung**: Sub-Kategorie-Filter für alle Kategorien, Modul-Filter für MODULE und Node-RED
- ✅ **Statistiken**: Gesamt-Topics, Kategorien, Sub-Kategorien
- ✅ **Sub-Kategorie-Details**: Icons und Beschreibungen für alle Kategorien
- ✅ **Vollständige Sub-Kategorien**: Alle Kategorien haben strukturierte Sub-Kategorien

### **Tabellen-Spalten:**
1. **Topic**: Vollständiger MQTT-Topic-Pfad
2. **Friendly-Name**: Benutzerfreundlicher Name für Dashboard
3. **Sub-Kategorie**: Modul-Sub-Kategorie mit Icon (nur bei Modulen)
4. **Modul**: Modul-Name (nur bei Modulen)
5. **Beschreibung**: Detaillierte Topic-Beschreibung

## **Topic-Beispiele**

### **CCU Topics:**
```yaml
"ccu/state":
  category: "CCU"
  friendly_name: "CCU : state"
  description: "Zentraler System-Status"
```

### **TXT Topics:**
```yaml
"/j1/txt/1/f/i/stock":
  category: "TXT"
  friendly_name: "TXT : f : i : stock"
  description: "TXT Input - Werkstück-Lagerbestand"
```

### **Module Topics:**
```yaml
"module/v1/ff/SVR3QA2098/connection":
  category: "MODULE"
  sub_category: "Connection"
  module: "MILL"
  friendly_name: "MILL : connection"
  description: "MILL-Verbindungsstatus"
```

### **Node-RED Topics:**
```yaml
"module/v1/ff/NodeRed/SVR4H76530/connection":
  category: "Node-RED"
  sub_category: "Connection"
  module: "AIQS"
  friendly_name: "NodeRed → AIQS : connection"
  description: "Node-RED Gateway - AIQS-Verbindung"
```

## **Verwendung in Analysatoren**

### **Integration in Template-Analyzern:**

```python
from src_orbis.mqtt.tools.topic_manager import get_topic_manager

topic_manager = get_topic_manager()

# Topic-Informationen für Template-Generierung
for topic in discovered_topics:
    friendly_name = topic_manager.get_friendly_name(topic)
    category = topic_manager.get_topic_category(topic)
    module = topic_manager.get_topic_module(topic)
    
    # Template mit Friendly-Names generieren
    template = {
        "topic": topic,
        "friendly_name": friendly_name,
        "category": category,
        "module": module
    }
```

### **Topic-Erkennung:**

```python
# Bekannte Topics identifizieren
known_topics = []
unknown_topics = []

for topic in all_topics:
    if topic_manager.is_known_topic(topic):
        known_topics.append(topic)
    else:
        unknown_topics.append(topic)
```

## **Vorteile**

### **1. Zentralisierung:**
- ✅ Alle Topic-Informationen an einem Ort
- ✅ Einheitliche Struktur für alle Kategorien
- ✅ Einfache Wartung und Updates

### **2. Erweiterbarkeit:**
- ✅ Neue Kategorien einfach hinzufügbar
- ✅ Neue Module automatisch unterstützt
- ✅ Flexible Sub-Kategorien für Module

### **3. Dashboard-Integration:**
- ✅ Benutzerfreundliche Anzeige
- ✅ Collapsible Kategorien
- ✅ Detaillierte Statistiken

### **4. Backward Compatibility:**
- ✅ Alte Topic-Mapping-Funktionen funktionieren weiterhin
- ✅ Schrittweise Migration möglich
- ✅ Keine Breaking Changes

## **Migration von alten Systemen**

### **Ersetzte Dateien:**
- ❌ `src_orbis/mqtt/dashboard/config/topic_mapping.py` (✅ **GELÖSCHT**)
- ❌ Verstreute Topic-Mappings in verschiedenen Dateien

### **Neue Struktur:**
- ✅ `src_orbis/mqtt/config/topic_config.yml` (zentrale Konfiguration)
- ✅ `src_orbis/mqtt/tools/topic_manager.py` (zentrale Verwaltung)

### **Migration-Schritte:**
1. ✅ **Topic-Informationen** aus alten Dateien in `topic_config.yml` übertragen
2. ✅ **Dashboard** auf `TopicManager` umgestellt
3. ✅ **Filter-Komponenten** auf `TopicManager` umgestellt
4. ✅ **Tests** auf `TopicManager` umgestellt
5. ✅ **Alte Dateien** gelöscht
6. ✅ **Tab-Reihenfolge** optimiert (Topic-Mappings entfernt)
7. 🔄 **Analyzern** verwenden bereits `ModuleManager` (keine Änderung nötig)

## **Wartung und Updates**

### **Neue Topics hinzufügen:**
1. **YAML-Datei** bearbeiten: `src_orbis/mqtt/config/topic_config.yml`
2. **Topic-Eintrag** hinzufügen mit allen erforderlichen Feldern
3. **Dashboard** automatisch aktualisiert

### **Neue Module hinzufügen:**
1. **Module-ID** in `module_config.yml` hinzufügen
2. **Topic-Einträge** für alle 4 Sub-Kategorien erstellen
3. **Friendly-Names** entsprechend formatieren

### **Neue Kategorien hinzufügen:**
1. **Kategorie-Eintrag** in `categories` Sektion hinzufügen
2. **Icon und Beschreibung** definieren
3. **Topic-Einträge** für neue Kategorie erstellen

## **Statistiken**

### **Aktuelle Zahlen:**
- **Gesamt Topics**: 67
- **Kategorien**: 4 (CCU, TXT, MODULE, Node-RED)
- **Module**: 6 (MILL, DRILL, AIQS, DPS, HBW, FTS)
- **Sub-Kategorien**: 12 (alle Kategorien haben Sub-Kategorien)

### **Verteilung:**
- **CCU**: 10 Topics (14.9%)
- **TXT**: 17 Topics (25.4%)
- **MODULE**: 24 Topics (35.8%)
- **Node-RED**: 16 Topics (23.9%)

### **Sub-Kategorie-Verteilung:**
- **CCU**: State (4), Control (3), Status (3)
- **TXT**: Function Input (5), Function Output (4), Control (3), Input (4), Output (1)
- **Module**: Connection (6), State (6), Order (6), Factsheet (6)
- **Node-RED**: Connection (5), State (5), Factsheet (5), Status (1)

## **Zukunft**

### **Geplante Erweiterungen:**
- 🔄 **Template-Integration**: Automatische Template-Generierung
- 📊 **Topic-Analyse**: Erweiterte Statistiken und Metriken
- 🔍 **Topic-Validierung**: Automatische Topic-Struktur-Validierung
- 📈 **Trend-Analyse**: Topic-Nutzung über Zeit

### **Mögliche Verbesserungen:**
- 🎯 **Topic-Prioritäten**: Wichtige vs. unwichtige Topics
- 🔐 **Topic-Sicherheit**: Verschlüsselte vs. unverschlüsselte Topics
- 📱 **Mobile Optimierung**: Responsive Dashboard-Anzeige
- 🔗 **API-Integration**: REST-API für Topic-Management

---

**Status**: ✅ **IMPLEMENTIERT UND AKTIV**

**Letzte Aktualisierung**: 2025-08-28

**Nächste Schritte**: ✅ **MIGRATION ABGESCHLOSSEN** - Alle Systeme verwenden TopicManager
