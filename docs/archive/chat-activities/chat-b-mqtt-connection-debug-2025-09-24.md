# Chat-B: MQTT-Verbindungsabbruch Debug - 24.09.2025

## 🎯 **Ziel:**
MQTT-Verbindungsabbruch bei Sidebar "Seite aktualisieren" und FTS-Actions beheben

## 🔍 **Problem-Analyse:**

### **Symptome:**
- ❌ Sidebar "Seite aktualisieren" → MQTT-Verbindungsabbruch
- ❌ FTS-Actions (Docke an, FTS laden, Laden beenden) → MQTT-Verbindungsabbruch
- ❌ Umgebungswechsel (Radio-Buttons) → MQTT-Verbindungsabbruch
- ❌ "Sent" Messages werden nicht in Message-Center angezeigt

### **Zeitpunkt:**
- Problem trat auf **nach APS-Tabs Implementierung**
- War **vorher nicht vorhanden** (2-3 Wochen stabil gelaufen)

## 🛠️ **Durchgeführte Maßnahmen:**

### **1. Registry-Konsolidierung abgeschlossen:**
- ✅ Alle Legacy-Konfigurationen zu Registry migriert
- ✅ Neue Manager implementiert (WorkpieceManager, ProductManager, ShopfloorManager)
- ✅ Dashboard-Komponenten auf Registry umgestellt
- ✅ Abhängigkeiten zu `overview_module_status` entfernt

### **2. MQTT-Verbindungsstabilität repariert:**
- ✅ `st.success()`/`st.error()` in FTS-Actions durch `logger.info()` ersetzt
- ✅ `request_refresh()` Aufrufe in `aps_modules` entfernt
- ✅ Abhängigkeiten zu `overview_module_status` in `aps_modules` entfernt

### **3. Development Rules aktualisiert:**
- ✅ MQTT-Verbindungsstabilität dokumentiert
- ✅ Registry-Pfad-Regeln erweitert

### **4. Stack-Trace Debug versucht:**
- ❌ Stack-Trace funktioniert nicht mit Streamlit (Thread-Problem)
- ❌ Nur 14 Einträge erfasst (nur Dashboard-Initialisierung)

## 🔍 **Systematische Problem-Analyse:**

### **Kandidaten geprüft:**
1. ✅ **Message-History:** Funktioniert korrekt
2. ✅ **MQTT-Client Initialisierung:** Funktioniert korrekt
3. ✅ **MqttGateway send():** Funktioniert korrekt
4. ✅ **Message-Center:** Funktioniert korrekt
5. ✅ **Session State:** Funktioniert korrekt

### **Git-Rollback Test:**
- ✅ **Aktueller Stand gestaged** (alle Änderungen gesichert)
- ✅ **Zurück zu Commit 67617bc** (vor APS-Tabs)
- ❌ **Problem besteht weiterhin** → Problem war schon vorher da
- ✅ **Zurück zu Commit e1270c4** (noch älter)
- ❌ **Problem besteht weiterhin** → Problem liegt noch früher
- ✅ **Zurück zu Commit 3e3c84c** (MQTT-Singleton-Architektur)
- ❌ **Dashboard funktioniert nicht** → Architektur-Problem

## 📊 **Ergebnis:**

### **Problem-Status:**
- ❌ **MQTT-Verbindungsabbruch besteht weiterhin**
- ❌ **Problem liegt nicht in meinen Änderungen**
- ❌ **Problem war schon vor APS-Tabs vorhanden**

### **Nächste Schritte:**
1. **Zu noch älterem Commit wechseln** (vor Registry-Konsolidierung)
2. **Problem isolieren** durch systematischen Rollback
3. **Echte Ursache finden** durch Vergleich funktionierender vs. defekter Version

## 🧠 **Lernpunkte:**

