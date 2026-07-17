# How-To: TXT-Controller Deployment mit ROBO Pro Coding

**Datum:** 06.01.2026 · **Letzte Aktualisierung:** 17.07.2026  
**Status:** ✅ Verifizierter Workflow (AIQS Sprint 17 + DPS NFC On-Site / Home-Office Jul 2026)

**Verwandt:** [ROBO Pro Setup](setup/robo-pro-setup.md) · [DR-17](../03-decision-records/17-txt-controller-deployment.md) · [AIQS-Beispiel](aiqs-quality-check-enumeration.md)

---

## Kurz: Der kanonische Weg

```text
archives/*.ft öffnen (Lokal)
  → Speichern unter… (Arbeitskopie, Original unberührt)
  → Dateiliste einblenden → lib/<Modul> öffnen
  → Nur Blockly ändern (Python-Panel = Anzeige)
  → Cmd+S
  → TXT verbinden (grüner Punkt) → Toolbar „Programm hochladen“
  → Am TXT: Load + Autostart
```

**Startpunkt ist immer das Repo:** `integrations/TXT-*/archives/*.ft`  
**Nicht** `workspaces/*.py` deployen. **Nicht** erwarten, dass „Projekt laden“ vom Controller zieht.

---

## Archives im Repo (Stand 17.07.2026)

| Modul | Pfad | Baseline / Varianten |
|-------|------|----------------------|
| **AIQS** | `integrations/TXT-AIQS/archives/` | `FF_AI_24V.ft`, `_wav`, `_cam`, `_cam_clfn` |
| **DPS** | `integrations/TXT-DPS/archives/` | `FF_DPS_24V.ft`, `FF_DPS_24V_osf_nfc.ft` |
| **CGW** | `integrations/TXT-CGW/archives/` | `FF_CGW_24V.ft` |
| **FTS** | `integrations/TXT-FTS/archives/` | `fts_main.ft` |

Fehlt eine Baseline: **☰ → Projekt → Laden → fischertechnik GitLab** → Agile Production Simulation 24V → Speichern unter `archives/`.

`workspaces/` = nur Analyse (grep/diff nach `unzip`). Kein Deploy-Format.

---

## ROBO Pro UI – was wo sitzt (Mac, verifiziert)

### Zwei Menü-Ebenen

| Ort | Inhalt |
|-----|--------|
| **☰** (Hamburger, App links oben) | Projekt: Neu, Laden, Speichern, Speichern unter…, Schließen |
| **macOS-Menüleiste** (Apfel-Leiste) | **Kein** Eintrag „Controller → Verbinden“ / „Controller → Download“ |

### Toolbar (rechts oben in der App)

Typische Icons (v.l.n.r.): Play · Stop · Debug · Schnittstellentest · **Programm hochladen** (Dokument mit Pfeil) · **Controller** (grüner Punkt = verbunden).

**Deploy = Toolbar „Programm hochladen“** (Tooltip mit Maus prüfen). Nicht in der Mac-Menüleiste suchen.

### Projekt laden ≠ vom Controller holen

**☰ → Projekt → Laden** bietet nur:

- **Lokal** — `.ft` vom Laptop (unser Standard: `archives/`)
- **fischertechnik GitLab** — offizielle Baseline

Es gibt **keinen** Eintrag „Controller“ in diesem Dialog — auch bei grüner Verbindung.

### Dateiliste (Projekt-Explorer)

Die Dateiliste (`data/`, `lib/`, …) ist **nicht immer sichtbar**.

- **Einblenden:** Icon **rechts oben** (Sidebar / Ordner-Symbol neben den Toolbar-Icons)
- Dann: `lib` → gewünschtes Modul (z. B. `VGR`, `sorting_line`) anklicken → eigener Tab

### Tabs

| Tab | Inhalt |
|-----|--------|
| **Controllerkonfiguration** | Hardware (`txt_factory`, Mini-Taster, …) — **nicht** die Business-Logik |
| **Hauptprogramm** | Start/Threads/MQTT-Setup |
| **`lib/…`** (z. B. `VGR`) | Modul-Code — hier die NFC-/Prozess-Logik |

---

## Häufige Irrtümer (Jul 2026)

