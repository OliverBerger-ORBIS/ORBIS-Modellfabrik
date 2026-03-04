# AIQS Classification Reference

**Modul:** TXT-AIQS (AI Quality System)  
**Zweck:** Weitergebare Dokumentation zu Classification-Werten, Topic-Inhalten und MQTT-Payload  
**Stand:** März 2026

---

## 1. MQTT Topic

| Eigenschaft | Wert |
|-------------|------|
| **Topic** | `/j1/txt/1/i/quality_check` |
| **QoS** | 1 |
| **Retain** | true |
| **Publisher** | TXT-AIQS Controller (RoboPro-Projekt `FF_AI_24V_cam_clfn`) |
| **Trigger** | Nach jedem Quality-Check (CHECK_QUALITY Command oder manuell) |

---

## 2. Payload-Struktur (JSON)

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `ts` | string | ISO-8601 Timestamp | `"2026-02-12T10:30:45.123Z"` |
| `result` | string | Qualitätsergebnis | `"PASSED"` oder `"FAILED"` |
| `num` | number | Feature-Kennzahl (1–4 oder -1) | `1`, `2`, `3`, `4`, `-1` |
| `classification` | string \| null | ML-Label (Enumeration) | `"BOHO"`, `"MIPO2"`, `"CRACK"`, etc. |
| `classificationDesc` | string | Lesbare Beschreibung | `"Round hole"`, `"2x milled pocket"`, etc. |
| `data` | string | Base64-kodiertes PNG-Bild (data URL) | `"data:image/png;base64,iVBORw0KGgo..."` |

**Hinweis:** `classification` und `classificationDesc` sind nur in der Variante `_cam_clfn` enthalten. Die Basisvariante `_cam` enthält nur `ts`, `result`, `num`, `data`.

---

## 3. Classification-Werte (Enumeration + Beschreibung)

Die Werte kommen aus `lib/machine_learning.py` (TensorFlow Lite Object Detection).  
Quelle: `MakePictureRunKiReturnFoundPart()` → Variablen `key` (Label) und `keytext` (Beschreibung).

| `classification` (ML-Label) | `classificationDesc` (Beschreibung) | Bedeutung |
|----------------------------|--------------------------------------|-----------|
| **CRACK** | Cracks in Workpiece | Risse im Werkstück |
| **MIPO1** | 1x milled pocket | 1x gefräste Tasche |
| **MIPO2** | 2x milled pocket | 2x gefräste Taschen |
| **BOHO** | Round hole | Rundes Loch |
| **BOHOEL** | Hole elyptical | Elliptisches Loch |
| **BOHOMIPO1** | Hole and 1x milled pocket | Loch + 1x gefräste Tasche |
| **BOHOMIPO2** | Hole and 2x milled pocket | Loch + 2x gefräste Taschen |
| **BLANK** | Workpiece without features | Werkstück ohne Merkmale |
| *(sonst)* | `key` selbst | Unbekanntes Label – `keytext` = `key` |
| **null** (kein Ergebnis) | "No feature found" | Kein Feature erkannt |

---

## 4. Zuordnung: `num` und `result`

Die Logik in `machine_learning.py` setzt `num` und `result` anhand von **Classification + Farbe** (HLS aus Bild):

| `num` | `result` | Bedingung |
|-------|----------|-----------|
| 1 | PASSED | `classification` = BOHO **und** Farbe = Weiß (color=1) |
| 2 | PASSED | `classification` = MIPO2 **und** Farbe = Rot (color=2) |
| 3 | PASSED | `classification` = BOHOMIPO2 **und** Farbe = Blau (color=3) |
| 4 | FAILED | Alle anderen erkannten Features |
| 4 | FAILED | Kein Feature erkannt (`len(result)==0`) |

**Farblogik (HLS):**
- `color=1` → Weiß (hue 85–130, sat ≥ 40)
- `color=2` → Rot (hue 130–180 oder 0–15, sat ≥ 40)
- `color=3` → Blau (sonst)

---

## 5. Beispiel-Payloads

### Erfolgreiche Prüfung (PASSED)

```json
{
  "ts": "2026-02-12T10:30:45.123Z",
  "result": "PASSED",
  "num": 1,
  "classification": "BOHO",
  "classificationDesc": "Round hole",
  "data": "data:image/png;base64,iVBORw0KGgo..."
}
```

### Fehlgeschlagene Prüfung (FAILED) – Feature erkannt

```json
{
  "ts": "2026-02-12T10:31:02.456Z",
  "result": "FAILED",
  "num": 4,
  "classification": "CRACK",
  "classificationDesc": "Cracks in Workpiece",
  "data": "data:image/png;base64,..."
}
```

### Kein Feature erkannt (FAILED)

```json
{
  "ts": "2026-02-12T10:31:02.456Z",
  "result": "FAILED",
  "num": 4,
  "classification": null,
  "classificationDesc": "No feature found",
  "data": "data:image/png;base64,..."
}
```

---

## 6. Projekt-Varianten (TXT-AIQS)

| Variante | classification / classificationDesc |
|----------|-------------------------------------|
| `FF_AI_24V_cam` | ❌ Nicht enthalten |
| `FF_AI_24V_cam_clfn` | ✅ Enthalten |

---

## 7. Referenzen

- **How-To:** `docs/04-howto/aiqs-quality-check-enumeration.md`
- **TXT-AIQS README:** `docs/06-integrations/TXT-AIQS/README.md`
- **Quellcode:** `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/lib/machine_learning.py`, `sorting_line.py`
- **Archiv:** `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`
