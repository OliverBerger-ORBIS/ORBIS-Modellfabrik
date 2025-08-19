# 📊 MQTT-Session-Analyse Plan

## 🎯 **Analyse-Ziel**

Systematische Analyse der MQTT-Nachrichten während spezifischer Workflows, um Muster und Abhängigkeiten zu identifizieren, die die MQTT-Command-Probleme verursachen.

## 📋 **Geplante MQTT-Sessions**

### **Session 1: Wareneingang (Rot, Weiß, Blau)**
**Ziel**: Verstehen der MQTT-Nachrichten beim Wareneingang verschiedener Werkstück-Typen

#### **Workflow-Schritte:**
1. **Werkstück Rot** in Wareneingang platzieren
2. **MQTT-Session aufnehmen** während des gesamten Prozesses
3. **Werkstück Weiß** in Wareneingang platzieren
4. **MQTT-Session aufnehmen** während des gesamten Prozesses
5. **Werkstück Blau** in Wareneingang platzieren
6. **MQTT-Session aufnehmen** während des gesamten Prozesses

#### **Session-Labels:**
- `wareneingang-rot`
- `wareneingang-weiss`
- `wareneingang-blau`

#### **Zu analysierende Aspekte:**
- **ORDER-ID Generierung**: Wie werden eindeutige Order-IDs erstellt?
- **Timing-Patterns**: Wann werden Commands gesendet?
- **Status-Updates**: Wie ändern sich Modul-Status?
- **Error-Handling**: Wie werden Fehler behandelt?

### **Session 2: Auftrag (Rot, Weiß, Blau)**
**Ziel**: Verstehen der MQTT-Nachrichten bei Auftragsverarbeitung

#### **Workflow-Schritte:**
1. **Auftrag für Werkstück Rot** erstellen
2. **MQTT-Session aufnehmen** während der Verarbeitung
3. **Auftrag für Werkstück Weiß** erstellen
4. **MQTT-Session aufnehmen** während der Verarbeitung
5. **Auftrag für Werkstück Blau** erstellen
6. **MQTT-Session aufnehmen** während der Verarbeitung

#### **Session-Labels:**
- `auftrag-rot`
- `auftrag-weiss`
- `auftrag-blau`

#### **Zu analysierende Aspekte:**
- **Workflow-Sequenz**: Reihenfolge der Module
- **Dependency-Management**: Welche Module müssen bereit sein?
- **Command-Timing**: Wann werden Commands gesendet?
- **Status-Transitions**: Übergänge zwischen Modul-Status

### **Session 3: Auftrag mit AI-Modul (Not OK) - Rot, Weiß, Blau**
**Ziel**: Verstehen der MQTT-Nachrichten bei Qualitätsproblemen

#### **Workflow-Schritte:**
1. **Auftrag mit Werkstück Rot** erstellen, das AI-Qualitätsprüfung nicht besteht
2. **MQTT-Session aufnehmen** während der Verarbeitung
3. **Auftrag mit Werkstück Weiß** erstellen, das AI-Qualitätsprüfung nicht besteht
4. **MQTT-Session aufnehmen** während der Verarbeitung
5. **Auftrag mit Werkstück Blau** erstellen, das AI-Qualitätsprüfung nicht besteht
6. **MQTT-Session aufnehmen** während der Verarbeitung

#### **Session-Labels:**
- `ai-not-ok-rot`
- `ai-not-ok-weiss`
- `ai-not-ok-blau`

#### **Zu analysierende Aspekte:**
- **Error-Detection**: Wie wird "Not OK" erkannt?
- **Error-Response**: Wie reagiert das System?
- **Recovery-Strategies**: Welche Wiederherstellungsmaßnahmen?
- **Status-Updates**: Status-Änderungen bei Fehlern

### **Session 4: FTS-Commands**
**Ziel**: Verstehen der FTS-Steuerung über MQTT

#### **FTS-Commands zu testen:**
1. **Laden**: FTS zur Ladestation schicken
2. **Dock an DPS**: FTS an DPS andocken
3. **Laden beenden**: Ladevorgang beenden

