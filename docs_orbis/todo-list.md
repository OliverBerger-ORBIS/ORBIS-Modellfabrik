# 📋 ORBIS Modellfabrik - ToDo-Liste

## 🚀 Priorität 1 - Live APS Integration

### ✅ Abgeschlossen
- [x] **Template Message Manager** - Vollständig implementiert und integriert
- [x] **Dashboard Integration** - Läuft auf Port 8501
- [x] **NFC-Mapping** - 10/24 Codes gefunden
- [x] **MQTT Control Interface** - Template Control mit 5 Tabs

### 🔄 In Arbeit
- [ ] **Live MQTT Test** - Template Messages mit echter APS testen
- [x] **CCU-Nachrichten** - CCU-Templates implementiert (separates Tool)
- [ ] **ORDER-ID Tracking** - CCU-generierte ORDER-IDs verfolgen
- [ ] **Workflow Validation** - Wareneingang, Auftrag und AI-not-ok Workflows testen

### Separate Analyse-Architektur
- [x] **TXT Template Analyzer** - Als separates Tool implementiert
- [x] **CCU Template Analyzer** - Als separates Tool implementiert
- [x] **Dashboard bereinigt** - Analyse-Buttons entfernt
- [x] **Template Library fokussiert** - Nur noch Anzeige und Verwaltung

### 📱 NFC-Code Integration
- [ ] **Physische NFC-Code Auslesung** - 14 restliche Codes auslesen
- [ ] **Live-Test mit echten Werkstücken** - Wareneingang Templates testen
- [ ] **NFC-Code Validierung** - Korrekte Zuordnung verifizieren

## 🏭 Priorität 2 - Module & Fertigungsschritte

### 🏭 Fertigungsschritt-Verwaltung
- [ ] **Fertigungsschritt-Tracking** implementieren
- [ ] **Replay-Dashboard** in APS-Dashboard integrieren
- [ ] **Workflow-Visualisierung** für Fertigungsschritte
- [ ] **Schritt-für-Schritt Replay** von Fertigungsprozessen
- [ ] **Fertigungsschritt-Historie** speichern und anzeigen

### 🏭 Module Status Management
- [ ] **HBW Status** - Werkstück-Positionen abfragen und anzeigen
- [ ] **DPS Status** - Verfügbare Plätze und Werkstücke prüfen
- [ ] **Status Integration** - Dashboard mit Echtzeit-Status-Anzeige
- [ ] **MQTT Topics** - Status-Abfrage Topics identifizieren

### 🚗 FTS Navigation
- [ ] **Navigation-Parameter** - Zielstation-Bestimmung implementieren
- [ ] **Routenplanung** - Automatische Routenplanung verstehen
- [ ] **Station-Mapping** - Verfügbare Stationen identifizieren
- [ ] **Dashboard Integration** - FTS Navigation im Control Tab

## 🔄 Priorität 3 - Erweiterte Features

### 🔄 Dynamische Template-Generierung (später)
- [ ] **Dynamische Template-Funktion** implementieren
- [ ] **Module + Command + Color** Kombinationen generieren
- [ ] **Dashboard-Integration** mit dynamischer Auswahl
- [ ] **Status-Anzeige** für Test-Status (getestet/erwartet/nicht getestet)

### 🎯 Erweiterte Workflow Features
- [ ] **WorkflowOrderManager** - Automatische ORDER-ID Verwaltung
- [ ] **Error Recovery** - Automatische Fehlerbehandlung für Template Messages
- [ ] **Performance Monitoring** - Template-Ausführung überwachen
- [ ] **Batch Processing** - Mehrere Aufträge gleichzeitig verwalten

### 🔗 ERP-Integration (Alternative Lösung)
- [ ] **ERP-Order-ID ↔ FT-Order-ID Mapping** implementieren
- [ ] **APS-Dashboard verwaltetes Mapping** für Order-IDs
- [ ] **Alternative Lösung** über Dashboard-basiertes Mapping
- [ ] **ERP-Integration UI** im Dashboard

## 🚀 Priorität 4 - Advanced Features

### 🚀 Advanced Features
- [ ] **Predictive Analytics** - Workflow-Performance Vorhersagen
- [ ] **API Development** - REST API für Template Messages
- [ ] **Security** - Erweiterte Sicherheitsfeatures für Production
- [ ] **Performance Optimization** - Dashboard-Performance verbessern

### 📊 Analytics & Monitoring
- [ ] **Real-time Analytics** - Live-Performance-Monitoring
- [ ] **Historical Data Analysis** - Langzeit-Performance-Trends
- [ ] **Alert System** - Automatische Benachrichtigungen bei Problemen
- [ ] **Reporting** - Automatische Berichte generieren

## ❌ Entfernte/Fehlgeschlagene Features

### 🔗 ERP-Integration Test
- ❌ **ERP-Integration-Test** - Nicht funktional, entfernt
- ❌ **ERP-Integration-Dokumentation** - Entfernt
- ❌ **ERP-Integration-Tools** - Entfernt
- ✅ **Alternative Lösung** - Dashboard-basiertes Mapping geplant

## 📊 Fortschritt

### ✅ Abgeschlossen (16/25 Tasks)
- Template Message Manager ✅
- Dashboard Integration ✅
- NFC-Mapping ✅
- MQTT Control Interface ✅
- Workflow-Analyse ✅
- Session-Analyse ✅
- Template Library ✅
- Order Tracking ✅
- CCU Response Handling ✅
- Module Icons ✅
- Status Icons ✅
- Bestellung-System ✅
- FTS Control (Grundfunktionen) ✅
- Template Library Manager ✅
- Core Infrastructure ✅
- Testing Framework ✅

### 🔄 In Arbeit (5/25 Tasks)
- Live MQTT Testing 🔄
- CCU-Templates 🔄
- NFC-Code Auslesung 🔄
- Module Status Management 🔄
- Fertigungsschritt-Verwaltung 🔄

### ⏳ Geplant (5/25 Tasks)
- Dynamische Template-Generierung ⏳
- ERP-Integration (Alternative) ⏳
- Advanced Features ⏳
- Analytics & Monitoring ⏳
- Performance Optimization ⏳

---

**Gesamtfortschritt: 60% (15/25 Tasks abgeschlossen)**

*Letzte Aktualisierung: 26.08.2025*
