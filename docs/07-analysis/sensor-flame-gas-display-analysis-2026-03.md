# Analyse: Flammen- und Gas-Sensor Anzeige (Sensor-Tab)

**Datum:** 2026-03  
**Kontext:** Sprint 18 – Flammensensor Alarm-Werte, Darstellung wissenschaftlicher gestalten

**Architektur-Entscheidung:** Die Wahrheit liegt beim Arduino. Schwellen und Klassifikation (gasLevel 0/1/2) werden ausschließlich im Sketch definiert. Die UI interpretiert keine Rohwerte – sie zeigt nur an, was der Sensor publiziert. Siehe [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md) §0.

---

## 1. Publish-Frequenz (Arduino → MQTT)

| Aspekt | Wert |
|--------|------|
| **Sensor-Auslesung** | Alle 10 ms (`sampleInterval = 10`) |
| **MQTT Publish (Flame/Gas)** | Bei **Zustandsänderung** sofort; bei **Idle** alle **15 s** (Heartbeat) |

**Publish-Logik (Sketch Zeile 561–574):**
- Flame: `shouldPublishFlame = (flameDetected != lastFlameDetected) || (!flameDetected && (now - lastFlamePublish) >= 15000)`
- Gas: analog

**Folge:** Im Idle-Zustand (kein Alarm) werden Werte maximal alle 15 s aktualisiert. Die UI zeigt den letzten empfangenen Wert – bis zu 15 s alt. Das kann den Eindruck erwecken, die Werte „hängen“ oder aktualisieren sich nicht.

---

## 2. Warum „68% Flame detected“ missverständlich ist

**Aktuelle Darstellung (HTML):**
```html
{{ formatFlameDangerPercent(flameState$ | async) }}
<span *ngIf="...flameDetected">Flame detected!</span>
```

**Ergebnis:** `68%  Flame detected!` (nebeneinander)

**Bedeutung der Werte:**
- **68%** = `flameDangerPercent` = Gefahrenstufe in % (0–100). Formel: `(1 - log10(raw+1)/log10(1024)) * 100`
- **Flame detected!** = Boolean-Alarm (raw < 25 über 200 ms)

**Problem:** „68%“ wird als „68% Flamme“ gelesen, ist aber **68% Gefahr**. Die Prozentangabe hat keine explizite Einheit/Label. „Flame detected!“ klingt wie eine Erweiterung von „68%“ → „68% Flame detected“.

---

## 3. Skalierung und Orientierung

### Flammensensor (KY-026)
- **Raw:** 0–1023 (ADC). **0 = Flamme nah** (Gefahr), **1023 = keine Flamme** (sicher)
- **Bar:** Links = sicher (grün), rechts = Gefahr (rot). Maskenbreite = sicherer Anteil (logarithmisch)
- **Anzeige:** Nur „X%“ = Gefahrenstufe. **Raw-Wert wird nicht angezeigt.**

### Gas-Sensor (MQ-2)
- **Raw:** 0–1023. **0 = sicher**, **1023 = maximale Belastung** (Gefahr)
- **Bar:** Links = sicher, rechts = Gefahr. Linear: `raw/1023`
- **Anzeige:** Nur „X%“ = Gefahrenstufe. **Raw-Wert wird nicht angezeigt.**

**User-Hinweis:** „Darstellung von 1023–0 und nicht 0–1023“ – vermutlich: Die Bar/Logik ist invertiert (Flame: low=Gefahr), aber die Anzeige zeigt nur einen abgeleiteten Prozentwert. Wissenschaftlich wäre: **Raw-Wert 0–1023 sichtbar** plus optional Gefahrenstufe mit klarem Label.

---

## 4. Empfehlungen für wissenschaftlichere Anzeige

### Flammensensor
| Aktuell | Vorschlag |
|---------|-----------|
| `68%` + `Flame detected!` | **Raw: 312** · Gefahr: 68% (log) · *Flamme erkannt* |
| Nur Prozent | Raw-Wert (0–1023) immer anzeigen |
| Unklare Einheit | Label „Gefahr:“ oder „Danger:“ vor dem % |

### Gas-Sensor
| Aktuell | Vorschlag |
|---------|-----------|
| `12%` | **Raw: 123** · Belastung: 12% |
| Nur Prozent | Raw-Wert (0–1023) anzeigen |
| „Gas detected!“ | Evtl. „Schwellwert überschritten“ oder Schwellenwert anzeigen (Warn 500, Alarm 750) |

### Gemeinsam
- **Raw-Wert** (0–1023) immer sichtbar – entspricht ADC-Messung, reproduzierbar
- **Abgeleiteter Wert** (Gefahr/Belastung %) mit klarem Label
- **Alarm-Status** getrennt von der Zahlenanzeige (z.B. Badge/Icon statt Text neben der Zahl)

---

## 5. Publish-Frequenz (umgesetzt)

**Entscheidung:** Heartbeat von 15 s auf **5 s** reduziert (MQTT_HEARTBEAT_INTERVAL = 5000). Bessere UI-Aktualisierung, Overhead vernachlässigbar. Siehe [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md) §4.

---

## 6. Referenzen

- Sketch: `integrations/Arduino/OSF_MultiSensor_R4WiFi/OSF_MultiSensor_R4WiFi.ino` (Zeile 70–71, 108, 561–574)
- UI: `osf/apps/osf-ui/src/app/tabs/sensor-tab.component.ts` (flameDangerPercent, formatFlameDangerPercent, gasDangerPercent)
- UI: `sensor-tab.component.html` (Flame/Gas gauge-cards)
