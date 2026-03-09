# Decision Record: DSP Use-Cases – Konzept vs. Live Demo (einheitliches Muster)

**Datum:** 2026-03-10  
**Status:** Accepted  
**Kontext:** OSF dient der Demo von DSP-/MES-Funktionalität. Live-Demos sind dafür am besten geeignet – sie sind einfach nachvollziehbar und zeigen die Funktionalität direkt. Bisher gibt es keine einheitliche Struktur: UC-01 Track & Trace hat zwei separate Kacheln (Schema + Live Demo), andere UCs nur eine. Die Gefahrensimulation (UC-05 Predictive Maintenance) benötigt einen klaren Ort.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird → [README – Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Sinn und Zweck von OSF

**OSF demonstriert die Funktionalität von DSP/MES.** Das gelingt am besten mit Live-Demos, die einfach nachvollziehbar sind – gegenüber reinen Konzept-Diagrammen, die abstrakt bleiben.

---

## Entscheidung

### Einheitliches Muster: Eine Kachel pro Use-Case, zwei Auswahlmöglichkeiten

1. **Eine Kachel pro Use-Case** – keine doppelten Kacheln wie bisher bei UC-01 („Track & Trace (Schema)“ und „Track & Trace (Live Demo)“).

2. **Bei Auswahl eines Use-Cases** erscheint die Beschreibung; statt einem einzelnen „View Details“-Button gibt es:
   - **Konzept** – führt zur Konzept-Seite (animiertes SVG/Diagramm)
   - **Live Demo** – führt zur interaktiven Live-Demo (nur wenn vorhanden)

3. **UCs ohne Live-Demo** (z.B. UC-00 Interoperability) zeigen nur den **Konzept**-Button. Es wird kein „Live Demo (Coming soon)“ angezeigt – manche UCs bleiben dauerhaft reine Konzept-Darstellungen.

4. **Routing für UCs mit beiden Varianten (Option A):** Die Use-Case-Seite hat Tabs „Konzept“ / „Live Demo“ (oder entsprechende Navigation), nicht zwei getrennte Routes. Beispiel UC-05: `dsp/use-case/predictive-maintenance` mit Tabs.

5. **Gefahrensimulation (UC-05):** Logik und UI wandern von Sensor-Tab in die UC-05 Live-Demo. Der Button „Gefahr simulieren“ wird aus dem Sensor-Tab entfernt – UC-05 ist der einzige Ort für die Alarm→Fabrik-Stop-Simulation.

6. **Vorgehen: Quick Win** – Zuerst UC-05 Live-Demo implementieren, dann UC-01 Track & Trace auf das neue Muster umstellen (Kacheln zusammenführen, Konzept/Live-Demo-Auswahl).

---

## Alternativen

- **Alternative 1 (verworfen):** Zwei Kacheln pro Use-Case (Konzept + Live Demo) – führt zu Kachel-Explosion bei 6+ UCs, unübersichtlich.
- **Alternative 2 (verworfen):** Gefahrensimulation im Sensor-Tab belassen – Sensor-Tab mischt Umweltdaten mit Fabrik-Steuerung; UC-05 ist konzeptionell der richtige Ort (Alarm → Aktion).
- **Alternative 3 (verworfen):** Separate Route für Live-Demo (z.B. `predictive-maintenance-demo`) – Option A (Tabs auf einer Seite) hält Konzept und Live-Demo zusammen und ist konsistenter.
- **Alternative 4 (verworfen):** Zuerst UC-01 Refactoring – Quick Win (UC-05) liefert schneller sichtbaren Mehrwert und validiert das Muster.

---

## Konsequenzen

- **Positiv:** Einheitliches Muster für alle UCs; klare Trennung Konzept vs. Live-Demo; Skalierbar für weitere Live-Demos; OSF-Zweck (Demo) wird besser erfüllt.
- **Negativ:** Datenmodell- und UI-Änderungen erforderlich; UC-01-Kacheln müssen zusammengeführt werden; Sensor-Tab verliert Gefahrensimulation.
- **Risiken:** Keine – Muster ist vorhersehbar und erweiterbar.

---

## Implementierung

- [ ] UseCase-Interface erweitern: `conceptRoute`, `liveDemoRoute` (statt einzelnem `detailRoute`)
- [ ] UC-05 Live-Demo: Neue Seite/Route mit Tabs „Konzept“ | „Live Demo“; Live-Demo enthält Gefahrensimulation (Button „Gefahr simulieren“, `simulateDanger`)
- [ ] Gefahrensimulation aus Sensor-Tab entfernen
- [ ] UC-01: Beide Track-&-Trace-Kacheln zu einer zusammenführen; `conceptRoute` = track-trace-genealogy, `liveDemoRoute` = track-trace
- [ ] DSP Use-Cases Detail-UI: „View Details“ durch „Konzept“ und „Live Demo“ ersetzen („Live Demo“ nur anzeigen, wenn `liveDemoRoute` vorhanden)

---

## Referenzen

- [Use-Case-Bibliothek](../02-architecture/use-case-library.md)
- [alarm-fabrik-stop-ccu-commands](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md)
- [DspUseCasesComponent](../../osf/apps/osf-ui/src/app/pages/dsp/components/dsp-use-cases/dsp-use-cases.component.ts)

---
*Entscheidung getroffen von: OSF-Entwicklung*