### **Was funktioniert hat:**
- ✅ Registry-Konsolidierung erfolgreich
- ✅ Tab-Konsolidierung vorbereitet
- ✅ Development Rules erweitert

### **Was nicht funktioniert hat:**
- ❌ Stack-Trace mit Streamlit
- ❌ Voreilige Schlüsse über `st.success()` als Problem
- ❌ Komplexe Debug-Ansätze

### **Bessere Ansätze:**
- ✅ **Systematischer Git-Rollback** statt komplexe Debug-Tools
- ✅ **Schritt-für-Schritt Rückgängigmachen** statt Spekulation
- ✅ **Einfache, direkte Methoden** statt komplizierte Lösungen

## 🔍 **Neue Erkenntnis: MQTT-Broker-Konfiguration**

### **Mögliche Ursache identifiziert:**
- **Replay:** Lokaler mosquitto Broker
- **Live:** Mosquitto im Docker der APS-Factory
- **Unterschiedliche Konfigurationen** zwischen den Brokern könnten das Problem verursachen

### **Hypothese:**
Das Problem liegt **nicht im Code**, sondern in der **MQTT-Broker-Konfiguration**:
- **Lokaler mosquitto:** Andere Einstellungen
- **Docker mosquitto:** Andere Einstellungen
- **Unterschiedliche QoS-Level, Retain-Flags, etc.**

### **Test-Ansatz:**
1. **Nur mit einem Broker testen** (z.B. nur Replay)
2. **Broker-Konfigurationen vergleichen**
3. **MQTT-Client-Einstellungen prüfen**

### **Wichtige Erkenntnis:**
- **Commit 3e3c84c:** Dashboard funktioniert **nicht** ❌
- **Commit e1270c4:** Dashboard funktioniert, Message-Center zeigt **sent-Messages** ✅
- **Problem liegt vor MQTT-Singleton-Architektur** (3e3c84c)
- **Message-Center funktioniert** in e1270c4, aber MQTT-Verbindungsabbruch tritt trotzdem auf

### **Neue Erkenntnis: MQTT-Client Robustheit**
- ✅ **Manchmal funktioniert das Senden** → Messages werden korrekt angezeigt
- ❌ **Manchmal schlägt das Senden fehl** → MQTT-Client kappt die Verbindung
- 🔄 **Inkonsistentes Verhalten** → Abhängig von Broker-Verfügbarkeit

**Vermutung:** Der MQTT-Client macht Probleme wenn er die Messages nicht an den Broker abliefern kann. Dann wird auch die Verbindung gekappt.

### **PROBLEM GEFUNDEN: Session Manager Konflikt!**
- ✅ **Session Manager** lief parallel zum Dashboard
- ✅ **Beide verwendeten die gleiche Client-ID** `omf_dashboard_replay`
- ✅ **Mosquitto kappte alte Verbindungen** wenn neue mit gleicher ID kamen
- ✅ **Das verursachte die MQTT-Verbindungsabbrüche**

**Lösung:** Session Manager gestoppt → Problem behoben!

### **Client-ID-Konflikt dauerhaft behoben:**
- ✅ **Session Manager Test:** `session_manager_test`
- ✅ **Session Manager Replay:** `session_manager_replay`  
- ✅ **Dashboard:** `omf_dashboard_replay` (unverändert)
- ✅ **Alle `mosquitto_pub` Aufrufe** mit eindeutigen Client-IDs

## 📋 **Offene Fragen:**
1. **Welcher Commit war der letzte funktionierende?**
2. **Was wurde zwischen funktionierendem und defektem Commit geändert?**
3. **Liegt das Problem in der Registry-Konsolidierung oder woanders?**
4. **Sind die MQTT-Broker-Konfigurationen unterschiedlich?**
5. **Funktioniert es mit nur einem Broker (z.B. nur Replay)?**

---
**Datum:** 24.09.2025  
**Chat:** B  
**Status:** 🔄 In Bearbeitung (Problem-Isolation)
