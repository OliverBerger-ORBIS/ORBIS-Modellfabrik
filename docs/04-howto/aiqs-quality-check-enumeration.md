# How-To: AIQS Quality-Check – Enumeration und Beschreibung in MQTT-Nachricht ergänzen

**Datum:** 12.02.2026  
**Status:** Anleitung für RoboPro-Änderungen

---

## ⚠️ Wichtige Rahmenbedingungen

| Punkt | Hinweis |
|------|---------|
| **Keine Änderungen im Repo** | Alle Änderungen am TXT-Projekt erfolgen **ausschließlich in RoboPro Coding**. Quellen im Repo (`workspaces/`) werden **nicht** direkt bearbeitet. Sie dienen nur der Analyse (z.B. nach Entpacken des `.ft`-Archivs). |
| **RoboPro erforderlich** | RoboPro Coding muss installiert sein. *Aktuell:* nur auf **Mac** verfügbar. |
| **Nur Blockly-Modus** | Code-Anpassungen erfolgen **ausschließlich im Blockly-Editor** (grafischer Modus). Das Ergebnis wird über den generierten Python-Code verifiziert. |
| **Kein direkter Python-Edit** | Ein direktes Bearbeiten des Python-Codes im Professional-Modus ist **problematisch**: Der TXT-Controller reagiert extrem empfindlich auf Leerzeichen und Einrückungen. Änderungen daher nur über Blockly-Blöcke. |

---

## Vorgehensweise (Übersicht)

**Ziel:** Neue Variante `FF_AI_24V_cam_clfn` erstellen (clfn = Classification mit Enumeration + Beschreibung).

| Schritt | Aktion |
|--------|--------|
| 1 | **Altes Projekt öffnen** in RoboPro: `integrations/TXT-AIQS/archives/FF_AI_24V_cam.ft` |
| 2 | **Sofort als neues Projekt speichern:** `Datei → Speichern unter...` (Cmd+Shift+S) → `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft` *(damit das Original unverändert bleibt)* |
| 3 | **Projekt umbenennen** (falls gewünscht): In RoboPro den Projektnamen auf `FF_AI_24V_cam_clfn` setzen |
| 4 | **Code-Anpassungen** in Blockly vornehmen (Schritte 2a–2c unten) |
| 5 | **Speichern** und **auf Controller deployen:** `Controller → Download` |
| 6 | **Auf TXT-Controller:** Programm `FF_AI_24V_cam_clfn` laden (Load), als aktives Programm auswählen und Autostart aktivieren |
| 7 | **OSF anpassen** (optional): MQTT-Nachricht mit `classification` und `classificationDesc` in der UI anzeigen (Schritt 5 unten) |

---

## 🎯 Ziel

Die MQTT-Nachricht auf dem Topic `/j1/txt/1/i/quality_check` soll um zwei neue Felder erweitert werden:

- **`classification`** – Enumeration (ML-Label), z.B. `BOHO`, `MIPO2`, `CRACK`, `BLANK` …
- **`classificationDesc`** – Lesbare Beschreibung der Klassifizierung, z.B. "Round hole", "2x milled pocket", "Cracks in Workpiece" …

**Bereits vorhanden (bestehende Änderung):**
- `result` – PASSED | FAILED
- `num` – 1–4 (PASSED: 1/2/3, FAILED: 4) oder -1 (kein Feature)
- `data` – Base64-Bild (`data:image/png;base64,...`)
- `ts` – Timestamp

---

## 📋 Analyse: Woher kommen die Werte?

Die Werte `key` (Enumeration) und `keytext` (Beschreibung) werden in **`lib/machine_learning.py`** in der Funktion `MakePictureRunKiReturnFoundPart()` berechnet:

| `key` (ML-Label) | `keytext` (Beschreibung)        |
|-----------------|----------------------------------|
| CRACK           | Cracks in Workpiece              |
| MIPO1           | 1x milled pocket                 |
| MIPO2           | 2x milled pocket                 |
| BOHO            | Round hole                        |
| BOHOEL          | Hole elyptical                   |
| BOHOMIPO1       | Hole and 1x milled pocket        |
| BOHOMIPO2       | Hole and 2x milled pocket        |
| BLANK           | Workpiece without features       |
| (sonst)         | key selbst                       |
| (kein Ergebnis) | No feature found                 |

Ablauf:

1. `sorting_line.py` ruft `num = MakePictureRunKiReturnFoundPart()` auf.
2. Danach stehen in `machine_learning` die Module-Variablen `key` und `keytext` zur Verfügung.
3. Über `getClassification()` und `getClassificationDesc()` können diese Werte in Blockly wie bei `num` zugewiesen werden.
4. `publish_quality_check_image(result, num, classification, classificationDesc)` baut sie in den MQTT-Payload ein.

---

## 🔧 Änderungen in Blockly

### Voraussetzungen

- **RoboPro Coding** installiert (aktuell nur Mac)
- **TXT-Controller** im WLAN, RoboPro damit verbunden (API-Key vom Display)
- Alle Änderungen **ausschließlich im Blockly-Editor** – kein Professional-Modus

