# Sprint B – Documentation (Template)

Version: 0.1 (Draft)
Last updated: 2025-09-14
Author: OMF Development Team

---

## 📑 Table of Contents
- [1. Scope](#1-scope)
- [2. Goals](#2-goals)
- [3. Planned Changes](#3-planned-changes)
- [4. Validation & Testing](#4-validation--testing)
- [5. Open Issues](#5-open-issues)
- [6. Next Steps](#6-next-steps)

---

## 1. Scope
Sprint B konzentriert sich auf die Verfeinerung der Template-Struktur,
die Erweiterung der Schemas und die ersten produktionsnahen Tests
des OMF-Dashboards mit Session-Replay.

---

## 2. Goals
- Aufteilung von `module/state.yml` in modul-spezifische Templates
- Entfernen von Topic-Strings aus Templates (Trennung von Struktur & Mapping)
- Erweiterung der Registry-Schemas (modules, workpieces)
- CI-Pipeline erweitern (Template-Checks)
- Dokumentation fortführen (Developer Guide & Registry Reference)

---

## 3. Planned Changes
- [ ] Neue modul-spezifische State-Dateien erstellen
- [ ] Schema `modules.schema.json` finalisieren
- [ ] Template-Fixer in CI integrieren
- [ ] Developer Guide Kapitel "Registry & Schemas" ergänzen

---

## 4. Validation & Testing
- Tests für Template-Splitting definieren
- Session-Replay mit neuen Templates durchführen
- Validierung gegen Registry-Schemas automatisieren

---

## 5. Open Issues
- Klärung: Welche Templates bleiben generisch, welche modul-spezifisch?
- Umgang mit Versionsverwaltung der Schemas (v1 → v2)
- Definition von Akzeptanzkriterien für Modul-States

---

## 6. Next Steps
- Sprint B Inhalte umsetzen und reviewen
- Vorbereitung Sprint C: Integration ins Dashboard & UI-Validierung
