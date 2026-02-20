# ORBIS SmartFactory – Roadmap & Entwicklungsphasen

**Version:** 2.0  
**Letzte Aktualisierung:** 2026-02-18  

---

## 🎯 Vision & Ziele

Entwicklung einer modernen, modularen Web-Anwendung (OSF-UI) zur Steuerung und Überwachung der ORBIS SmartFactory. OSF-UI nutzt die Fischertechnik APS als Testumgebung und bietet erweiterte Funktionalitäten für Produktionssteuerung, Monitoring und Analytics.

**Ziel-Architektur:**
```
OSF-UI ←→ APS-CCU ←→ APS-NodeRED ←→ ORBIS-DSP ←→ OPC-UA Module
```

---

## 🚀 Entwicklungsphasen

### **Phase 0: APS "as IS" – Fischertechnik-System verstehen**
- **Status:** ✅ Abgeschlossen (bis Sprint 2, 22.08.2025)
- **Ziel:** Das bestehende Fischertechnik APS-System vollständig verstehen
- **Erreicht:**
  - APS-Ecosystem dokumentiert (System-Übersicht, Komponenten-Mapping)
  - Mosquitto Log-Analyse (MQTT-Kommunikation, Client-IDs, Topics)
  - APS-NodeRED Flows analysiert (OPC-UA, State-Machine, VDA 5050)
  - APS-CCU als Herz der Fabrik identifiziert
- **Dokumentation:** `docs/06-integrations/APS-Ecosystem/`

---

### **Phase 1: OMF1/OMF2 – Streamlit Python-App**
- **Status:** ✅ Abgeschlossen (abgelöst nach Sprint 3, 03.09.2025)
- **Hintergrund:** Basierend auf OMF1 und OMF2 als Streamlit Python-App.
- **Problem:** Keine WebSocket-Unterstützung – ungeeignet für Echtzeit-MQTT-Kommunikation.
- **Folge:** Umstieg auf OMF3 (siehe Phase 2).

---

### **Phase 2: OMF3/OSF – Angular-App (CCU-Frontend)**
- **Status:** ✅ Abgeschlossen (Sprint 9, 27.11.2025)
- **Ziel:** OSF-UI als Angular-App etablieren (OMF3 = OSF).
- **Erreicht:**
  - CCU-Tabs, Production Order Manager, Storage Orders Logic
  - i18n-System (DE, EN, FR)
  - Drei-Schichten-Architektur (MQTT Client → Gateway → Business)
  - **Messe BE5.0** (Mulhouse, Frankreich, 24–26.11.2025)

---

### **Phase 3: APS-NodeRED Ablösung**
- **Status:** ⏳ Umpriorisiert (aktuell nicht geplant)
- **Ziel:** APS-NodeRED durch ORBIS-DSP ersetzen.
- **Hinweis:** Phase wurde nicht angegangen und umpriorisiert. Kann als optionale Phase erhalten bleiben.
- **MQTT-Entkopplung:** APS-CCU und ORBIS-DSP können parallel arbeiten.

---

### **Phase 4: OSF-UI mit DSP-Fokus**
- **Status:** ✅ Abgeschlossen (Sprint 15, 18.02.2026, Version v0.7.10)
- **Ziel:** OSF-UI als Angular-App mit Konzentration auf DSP-Tab.
- **Erreicht:**
  - DSP-Architecture + animierte Diagramme
  - DSP-Vorgehensweise
  - DSP Use-Cases, DSP Customer Architekturen
  - OSF-Demo per OBS
  - Messe BE5.0 (November 2025), Use-Case-Bibliothek UC-01 bis UC-07

---

### **Phase 5: Erweiterbare Plattform – Messevorbereitung**
- **Status:** 🔄 In Bearbeitung
- **Ausgangslage:** Fischertechnik-Dokumentation liegt vor und erleichtert Erweiterungen.
- **Erweiterungsrichtungen:**
  - **Hardware:** z.B. Arduino Vibrationssensor → Use Case Predictive Maintenance (`docs/05-hardware/arduino-vibrationssensor.md`)
  - **APS-CCU:** ERP/MES-Integration (geplant, ggf. temporär bis DSP CCU übernimmt; Parallelbetrieb möglich)
- **Aktuelle Prioritäten:**
  - **LogiMAT 2026**
  - **Hannover Messe 2026**
  - **ORBIS Customer-Connect Event 2026** (Ende April 2026)

---

## 📋 Verweise

### **Aktuelle Arbeiten:**
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) – Sprint-Status, Tabelle Sprint ↔ ORBIS-Projekt ↔ OSF-Phase
- [docs/sprints/](../sprints/) – Detaillierte Sprint-Dokumentation
- [ORBIS-Projekt-Abschlussbericht Sprints 1-12](../sprints/ORBIS-Projekt-Abschlussbericht_sprints_01-12.md) – Erstes ORBIS-Projekt (ORBIS-Modellfabrik)

### **Strategische Dokumentation:**
- [vision.md](vision.md) – Konzept, Scope

### **Technische Dokumentation:**
- [docs/02-architecture/](../02-architecture/) – Architektur
- [docs/03-decision-records/](../03-decision-records/) – Architektur-Entscheidungen
- [docs/04-howto/](../04-howto/) – Praktische Anleitungen
