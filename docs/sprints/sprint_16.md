# Sprint 16 – Vibration-Sensor, Doku-Check, Marketing-Konsistenz

**Zeitraum:** 19.02.2026 - 04.03.2026 (2 Wochen)  
**Status:** Laufend  

**Stakeholder-Update:** Fokus auf Hardware-Integration (Vibration-Sensor), Dokumentationsbereinigung und Konsistenz-Check Marketing vs. Use-Cases.

---

## 🎯 Ziele

### Übernommen aus Sprint 15
- [ ] Azure DevOps Migration & Docker-Setup
- [x] ORBIS-Projekt-Abschlussbericht finalisieren (für ORBIS-Modellfabrik Sprint 01-12 )
- [ ] Projektantrag ORBIS-Smartfactory Q1/Q2 2026

### Vibration-Sensor
- [ ] Implementieren (Arduino, Signalampel)
- [ ] Testen
- [ ] Integrieren in OSF-UI
- Projektplan: [arduino-vibrationssensor.md](../05-hardware/arduino-vibrationssensor.md)

### Dokumentation
- [x] Fischertechnik: Lokale Kopie der MQTT-Doku ([fischertechnik-official/](../06-integrations/fischertechnik-official/)) + Verweis auf Upstream ([FISCHERTECHNIK-OFFICIAL](../06-integrations/FISCHERTECHNIK-OFFICIAL.md))
- [ ] As-Is Doku: großes Aufräumen nach Doku-Check
- [x] dsp-architecture-inventory Dokumentation der SVGs

**Doku-Audit-Pfad:** Unsere Interpretationen und Prämissen gegen die Fischertechnik-Doku prüfen. Beispiel: [aps-data-flow.md](../02-architecture/aps-data-flow.md) – stimmen Datenfluss, Topics, Komponenten? Autoritative Quelle: [fischertechnik-official/](../06-integrations/fischertechnik-official/) (lokale Kopie). Quellen-Zuordnung: [README – Fischertechnik-Quellen](../../README.md#-fischertechnik-quellen--wo-liegt-was).
  
### ERP/MES Integration
- [ ] Erweiterung der APS/FMF/CCU-Komponente: Order/request-Topic von (DSP_Edge) sendet zusätzlich eine request-ID, CCU sendet eine Order/request-ack mit Request-ID und order-id
- [ ] OSF-UI sendet ein Topic ERP-Order-request-Meta, DSP sendet response mit ERP-Info zur Order (-> Track & Trace) mit SAP/EREP-Daten

### Marketing & Konsistenz
- [ ] Marketing-Präsentation zu DSP und Cross-Selling – Analyse
- [ ] Konsistenz-Check: Marketing-Inhalte vs. Use-Cases der OSF-UI

### Blog-Serie
- [ ] UC-06: UC-00 aufführen, da kein USE-Case an sich sondern Grundlage für a1. Outcomes Neu 6 Use-Cases, Prüfen ob man im DSP-Layer Vorgehensmodell anzeigen soll?
- [ ] a1-DE: TODO Review-Kommentare einarbeiten, 
- [ ] UC-02: Layout-Entscheidung (Vertical Concept vs. Horizontal Lanes)
- [ ] A2/A3: Review-Prozess starten, A3 mit UC-07 überarbeiten
- [ ] A4 Closed Loops – Draft erstellen

### Sprint-Abschluss (Pflicht vor Neuanlage Sprint 17)
- [ ] Sprint-Dokument: Status → "Abgeschlossen", Abschlussdatum setzen
- [ ] Neuer Sprint: Aus Template anlegen (`sprint_17.md`), offene `[ ]` übernehmen
- [ ] PROJECT_STATUS: Neue Tabellenzeile (Sprint 17, Zeitraum, ORBIS-Projekt, OSF-Phase, Externe Events)
- [ ] Roadmap prüfen: Phasen/Daten noch stimmig? (bei Bedarf anpassen)

---

## 📋 Detail-Doku (nur wo nötig)

*Wird bei Bedarf ergänzt.*

---

## 🔗 Entscheidungen

*Wird bei Bedarf ergänzt.*

---

## 📎 Referenzen
- [Use-Case Bibliothek](../02-architecture/use-case-library.md) | [Inventar](../02-architecture/use-case-inventory.md)
- [Vibration-Sensor Projektplan](../05-hardware/arduino-vibrationssensor.md)

---

*Letzte Aktualisierung: 19.02.2026*
