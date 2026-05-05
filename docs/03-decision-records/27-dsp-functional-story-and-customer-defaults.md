# Decision Record: DSP Functional Story und Customer-Defaults (OCC)

**Datum:** 2026-05-05  
**Status:** Accepted  
**Kontext:** Die Functional-Story der DSP-Animation, die Rolle des Management Cockpits sowie die Default-Customer-Auspraegung wurden iterativ angepasst. Ohne formale Festlegung drohen Rueckfaelle auf inkonsistente Schrittbeschreibungen, veraltete Defaults und uneinheitliche I18n-Keys.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird -> [README - Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung
1. **OCC als kanonischer Default-Customer:**  
   Die Functional-View nutzt OCC als Standard mit BP-Reihenfolge `ERP -> MES -> EWM -> CRM -> Analytics -> Data Lake`.

2. **Functional-Story mit 9 Edge-Function-Icons:**  
   Es gelten neun DSP-Edge-Function-Icons als Zielumfang (inkl. Interoperability, Connectivity, Event-Driven, Choreography, Digital Twin, Best-of-Breed, Analytics, AI Enablement, Autonomous Enterprise) mit schrittweiser Story-Einblendung.

3. **Management Cockpit als Design-/Deployment-Ebene:**  
   Das Management Cockpit wird als cloudbasierter Design-/Deployment-Arbeitsbereich gefuehrt (Modelle, Governance, Releases), nicht als 24/7-Runtime-Orchestrator fuer Shopfloor-Zugriffe.

4. **Edge-Runtime bleibt autonom:**  
   Operative Laufzeitprozesse und direkter Zugriff auf Shopfloor-Komponenten laufen ueber Edge-Instanzen.

5. **Klarere I18n-Semantik:**  
   Der letzte Functional-Step nutzt explizite Step-20-Keys (`dspArchStep20`, `dspArchStep20Desc`) statt historisch missverstaendlicher Key-Namen.

6. **BP-Label-Kuerzung fuer Lesbarkeit:**  
   `dspArchLabelAnalytics` wird auf `Analytical Apps` vereinheitlicht.

## Alternativen
- **Historische FMF-/LogiMAT-Reihenfolge als Default beibehalten:** verworfen, da OCC die aktuelle Zielarchitektur besser repraesentiert.
- **Management Cockpit als Runtime-Orchestrator beschreiben:** verworfen, da fachlich unpraezise und irrefuehrend fuer Betriebskonzepte.
- **Historische I18n-Key-Namen behalten:** verworfen, da wiederkehrende Verwirrung in Wartung und Reviews.

## Konsequenzen
- **Positiv:** Klarere Architekturkommunikation, konsistentere Doku/Code-Story, geringere Fehlinterpretation in Reviews und Demos.
- **Negativ:** Migrationsaufwand in Doku, i18n und Referenzbeispielen.
- **Risiken:** Weitere Textaenderungen ohne DR-Pflege koennen neue Inkonsistenzen erzeugen.

## Implementierung
- [x] Functional-Story und Step-Texte in `layout.functional.config.ts` auf OCC-/MC-/Edge-Semantik ausgerichtet.
- [x] I18n auf `dspArchStep20*` umgestellt (`src/locale` und `public/locale`).
- [x] `dspArchLabelAnalytics` auf `Analytical Apps` vereinheitlicht.
- [x] Referenzdoku (`DSP_Architecture_Objects_Reference.md`) auf aktuelles Verhalten korrigiert.

---
*Entscheidung getroffen von: Team OSF / ORBIS DSP Architektur*
