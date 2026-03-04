# Decision Record: APS-CCU OSF-Modifikationen – zentrale Dokumentation

**Datum:** 2026-03-04  
**Status:** Accepted  
**Kontext:** Phase 5 zielt auf zunehmende MES-/DSP-Steuerung (z.B. QM-Check). Die APS-CCU stammt von Fischertechnik und wird für OSF angepasst. Abweichungen vom Original müssen nachvollziehbar und zentral dokumentiert sein.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird → [README – Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

**Ort der Dokumentation:** `integrations/APS-CCU/OSF-MODIFICATIONS.md`

Alle vom Fischertechnik-Original abweichenden Änderungen an der APS-CCU werden zentral in dieser Datei erfasst:
- Modifikation mit Kurzbeschreibung
- Betroffene Datei(n) und Funktionen
- Grund/Anlass (Sprint, DR, Analyse)
- Zusammenhang mit Phase-5-Ziel (MES/DSP-Steuerungsübernahme), falls zutreffend

**Quell-Referenz:** Fischertechnik Agile-Production-Simulation-24V-Dev (siehe [docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md](../06-integrations/FISCHERTECHNIK-OFFICIAL.md)).

---

## Alternativen

- **Alternative 1:** Änderungen nur in Commit-Messages dokumentieren – verworfen, da schwer auffindbar und ohne Kontext.
- **Alternative 2:** Ein DR pro Modifikation – verworfen für kleine Anpassungen; DRs bleiben für architekturrelevante Entscheidungen. OSF-MODIFICATIONS.md dient als übersichtliches Register.
- **Alternative 3:** Dokumentation nur in `docs/07-analysis/` – verworfen, da Analysen temporär/Planungscharakter haben; Modifikationen sind dauerhaft und gehören zur CCU selbst.

---

## Konsequenzen

- **Positiv:** Eine zentrale Stelle für alle CCU-Abweichungen; einfaches Onboarding für Entwickler; klare Rückverfolgbarkeit zum Fischertechnik-Upstream.
- **Negativ:** Disziplin erforderlich – jede Modifikation muss in OSF-MODIFICATIONS.md eingetragen werden.
- **Risiken:** Keine – rein dokumentarisch.

---

## Implementierung

- [x] `integrations/APS-CCU/OSF-MODIFICATIONS.md` anlegen
- [x] Verweise in Roadmap, PROJECT_STATUS und ggf. CCU-README ergänzen
- [x] Erste Einträge für geplante/bereits vorhandene Modifikationen vornehmen
- [ ] Bei jeder neuen CCU-Modifikation: Eintrag in OSF-MODIFICATIONS.md pflegen

---
*Entscheidung getroffen von: OSF-Entwicklung*
