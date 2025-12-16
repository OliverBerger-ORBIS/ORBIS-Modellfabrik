# OBS Video-Präsentation Setup für ORBIS SmartFactory (OMF3)

**Zielgruppe:** Präsentatoren, die OMF3 (ORBIS SmartFactory) in Teams-Meetings demonstrieren  
**Plattform:** Windows  
**Tools:** OBS Studio, Microsoft Teams

---

## 🎯 Zielzustand

- **Monitor 1 (Laptop):** OBS-Bedienung (Studio Mode), Browser/OMF3, Teams-Controls, Notizen
- **Monitor 2 (extern):** Nur das fertige OBS-Program im Vollbild (Fullscreen Projector)
- **Teams:** Teilt Monitor 2 (nicht das OBS-Fenster)

---

## A. Vorbereitungen in Windows

### A1) Monitore korrekt konfigurieren

1. **Windows Einstellungen** → **System** → **Anzeige**
2. Unter **"Mehrere Bildschirme"**: **"Diese Anzeigen erweitern"** wählen
3. Auf **"Identifizieren"** klicken und sicherstellen, welcher Monitor #1 (Laptop) und #2 (extern) ist
4. **Empfehlung:** Monitor 2 als die Präsentationsfläche verwenden (nicht zwingend "Hauptanzeige")

### A2) Skalierung stabil halten

1. In derselben Anzeige-Ansicht: pro Monitor die Skalierung prüfen
2. **Monitor 2 auf 100% oder 125%** setzen (wichtig: später nicht ständig umstellen)
3. Monitor 2 auf eine "saubere" Auflösung lassen (z.B. 3600×1900 ist ok; OBS/Teams arbeiten trotzdem auf dem von Ihnen definierten Output)

---

## B. OBS Grundkonfiguration (absoluter Start)

### B1) OBS starten und zwei organisatorische Container anlegen

In OBS gibt es zwei Dinge:
- **Profile** = Video/Output/Encoder-Einstellungen
- **Scene Collection** = Szenen + Quellen (Ihre Demo-Layouts)

#### Schritt 1: Erstes Profil anlegen (30 fps)

1. **OBS** → Menü **Profile** → **New**
2. Name: `Teams-Demo-1080p30`
3. **OK**

#### Schritt 2: Scene Collection anlegen

1. **OBS** → Menü **Scene Collection** → **New**
2. Name: `ORBIS SmartFactory Demo`
3. **OK**

---

## C. OBS Video-Einstellungen (empfohlen für UI + Shopfloor)

### C1) Video (Canvas/Output/FPS)

1. **OBS Settings** → **Video**
2. Setzen:
   - **Base (Canvas) Resolution:** `2560x1440`
   - **Output (Scaled) Resolution:** `1920x1080`
   - **Common FPS Values:** `30`
3. **Apply** → **OK**

**Ergebnis:** Sie layouten mit 1440p (bessere Schärfe/Reserve), liefern aber 1080p aus (Teams-kompatibel).

---

## D. OBS Output/Recording (für reproduzierbare Tests)

### D1) Output (Recording für Qualitätskontrolle)

1. **Settings** → **Output**
2. **Output Mode:** `Advanced`
3. Tab **Recording**
   - **Type:** `Standard`
   - **Recording Format:** `MKV`
   - **Encoder:** Hardware (NVENC/QSV/AMF), falls vorhanden; sonst `x264`
4. **Apply/OK**

**Hinweis:** Sie "streamen" nicht aus OBS. Recording ist nur, um nach dem Test die Qualität zu prüfen.

---

## E. Szenen anlegen (Vollbild, 4-up, Hero+3)

### E1) Szenenliste erstellen

Links unten im **"Scenes"**-Panel nacheinander **+** klicken und anlegen:

- **S1 - Kamera Vollbild**
- **S2 - Shopfloor Vollbild**
- **S3 - Overview Vollbild**
- **S4 - Active Orders Vollbild**
- **S5 - Track&Trace Vollbild**
- **S6 - 4up Grid**
- **S7 - Hero + 3**

---

## F. Quellen anlegen

### F1) Kamera als Quelle (USB)

