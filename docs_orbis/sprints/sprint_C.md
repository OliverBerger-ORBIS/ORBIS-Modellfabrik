# Sprint C – Documentation (Skeleton)

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
Sprint C legt den Schwerpunkt auf die Integration der Registry-Validierungen
in das OMF-Dashboard, UI-Tests und erweiterte Session-Analysen.

---

## 2. Goals
- Integration der Registry in das OMF-Dashboard (Live- und Replay-Modus)
- Automatisierte Validierung von Topics und Templates im UI
- Erweiterung der Session-Analyse (Graphen, OrderIDs, Zeitbeziehungen)
- Dokumentation der Test-Strategie

---

## 3. Planned Changes
- [ ] Registry-Loader in Dashboard-Komponenten einbinden
- [ ] UI-Komponenten für Status-/Order-Monitoring erweitern
- [ ] Session-Graphen (Message Flow, Abhängigkeiten) darstellen
- [ ] Developer Guide Kapitel "Dashboard Integration" erstellen

---

## 4. Validation & Testing
- End-to-End Test mit Session-Replay im Dashboard
- Validierung der Anzeige von Order-IDs, Workpieces, States
- Abgleich der realen APS-Nachrichten mit Templates

---

## 5. Open Issues
- Performance bei großen Sessions (Replay)
- Umgang mit inkompatiblen Schema-Versionen
- Definition von Fallback-Strategien bei Validierungsfehlern im Live-Betrieb

---

## 6. Next Steps
- Sprint C Inhalte reviewen & mergen
- Vorbereitung Sprint D: Erweiterung Produktions-Workflows und Orchestrierung