### Schritt 1: Projekt öffnen und als Variante speichern

1. **RoboPro Coding** starten
2. **Projekt öffnen:** `Datei → Öffnen` → `integrations/TXT-AIQS/archives/FF_AI_24V_cam.ft`
3. **Sofort „Speichern unter…“:** `Datei → Speichern unter...` (Cmd+Shift+S) → Pfad: `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`
   - *Damit bleibt das Original `FF_AI_24V_cam` unverändert.*
4. **Projekt umbenennen** (falls in RoboPro sichtbar): Name auf `FF_AI_24V_cam_clfn` setzen
5. Für die folgenden Schritte: **`lib/machine_learning`** (Schritt 2a) und **`lib/sorting_line`** (Schritte 2b, 2c) im Blockly-Editor öffnen

---

### Schritt 2a: Funktionen in `lib/machine_learning` anlegen

In **`lib/machine_learning`** zwei neue Prozeduren mit Rückgabewert anlegen:

| Name | Rückgabewert | Bedeutung |
|------|--------------|-----------|
| `getClassification` | `key` | ML-Label (z.B. BOHO, MIPO2, CRACK) |
| `getClassificationDesc` | `keytext` | Lesbare Beschreibung (z.B. "Round hole") |

**Vorgehen:** Block „Prozedur mit Rückgabewert definieren“ (procedures_defreturn), Name eintragen, im Rückgabe-Block die Variable `key` bzw. `keytext` aus `machine_learning` zuweisen. Die Werte werden in `MakePictureRunKiReturnFoundPart()` gesetzt.

---

### Schritt 2b: Prozedur `publish_quality_check_image` erweitern

In **`lib/sorting_line`**: Block **„publish_quality_check_image“** (Prozedur-Definition) finden. Er enthält einen „Python-Code“-Block.

1. **Zwei Parameter hinzufügen:** `classification` und `classificationDesc`
2. **Python-Code im Block** durch folgenden ersetzen:

**Bisher:**

```python
def publish_quality_check_image(result, num):
  """
  Publiziert das zuletzt gespeicherte AIQS-Bild als Base64 (data URL) zusammen mit Result/Num.
  """
  filename = '/opt/ft/workspaces/last-image.png'
  try:
      with open(filename, "rb") as img_file:
          img_data = base64.b64encode(img_file.read()).decode('utf-8')
      payload_obj = {
          "ts": vda_timestamp(),
          "result": result,
          "num": num,
          "data": "data:image/png;base64," + img_data
      }
      # ... publish ...
```

**Neu (im Blockly-Python-Block einfügen):**

```python
def publish_quality_check_image(result, num, classification, classificationDesc):
  """
  Publiziert das zuletzt gespeicherte AIQS-Bild als Base64 mit Result/Num und Klassifizierung.
  classification: ML-Label (z.B. BOHO, MIPO2, CRACK)
  classificationDesc: Lesbare Beschreibung (z.B. "Round hole", "2x milled pocket")
  """
  filename = '/opt/ft/workspaces/last-image.png'
  try:
      with open(filename, "rb") as img_file:
          img_data = base64.b64encode(img_file.read()).decode('utf-8')
      payload_obj = {
          "ts": vda_timestamp(),
          "result": result,
          "num": num,
          "classification": classification,
          "classificationDesc": classificationDesc,
          "data": "data:image/png;base64," + img_data
      }
      mqtt_get_client().publish(
          topic='/j1/txt/1/i/quality_check',
          payload=json.dumps(payload_obj),
          qos=2,
          retain=True
      )
      print('Quality check image published')
  except Exception as e:
      print("Error publishing quality check image")
```

### Schritt 2c: Aufrufstelle in `mainSLDexternal_th` (nur Blockly-Blöcke)

Die Werte werden mit **denselben Blockly-Mitteln** wie bei `num = MakePictureRunKiReturnFoundPart()` zugewiesen – **ohne Python-Code-Block**.

Das Modul `lib/machine_learning` stellt zwei neue Funktionen bereit:

- **`getClassification()`** – gibt das ML-Label zurück (z.B. BOHO, MIPO2, CRACK)
- **`getClassificationDesc()`** – gibt die lesbare Beschreibung zurück (z.B. "Round hole", "2x milled pocket")

#### 1. Variablen-Zuweisungen einfügen

Direkt **nach** `num = MakePictureRunKiReturnFoundPart()` zwei weitere **„Variable setzen“**-Blöcke einfügen:

| Variable            | Wert (Block-Typ)                    |
|---------------------|-------------------------------------|
| `classification`    | `getClassification()`               |
| `classificationDesc`| `getClassificationDesc()`           |

**Vorgehen (analog zu num):**

1. Block **„Variable setzen“** einfügen → Variable `classification` wählen
2. Als Wert den Block **„Rückgabewert von …“** / **import_function_return** verwenden
3. Funktion aus **`lib/machine_learning`**: **`getClassification`** auswählen
4. Dasselbe für `classificationDesc` mit **`getClassificationDesc`** wiederholen

#### 2. Reihenfolge der Blöcke

