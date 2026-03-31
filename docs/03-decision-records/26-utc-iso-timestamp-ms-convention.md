# Decision Record: UTC-Zeitstempel (ISO-8601 mit Millisekunden)

**Datum:** 2026-03-31  
**Status:** Accepted  
**Kontext:** OSF-UI, Business/Gateway/MQTT-Adapter und Session Manager erzeugen Zeichenketten für **Envelope-`timestamp`**, generierte Events und Session-Logs. Arduino **`OSF_MultiSensor_R4WiFi` v1.1.6** liefert Payload-**`timestamp`** als ISO-8601 **UTC mit Millisekunden**. Ohne gemeinsame Konvention sind Log-Zeilen und MQTT-Payloads schwer vergleichbar; Ad-hoc `new Date().toISOString()` bzw. `datetime.now().isoformat()` ohne feste UTC-/Format-Regel führen zu Inkonsistenz.

> **Vorgehensweise:** [README – Wann ein DR?](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

1. **Format (kanonisch):** **ISO-8601 in UTC** mit **Millisekunden** und **`Z`**:  
   `YYYY-MM-DDThh:mm:ss.sssZ`  
   (entspricht `Date.prototype.toISOString()` in JavaScript und der Arduino-Payload-Form v1.1.6+.)

2. **TypeScript (OSF):** zentrale Hilfsfunktion **`utcIsoTimestampMs`** aus **`@osf/entities`** — für „jetzt“ und für beliebige `Date`-Werte.

3. **Python (Session Manager):** **`utc_iso_timestamp_ms()`** (Modul `session_manager.utils.utc_iso_timestamp`) — gleiche String-Form.

4. **Abgrenzung:** **CCU-/TXT-Publisher** und Fremdsysteme werden **nicht** durch dieses DR geändert; deren Felder (`timestamp`, `ts`, …) bleiben wie von der jeweiligen Quelle definiert. OSF **konsumiert** diese Payloads; wo OSF **selbst** Zeitstempel setzt, gilt die kanonische Form.

---

## Alternativen

| Alternative | Warum verworfen |
|-------------|------------------|
| Nur Sekunden-Präzision (`…T12:00:00Z`) | Weicht von Arduino v1.1.6 und `toISOString()` ab; schlechtere Vergleichbarkeit. |
| Lokale Zeitzone / Offsets statt UTC | erschwert Korrelation zwischen Systemen und Logs. |
| Keine zentrale Hilfsfunktion | wiederholte Patterns, leicht abweichende Formate (z. B. `isoformat()` ohne `Z`). |

---

## Konsequenzen

- **Positiv:** Einheitliche, sortier- und vergleichbare Zeitstempel in OSF-erzeugten Daten und Session-Logs; klare Referenz auf eine Implementierung.
- **Negativ:** Import von `@osf/entities` bzw. Nutzung des Python-Helpers überall, wo OSF Zeit erzeugt (gering).
- **Risiken:** Fremdpayloads mit anderem Format weiterhin möglich — Parser/Anzeige müssen robust bleiben (bestehendes Verhalten).

---

## Implementierung (Referenz)

- **TS:** `osf/libs/entities/src/utc-iso-timestamp.ts` — Export über `@osf/entities`.
- **Python:** `session_manager/utils/utc_iso_timestamp.py` — Nutzung in Recorder/Replay nach Bedarf.

---

*Entscheidung dokumentiert im Rahmen der Angleichung an Arduino v1.1.6 und OSF-Session-Logs (Sprint 18).*