1. Szene **S1 - Kamera Vollbild** auswählen
2. **Sources** → **+** → **Video Capture Device**
3. Name: `CAM - USB`
4. **Device:** Ihre USB-Kamera auswählen
5. Setzen:
   - **Resolution/FPS Type:** `Custom`
   - **Resolution:** `1920x1080`
   - **FPS:** `30` (Startwert)
   - **Video Format:** zuerst `MJPEG` testen (falls vorhanden), sonst `Default`
6. **OK**
7. Rechtsklick auf **CAM - USB** → **Transform** → **Fit to Screen**

#### Kamera-Stellräder (das Wichtigste)

**Rechtsklick auf CAM - USB → Properties:**

- **Resolution** (1080p vs. 720p)
- **FPS** (30 vs. 60)
- **Video Format** (MJPEG / YUY2 / NV12 …)

**Rechtsklick → Properties → Configure Video…** (Treiber-Dialog):

- **Exposure:** Auto nach Möglichkeit aus / stabilisieren
- **White Balance:** fixieren, wenn Farbdrift stört
- **Flicker/Anti-banding:** `50 Hz` (in DE typisch)
- **Gain:** nicht zu hoch (sonst Rauschen)

Das sind die **"richtigen Stellräder"**, die später den Unterschied machen.

---

### F2) OMF3/Dashboard als Quellen: zwei Varianten

#### Variante A (am stabilsten): OBS "Browser"-Quellen

Wenn Sie URLs pro Tab/Route verwenden können:

- `…/shopfloor`
- `…/overview`
- `…/orders`
- `…/tracktrace`

(die echten URLs setzen Sie dann ein)

**Für jede Vollbild-Szene:**

1. Szene auswählen (z. B. **S3 - Overview Vollbild**)
2. **Sources** → **+** → **Browser**
3. Name: z. B. `OMF3 - Overview`
4. **URL:** Ihre Overview-URL
5. **Width/Height:**
   - **Width:** `1920`
   - **Height:** `1080`
6. **OK**
7. **Transform** → **Fit to Screen**

Wiederholen für Shopfloor/Orders/Track&Trace.

#### Variante B (wenn Login/SSO nur im echten Browser zuverlässig geht): Window Capture

1. Öffnen Sie je Ansicht ein **eigenes Browserfenster** (nicht nur Tabs)
2. In OBS Szene auswählen
3. **Sources** → **+** → **Window Capture**
4. Passendes Fenster wählen
5. **Transform** → **Fit to Screen**

**Wichtig bei Window Capture:**

- Fenstergröße einmal einstellen, danach nicht mehr anfassen
- In OBS nach Fertigstellung Quellen sperren (siehe Abschnitt H)

---

## G. Multi-Layouts exakt bauen

**Voraussetzung:** Output ist 1920×1080.

### G1) S6 - 4up Grid (4 gleich große Fenster)

1. Szene **S6 - 4up Grid** wählen
2. Vier Quellen hinzufügen (Browser oder Window Capture), z. B.:
   - `OMF3 - Shopfloor`
   - `OMF3 - Overview`
   - `OMF3 - Active Orders`
   - `OMF3 - Track&Trace`
3. Für jede Quelle: **Rechtsklick** → **Transform** → **Edit Transform**

**Setzen Sie exakt:**

- **Oben links:** X=`0`, Y=`0`, W=`960`, H=`540`
- **Oben rechts:** X=`960`, Y=`0`, W=`960`, H=`540`
- **Unten links:** X=`0`, Y=`540`, W=`960`, H=`540`
- **Unten rechts:** X=`960`, Y=`540`, W=`960`, H=`540`

---

### G2) S7 - Hero + 3 (Hauptfenster + 3 rechts)

1. Szene **S7 - Hero + 3** wählen
2. Quellen hinzufügen:
   - **Hero:** Shopfloor oder Kamera
   - **3 kleine:** Overview, Orders, Track&Trace
3. **Transform-Werte exakt:**

- **Hero links groß:** X=`0`, Y=`0`, W=`1280`, H=`1080`
- **Rechts oben:** X=`1280`, Y=`0`, W=`640`, H=`360`
- **Rechts Mitte:** X=`1280`, Y=`360`, W=`640`, H=`360`
- **Rechts unten:** X=`1280`, Y=`720`, W=`640`, H=`360`

---

## H. Stabilität: alles sperren und Snapping sinnvoll nutzen

