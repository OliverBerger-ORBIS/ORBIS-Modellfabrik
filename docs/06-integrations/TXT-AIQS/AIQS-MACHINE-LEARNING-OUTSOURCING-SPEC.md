# AIQS machine_learning.py – Technische Spezifikation zur Auslagerung (DSP)

**Zweck:** Alle technischen Angaben, die benötigt werden, damit die **DSP (Digital Shopfloor Platform)** die Klassifikation selbst durchführen kann – ohne Abhängigkeit vom TXT-AIQS-Controller.

**Stand:** März 2026

---

## 1. Übersicht: Was macht `lib/machine_learning.py`?

Die Klassifikation läuft in **zwei Stufen**:

1. **Object Detection (TensorFlow Lite):** Bild → ML-Modell → erkanntes Objekt mit Label + Bounding Box
2. **Regelbasierte Bewertung:** Label + Farbe (aus Bild) → `num` (1–4) und `result` (PASSED/FAILED)

---

## 2. Ablauf `MakePictureRunKiReturnFoundPart()` (verkürzt)

```
1. LED an (Beleuchtung vor Aufnahme)
2. frame = Kamera.read_frame()           ← BGR-Bild 320×240
3. Farbe aus ROI extrahieren (HLS)
4. detector = ObjectDetector(model.tflite, labels.txt)
5. result = detector.process_image(frame) ← Liste von Detections
6. Erstes Ergebnis: key=label, pos=bbox
7. key → keytext (Beschreibung)
8. key + Farbe → num (1–4)
9. num 1–3 = PASSED, num 4 = FAILED
10. saveFileandPublish() (Bild speichern, MQTT senden)
```

---

## 3. Eingaben (Inputs für DSP-Klassifikation)

### 3.1 Bildquelle

| Eigenschaft | Wert | Quelle |
|-------------|------|--------|
| **Auflösung** | 320 × 240 Pixel | `lib/camera.py` |
| **Format** | BGR (OpenCV) | USB-Kamera, OpenCV default |
| **Rotate** | false | Keine Drehung |
| **FPS** | 15 | Konfiguration |

**DSP-Alternative:** Das Bild kommt bereits über MQTT im Payload von `/j1/txt/1/i/quality_check` als Base64-PNG (`data`). Die DSP könnte dieses Bild verwenden – **wichtig:** Das Original-Frame ist 320×240; wenn es als PNG gespeichert wird, bleibt die Auflösung erhalten.

### 3.2 ML-Modell und Labels

| Ressource | Pfad (TXT-Controller) | Beschreibung |
|-----------|------------------------|--------------|
| **Modell** | `/opt/ft/workspaces/machine-learning/object-detection/sorting_line/model.tflite` | TensorFlow Lite Object-Detection-Modell |
| **Labels** | `/opt/ft/workspaces/machine-learning/object-detection/sorting_line/labels.txt` | Zeilenweise Label-Namen, Reihenfolge = Klassen-Index |

**RoboPro-Export:** Das Projekt liegt als `.ft`-Archiv in `integrations/TXT-AIQS/archives/` (z.B. `FF_AI_24V_cam_clfn.ft`). Entpackt für Code-Analyse in `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/`. Die `.ft`-Archive enthalten **keine** `model.tflite` oder `labels.txt` – diese liegen separat auf dem TXT-Controller.

**Beschaffung von Modell und Labels:**
- **Hinweis:** SSH/SCP auf den TXT-Controller funktioniert nicht (Permission-Problem ft/ftgui, siehe [DR-17](../../03-decision-records/17-txt-controller-deployment.md) – Alternative 1 verworfen).
- **Mögliche Quellen:** Fischertechnik-Repo [Agile-Production-Simulation-24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V) (TXT4.0-programs/), RPI-Image, oder bei Fischertechnik anfragen.
- **Dokumentation:** [TXT-Controller Deployment](../../04-howto/txt-controller-deployment.md), [INTEGRATIONS-VENDOR-ANALYSIS](../../07-analysis/INTEGRATIONS-VENDOR-ANALYSIS.md)

**Labels (bekannte Werte aus Code):** CRACK, MIPO1, MIPO2, BOHO, BOHOEL, BOHOMIPO1, BOHOMIPO2, BLANK. Die Reihenfolge in `labels.txt` entspricht den Klassen-Indizes des Modells.

*Quellreferenz:* `lib/machine_learning.py` Zeile 70 (ObjectDetector mit Modell- und Labels-Pfad).

---

## 4. ObjectDetector-API (Fischertechnik SDK)

**Klasse:** `fischertechnik.machine_learning.ObjectDetector`  
**SDK:** RoboPro Coding / Fischertechnik Python-Laufzeit (vendor-spezifisch)

```python
detector = ObjectDetector(
    model_path,   # Pfad zu .tflite
    labels_path   # Pfad zu labels.txt
)
result = detector.process_image(frame)  # frame: numpy array BGR
```

### 4.1 Rückgabeformat `result`

`result` ist eine **Liste von Dictionaries**. Es wird nur das **erste** Element verwendet (`result[0]`):