```
num = MakePictureRunKiReturnFoundPart()
→ classification = getClassification()
→ classificationDesc = getClassificationDesc()
→ print(num)
→ if num == 1 or num == 2 or num == 3:
     ... publish_quality_check_image(RESULT_PASSED, num, classification, classificationDesc)
   else:
     ... publish_quality_check_image(RESULT_FAILED, num, classification, classificationDesc)
```

#### 3. Beide Aufrufe von `publish_quality_check_image`

Sowohl im PASSED- als auch im FAILED-Zweig die Variablen `classification` und `classificationDesc` als zusätzliche Parameter übergeben – **keine** `None`-Werte.

---

### Schritt 3: Rückwärtskompatibilität

- Bestehende Abonnenten nutzen weiterhin `result`, `num`, `data`, `ts`; die neuen Felder `classification` und `classificationDesc` können optional ausgewertet werden.
- OSF-UI und andere Systeme können die neuen Felder schrittweise integrieren.

### Schritt 4: Variante speichern und auf TXT deployen

1. **Projekt speichern:** `Datei → Speichern` (Cmd+S)
2. **Controller verbinden:** Falls noch nicht verbunden – RoboPro öffnet Verbindungsdialog, API-Key vom TXT-Display ablesen und eingeben
3. **Deployment:** `Controller → Download` – das Projekt wird auf den TXT-Controller übertragen
4. **Auf dem TXT-Controller:**
   - Programm **`FF_AI_24V_cam_clfn`** in der Programmliste auswählen (**Load**)
   - Als aktives Programm festlegen
   - **Autostart** aktivieren (Programm startet beim Booten des Controllers)

---

### Schritt 5: OSF-UI anpassen (classification und classificationDesc anzeigen)

Damit die neuen Felder in der OSF-Oberfläche sichtbar werden, sind Anpassungen in `osf/apps/osf-ui` nötig:

1. **`QualityCheckPayload`** erweitern (in `shopfloor-tab.component.ts`):
   - `classification?: string`
   - `classificationDesc?: string`

2. **`QualityCheckImage`** erweitern (dort ebenfalls):
   - `classification?: string`
   - `classificationDesc?: string`

3. **`qualityCheckImage$`**-Stream anpassen – beim Mapping `classification` und `classificationDesc` aus dem Payload ins return-Objekt übernehmen.

4. **Template** (`shopfloor-tab.component.html`) – im AIQS-Bereich „Last Image“ die beiden Werte anzeigen, z.B.:
   - `{{ qualityImage.classification }}` (ML-Label)
   - `{{ qualityImage.classificationDesc }}` (lesbare Beschreibung)

**Referenz:** `osf/apps/osf-ui/src/app/tabs/shopfloor-tab.component.ts` (ca. Zeile 112, 705).

---

### Was kommt danach?

| Priorität | Nächster Schritt |
|-----------|------------------|
| 1 | **OSF-UI** – `classification` und `classificationDesc` im AIQS-Bereich anzeigen (Schritt 5) |
| 2 | **Test** – Quality-Check auslösen, MQTT-Nachricht und UI prüfen |
| 3 | **Dokumentation** – Änderungen ggf. in README oder Modul-Beschreibung ergänzen |
| 4 | **Optional** – Weitere Abonnenten (andere UIs, Backend-Services) für die neuen Felder anpassen |

---

## 📊 Beispiel-Payload (nach Änderung)

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

Bei „No feature found“:

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

**Hinweis:** Bei leerem ML-Ergebnis setzt `machine_learning.py` `keytext = 'No feature found'`; `key` kann dann `None` sein oder einen Fallback haben. Für den Payload empfiehlt sich, in solchen Fällen `classification` und `classificationDesc` explizit zu setzen (z.B. `"No feature found"` für `classificationDesc`).

---

## 🔍 Blockly vs. Python

- Der Code in `lib/` wird von **Blockly generiert**.
- **Änderungen ausschließlich im Blockly-Modus:** Kein Wechsel in den Professional-Modus. Direkte Bearbeitung des Python-Codes ist **problematisch**, da der TXT-Controller extrem auf Leerzeichen und Einrückungen reagiert – bereits minimale Abweichungen können zu Laufzeitfehlern führen.
- **Verifizierung:** Das Ergebnis wird nach dem Speichern im generierten Python-Code geprüft (z.B. in `workspaces/`, nach Entpacken des `.ft`-Archivs).
- Die Anpassungen erfolgen ausschließlich mit **Blockly-Blöcken**: `getClassification()` und `getClassificationDesc()` wie `MakePictureRunKiReturnFoundPart()` verwenden; die Prozedur `publish_quality_check_image` sowie ihre Aufrufe um die Parameter `classification` und `classificationDesc` ergänzen.

---

## 📚 Referenzen

- [How-To: TXT-Controller Deployment](./txt-controller-deployment.md)
- [TXT-AIQS README](../06-integrations/TXT-AIQS/README.md)
- **Archiv:** `integrations/TXT-AIQS/archives/FF_AI_24V_cam_clfn.ft`
- **Quellen (nach Entpacken):** `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam_clfn/lib/sorting_line.py`, `machine_learning.py`

---

*Letzte Aktualisierung: 17.02.2026*
