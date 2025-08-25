# ERP Order-ID Integration Test Guide

## 🎯 Übersicht

Diese Anleitung beschreibt die Durchführung der ERP Order-ID Integration Tests mit den im Projekt abgelegten Test-Skripten.

## 📁 Projekt-Struktur

```
src_orbis/mqtt/tools/
├── erp_order_id_integration.py      # ERP Integration Klasse
├── test_erp_integration.py          # Einfacher ERP Test
└── test_erp_workflow.py             # Vollständiger ERP Workflow Test
```

## 🚀 **Schritt-für-Schritt Anleitung**

### **📋 Vorbereitung (5 Minuten)**

#### **Schritt 1: Terminal vorbereiten**
```bash
# 1. Terminal öffnen und ins Projektverzeichnis wechseln
cd /Users/oliver/Projects/ORBIS-Modellfabrik

# 2. Virtual Environment aktivieren
source .venv/bin/activate

# 3. Bestätigen dass Python verfügbar ist
python --version
```

#### **Schritt 2: APS System Status prüfen**
```bash
# 1. Prüfen ob APS System erreichbar ist
ping 192.168.0.100

# 2. MQTT Broker Status prüfen (falls verfügbar)
# Falls MQTT Explorer installiert ist, öffnen und Verbindung testen
```

### **🔧 Test 1: Einfacher ERP Order-ID Test (10 Minuten)**

#### **Schritt 3: Einfachen Test ausführen**
```bash
# 1. Test-Skript ausführbar machen
chmod +x src_orbis/mqtt/tools/test_erp_integration.py

# 2. Test ausführen
python src_orbis/mqtt/tools/test_erp_integration.py
```

#### **Schritt 4: Test-Ergebnisse analysieren**
```bash
# Test-Logs überprüfen:
# - MQTT Verbindung erfolgreich?
# - ERP Order Request gesendet?
# - CCU Response empfangen?
# - Modul Command gesendet?
# - Modul Response empfangen?
```

### **🔧 Test 2: Vollständiger ERP Workflow Test (15 Minuten)**

#### **Schritt 5: Vollständigen Test ausführen**
```bash
# 1. Test-Skript ausführbar machen
chmod +x src_orbis/mqtt/tools/test_erp_workflow.py

# 2. Vollständigen Test ausführen
python src_orbis/mqtt/tools/test_erp_workflow.py
```

#### **Schritt 6: Workflow-Ergebnisse analysieren**
```bash
# Vollständige Test-Logs überprüfen:
# - Wareneingang mit ERP Order-ID
# - Produktionsauftrag mit ERP Order-ID
# - Direkte Modul Commands mit ERP Order-ID
# - ERP Order-ID Erfolg in Responses
```

### ** Test-Auswertung (5 Minuten)**

#### **Schritt 7: Ergebnisse dokumentieren**
```bash
# 1. Test-Ergebnisse in Datei speichern
python src_orbis/mqtt/tools/test_erp_integration.py > erp_test_results.log 2>&1

# 2. Vollständigen Test in Datei speichern
python src_orbis/mqtt/tools/test_erp_workflow.py > erp_workflow_results.log 2>&1

# 3. Logs analysieren
cat erp_test_results.log
cat erp_workflow_results.log
```

## 🎯 **Erwartete Ergebnisse**

### **✅ Erfolgreicher Test:**
```
🚀 ERP Order-ID Integration Test
==================================================
🔌 Verbinde zum APS System...
✅ MQTT Verbindung erfolgreich
✅ Verbindung zum APS System hergestellt

🎯 Test 1: ERP Order-ID Injection
==================================================
📤 Sende ERP Order Request:
   Topic: ccu/order/request
   ERP Order-ID: ERP-TEST-2024-001
   Payload: {...}
✅ ERP Order Request gesendet
⏳ Warte auf CCU Response (10 Sekunden)...
📨 Nachricht empfangen: ccu/order/active
   ✅ ERP Order-ID gefunden: ERP-TEST-2024-001

🎯 Test 2: Modul Command mit ERP Order-ID
==================================================
📤 Sende Modul Command:
   Topic: module/v1/ff/SVR3QA0022/order
   ERP Order-ID: ERP-TEST-2024-001
   Command: PICK
✅ Modul Command gesendet
📨 Nachricht empfangen: module/v1/ff/SVR3QA0022/state
   ✅ ERP Order-ID gefunden: ERP-TEST-2024-001

📊 Test-Ergebnisse
==================================================
1. Response:
   Topic: ccu/order/active
   Zeit: 2024-01-20T10:30:00Z
   Payload: {"erpOrderId": "ERP-TEST-2024-001", ...}

2. Response:
   Topic: module/v1/ff/SVR3QA0022/state
   Zeit: 2024-01-20T10:30:05Z
   Payload: {"erpOrderId": "ERP-TEST-2024-001", ...}

🎉 ERP Order-ID Integration funktioniert!
```