#### **Session-Labels:**
- `fts-laden`
- `fts-dock-dps`
- `fts-laden-beenden`

#### **Zu analysierende Aspekte:**
- **VDA5050 Standard**: Wie wird VDA5050 implementiert?
- **FTS-Status**: Status-Updates des FTS
- **Command-Responses**: Antworten auf FTS-Commands
- **Error-Handling**: FTS-spezifische Fehlerbehandlung

## 🔍 **Analyse-Methodik**

### **1. Session-Recording**
```bash
# Für jede Session manuell
python src_orbis/mqtt/loggers/aps_session_logger.py --session-label wareneingang-rot --auto-start
```

### **2. Daten-Analyse**
- **Topic-Patterns**: Häufige Topic-Strukturen
- **Payload-Analyse**: JSON-Strukturen und Felder
- **Timing-Analysis**: Zeitstempel und Sequenzen
- **Status-Transitions**: Übergänge zwischen Status

### **3. Muster-Identifikation**
- **ORDER-ID Patterns**: Generierung und Verwendung
- **Command-Sequences**: Reihenfolge der Commands
- **Dependency-Patterns**: Abhängigkeiten zwischen Modulen
- **Error-Patterns**: Häufige Fehlermuster

## 📊 **Erwartete Erkenntnisse**

### **ORDER-ID Management**
- **Generierung**: Wie werden eindeutige IDs erstellt?
- **Verwendung**: Wie werden IDs in Commands verwendet?
- **Timing**: Wann werden neue IDs generiert?

### **Modul-Status-Monitoring**
- **Available**: Wann sind Module verfügbar?
- **Busy**: Wann sind Module beschäftigt?
- **Blocked**: Wann sind Module blockiert?
- **Error**: Wann treten Fehler auf?

### **Workflow-Dependencies**
- **Sequencing**: Korrekte Reihenfolge der Commands
- **Dependencies**: Welche Module müssen bereit sein?
- **Timing**: Wann müssen Commands gesendet werden?

### **Error-Handling**
- **Error-Detection**: Wie werden Fehler erkannt?
- **Error-Response**: Wie reagiert das System?
- **Recovery**: Wie werden Fehler behoben?

## 🚀 **Implementierungs-Schritte**

### **Phase 1: Session-Recording Setup**
- [ ] **Session-Logger konfigurieren** für spezifische Workflows
- [ ] **Workflow-Scripts erstellen** für manuelle Tests
- [ ] **Data-Collection** für alle Sessions

### **Phase 2: Pattern-Analysis**
- [ ] **Topic-Patterns** identifizieren
- [ ] **Payload-Structures** analysieren
- [ ] **Timing-Patterns** erkennen
- [ ] **Status-Transitions** dokumentieren

### **Phase 3: Muster-Implementierung**
- [ ] **ORDER-ID Management** basierend auf Erkenntnissen
- [ ] **Status-Monitoring** verbessern
- [ ] **Workflow-Engine** implementieren
- [ ] **Error-Handling** optimieren

## 📋 **Session-Labels (Übersicht)**

### **Wareneingang Sessions:**
- `wareneingang-rot`
- `wareneingang-weiss`
- `wareneingang-blau`

### **Auftrag Sessions:**
- `auftrag-rot`
- `auftrag-weiss`
- `auftrag-blau`

### **AI-Error Sessions:**
- `ai-not-ok-rot`
- `ai-not-ok-weiss`
- `ai-not-ok-blau`

### **FTS Sessions:**
- `fts-laden`
- `fts-dock-dps`
- `fts-laden-beenden`

## 🎯 **Nächste Schritte**

1. **Session-Recording Setup** implementieren
2. **Erste Session** (Wareneingang Rot) durchführen
3. **Pattern-Analysis** der ersten Session
4. **Weitere Sessions** systematisch durchführen
5. **Muster-Implementierung** basierend auf Erkenntnissen

---

**Status**: 📋 **ANALYSE-PLAN ERSTELLT** - Bereit für systematische MQTT-Session-Analyse
**Nächster Schritt**: Manuelle Session-Aufnahme beginnen