| Schlüssel | Typ | Beschreibung |
|-----------|-----|--------------|
| `label` | str | Klassen-Label (z.B. `"BOHO"`, `"CRACK"`) |
| `probability` | float | Konfidenz 0–1 |
| `position` | list | Bounding Box `[x1, y1, x2, y2]` (Pixel-Koordinaten) |

**Beispiel:**
```python
result = [
    {
        "label": "BOHO",
        "probability": 0.92,
        "position": [45, 80, 120, 160]  # x1, y1, x2, y2
    }
]
# Bei keinem Treffer: result = []
```

### 4.2 DSP-Ersetzung des ObjectDetectors

Die Fischertechnik `ObjectDetector` ist ein Wrapper um **TensorFlow Lite**. Die DSP kann stattdessen verwenden:

- **TensorFlow Lite Interpreter** (Python: `tflite_runtime` oder `tensorflow.lite`)
- Oder ein anderes Inference-Framework (ONNX, PyTorch, etc.), **sofern das Modell konvertiert wird**

**Voraussetzung:** Das Modell `model.tflite` muss für die Zielplattform (z.B. Node.js, Python auf Server, Browser) nutzbar sein. TFLite wird u.a. von Python, C++, JavaScript unterstützt.

---

## 5. Farberkennung (für `num` und `result`)

Die **Farbe** des Werkstücks wird aus einem **festen ROI** im Bild ermittelt. Sie ist entscheidend für die Bewertung (PASSED nur bei passender Kombination Label+Farbe).

### 5.1 ROI (Region of Interest)

```python
# ROI: Mittlerer Bereich des Bildes (Werkstück liegt dort)
# frame shape: (240, 320, 3) -> [height, width, channels]
roi = frame[80:120, 100:240]   # y: 80–120, x: 100–240
```

| Dimension | Bereich | Größe |
|-----------|---------|-------|
| Y (Zeilen) | 80–120 | 40 Pixel |
| X (Spalten) | 100–240 | 140 Pixel |

### 5.2 Farbberechnung

```python
import cv2
import numpy as np

# Durchschnittsfarbe im ROI
color_bgr = np.mean(roi, axis=(0, 1))
# Konvertieren zu HLS (OpenCV: Hue, Lightness, Saturation)
color_hls = cv2.cvtColor(
    np.uint8([[[color_bgr[0], color_bgr[1], color_bgr[2]]]]),
    cv2.COLOR_BGR2HLS
)[0][0]

hue = color_hls[0]   # 0–180 (OpenCV HLS)
sat = color_hls[2]  # 0–255
```

### 5.3 Farbzuordnung zu `color` (1, 2, 3)

```python
def get_color(hue, sat):
    if hue >= 85 and hue < 130 and sat >= 40:
        return 3   # Blau
    elif (hue >= 130 and hue <= 180 or hue >= 0 and hue < 15) and sat >= 40:
        return 2   # Rot
    else:
        return 1   # Weiß
```

| color | Bedeutung | HLS-Bedingung |
|-------|-----------|---------------|
| 1 | Weiß | sonst (niedrige Sättigung oder andere Hue-Bereiche) |
| 2 | Rot | hue 130–180 oder 0–15, sat ≥ 40 |
| 3 | Blau | hue 85–130, sat ≥ 40 |

---

## 6. Label → keytext (classificationDesc)

| key (label) | keytext (classificationDesc) |
|-------------|-------------------------------|
| CRACK | Cracks in Workpiece |
| MIPO1 | 1x milled pocket |
| MIPO2 | 2x milled pocket |
| BOHO | Round hole |
| BOHOEL | Hole elyptical |
| BOHOMIPO1 | Hole and 1x milled pocket |
| BOHOMIPO2 | Hole and 2x milled pocket |
| BLANK | Workpiece without features |
| *(anderes)* | key selbst |
| *(kein Ergebnis)* | No feature found |

---

## 7. Bewertungslogik: key + color → num, result

```python
def evaluate(key, color):
    if key == 'BOHO' and color == 1:
        return 1, 'PASSED'   # Weiß + Rundes Loch
    elif key == 'MIPO2' and color == 2:
        return 2, 'PASSED'   # Rot + 2x gefräste Tasche
    elif key == 'BOHOMIPO2' and color == 3:
        return 3, 'PASSED'   # Blau + Loch + 2x Tasche
    else:
        return 4, 'FAILED'
```

| num | result | Bedingung |
|-----|--------|-----------|
| 1 | PASSED | BOHO + Weiß (color=1) |
| 2 | PASSED | MIPO2 + Rot (color=2) |
| 3 | PASSED | BOHOMIPO2 + Blau (color=3) |
| 4 | FAILED | Alle anderen Fälle |

**Kein Detection:** `len(result) == 0` → num=4, result=FAILED, keytext="No feature found"

---

## 8. Abhängigkeiten (Python, TXT-Seite)

