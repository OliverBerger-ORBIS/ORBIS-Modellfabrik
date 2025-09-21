# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 20.09.2025  
**Aktueller Sprint:** Sprint 05 (18.09 - 01.10.2025)

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Sprint-Status. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### ✅ **APS Dashboard Integration abgeschlossen** (20.09.2025)
- **4 neue APS Tabs** vollständig implementiert
- **APS-spezifische Manager** (VDA5050, TXT Controller, System Control)
- **MQTT-Integration** mit einheitlichem Logging
- **Registry-Erweiterung** für APS-spezifische Topics
- **Fischertechnik TXT-Programme** extrahiert und analysiert
- **Session Manager** mit Replay Station als Default

### ✅ **Mermaid Diagramm-System optimiert** (20.09.2025)
- **Hybrid-Ansatz** implementiert: zentrale vs. dezentrale Diagramme
- **`docs/_shared/diagrams/`** als zentrale Bibliothek für wiederverwendbare Architektur-Diagramme
- **Build-System** mit `npm run diagrams` für automatische SVG-Generierung
- **Kontext-spezifische Diagramme** bleiben bei entsprechenden Dokumenten
- **Obsolet `docs/diagrams/`** entfernt - nutzt jetzt vorhandene `_shared/` Infrastruktur

### 🔄 **Nächste Schritte**
1. ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_05)
2. ✅ **PROJECT_OVERVIEW.md** zu statischer Dokumentation umwandeln
3. ✅ **Doku Overkill vermeiden** - docs aufräumen und konsolidieren
4. ✅ **Mermaid Doku** - Hybrid-Ansatz mit `docs/_shared/diagrams/` implementiert
5. ✅ **Mermaid Diagramme vollständig implementieren** - Dokumentation reorganisiert und committed
6. ✅ **Hybrid-Ansatz für Diagramm-Organisation** - `docs/_shared/diagrams/` als zentrale Bibliothek
7. **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen (Registry-Prinzip: Templates topic-frei, Topics in mapping.yml)
8. **Direction-Klärung mapping.yml** - Aus Sicht welcher Komponente? (CCU oder NodeRED) - aktuell Dashboard-zentrisch, aber semantisch unklar
9. **APS Configuration Tab** implementieren - fehlender 5. APS Tab (später)
10. ✅ **Pre-commit und Git/GitHub Workflow** - Projekt so anpassen dass pre-commit und git/github Workflow funktioniert
11. ✅ **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung
12. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen - As-Is (FT APS) vs. To-Be (ORBIS) Strategie mit Migrations-Phasen dokumentieren
13. **Node-RED Simulation** im Dashboard vorbereiten
14. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
15. **OMF-Dashboard Tab-Konsolidierung** - APS-Tabs in vorhandene OMF-Tabs integrieren, unnötige Tabs entfernen (alte FTS/CCU-Tabs), Logs in Settings-Tab verschieben
16. **OMF-Dashboard User-Konzept definieren** - Standard-User vs. DSP-Admin Rollen
17. **APS-UI Bereich isolieren** - Standard-User sieht nur APS-Bedienung
18. **DSP-Steuerungsbereich implementieren** - DSP-Admin sieht Node-RED-Simulation Tabs
19. **Node-RED-Simulation Tabs erstellen** - DSP-Steuerung für OT-Übernahme
20. **User-Rollen-System implementieren** - Default vs. DSP-Admin Sichtbarkeit
21. **I18n Unterstützung** implementieren (EN, DE, FR)

## 📊 Sprint-Vorgehen

### **Sprint-Strategie:**
- **2-Wochen-Zyklen** für kontinuierliche Entwicklung
- **PROJECT_STATUS.md** = Zentrale Change-Dokumentation
- **Sprint-Dokumentation** = Detaillierte Rückblicke in `docs/sprints/`
- **Keine CHANGELOG.md** = Redundanz vermeiden

### **Change-Management:**
- **Alle Änderungen** werden hier dokumentiert
- **Sprint-Status** wird kontinuierlich aktualisiert
- **Wichtige Entscheidungen** in `docs/03-decision-records/`

## 📊 Sprint-Status

### Sprint 05 (18.09 - 01.10.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** DPS TXT Komponente Analyse und Integration
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert
- **Nächste Schritte:** Sprint-Dokumentation, Architektur-Anpassung

### Sprint 04 (04.09 - 17.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF-Architektur, Singleton Pattern, Registry Support
- **Erreicht:** FTS-Steuerung, Pub-Sub Analyse, Client-ID Zuordnung, Node-RED Analyse

### Sprint 03 (23.08 - 03.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Tiefe Analyse, Template Analyser, Session Analyse
- **Erreicht:** Topics-Verständnis, Registry-Aufbau

### Sprint 02 (07.08 - 22.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Einfaches OMF-Dashboard, Nachrichten-Zentrale
- **Erreicht:** Overview über Modul-Status, erste Commands

### Sprint 01 (24.07 - 06.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Verstehen des APS-Systems, Helper-Apps
- **Erreicht:** Session Manager, MQTT-Aufnahme, Themenbezogene Sessions

## 🎯 Wichtige Doings

### **Entscheidungen getroffen:**
- **Singleton Pattern** für MQTT-Client
- **Wrapper Pattern** für Dashboard-Tabs
- **Registry-basierte Konfiguration**
- **Per-Topic-Buffer Pattern** für MQTT-Nachrichten

### **Technische Meilensteine:**
- **APS Dashboard** vollständig integriert
- **MQTT-Logging** einheitlich implementiert
- **Dictionary-Payloads** für korrekte Kommunikation
- **Session Manager** mit Replay Station als Default
- **Mermaid Doku** - Hybrid-Ansatz implementiert mit `docs/_shared/diagrams/`
- **Code-Cleanup** - Sequenz-Kontrolle Helper Apps entfernt (VDA5050 übernimmt)


## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **APS-Analyse:** `docs/analysis/dps/`

---

**Status:** Projekt läuft erfolgreich, alle geplanten Meilensteine erreicht 🎉
