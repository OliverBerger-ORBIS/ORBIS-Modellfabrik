# OMF2 Project Roadmap

**Version:** 1.0  
**Last updated:** 2025-10-16  
**Author:** OMF Development Team  

---

## 🎯 Vision & Ziele

Entwicklung einer modernen, modularen Web-Anwendung (OMF2) zur Steuerung und Überwachung der ORBIS Modellfabrik. OMF2 ersetzt das bestehende APS Fischertechnik System und bietet erweiterte Funktionalitäten für Produktionssteuerung, Monitoring und Analytics.

**Ziel-Architektur:**
```
OMF CCU-Frontend ←→ OMF CCU-Backend ←→ OMF-NodeRED ←→ ORBIS-DSP ←→ OPC-UA Module
```

---

## 🚀 Entwicklungsphasen

### **Phase 1: CCU-Frontend Funktionalität** 🔄 **In Bearbeitung**
- **Status:** Bis Messe 25.11.2025
- **Ziel:** Vollständige CCU-Frontend Funktionalität
- **Bereits implementiert:** CCU-Tabs, Production Order Manager, Storage Orders Logic, i18n-System, Drei-Schichten-Architektur
- **Noch zu tun:** Letzter Schliff und Erweiterung der noch nicht funktionierenden Teile
- **Konkrete ToDos:** Siehe [plan.md](../../plan.md)

### **Phase 2: CCU-Backend Funktionalität** ⏳ **Geplant (Post-Messe)**
- **Status:** ⏳ Geplant
- **Ziel:** Logik zur Erstellung der MQTT Messages die das CCU-Backend versendet
- **Ergebnis:** Theoretische Ablösung der Fischertechnik APS CCU-Anwendung
- **Domäne:** CCU wird aufgeteilt in CCU Frontend (Phase 1) und CCU Backend (Phase 2)
- **Konkrete Inhalte:** Siehe [plan.md](../../plan.md) - Task "Ausarbeitung der Roadmap"

### **Phase 3: APS-NodeRED Ablösung** ⏳ **Geplant (Post-Messe)**
- **Status:** ⏳ Geplant
- **Ziel:** Abschalten der APS NodeRED Anwendung
- **Übernahme:** Funktionalität durch ORBIS-DSP
- **Integration:** Eigenen OMF-NodeRED Flow als Integrator zwischen OPC-UA Modulen und DSP
- **Ergebnis:** Vollständige Ablösung der APS-Infrastruktur
- **Konkrete Inhalte:** Siehe [plan.md](../../plan.md) - Task "Ausarbeitung der Roadmap"

### **Phase 4: Erweiterungen** ⏳ **Geplant (Post-Messe)**
- **Status:** ⏳ Geplant (teilweise nach Phase 1 einplanbar)
- **ORBIS Cloud:** Verwaltung der Fabrik-Daten in der Cloud
- **DSP-Zweig:** Parallel-Entwicklung durch anderes Team
- **Timing:** Falls technisch möglich, auch nach Phase 1 einplanbar
- **Konkrete Inhalte:** Siehe [plan.md](../../plan.md) - Task "Ausarbeitung der Roadmap"

---

## 📋 Verweise auf konkrete Dokumentation

### **Aktuelle Arbeiten:**
- **[PROJECT_STATUS.md](../../PROJECT_STATUS.md)** - Sprint-Status und aktuelle Arbeiten
- **[plan.md](../../plan.md)** - Messe-Vorbereitung und konkrete ToDos
- **[docs/sprints/](../sprints/)** - Detaillierte Sprint-Dokumentation

### **Strategische Dokumentation:**
- **[project-overview.md](project-overview.md)** - Projekt-Übersicht
- **[development-phases.md](development-phases.md)** - Detaillierte Phasen-Dokumentation
- **[vision.md](vision.md)** - Projekt-Vision

### **Technische Dokumentation:**
- **[docs/02-architecture/](../02-architecture/)** - Implementierte Architektur
- **[docs/03-decision-records/](../03-decision-records/)** - Architektur-Entscheidungen
- **[docs/04-howto/](../04-howto/)** - Praktische Anleitungen

---

## 🎯 Aktuelle Prioritäten

### **Messe-Vorbereitung (bis 25.11.2025):**
- **Fokus:** Phase 1 abschließen
- **Status:** Auf Kurs für Messe-Demo
- **Details:** Siehe [plan.md](../../plan.md)

### **Post-Messe Entwicklung:**
- **Fokus:** Phase 2-4 planen und implementieren
- **Roadmap-Ausarbeitung:** Siehe [plan.md](../../plan.md) - Task "Ausarbeitung der Roadmap"

---

*Letzte Aktualisierung: 2025-10-16*