### H1) Quellen sperren

Wenn ein Layout stimmt:

- Im **Sources-Panel** bei jeder Quelle das **Schloss** aktivieren

### H2) Studio Mode aktivieren

- **OBS:** Studio Mode einschalten (Preview/Program getrennt)

---

## I. Teams-Integration (Präsentation über Monitor 2)

### I1) OBS-Program auf Monitor 2 ausgeben

1. **Rechtsklick** in OBS auf die **Program-Ansicht** (rechte Seite im Studio Mode)
2. **Fullscreen Projector (Program)** → **Monitor 2**

Jetzt zeigt Monitor 2 nur das Sendebild.

---

### I2) Teams: genau Monitor 2 teilen

1. **Teams Meeting** starten
2. **Teilen** → **Bildschirm** → **Monitor 2**
3. In der Share-Leiste: **Optimize** aktivieren (bei Bewegung/Animation)

**Optional** (wenn Bewegung ruckelt):

- Während des Teilens **Ctrl + Alt + Shift + T** testen (High Motion)

---

## J. 60-fps Setup ergänzen (jetzt sinnvoll, weil 1080p30 bereits stabil war)

### J1) Profil duplizieren und auf 60 fps setzen

1. **OBS** → **Profile** → **Duplicate**
2. Name: `Teams-Demo-1080p60`
3. **OK**
4. **Settings** → **Video**
5. **Common FPS Values:** `60`
6. **Apply/OK**

**Hinweis:** Scenes/Quellen bleiben, Sie wechseln nur das Profil (30↔60).

---

## K. Test-Checkliste (15 Minuten, reproduzierbar)

### K1) Vor dem Call

- [ ] Profil wählen: zuerst `Teams-Demo-1080p60` (da es bei Ihnen besser wirkte)
- [ ] Studio Mode ON
- [ ] Fullscreen Projector auf Monitor 2 aktiv

### K2) In Teams

- [ ] Monitor 2 teilen
- [ ] Optimize ON

### K3) Szenen-Test-Reihenfolge (mit kurzem Blick auf Lesbarkeit)

1. **S1** Kamera Vollbild (FTS fährt)
2. **S2** Shopfloor Vollbild
3. **S3** Overview Vollbild
4. **S4** Active Orders Vollbild
5. **S5** Track&Trace Vollbild
6. **S7** Hero + 3 (entscheidend: kleine Panels lesbar?)
7. **S6** 4up Grid (nur wenn lesbar genug)

### K4) OBS-Performance prüfen

1. Menü **View** → **Stats**
2. Wenn **"Dropped/Skipped Frames"** steigen:
   - Profil auf 30 fps wechseln oder
   - Kamera 1080p60 → 1080p30 oder
   - Kamera 1080p60 → 720p60

---

## L. Kamera-Finetuning: konkrete Regeln

### Wenn Bild flüssig, aber unscharf:

- Auflösung hoch (1080p), FPS ggf. 30, Exposure/Gain sauber einstellen

### Wenn Bild ruckelt / laggt:

1. Erst **Video Format** wechseln (MJPEG ↔ YUY2)
2. Dann **FPS** reduzieren (60 → 30)
3. Dann **Auflösung** reduzieren (1080p → 720p)

### Wenn Bild flimmert (LED/Innenlicht):

- **Anti-banding/Flicker:** `50 Hz` im Kamera-Dialog

### Wenn Helligkeit pumpt:

- **Exposure/White Balance** nicht auto, sondern stabilisieren/fixieren

---

## M. Empfohlene "Default"-Konfiguration für Demos

- **Standardprofil:** `Teams-Demo-1080p60` (wenn OBS Stats sauber bleiben)
- **Fallbackprofil:** `Teams-Demo-1080p30`
- **Standard-Szene:** **S7 Hero + 3** (Hero = Shopfloor oder Kamera; rechts = Overview/Orders/Track&Trace)
- **Detail-Szenen:** Vollbild je Tab für Lesbarkeit

---

## N. Naming-Schema (wichtig für Organisation und Wartbarkeit)

### N1) Scene Collection Struktur (Scenes)

**Empfehlung:** Szenennamen immer mit Prefix, damit sie sortiert sind.

#### N1.1 Hauptszenen (Program-Szenen)