| Abhängigkeit | Verwendung |
|--------------|------------|
| `cv2` (OpenCV) | BGR→HLS, ROI, `imwrite`, `rectangle` |
| `numpy` | `np.mean`, Array-Operationen |
| `fischertechnik.machine_learning.ObjectDetector` | Inference (TFLite-Wrapper) |
| `fischertechnik.camera` | `read_frame()` – **nur auf TXT** |
| `lib.controller` | Kamera-Instanz, LED |
| `lib.display` | UI-Updates – **nur auf TXT** |

**DSP-Relevanz:** Für die reine Klassifikation werden nur `cv2`, `numpy` und ein TFLite-kompatibler Inferenz-Code benötigt. Kamera, LED, Display entfallen.

---

## 9. Checkliste: Auslagerung zur DSP

| # | Anforderung | Status |
|---|-------------|--------|
| 1 | Python-Source aus RoboPro-Export (`archives/*.ft` → `workspaces/`) | ✅ Vorhanden |
| 2 | `model.tflite` beschaffen (Fischertechnik-Quelle; SSH/SCP am TXT-Controller funktioniert nicht) | ❓ Separately |
| 3 | `labels.txt` beschaffen (ebenso) | ❓ Separately |
| 4 | Bild-Input: 320×240 BGR (oder Base64 aus MQTT) | ✅ Spezifikation klar |
| 5 | TFLite-Interpreter für Zielplattform (z.B. Node/TS, Python) | ⬜ Zu implementieren |
| 6 | Preprocessing: ggf. Resize je nach Modell-Eingabegröße | ❓ Modell-Metadaten prüfen |
| 7 | Farb-ROI: `frame[80:120, 100:240]`, HLS, `get_color()` | ✅ Spezifikation klar |
| 8 | Label→keytext-Mapping | ✅ Vollständig dokumentiert |
| 9 | Bewertungslogik key+color→num/result | ✅ Vollständig dokumentiert |
| 10 | Output: `num`, `result`, `classification`, `classificationDesc` | ✅ Definiert |

---

## 10. Datenfluss (DSP-Szenario)

```
[Bild aus MQTT quality_check oder eigenem Kamerastream]
         │
         ▼
┌─────────────────────────────────────────┐
│ 1. TFLite Inference (model.tflite)      │
│    → result[0]: label, probability, pos │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 2. Farbe aus ROI [80:120, 100:240]     │
│    BGR → HLS → hue, sat → color (1–3)   │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 3. key + color → num, result            │
│    key → keytext (Label-Mapping)        │
└─────────────────────────────────────────┘
         │
         ▼
[num, result, classification, classificationDesc]
```

---

## 11. Offene Punkte / Risiken

1. **Modell-Eingabegröße:** Unbekannt. Typische TFLite-OD-Modelle erwarten z.B. 320×320 oder 640×640. Der ObjectDetector könnte intern resizen.
2. **Modell-Besitz/ Lizenz:** Klären, ob `model.tflite` weitergegeben werden darf (Fischertechnik, Schulung, etc.).
3. **Labels-Reihenfolge:** Muss mit `labels.txt` abgeglichen werden, falls Index-basierte Ausgabe.
4. **Performance:** TFLite auf Edge (z.B. TXT) vs. Server/Cloud – Latenz und Ressourcen planen.

---

## 12. Python-Source-Referenzen

Relevante Stellen in den entpackten Workspace-Dateien (aus `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`):

| Thema | Datei | Zeilen |
|-------|-------|--------|
| ObjectDetector-Initialisierung, Pfade | `lib/machine_learning.py` | 70 |
| TFLite-Inference, result-Struktur | `lib/machine_learning.py` | 71, 76–78 |
| ROI Farberkennung (BGR→HLS) | `lib/machine_learning.py` | 66–69 |
| get_color() (hue/sat → 1/2/3) | `lib/machine_learning.py` | 128–137 |
| Label→keytext-Mapping | `lib/machine_learning.py` | 80–96 |
| Bewertung key+color→num | `lib/machine_learning.py` | 99–112 |
| getClassification / getClassificationDesc | `lib/machine_learning.py` | 119–125 |
| Aufruf MakePictureRunKiReturnFoundPart | `lib/sorting_line.py` | 125 |
| publish_quality_check_image | `lib/sorting_line.py` | 138, 148, 173–196 |
| Kamera-Config (320×240, BGR) | `lib/camera.py` | 5–9 |
| Bounding Box (pos für Rechteck) | `lib/machine_learning.py` | 150–151 |

**Basis-Pfad:** `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/`

---

## 13. Referenzen

- **Quellcode:** `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/lib/machine_learning.py`, `sorting_line.py`
- **Archiv:** `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`
- **Camera-Config:** `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/lib/camera.py`
- **Classification-Referenz:** [AIQS-CLASSIFICATION-REFERENCE.md](./AIQS-CLASSIFICATION-REFERENCE.md)
- **TXT-AIQS README:** [TXT-AIQS/README.md](./README.md)
- **TXT-Controller Deployment:** [txt-controller-deployment.md](../../04-howto/txt-controller-deployment.md)
