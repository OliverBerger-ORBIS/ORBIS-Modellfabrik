# OSF-UI: Kurz-Checkliste vor LogiMAT (wenig Zeit, kein Fix-Roulette)

**Ziel:** Mit minimalem Aufwand **Stabilität der Demo** absichern – **keine** experimentellen Refactorings oder mehrere parallele Fixes kurz vor der Messe.

**Debug-Details bei Bedarf:** [osf-ui-console-debug.md](osf-ui-console-debug.md) (`localStorage` `osf.debug` = `1`)

---

## Nicht mehr anfangen (hohes Risiko / Zeitfresser) – bis nach der Messe

| Thema | Warum warten |
|--------|----------------|
| **Message Monitor Duplikate** (technischer Code-Fix) | Analyse liegt vor; Refactoring ist [Sprint 18 – Nach LogiMAT](../sprints/sprint_18.md). |
| **baseHref / Fixture-Pfad-Refactoring** | Bewusst verschoben; Regression-Risiko. |
| **Sensor-Kamera Live-Code** ohne Repro | Ohne MQTT/Live nur raten – siehe [sensor-tab-camera-live-loading-2026-03.md](../07-analysis/sensor-tab-camera-live-loading-2026-03.md). |

---

## Noch sinnvoll (kurz, Mock / lokaler Build)

1. **Aktuellen Stand festhalten** (Commit/Hash notieren), damit Smoke-Tests nachvollziehbar sind.
2. **Smoke (10–15 Min, Mock):** OSF starten → **Shopfloor** (Fixture laden) → **Sensor** (Mock) → **Message Monitor** öffnen: keine harten Fehler, keine Chunk-404 nach Reload (**Hard-Reload** / Tab neu bei merkwürdigen JS-Fehlern).
3. **`osf.debug`:** Nur einschalten, wenn ihr wirklich Logs braucht; sonst ruhige Konsole lassen.
4. **localStorage bei Problemen (Quota / volle Konsole):** In Message Monitor Topics ggf. leeren oder nur OSF-Keys – **Cam wird ohnehin nicht persistiert**; voller Speicher ist selten die Ursache für **nur** Sensor-Kamera (siehe Analyse-Link oben).

---

## Release und Messe-Version (nach allen Fixes)

**Team-Vorgabe:** Produktions-Build und **neue Messe-Version `v1.0.0` oder `v1.0.x`** erst **nach** abgeschlossenen Fixes – nicht parallel zu offenen Bugfix-Runden.

- **Version (Repo):** nur `package.json` (root) → Feld `"version"`, danach `npm run update-version` (siehe Projektregeln / [.cursorrules](../../.cursorrules)).
- **Zweck:** Ein klarer, getaggter Stand für Messe-Deployment **ohne** Versions-Sprünge mitten in der Fix-Phase.

---

## Nur wenn Hardware / Live vor Ort (sehr knapp halten)

1. **Verbindung:** Live-Umgebung → Broker verbunden (wie geplant).
2. **Sensor-Tab Kamera:** Einmal prüfen: Bild oder weiterhin Loading – **wenn Loading:** MQTT-Subscribe/Payload nur mit Mess-Setup (nicht durch UI-Code-Experimente ersetzen).
3. **AGV / FTS / Customer:** Nur die Punkte testen, die **für eure Demo-Skripte** Pflicht sind; Rest **dokumentieren** („bekannt / nach Messe“).

---

## Auf der Messe bei Glitches

- **Hard-Reload** oder **Inkognito** bei altem Bundle / Chunk-404.
- **Mock-Modus** als Fallback, wenn Live streikt (wenn für eure Story ok).
- Keine panischen Hotfixes ohne Commit – lieber **bekanntes** Verhalten zeigen.

---

## Verknüpfte Doku

- [Konsolen-Debug `osf.debug`](osf-ui-console-debug.md)
- [Message Monitor Duplikate – Analyse](../07-analysis/message-monitor-duplicate-topics-2026-03.md)
- [Sensor-Kamera Live – Analyse](../07-analysis/sensor-tab-camera-live-loading-2026-03.md)