- **P01_Cam_Full** - Kamera Vollbild
- **P02_DT_Shopfloor_Full** - Shopfloor Vollbild
- **P03_UI_Overview_Full** - Overview Vollbild
- **P04_UI_Orders_Full** - Active Orders Vollbild
- **P05_UI_TrackTrace_Full** - Track&Trace Vollbild
- **P06_UI_4Up** - 4-Up Grid Layout
- **P07_UI_HeroPlus3** - Hero + 3 Layout (Standard)
- **P08_PiP_CamOverUI** - Picture-in-Picture: Kamera über UI (optional)
- **P09_PiP_UIOverCam** - Picture-in-Picture: UI über Kamera (optional)
- **P99_Hold_Slate** - Standbild/Logo "Einen Moment…"

#### N1.2 Hilfsszenen (als Quelle wiederverwendbar, optional aber sehr nützlich)

Diese Szenen werden später in P06/P07 als "Scene Source" eingebunden:

- **H01_UI_Overview_Panel** - Overview als Panel
- **H02_UI_Orders_Panel** - Orders als Panel
- **H03_UI_TrackTrace_Panel** - Track&Trace als Panel
- **H04_DT_Shopfloor_Panel** - Shopfloor als Panel
- **H05_Cam_Panel** - Kamera als Panel

**Vorteil:** Sie ändern eine Panel-Quelle einmal, und alle Layouts profitieren.

---

### N2) Sources Naming (Quellen)

**Regel:** Prefix nach Typ + kurzer Zweck + ggf. Variante.

#### N2.1 Kamera

- **VID_CAM_USB_Main** - Haupt-USB-Kamera
- **VID_CAM_USB_Alt** - Zweite USB-Kamera (optional)

Wenn Sie mal Capture Card nutzen:

- **VID_CAP_HDMI_Camlink** - Capture Card über HDMI

#### N2.2 OMF3 / Web-UI (Browser Source)

Wenn möglich, je Ansicht eine Browser Source:

- **WEB_OMF3_DT_Shopfloor** - Shopfloor-Ansicht (Browser Source)
- **WEB_OMF3_UI_Overview** - Overview-Tab (Browser Source)
- **WEB_OMF3_UI_Orders** - Orders-Tab (Browser Source)
- **WEB_OMF3_UI_TrackTrace** - Track&Trace-Tab (Browser Source)

Wenn Sie Window Capture statt Browser Source nutzen müssen:

- **WIN_Chrome_OMF3_DT_Shopfloor** - Shopfloor (Window Capture)
- **WIN_Chrome_OMF3_UI_Overview** - Overview (Window Capture)
- **WIN_Chrome_OMF3_UI_Orders** - Orders (Window Capture)
- **WIN_Chrome_OMF3_UI_TrackTrace** - Track&Trace (Window Capture)

**Wichtig:** Halten Sie die Variante (WEB_ vs WIN_) im Namen fest, sonst verlieren Sie später Zeit.

#### N2.3 Overlays / Branding

- **GFX_Logo_ORBIS** - ORBIS Logo
- **GFX_LowerThird_Title** - Unterer Drittel-Titel
- **GFX_Frame_Panel** - Panel-Rahmen (wenn Sie Panels optisch rahmen)
- **TXT_SceneLabel** - Kleines Label, z. B. "Orders" (optional)

#### N2.4 Display/Monitor Capture (nur falls genutzt)

- **DSP_Monitor2_Presenter** - Display Capture, falls Sie den Presenter-Desktop capturen

---

### N3) Audio Naming (klar trennen)

Wenn Sie in Teams präsentieren, ist Audio oft "heikel". Empfehlung: eindeutige Namen.

#### N3.1 Mikrofon

- **AUD_MIC_Headset** - Headset-Mikrofon
- oder **AUD_MIC_USB** - USB-Mikrofon

#### N3.2 System-Audio (optional; nur wenn Sie es bewusst brauchen)

- **AUD_SYS_Desktop** - Desktop-Audio

#### N3.3 Kamera-Audio (meist aus!)

- **AUD_CAM_USB** - Kamera-Audio (in OBS meist muten/deaktivieren)

**Standardregel:** Genau eine Mikrofonquelle aktiv; Kamera-Audio aus, um Echo zu vermeiden.