| Irrtum | Realität |
|--------|----------|
| „Projekt laden“ holt `FF_DPS_24V` vom TXT | Nein — nur Lokal / GitLab |
| „Upload vom Controller“ im ☰-Menü | Existiert so nicht (in dieser UI) |
| Mac-Menüleiste → Controller → Download | Existiert nicht |
| Rechts Python tippen | **Nur Anzeige.** Blockly → Python, **nicht** umgekehrt |
| `workspaces/` editieren und deployen | Funktioniert nicht — nur `.ft` in ROBO Pro |
| Leeres Projekt (`while True: pass`) bearbeiten | Falsches/neues Projekt — richtige `.ft` aus `archives/` öffnen |
| Große Module (`VGR`) per Blockly-Suche finden | Schwer — Zoom verkleinern, panen, großen Monitor nutzen |

---

## Workflow A — Bestehende Variante ändern (Standard)

Beispiel: DPS NFC → `FF_DPS_24V_osf_nfc.ft` · AIQS → `FF_AI_24V_cam_clfn.ft`

1. Laptop im FT-/Demo-LAN (Deploy) **oder** nur lokal speichern (Home-Office ohne TXT).
2. ROBO Pro: **☰ → Projekt → Laden → Lokal** →  
   `…/ORBIS-Modellfabrik/integrations/TXT-<MODUL>/archives/<datei>.ft`
3. Optional Arbeitskopie: **☰ → Projekt → Speichern unter…** → neuer Name in `archives/` (Original unberührt).
4. Dateiliste einblenden → **`lib/<Modul>`** öffnen (nicht nur Controllerkonfiguration).
5. Änderungen **nur in Blockly** (siehe unten).
6. Rechts im Python-Panel **verifizieren** (nicht tippen).
7. **`Cmd+S`**
8. **Vor Ort:** Controller verbinden (API-Key vom Display) → grüner Punkt → Toolbar **Programm hochladen**.
9. Am TXT: Programm **Load**, **Autostart**.
10. Testen. Bei Fehler: Baseline-`.ft` erneut deployen.

---

## Workflow B — Neue Baseline aus GitLab (wenn `archives/` fehlt)

1. **☰ → Projekt → Laden → fischertechnik GitLab**
2. Projekt wählen (z. B. `FF_DPS_24V` unter Agile Production Simulation 24V)
3. Sofort **Speichern unter…** → `integrations/TXT-…/archives/<name>.ft`
4. Danach wie Workflow A (Arbeitskopie + Änderungen)

---

## Blockly ändern (verbindliche Regeln)

### Regel 1: Nur Blockly → Python

- Das rechte Python-Panel ist **read-only** / wird aus Blockly generiert.
- Tippen im Python-Panel speichert die Logik **nicht** zurück in Blockly.
- Professional-Modus / externes Editieren der `.py` in der `.ft` ist für APS-Projekte **unzuverlässig** (Einrückung, Metadaten) — siehe DR-17.

### Regel 2: Bestehende Prozeduren finden

1. Tab des Moduls (`VGR`, …) aktiv.
2. Zoom **stark verkleinern** (−), Canvas **panen**.
3. Nach `definiere <funktionsname>` suchen (z. B. `handle_NFC`).
4. Hineinzoomen. **Keine neuen Prozeduren anlegen**, wenn die Funktion schon existiert.

### Regel 3: Imports

1. Block **„Python-Importe“** (oft oben im Modul) **anklicken**.
2. Zeilen ergänzen, z. B. `import os` (mehrere Zeilen im selben Block möglich).
3. Kategorie **„Importe“** in der Palette, falls kein Block vorhanden.

### Regel 4: Neue Variable

1. Palette **„Variablen“** → **„Variable erstellen…“**
2. Name eingeben (z. B. `physical_uid`)
3. In `setze […] auf`-Blöcken die Variable im rosa Dropdown wählen  
   (**Nicht** „umbenennen“, wenn das alle Vorkommen von `uid` global ändert.)

### Regel 5: Kurzer Python-Schnipsel

1. Palette **„Verarbeitung“** → Block **„Python-Code“**
2. In die richtige Stelle der Prozedur stecken (Reihenfolge beachten!)
3. Block anklicken → Text eingeben, z. B. `uid = os.urandom(7).hex()`
4. Rechts prüfen: Zeile erscheint an der **richtigen** Stelle (vor abhängigen Aufrufen)

### Regel 6: Logik-Blöcke (Vergleiche)

