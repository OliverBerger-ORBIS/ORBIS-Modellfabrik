# Test-Strategie: Replay vs. Automatisiertes Framework

**Datum:** März 2026  
**Kontext:** Diskussion Test-Ansätze, Replay-Workflow vs. Framework für automatisierte UI-Tests  
**Verwandt:** [testing-strategy.md](../04-howto/testing/testing-strategy.md), [replay-station.md](../04-howto/helper_apps/session-manager/replay-station.md)

---

## 1. Aktueller Ansatz: Replay mit aufgezeichneten Sessions

### Ablauf

1. **Aufnahme:** Session-Manager zeichnet MQTT-Topics aus Live-Betrieb auf (Mosquitto-Broker, aufgezeichnete Nachrichten).
2. **Replay:** Lokaler Mosquitto-Broker wird mit den Topics aus der Session beliefert.
3. **Test:** osf-ui verbindet sich im Replay-Modus mit dem Broker; manuelle Prüfung der Tabs.

### Vorteile

- **Eine Session → viele Tabs:** Man kann mit einer Session die Auswirkung auf mehrere Tabs gleichzeitig prüfen.
- **Realistische Abläufe:** Echte Daten aus der APS, keine künstlichen Fixtures.
- **Keine zusätzliche Test-Infrastruktur:** Kein Cypress/Playwright, kein Browser-Automatisierungssetup.

### Nachteile

- **Aufwändige Aufnahme:** Sessions müssen erst mit laufender Fabrik aufgenommen werden.
- **Viele irrelevante Topics:** Eine Session enthält oft viele Topics, die für einen konkreten Testablauf nicht nötig sind.
- **Manuelle Prüfung:** Keine automatisierten Assertions, Ergebnisse werden vom Nutzer bewertet.

### Verwendung

- Typischerweise **15–30 Sessions** mit unterschiedlichem Inhalt.
- Jede Session kann für **~10 Tabs** genutzt werden (nicht jeder Tab hat in jeder Session relevante Daten).
- Referenz: [SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md](SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md), [replay-station.md](../04-howto/helper_apps/session-manager/replay-station.md)

---

## 2. Alternative: Framework für automatisierte UI-Tests

### Idee

- **Ein Test = eine Funktionalität:** Z.B. „Track & Trace zeigt beide AGVs bei Fixture storage_blue_parallel“.
- **Gezieltes Setup:** Replay-Speicher enthält nur die benötigten Topics (Fixture-basiert oder gefilterte Session).
- **Automatisierte Assertions:** Framework (z.B. Playwright, Cypress) startet App, lädt Fixture/Session, prüft DOM/State.

### Vorteile

- **Keine Live-Aufnahme nötig:** Fixtures werden gezielt erstellt (Merge, Filter, Handedit) – z.B. `storage_blue_parallel`.
- **Schlanker Inhalt:** Nur die Topics, die der Test benötigt.
- **Reproduzierbar:** Deterministische Fixtures, unabhängig von Hardware.
- **Hohe Testanzahl:** Pro Tab ca. 10–30 Tests, insgesamt ca. 200–300 Tests möglich.

### Nachteile

- **Eine Funktionalität pro Test:** Weniger „ganzheitliche“ Abläufe über Tabs hinweg.
- **Framework-Einführung:** Playwright/Cypress einrichten, Wartung, CI-Integration.
- **Fixture-Pflege:** Fixtures müssen bei Änderungen an Topic-Strukturen angepasst werden.

---

## 3. Vergleich

| Aspekt              | Replay (Sessions)        | Automatisiert (Fixture-basiert)      |
|---------------------|--------------------------|--------------------------------------|
| **Aufnahme**        | Aufwändig (Live-Betrieb) | Fixtures gezielt erstellen           |
| **Inhalt**          | Viele Topics, oft überflüssig | Nur nötige Topics                |
| **Abdeckung**       | Eine Session → viele Tabs | Ein Test → eine Funktion            |
| **Volumen**         | 15–30 Sessions            | ~10–30 Tests/Tab × ~10 Tabs ≈ 200–300 |
| **Wartung**         | Session kann veralten     | Fixture bleibt stabil bei Topic-Struktur |
| **Reproduzierbarkeit** | Je nach Setup          | Hoch (definierte Fixtures)           |
| **Assertions**      | Manuell                  | Automatisiert                        |

---

## 4. Hybrid-Variante

**Replay** weiterhin für breite Abnahme und realistische End-to-End-Szenarien nutzen.  
**Zusätzlich** gezielte Fixtures für kritische Pfade (z.B. beide AGVs, Quality-Fail, Storage vs. Production):

- Manuell im Replay-Modus mit Fixture-Dropdown (Mock-Modus) testen, oder
- Später mit Framework: Fixture in Replay-Speicher spielen und Assertions automatisiert ausführen.

Fixtures wie `storage_blue_parallel` ergänzen den Replay-Workflow, ersetzen ihn nicht.

---

## 5. Backlog-Empfehlung

**EPIC: Aufbau eines Test-Frameworks für osf-ui**

- **Ziel:** Optionale Ergänzung zum Replay-Workflow; automatisierte UI-Tests für kritische Szenarien.
- **Scope:** Framework-Evaluierung (Playwright vs. Cypress), Fixture-Anbindung an Replay-Speicher oder Mock-Modus, erste Pilot-Tests.
- **Priorität:** Backlog (Prio 2).
- **Abhängigkeit:** Keine – Replay bleibt primärer Ansatz.

---

## 6. Referenzen

- [Testing Strategy](../04-howto/testing/testing-strategy.md)
- [Replay Station](../04-howto/helper_apps/session-manager/replay-station.md)
- [Session Recordings Usage](SESSION-RECORDINGS-USAGE-AND-PRELOAD-AUDIT.md)
- [testing-fixtures README](../../osf/libs/testing-fixtures/README.md)

---

*Erstellt: März 2026*
