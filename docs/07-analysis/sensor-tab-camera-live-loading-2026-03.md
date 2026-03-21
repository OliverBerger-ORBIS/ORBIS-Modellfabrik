# Analyse: Sensor-Tab – „Camera image loading…“ (nur Live)

**Datum:** 2026-03  
**Sprint:** 18 (Priorität 1, Zeile 17)  
**Status:** Nicht live verifizierbar zum Analysezeitpunkt.

---

## Symptom

- **Nur Live-Modus:** Kamera-Bereich bleibt bei **„Camera image loading…“** (oder äußeres `cameraLoading`-Template).
- **Mock/Fixture:** typischerweise OK (andere Datenquelle).

---

## Datenpfad (Live)

1. **MQTT** `ConnectionService` abonniert `/j1/txt/1/i/cam` ([connection.service.ts](../../osf/apps/osf-ui/src/app/services/connection.service.ts)).
2. **Gateway** `createGateway`: `cameraFrames$` filtert `topic === '/j1/txt/1/i/cam'`, parst JSON, erwartet **`data`** (String, z. B. `data:image/jpeg;base64,...`) → `CameraFrame` mit `dataUrl` ([gateway/src/index.ts](../../osf/libs/gateway/src/index.ts)).
3. **Sensor-Tab** bindet `cameraFrame$` an `dashboard.streams.cameraFrames$` ([sensor-tab.component.ts](../../osf/apps/osf-ui/src/app/tabs/sensor-tab.component.ts) `bindStreams`).
4. **Template:** `*ngIf="cameraFrame$ | async as frame; else cameraLoading"` – solange **kein** gültiger Frame ankommt (oder Observable noch nichts Sinnvolles emitiert), bleibt die **Loading**-Ansicht ([sensor-tab.component.html](../../osf/apps/osf-ui/src/app/tabs/sensor-tab.component.html)).

---

## Datenfluss-Strategie: `cam` vs. andere Topics

| Schicht | `/j1/txt/1/i/cam` | „Normale“ Topics (z. B. BME680, Module-State) |
|--------|-------------------|-----------------------------------------------|
| **MQTT** | Gleicher Broker, gleiche Subscribe-Liste ([connection.service.ts](../../osf/apps/osf-ui/src/app/services/connection.service.ts)) | Gleich |
| **Gateway (`createGateway`)** | Eigener Stream `cameraFrames$`: Filter auf dieses Topic, **`throttleTime(1000)`** (hohe Frequenz) | Eigene Streams, meist **ohne** dieses Throttle |
| **Sensor-Tab UI (Bild)** | **`cameraFrames$`** (Gateway) | BME/LDR: u. a. **MessageMonitor** `getLastMessage` + Merge mit Fixture-Stream |

**Message Monitor / Persistenz:** Nur für die **Monitor-Ansicht** und **Historie**: `cam` ist **SKIP_BUFFER**, Retention **0**, **keine** Persistenz in `localStorage` – bewusst anders als viele andere Topics (Payload-Größe, ~1/s). Das betrifft **nicht** den Pfad **MQTT → Gateway → Sensor-Tab-Kamera**.

---

## Warum „Speicher voll“ (localStorage) die Kamera-Anzeige kaum erklärt

- **`/j1/txt/1/i/cam` wird nicht persistiert** (`NO_PERSIST_TOPICS` / kein Schreiben großer Cam-Payloads in `localStorage`).
- Die **Sensor-Tab-Vorschau** kommt aus **`cameraFrames$`** (Gateway), **nicht** aus geladenem `localStorage`.
- **`QuotaExceededError`** kann andere Topics / Filter betreffen und Konsole spammen – sollte aber **kein** dauerhaftes „nur Kamera loading“ über den Gateway-Pfad erzwingen.

---

## Wahrscheinliche Ursachen (Live)

| Ursache | Erklärung |
|--------|-----------|
| **Keine / sporadische MQTT-Nachrichten** | TXT sendet kein Cam-Topic, falsche Broker-URL, Firewall, DPS-Station offline. |
| **Payload-Form** | Gateway verlangt parsebares JSON mit Feld **`data`** ([CameraFrameSnapshot](../../osf/libs/entities/src/index.ts)). Abweichendes Feld (z. B. nur Binär/Base64 ohne Wrapper) → `parsed?.data` fehlt → **kein** Gateway-Output. |
| **throttleTime(1000)** | Max. ca. 1 Frame/s am Stream; verursacht **nicht** „ewiges“ Loading, höchstens Verzögerung bis zum ersten Frame. |
| **Sehr lange `data:`-URLs** | Browser-Limits für `<img [src]="data:...">` können zu `net::ERR_INVALID_URL` führen (vgl. Shopfloor Quality-Check). Das betrifft eher **Anzeige/Bildfehler** als „kein erstes Emission“; für **kein** erstes Frame ist es nur relevant, wenn der Parser wegen Format gar kein `data` liefert. |

---

## Bezug zu jüngeren Code-Änderungen (Message Monitor / Persistenz / Shopfloor)

- **Kamera** `/j1/txt/1/i/cam`: weiterhin **nicht** in `localStorage` persistiert, **SKIP_BUFFER** im Message Monitor – betrifft **Anzeige/Puffer**, **nicht** den **Gateway-MQTT→cameraFrames$**-Pfad.
- **Shopfloor:** Blob-URL-Hilfe für sehr große Bilder betrifft **Quality-Check / Shopfloor-Tab**, **nicht** den **Sensor-Tab** `cameraFrame$`.
- **Fazit:** Die beschriebenen Änderungen **lösen das Live-„Loading“-Problem sehr wahrscheinlich nicht**; Ursache liegt typischerweise **vor dem Gateway** (Broker, Topic, Payload-Schema) oder an **Sensor-Tab/Gateway**, die wir dafür nicht angepasst haben.

---

## Empfohlene Verifikation (wenn wieder Live möglich)

1. MQTT-Client (z. B. `mosquitto_sub`) auf `/j1/txt/1/i/cam`: kommen Nachrichten? JSON mit `data`?
2. Browser-**DevTools** → Network/WebSocket: MQTT verbunden?  
3. Optional: temporär `osf.debug` + Logging im Gateway-Pfad (nur in Absprache) oder Breakpoint in `cameraFrames$`-`map`.

---

## Mögliche spätere UI-Härtung (Backlog)

- Gleiche Idee wie Shopfloor: bei sehr langen `dataUrl` **Object-URL** statt reiner Data-URL für `<img>`, inkl. `revokeObjectURL` beim Wechsel – **falls** Live-Tests `ERR_INVALID_URL` zeigen, obwohl Frames ankommen.

---

## Kurz vor LogiMAT: was noch sinnvoll ist (ohne Fix-Roulette)

*Siehe zentral: [osf-ui-logimat-smoke-checklist.md](../04-howto/osf-ui-logimat-smoke-checklist.md)*

**Kernaussage:** Sensor-Kamera **ohne Live-Hardware** nicht endlos „fixen“; **voll localStorage** ist für dieses Symptom **kein** plausibler Hauptverdächtiger (siehe oben).