---

### N4) Szenenbelegung (konkret)

#### P01_Cam_Full
- `VID_CAM_USB_Main` (Fit to Screen)
- optional `GFX_Logo_ORBIS`

#### P02_DT_Shopfloor_Full
- `WEB_OMF3_DT_Shopfloor` (oder `WIN_…`)
- optional `GFX_Logo_ORBIS`

#### P03_UI_Overview_Full
- `WEB_OMF3_UI_Overview`

#### P04_UI_Orders_Full
- `WEB_OMF3_UI_Orders`

#### P05_UI_TrackTrace_Full
- `WEB_OMF3_UI_TrackTrace`

#### P06_UI_4Up
- Entweder direkt die vier `WEB_/WIN_`-Quellen
- oder besser: Scene Sources `H01..H04`

#### P07_UI_HeroPlus3
- **Hero:** `WEB_OMF3_DT_Shopfloor` oder `VID_CAM_USB_Main`
- **rechts:** Overview/Orders/TrackTrace (als Panels)

#### P99_Hold_Slate
- `GFX_Logo_ORBIS` + `TXT_SceneLabel` ("Einen Moment…")

---

### N5) Hotkeys (schnell und konfliktarm)

**Wichtig:** Wählen Sie Hotkeys, die nicht mit Teams kollidieren. Bewährt: `Ctrl + Alt + [Zahl]`.

**OBS → Settings → Hotkeys:**

- **Ctrl + Alt + 1** → Switch to `P01_Cam_Full`
- **Ctrl + Alt + 2** → Switch to `P02_DT_Shopfloor_Full`
- **Ctrl + Alt + 3** → Switch to `P03_UI_Overview_Full`
- **Ctrl + Alt + 4** → Switch to `P04_UI_Orders_Full`
- **Ctrl + Alt + 5** → Switch to `P05_UI_TrackTrace_Full`
- **Ctrl + Alt + 6** → Switch to `P07_UI_HeroPlus3` (Ihr Standard)
- **Ctrl + Alt + 7** → Switch to `P06_UI_4Up`
- **Ctrl + Alt + 0** → Switch to `P99_Hold_Slate`

**Optional:**

- **Ctrl + Alt + R** → Start/Stop Recording (für interne Tests)

---

## O. Operator-Checkliste für Live-Betrieb

### O1) Vor dem Meeting (5 Minuten)

- [ ] **OBS Profil:** `Teams-Demo-1080p60` (Fallback: `…30`)
- [ ] **Studio Mode:** ON
- [ ] **View → Stats** öffnen (Dauercheck auf Dropped/Skipped Frames)
- [ ] **Szene P99_Hold_Slate** aktivieren (damit nicht "zufällig" etwas gezeigt wird)
- [ ] **Kamera prüfen:** `P01_Cam_Full` (Bild steht, kein Flimmern)
- [ ] **UI prüfen:** `P03/P04/P05` kurz aufrufen (Login ok, Daten sichtbar)
- [ ] **Fullscreen Projector (Program)** auf Monitor 2 aktivieren

### O2) Meeting Start

- [ ] **Teams:** Bildschirm Monitor 2 teilen
- [ ] **Optimize** einschalten (wenn Bewegung)
- [ ] **Einstieg:** `P07_UI_HeroPlus3` oder `P02_DT_Shopfloor_Full`

### O3) Wenn etwas klemmt

- [ ] **Sofort auf P99_Hold_Slate** (`Ctrl+Alt+0`)
- [ ] Dann Problem beheben (Browser neu laden, Kamera replug, Profil auf 30 fps)

### O4) Nach dem Meeting

- [ ] **Recording stoppen** (wenn genutzt)
- [ ] **Kurzes Self-Review:** Lesbarkeit/Bewegung/Audio

---

## P. Troubleshooting

### Problem: Bild ruckelt in Teams

**Lösung:**
1. OBS Stats prüfen (Dropped Frames?)
2. Profil auf 30fps wechseln
3. Kamera-Auflösung reduzieren (1080p → 720p)
4. Teams Optimize aktivieren
5. High Motion testen (Ctrl + Alt + Shift + T)

### Problem: Bild unscharf

