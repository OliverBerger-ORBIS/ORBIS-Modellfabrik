# Decision Record: Step-by-Step Implementation Principle

**Datum:** 2025-10-19  
**Status:** Accepted  
**Kontext:** Architektur-Validierung vor Umstellung - Schrittweise Implementierung für komplexe Refactoring-Aufgaben

---

## Entscheidung

Verwendung des **Step-by-Step Implementation Principle** für komplexe Refactoring-Aufgaben, bei denen Architektur-Komponenten erst validiert werden müssen, bevor die finale Umstellung erfolgt.

### **🎯 Prinzip: Architektur-Validierung vor Umstellung**

**Problem:** Komplexe Refactoring-Aufgaben (z.B. hardcodierte Payloads entfernen) können Architektur-Komponenten brechen, wenn diese nicht vorher validiert wurden.

**Lösung:** Schrittweise Implementierung mit Architektur-Validierung als Voraussetzung für finale Umstellung.

---

## Implementierung

### **📋 Step-by-Step Pattern:**

#### **Schritt 1: Architektur-Analyse**
- **Ziel:** Bestehende Architektur-Komponenten verstehen
- **Anforderung:** Identifizierung aller relevanten Komponenten
- **Erfolgs-Kriterium:** Vollständige Übersicht über betroffene Systeme

#### **Schritt 2: Voraussetzungen prüfen**
- **Ziel:** Alle notwendigen Parameter und Konfigurationen verfügbar
- **Anforderung:** Registry-basierte Konfiguration, keine hardcodierten Werte
- **Erfolgs-Kriterium:** Alle Abhängigkeiten identifiziert und verfügbar

#### **Schritt 3: Architektur-Komponenten testen**
- **Ziel:** Schema-driven Approach in isolierter Umgebung validieren
- **Anforderung:** Funktionalität ohne Breaking Changes testen
- **Erfolgs-Kriterium:** Alle Architektur-Komponenten funktionieren fehlerfrei

#### **Schritt 4: Domain-Integration**
- **Ziel:** Neue Funktionalität in entsprechende Domain integrieren
- **Anforderung:** CCU/Admin Domain-spezifische Integration
- **Erfolgs-Kriterium:** Domain-spezifische Funktionalität implementiert

#### **Schritt 5: Live-Test**
- **Ziel:** End-to-End Test mit realen Daten/Systemen
- **Anforderung:** Echte MQTT-Verbindung, reale Payloads
- **Erfolgs-Kriterium:** Live-Test mit echter Fabrik erfolgreich

#### **Schritt 6: Finale Umstellung**
- **Ziel:** Legacy-Code durch neue Architektur ersetzen
- **Anforderung:** Alle Voraussetzungen erfüllt, Tests bestanden
- **Erfolgs-Kriterium:** Legacy-Code entfernt, neue Architektur funktional

---

## Anwendungsbeispiele

### **Task 2.9: Factory Steering Hardcoded Payloads Fix**

**Problem:** 6 Funktionen mit hardcodierten Payloads verletzen Command-Versende-Pattern

**Step-by-Step Implementierung:**

#### **Task 2.9-A: Schema-Validierung Analyse**
- Prüfen wo Schema-Validierungen im Projekt existieren
- Nur im MessageManager, nicht in Registry
- Zentrale Validierung identifizieren, keine Duplikate

#### **Task 2.9-B: Registry-Parameter prüfen**
- Alle Versende-Parameter aus Registry verfügbar
- QoS und Retain aus Registry, nicht hardcodiert
- Registry-basierte QoS/Retain-Werte funktional

#### **Task 2.9-C: Topic Steering testen**
- Admin → Generic Steering → Topic Steering funktional
- Schema-driven Approach in Admin Domain validieren
- Alle 3 Modi funktionieren fehlerfrei

#### **Task 2.9-D: CCU Domain publish_message**
- publish_message in CCU Domain implementieren
- CCU Gateway → MessageManager → MQTT Client
- CCU Domain kann schema-validierte Messages senden

#### **Task 2.9-E: Live-Modus Test**
- End-to-End Test mit echter Fabrik
- Echte MQTT-Verbindung, Schema-Validation mit realen Payloads
- Live-Test mit echter Fabrik erfolgreich

#### **Task 2.9-F: Factory Steering umstellen**
- Hardcodierte Payloads durch Schema-driven Approach ersetzen
- PayloadGenerator in Factory Steering, Schema-Validation aktivieren
- Keine hardcodierten Payloads mehr, alle Commands schema-validiert

---

## Vorteile

### **Positiv:**
- **Risiko-Minimierung:** Architektur-Komponenten werden vor Umstellung validiert
- **Inkrementelle Entwicklung:** Kleine, testbare Schritte
- **Frühe Fehlererkennung:** Probleme werden früh identifiziert
- **Rollback-Möglichkeit:** Jeder Schritt kann rückgängig gemacht werden
- **Dokumentation:** Jeder Schritt ist dokumentiert und nachvollziehbar

### **Negativ:**
- **Zeitaufwand:** Mehr Zeit für Analyse und Validierung
- **Komplexität:** Mehr Planung und Koordination erforderlich
- **Abhängigkeiten:** Schritte müssen sequenziell abgearbeitet werden

---

## Anwendungsregeln

### **Wann anwenden:**
- **Komplexe Refactoring-Aufgaben** mit Architektur-Änderungen
- **Breaking Changes** vermeiden wollen
- **Live-System-Integration** erforderlich
- **Mehrere Domänen** betroffen

### **Wann nicht anwenden:**
- **Einfache Bug-Fixes** ohne Architektur-Änderungen
- **Isolierte Komponenten** ohne Abhängigkeiten
- **Prototyp-Entwicklung** ohne Produktions-Anforderungen

---

## Implementierung

- [x] Step-by-Step Pattern definiert
- [x] Anwendungsbeispiele dokumentiert
- [x] Vorteile und Nachteile analysiert
- [x] Anwendungsregeln festgelegt
- [x] Task 2.9 als Beispiel implementiert

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