### **❌ Fehlgeschlagener Test:**
```
🚀 ERP Order-ID Integration Test
==================================================
🔌 Verbinde zum APS System...
❌ MQTT Verbindung fehlgeschlagen: 5
❌ Verbindung zum APS System fehlgeschlagen

ODER

✅ MQTT Verbindung erfolgreich
✅ ERP Order Request gesendet
⏳ Warte auf CCU Response (10 Sekunden)...
📨 Nachricht empfangen: ccu/order/active
   Payload: {"orderId": "ccu-generated-uuid", ...}  # Keine ERP Order-ID

❌ ERP Order-ID Integration nicht erfolgreich
```

## 🔧 **Troubleshooting**

### **Verbindungsprobleme:**
```bash
# 1. APS System IP prüfen
ping 192.168.0.100

# 2. MQTT Port prüfen
telnet 192.168.0.100 1883

# 3. Firewall prüfen
# 4. Netzwerk-Konfiguration prüfen
```

### **ERP Order-ID Probleme:**
```bash
# 1. Format prüfen - ERP Order-IDs müssen gültig sein
# 2. Duplikate vermeiden - Jede ERP Order-ID muss eindeutig sein
# 3. Zeichenkodierung prüfen - UTF-8 verwenden
# 4. Länge prüfen - Nicht zu lang oder zu kurz
```

### **CCU Response Probleme:**
```bash
# 1. CCU akzeptiert ERP Order-IDs nicht
# 2. CCU generiert eigene Order-IDs trotz ERP Order-ID
# 3. CCU ignoriert ERP Order-ID Felder
# 4. CCU validiert ERP Order-ID Format
```

## 📋 **Test-Checkliste**

### **Vor dem Test:**
- [ ] APS System läuft und ist erreichbar
- [ ] MQTT Broker ist aktiv
- [ ] Netzwerk-Verbindung funktioniert
- [ ] Python Environment ist aktiviert
- [ ] Test-Skripte sind ausführbar

### **Während des Tests:**
- [ ] MQTT Verbindung erfolgreich
- [ ] ERP Order Request gesendet
- [ ] CCU Response empfangen
- [ ] ERP Order-ID in Response gefunden
- [ ] Modul Command gesendet
- [ ] Modul Response empfangen

### **Nach dem Test:**
- [ ] Test-Ergebnisse dokumentiert
- [ ] Logs gespeichert
- [ ] Erfolg/Fehler analysiert
- [ ] Nächste Schritte geplant

## 🎯 **Nächste Schritte**

### **Bei erfolgreichem Test:**
1. **ERP Integration implementieren** - Vollständige Integration in Dashboard
2. **ERP-System anbinden** - Echte ERP Order-IDs verwenden
3. **Monitoring implementieren** - ERP Order Tracking
4. **Dokumentation erweitern** - ERP Integration Guide

### **Bei fehlgeschlagenem Test:**
1. **Problem analysieren** - Warum funktioniert es nicht?
2. **Alternative Strategien** - Andere Manipulations-Methoden
3. **CCU Konfiguration** - Node-RED Flows anpassen
4. **Fallback-Strategie** - Hybrid-Ansatz entwickeln

## 📊 **Test-Dokumentation**

### **Test-Dateien:**
- `erp_test_results.log` - Einfacher Test Ergebnisse
- `erp_workflow_results.log` - Vollständiger Test Ergebnisse
- `erp_integration_analysis.md` - Detaillierte Analyse

### **Erfolgs-Metriken:**
- **Verbindungsrate:** 100% MQTT Verbindung
- **ERP Order-ID Akzeptanz:** >0% in CCU Responses
- **Modul Kompatibilität:** >0% in Modul Responses
- **End-to-End Tracking:** ERP Order-IDs durchgängig verfolgbar

---

**Status: 🚧 BEREIT FÜR TEST** - Alle Test-Skripte sind im Projekt abgelegt und bereit für die Ausführung! 🚀✨