**Lösung:**
1. Canvas Resolution auf 1440p belassen
2. Output Resolution auf 1080p
3. Kamera auf 1080p setzen
4. Browser-Quellen auf 1920x1080 setzen

### Problem: Farbdrift bei Kamera

**Lösung:**
1. White Balance auf "Manual" setzen
2. Farbtemperatur fixieren (z.B. 5600K für Tageslicht)
3. Exposure stabilisieren (nicht Auto)

### Problem: Flimmern bei LED-Beleuchtung

**Lösung:**
1. Anti-banding/Flicker auf 50 Hz setzen
2. Exposure-Zeit anpassen
3. Falls möglich: LED-Beleuchtung dimmen

---

## Q. Erweiterte Tipps

### Q1) Audio-Setup (falls benötigt)

- **Sources** → **+** → **Audio Input Capture**
- Mikrofon auswählen (z.B. `AUD_MIC_Headset`)
- In Teams: Mikrofon separat teilen (nicht über OBS)
- **Kamera-Audio deaktivieren** (`AUD_CAM_USB` muten)

### Q2) Overlays (z.B. Logo, Text)

- **Sources** → **+** → **Image** (für Logo → `GFX_Logo_ORBIS`)
- **Sources** → **+** → **Text (GDI+)** (für Text-Overlays → `TXT_SceneLabel`)
- Positionierung über Transform

### Q3) Transitions zwischen Szenen

- **OBS Settings** → **General** → **Transition**
- Empfohlen: "Fade" oder "Cut" (schnell, keine Ablenkung)

---

## R. Kleine Zusatzregeln (vermeiden typische Fehler)

### R1) Quellen-Sperren

- **Quellen nach dem Einrichten immer sperren** (Lock im Sources-Panel)
- Verhindert versehentliche Verschiebungen während der Demo

### R2) Window Capture

- **Browser-Fenstergröße niemals während der Demo ändern**
- Einmal einstellen, dann nicht mehr anfassen

### R3) Audio

- **Kamera-Audio grundsätzlich aus**, wenn Sie ein Headset nutzen (Echo-Risiko)
- Nur eine Mikrofonquelle aktiv

### R4) Standard-Szene

- **Standard-Szene für Routine:** `P07_UI_HeroPlus3`

---

## S. Standard-Runbook-Sequenz (Demo-Storyline)

**Empfohlene 8–10 Minuten "Storyline" mit Szenenwechseln:**

1. **Einstieg (30s):** `P07_UI_HeroPlus3` - Hero = Shopfloor, rechts = Overview/Orders/TrackTrace
   - "Willkommen zur ORBIS SmartFactory Demo"

2. **Shopfloor-Übersicht (1-2 Min):** `P02_DT_Shopfloor_Full`
   - Shopfloor-Layout erklären
   - Module zeigen (HBW, DRILL, MILL, DPS, AIQS, FTS)

3. **Overview-Tab (1-2 Min):** `P03_UI_Overview_Full`
   - Active Orders zeigen
   - Inventory-Status

4. **Active Orders (1-2 Min):** `P04_UI_Orders_Full`
   - Order-Details
   - Production Steps

5. **Track&Trace (1-2 Min):** `P05_UI_TrackTrace_Full`
   - Workpiece-History
   - Event-Timeline

6. **Kamera-Demo (1 Min):** `P01_Cam_Full`
   - Live-FTS-Bewegung zeigen
   - Falls FTS gerade fährt

7. **Hero+3 Zusammenfassung (1-2 Min):** `P07_UI_HeroPlus3`
   - Alle Ansichten gleichzeitig
   - Fragen beantworten

8. **Ausklang:** `P99_Hold_Slate` oder zurück zu `P07_UI_HeroPlus3`

**Hotkeys während der Demo:**
- `Ctrl+Alt+6` für Hero+3 (Standard)
- `Ctrl+Alt+2` für Shopfloor
- `Ctrl+Alt+3/4/5` für UI-Tabs
- `Ctrl+Alt+0` für Hold-Slate (bei Problemen)

---

## 📚 Verwandte Dokumentation

- [OMF3 Project Structure](../../02-architecture/project-structure.md)
- [OMF3 Development Setup](../setup/project-setup.md)
- [OMF3 Routing](../../02-architecture/project-structure.md#routing)

---

**Letzte Aktualisierung:** 2025-12-16