Beispiel Ausgang DPS: statt `valid = wp_uid == uid` → Tag vorhanden:

`setze valid auf (wp_uid ≠ None) und (wp_uid ≠ "")`

Muster wie bei anderen `valid`-Checks im selben Modul kopieren.

---

## Beispiel: DPS NFC (B-soft) — was geändert wurde

Arbeitskopie: `integrations/TXT-DPS/archives/FF_DPS_24V_osf_nfc.ft` · Modul **`lib/VGR`**

| Stelle | Änderung |
|--------|----------|
| Import | `import os` im Block „Python-Importe“ |
| `handle_NFC` | Lesen → `physical_uid`; bei gültig: `uid = os.urandom(7).hex()` **dann** `nfc_input_history_handle()` |
| `delivery_verify_nfctag` | `valid = wp_uid != None and wp_uid != ''` |
| `delivery_write_history` | dieselbe `valid`-Zeile |

Deploy + Live-Test: vor Ort am DPS-TXT (historisch oft `.186` / DHCP).

---

## Controller verbinden & deployen

### Verbinden

1. Laptop im gleichen Netz wie TXT (Demo-WLAN `ORBIS_H15_F05` / FT-LAN).
2. Toolbar: **Controller**-Icon → TXT wählen (IP/Name; DPS ≠ CGW).
3. **API-Key** vom TXT-Display eingeben (ändert sich).
4. Erfolg: **grüner Punkt** am Controller-Icon.

### Deploy

1. Projekt gespeichert (`Cmd+S`).
2. Toolbar: **Programm hochladen** (Dokument mit Pfeil — Tooltip lesen).
3. Am TXT-Display: Programm auswählen → **Load** → **Autostart** nach Bedarf.

### Home-Office vs. Shopfloor

| Ort | Möglich |
|-----|---------|
| **Home-Office** | `.ft` aus `archives/` öffnen, Blockly ändern, speichern |
| **Shopfloor** | zusätzlich verbinden, deployen, Live-Test |

---

## AIQS-Schnellreferenz

Detailschritte Blockly: [aiqs-quality-check-enumeration.md](aiqs-quality-check-enumeration.md)

1. Lokal: `archives/FF_AI_24V_cam_clfn.ft` (oder `_cam` → Speichern unter `_cam_clfn`)
2. Änderungen in Blockly (`lib/machine_learning`, `lib/sorting_line`)
3. Speichern → Programm hochladen → Load + Autostart

---

## Entpacken für Analyse (optional)

```bash
cd integrations/TXT-DPS/workspaces/
unzip -o ../archives/FF_DPS_24V_osf_nfc.ft -d FF_DPS_24V_osf_nfc/
```

Nur lesen/diff — Änderungen danach **nicht** zurückzippen als Deploy-Weg (DR-17).

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| Nur Lokal / GitLab beim Laden | Erwartet. Baseline aus `archives/` oder GitLab. |
| Kein „Controller“ in Mac-Menüleiste | Erwartet. Verbinden/Deploy über **Toolbar**. |
| Keine `lib/`-Dateien sichtbar | Dateiliste rechts oben einblenden. |
| Python-Panel nicht editierbar | Erwartet. Nur Blockly ändern. |
| Prozedur nicht findbar | Zoom out, panen, großen Monitor; Name `definiere …` |
| Falsches leeres Projekt | `archives/`-`.ft` laden, nicht „Neu“. |
| Controller nicht gefunden | Gleiches WLAN, TXT an, API-Key neu, Scan. |
| Nach Deploy altes Verhalten | Am TXT richtiges Programm Load/Autostart? Richtige `.ft` hochgeladen? |

---

## Checkliste vor dem nächsten Eingriff

- [ ] Richtige `.ft` in `integrations/TXT-*/archives/` (Baseline + Arbeitskopie)
- [ ] Dateiliste sichtbar, richtiges `lib/`-Modul offen
- [ ] Nur Blockly geändert; Python-Panel zur Kontrolle
- [ ] Reihenfolge in `if`-Zweigen geprüft (z. B. ID erzeugen **vor** History)
- [ ] `Cmd+S` → Dateigröße/`archives/` aktualisiert
- [ ] Vor Ort: verbinden → Programm hochladen → Load + Autostart → Test
- [ ] Rollback-`.ft` bekannt
