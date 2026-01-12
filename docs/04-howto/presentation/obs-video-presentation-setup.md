# OBS Video-Präsentation Setup für ORBIS SmartFactory (OSF)

**Zielgruppe:** Präsentatoren, die OSF in Teams-Meetings demonstrieren  
**Plattform:** Windows  
**Tools:** OBS Studio, Microsoft Teams

---

## 🎯 Zielzustand

- **Monitor 1 (Laptop):** OBS-Bedienung (Studio Mode), Browser/OSF UI, Teams-Controls, Notizen
- **Monitor 2 (extern):** Nur das fertige OBS-Program im Vollbild (Fullscreen Projector)
- **Teams:** Teilt Monitor 2 (nicht das OBS-Fenster)

---

## A. Vorbereitungen in Windows

### A1) Monitors configured correctly

1. **Windows Settings** → **System** → **Display**
2. Under **Multiple displays** choose **Extend these displays**
3. Use **Identify** to confirm which screen is #1 (laptop) vs. #2 (external)
4. **Recommendation:** use monitor 2 as the presentation surface (it does not have to be the primary display)

### A2) Keep scaling stable

1. In the same Display view verify the scaling per screen
2. Set **monitor 2 to 100 % or 125 %** and avoid changing it later
3. Keep monitor 2 on a clean resolution (e.g., 2560×1440 or 1920×1080); OBS/Teams will still output whatever you configure in section C

---

## B. OBS Grundkonfiguration (absoluter Start)

### B1) OBS starten und zwei organisatorische Container anlegen

In OBS gibt es zwei Dinge:
- **Profile** = Video/Output/Encoder settings
- **Scene Collection** = Scenes + sources (Ihre Demo-Layouts)

#### Schritt 1: Erstes Profil anlegen (30 fps)

1. **OBS** → Menü **Profile** → **New**
2. Name: `Teams-Demo-1080p30`
3. **OK**

#### Schritt 2: Scene Collection anlegen

1. **OBS** → Menü **Scene Collection** → **New**
2. Name: `ORBIS SmartFactory Demo`
3. **OK**

### B2) Hardware-agnostic sandbox setup

Sie können das gesamte Layout vorbereiten, auch wenn weder Kamera noch Präsentationsmonitor verfügbar sind:

1. **Canvas-Größe unabhängig von Hardware:** Die Werte aus Abschnitt C gelten immer. OBS rendert intern auf 2560×1440 → 1920×1080, selbst wenn aktuell nur ein kleiner Laptop-Screen vorhanden ist.
2. **Kamera-Platzhalter:** Legen Sie eine `Color Source` oder ein statisches PNG (z. B. `placeholder-camera.png`) an und nennen Sie sie `VID_CAM_USB_Main`. Sobald die echte Kamera angeschlossen wird, tauschen Sie nur die Quelle über **Right-click → Properties → Device** aus.
3. **Browser-Fenster ohne Zweitmonitor:** Öffnen Sie pro Tab ein Edge/Chrome-Fenster, setzen Sie es auf 1920×1080 und lassen Sie es minimiert. Window-Capture behält die Größe, auch wenn das Fenster außerhalb des sichtbaren Bereichs liegt.
4. **Preview statt Fullscreen Projector:** Solange kein zweiter Monitor da ist, verwenden Sie **View → Multiview (Fullscreen)** oder **View → Windowed Projector (Program)**. Dieses Fenster können Sie später in Teams teilen; sobald der zweite Monitor angeschlossen ist, wechseln Sie auf den echten Fullscreen Projector.
5. **Testing ohne Kamera:** Aktivieren Sie bei Bedarf **Tools → Start Virtual Camera**, wählen Sie diese als Device und prüfen Sie so das Layout sogar in Teams, ohne physische Kamera.

---

## C. OBS Video-Einstellungen (empfohlen für UI + Shopfloor)

### C1) Video (Canvas/Output/FPS)

1. **File** → **Settings** → **Video**
2. Set the following values:
   - **Base (Canvas) Resolution:** `2560x1440`
   - **Output (Scaled) Resolution:** `1920x1080`
   - **Common FPS Values:** `30`
3. **Apply** → **OK**

**Result:** Canvas bleibt 1440p (mehr Schärfe/Reserve), Output ist 1080p und damit Teams-kompatibel.

> **Fallback:** Wenn Ihre Monitorkombi diese Werte nicht zulässt, nutzen Sie vorerst das aktuelle Profil (z. B. 3840×2160 → 1280×720). Die restliche Szene-/Quellenstruktur funktioniert trotzdem und kann später wieder auf 2560→1920 zurückgestellt werden.

---

## D. OBS Output/Recording (für reproduzierbare Tests)

### D1) Output (Recording für Qualitätskontrolle)

1. **File** → **Settings** → **Output**
2. **Output Mode:** `Advanced`
3. Tab **Recording**
   - **Type:** `Standard`
   - **Recording Format:** `MKV`
   - **Encoder:** Hardware (NVENC/QSV/AMF), falls vorhanden; sonst `x264`
4. **Apply** → **OK**

**Note:** Sie streamen nicht aus OBS. Recording dient nur zur Qualitätssicherung nach Tests.

---

## E. Szenen anlegen (Vollbild + Portrait + Hero+2)

### E1) Szenenliste erstellen

Links unten im **"Scenes"**-Panel nacheinander **+** klicken und anlegen. Die ersten vier Szenen füllen später automatisch die Multiview-Slots 1–4.

- **S1 - Orders Vollbild (Edge InPrivate)** – OSF Orders/Track&Trace im separaten Edge-Profil
- **S2 - Digital-Twin Vollbild (Chrome)** – Route `#/de/presentation` inkl. FTS/AGV-Feed
- **S3 - OSF Vollbild (Chrome)** – Hauptdashboard mit allen Tabs (Overview, DSP, KPIs)
- **S4 - Kamera Vollbild** – USB-Kamera oder Placeholder
- **S5 - Hero + 2** – Komposition aus OSF Hero (960×1080) + Digital Twin (960×540) + Kamera (960×540)
- **S6 - OSF Hero (Edge)** – Spezielle Ansicht für Hero-Bereich (960×1080), dient als Vollbildfallback und als Quelle für S5
- **S7 - Hold Slate** – Pausen-/Wartebild über Browser Source (siehe `hold-slate.html`)

---

## F. Quellen anlegen

### F1) Kamera als Quelle (USB)

1. Szene **S4 - Kamera Vollbild** auswählen
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

#### Kamera-Hardware (Konftel Cam50)

- **Modell:** Konftel Cam50 (USB-PTZ-Kamera), identifiziert sich in OBS als Standard-Webcam
- **Optimale Auflösung:** `1920x1080` (Shopfloor wird in der Totalen vollständig erfasst)
- **Alternative Auflösungen:** `800x448` oder `600x360`, falls Bandbreite/FPS wichtiger als Detail sind
- **FPS-Regler:** 5, 10, 15, 20, 24, 29.97 (NTSC), 30 sowie das vom Treiber gemeldete Maximum
- **Videoformate:** `MJPEG` oder `H264` (beide funktionieren stabil; MJPEG bevorzugen, wenn CPU-Headroom vorhanden ist)
- **Farbraum:** "Standard" sowie mehrere Rec*-Profile (z. B. Rec.601/709) – auf Standard bleiben, außer Sie kalibrieren gezielt auf Studiolicht
- **Pufferung:** wahlweise `Auto`, `Enabled`, `Disabled`; für Teams-Demos reicht `Auto`, bei Frame-Drops testweise auf `Enabled` schalten

---

### F2) Browser-Quellen (Window Capture, 4 Fenster)

Alle UI-Szenen laufen über Window Capture. Wir nutzen **zwei Chrome-** und **zwei Edge-Fenster**, damit Sessions voneinander getrennt bleiben und Multiview die Slots sauber füllt.

1. **Vier Fenster vorbereiten:**
   - **Chrome Fenster A (Landscape, S3):** Standardprofil (1920×1080) mit allen acht Demo-Tabs (DSP, Shopfloor, Process, Orders, Environment Data, Configuration, AGV, Track&Trace). Sprache immer `DE`, Environment `Live`, Sidebar eingeklappt.
   - **Chrome Fenster B (Digital Twin, S2):** Incognito/Privat-Fenster (1920×1080) mit Route `#/de/presentation` und aktivem FTS-/AGV-Feed, nur ein Tab.
   - **Edge Fenster A (Orders, S1):** InPrivate-Session (1920×1080) für Orders/Track&Trace, nur ein Tab.
   - **Edge Fenster B (Hero, S6):** Business-Profil, auf 960×1080 gestellt (entspricht Hero-Bereich in S5).
   Nutzen Sie `Win + Pfeil` und `Alt + Space → S`, um exakt zu skalieren. Zoom immer mit `Ctrl + 0` zurücksetzen.
2. **Tabs je Fenster fixieren:** Jede Route/Tab einmal laden, dann nicht mehr ändern. Bookmark-Bar ausblenden (`Ctrl+Shift+B`), damit nix flackert.
3. **Window Capture hinzufügen:**
   - **S1 - Orders Vollbild:** Quelle `Edge_Priv_OSF_ORDER` (Edge InPrivate Fenster A).
   - **S2 - Digital-Twin Vollbild:** Quelle `Chrome_Priv_DigitalTwin` (Chrome Fenster B).
   - **S3 - OSF Vollbild:** Quelle `Chrome_OSF_Landscape` (Chrome Fenster A).
   - **S6 - OSF Hero:** Quelle `Edge_OSF_Hero` (Edge Fenster B, 960×1080).
   Quellen nach dem Positionieren auf `Fit to Screen` setzen und sofort sperren.
4. **Naming im Sources-Panel:**
   - `Edge_Priv_OSF_ORDER` (Edge InPrivate → Orders/Track&Trace)
   - `Chrome_Priv_DigitalTwin` (Chrome Incognito → DT)
   - `Chrome_OSF_Landscape` (Chrome Standard → Dashboard)
   - `Edge_OSF_Hero` (Edge Business → Hero, 960×1080)
   Nutzen Sie exakt diese Namen, damit Hero + 2 und Multiview immer auf dieselben Assets verweisen.
5. **Kein zweiter Monitor?** Fenster minimieren reicht. OBS rendert minimierte Fenster weiter, solange sie nicht geschlossen werden.

### F3) OBS Multiview (Slots 1–4 direkt)

Statt einer zusätzlichen Szene nutzen wir das native Multiview und füttern Slots 1–4 mit `S1–S4` (Orders, Digital Twin, OSF Dashboard, Kamera).

1. **Reihenfolge prüfen:** In der Scenes-Liste muss exakt `S1 → S2 → S3 → S4 → S5 → S6` stehen. So landen die gewünschten Quellen automatisch in den Multiview-Slots 1–4.
2. **Settings → General → Multiview:** Layout `Top 8 (2×4)` wählen und `Disable Preview/Program` aktivieren.
3. **View → Multiview (Windowed)** testen. Wenn ein Slot falsch belegt ist, verschieben Sie die Szene in der Liste oder blenden Sie sie temporär aus.
4. **Fullscreen für Demo:** `View → Multiview (Fullscreen)` → Monitor 2. Beenden mit `Esc`.
5. **Keine zusätzliche Szene:** Multiview wird nicht mehr gecaptured. Sie teilen direkt den Multiview-Ausgang via Monitor 2, sodass die vier Perspektiven live bleiben.

**Vorteil:** Kein separates Raster pflegen; die Slots folgen der Szenenliste. Für andere Vierer-Kombinationen nur die Reihenfolge der ersten vier Szenen neu sortieren.

---

## G. Multi-Layouts exakt bauen

**Voraussetzung:** Output bleibt 1920×1080. Für echte 4-fach-Ansichten nutzen Sie ausschließlich das Multiview aus Abschnitt F3. Lediglich Szene `S5 - Hero + 2` benötigt ein manuelles Layout.

### G1) S5 - Hero + 2 (OSF Hero + Digital Twin + Kamera)

1. Szene **S5 - Hero + 2** wählen.
2. Drei Quellen hinzufügen (direkt die Window Captures / Kameraquellen aus Abschnitt F2/F1):
   - `Edge_OSF_Portrait`
   - `Chrome_Priv_DigitalTwin`
   - `CAM - USB` (oder `placeholder-camera`)
3. **Transform → Edit Transform** und folgende Werte setzen (alles in Pixel):

- **OSF Hero (links):** `X=0`, `Y=0`, `W=960`, `H=1080` (nutzt verfügbaren Platz optimal aus).
- **Digital Twin (rechts oben):** `X=960`, `Y=0`, `W=960`, `H=540`.
- **Kamera (rechts unten):** `X=960`, `Y=540`, `W=960`, `H=540` (16:9 Verhältnis für Konftel Cam50 beibehalten).

**Berechnung:**
- OBS Output: 1920×1080px
- Kamera (16:9): 960×540px (960/540 = 1.78 = 16:9)
- Hero-Bereich: 1920 - 960 = 960px Breite, volle Höhe 1080px = 960×1080px
- Digital Twin: 960×540px (gleiche Größe wie Kamera)

4. Optional Rahmen/Labels ergänzen (`GFX_Frame_Panel`, `TXT_SceneLabel`).
5. Quellen sperren, sobald die Positionen stimmen. Die rechten Quellen (Digital Twin + Kamera) teilen sich exakt 960×540px und behalten das 16:9 Verhältnis der Kamera bei.

### G2) Multiview ohne eigene Szene

Multiview rendert direkt aus den Szenen `S1–S4`. Sie müssen daher nichts im Canvas positionieren:

- Slots 1–4 übernehmen automatisch `S1` (Orders Edge), `S2` (Digital Twin Chrome), `S3` (OSF Chrome) und `S4` (Kamera).
- Änderungen am Viererbild erledigen Sie, indem Sie die Reihenfolge der Szenen verschieben oder einzelne Szenen temporär deaktivieren.
- Für Hero + 2 oder Hero-Vollbild bleiben `S5` und `S6` unverändert und beeinflussen Multiview nicht.

Wichtig: Die vier Browserfenster müssen geöffnet bleiben, sonst liefert Multiview leere Slots.

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
2. **S2** OSF Vollbild (Tabs durchklicken, Audio testen)
3. **S3** Shopfloor Vollbild (Digital Twin, Kamera-Feed)
4. **S4** OSF Portrait (responsive Darstellung prüfen)
5. **S5** Hero + 2 (lesen sich alle drei Bereiche?)
6. **Multiview:** `View → Multiview (Windowed)` (zeigen Slots 1–4 die richtigen Szenen?)

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
- **Standard-Szene:** **S5 Hero + 2** (links OSF Hero 960×1080, rechts Digital Twin + Kamera je 960×540)
- **Detail-Szenen:** `S3 - OSF Vollbild`, `S2 - Digital-Twin Vollbild`, `S6 - OSF Hero`

---

## N. Naming-Schema (wichtig für Organisation und Wartbarkeit)

### N1) Scene Collection Struktur (Scenes)

**Faustregel:** Alle Programmszenen erhalten das Prefix `S#`. Diese Reihenfolge muss stabil bleiben, weil Multiview Slots 1–4 daraus gebaut werden.

#### N1.1 Hauptszenen (Program)

- **S1 - Orders Vollbild (Edge InPrivate)** – OSF Orders/Track&Trace getrennt von den anderen Sessions
- **S2 - Digital-Twin Vollbild (Chrome)** – Route `#/de/presentation` mit FTS/AGV und KPIs
- **S3 - OSF Vollbild (Chrome)** – Hauptdashboard, alle Tabs vorbereiten
- **S4 - Kamera Vollbild** – USB-Kamera oder Placeholder
- **S5 - Hero + 2** – Komposition (OSF Hero 960×1080 links, Digital Twin + Kamera je 960×540 rechts)
- **S6 - OSF Hero (Edge)** – Hero-Ansicht (960×1080) als Vollbildfallback und Quelle für S5
- **S7 - Hold Slate** – Logo/Standbild für Pausen; als Browser Source mit [hold-slate.html](hold-slate.html) einbinden

#### N1.2 Optionale Hilfsszenen

Wenn Sie komplexere Layouts bauen möchten, können Sie zusätzliche `H##_*` Szenen definieren, die die Browser-Fenster oder die Kamera kapseln. In diesem Setup ist das nicht nötig, weil Hero + 2 direkt auf die Window-Capture-Quellen zugreift. Nutzen Sie Hilfsszenen nur, wenn mehrere Layouts dieselben Crops/Overlays teilen sollen.

---

### N2) Sources Naming (Quellen)

**Regel:** Prefix nach Typ + kurzer Zweck + ggf. Variante.

#### N2.1 Kamera

- **VID_CAM_USB_Main** - Haupt-USB-Kamera
- **VID_CAM_USB_Alt** - Zweite USB-Kamera (optional)

Wenn Sie mal Capture Card nutzen:

- **VID_CAP_HDMI_Camlink** - Capture Card über HDMI

#### N2.2 OSF / Web-UI (Window Capture)

- **Chrome_OSF_Landscape** – Chrome Standardprofil (1920×1080) mit allen Tabs für S3
- **Chrome P Digital-Twin** – Chrome Incognito (1920×1080) nur für Route `#/de/presentation` (S2)
- **Edge_P_OSF_ORDER** – Edge InPrivate (1920×1080) für Orders/Track&Trace (S1)
- **Edge_OSF_Hero** – Edge Business (960×1080) für die Hero-Ansicht (S6/S5)

Vier unterschiedliche Fenster stellen sicher, dass Logins/Geteilte Sessions sich nicht gegenseitig beeinflussen und dass Multiview keine Tabs vertauscht.

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

#### S1 - Orders Vollbild (Edge)
- Quelle `Edge_P_OSF_ORDER`
- Fit to Screen, danach sperren

#### S2 - Digital-Twin Vollbild (Chrome)
- Quelle `Chrome P Digital-Twin`
- Keine Overlays, nur DT-Route

#### S3 - OSF Vollbild (Chrome)
- Quelle `Chrome_OSF_Landscape`
- Optional `GFX_Logo_ORBIS`

#### S4 - Kamera Vollbild
- `CAM - USB` bzw. `placeholder-camera`
- Transform → Fit to Screen

#### S5 - Hero + 2
- Links (`X=0`, `Y=0`, `W=960`, `H=1080`): `Edge_OSF_Hero` (Hero-Bereich)
- Rechts oben (`X=960`, `Y=0`, `W=960`, `H=540`): `Chrome_Priv_DigitalTwin` (Digital Twin)
- Rechts unten (`X=960`, `Y=540`, `W=960`, `H=540`): `CAM - USB` (Konftel Cam50, 16:9)
- Optional Rahmen/Text hinzufügen

#### S6 - OSF Hero (Edge)
- Quelle `Edge_OSF_Hero` (960×1080) als Vollbild
- Dient als Backup, falls Hero + 2 nicht reicht

#### S7 - Hold Slate
- **Quelle:** Browser Source → Local File → [hold-slate.html](hold-slate.html)
- **Größe:** Auf Canvas-Größe setzen (z. B. 1920×1080)
- **Option:** "Shutdown source when not visible" deaktivieren für sofortiges Umschalten

---

### N5) Hotkeys (schnell und konfliktarm)

**Schema:** `Ctrl + Alt + [Zahl]` kollidiert nicht mit Teams und lässt sich blind bedienen.

**OBS → Settings → Hotkeys:**

- **Ctrl + Alt + 1** → `S1 - Orders Vollbild`
- **Ctrl + Alt + 2** → `S2 - Digital-Twin Vollbild`
- **Ctrl + Alt + 3** → `S3 - OSF Vollbild`
- **Ctrl + Alt + 4** → `S4 - Kamera Vollbild`
- **Ctrl + Alt + 5** → `S5 - Hero + 2`
- **Ctrl + Alt + 6** → `S6 - OSF Hero`
- **Ctrl + Alt + 7** → `S7 - Hold Slate`

**Optional:**

- **Ctrl + Alt + R** → Start/Stop Recording
- **Ctrl + Alt + Shift + M** (frei belegbar) → `View → Multiview (Fullscreen)` toggeln, falls Sie einen Hotkey für das Viererbild möchten

---

## O. Operator-Checkliste für Live-Betrieb

### O1) Vor dem Meeting (5 Minuten)

- [ ] **OBS Profil:** `Teams-Demo-1080p60` (Fallback: `…30`)
- [ ] **Studio Mode:** ON
- [ ] **View → Stats** öffnen (Dauercheck auf Dropped/Skipped Frames)
- [ ] **Optional:** `S7 - Hold Slate` aktiv halten, damit kein Browser durchsickert
- [ ] **Kamera prüfen:** `S4 - Kamera Vollbild` (Belichtung, Weißabgleich, Fokus)
- [ ] **UI prüfen:** `S1/S2/S3/S6` kurz aufrufen (Tabs geladen, DT-Feed aktiv, Hero-Ansicht responsive)
- [ ] **Fullscreen Projector (Program)** auf Monitor 2 aktivieren

### O2) Meeting Start

- [ ] **Teams:** Bildschirm Monitor 2 teilen
- [ ] **Optimize** einschalten (wenn Bewegung)
- [ ] **Einstieg:** `S5 - Hero + 2` (Standard) oder `S3 - OSF Vollbild`

### O3) Wenn etwas klemmt

- [ ] **Sofort auf S7 - Hold Slate** (`Ctrl+Alt+7`)
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

- **Standard-Szene für Routine:** `S5 - Hero + 2`

---

## S. Standard-Runbook-Sequenz (Demo-Storyline)

**Empfohlene 8–10 Minuten mit den sechs Szenen:**

1. **Intro (30 s):** `S5 - Hero + 2`
   - Begrüßung, kurze Einordnung der drei Fenster (Portrait links, Digital Twin + Kamera rechts).

2. **OSF Überblick (2 Min):** `S3 - OSF Vollbild`
   - Durch vorbereitete Tabs klicken (Orders, Track&Trace, DSP, KPIs).
   - Auf vorbereitete Browser-Hotkeys hinweisen.

3. **Shopfloor / Digital Twin (1–2 Min):** `S2 - Digital-Twin Vollbild`
   - Modulkameras, FTS-Lauf, Sensorwerte erklären.

4. **Responsive Detail (1–2 Min):** `S6 - OSF Hero`
   - Hero-Ansicht (960×1080) zeigen, Order- oder KPI-Details scrollen.

5. **Kamera-Livebild (1 Min):** `S4 - Kamera Vollbild`
   - Hardware/FTS in Echtzeit demonstrieren.

6. **Multiview Wrap-up (1 Min):** `View → Multiview (Fullscreen)` (Slots `S1–S4`)
   - Vier Perspektiven parallel zeigen, Fragen beantworten, spontan Szenen wechseln.

7. **Ausklang:** Zurück zu `S5 - Hero + 2` oder `S0 - Hold Slate` (falls vorhanden).
7. **Ausklang:** Zurück zu `S5 - Hero + 2` oder `S7 - Hold Slate`.

**Hotkeys während der Demo:**
- `Ctrl+Alt+5` → Hero + 2 (Intro & Wrap-up)
- `Ctrl+Alt+3/2/6` → OSF Vollbild / Digital Twin / Hero
- `Ctrl+Alt+1` → Orders Vollbild (slot 1 ersetzen, falls nötig)
- `Ctrl+Alt+4` → Kamera Vollbild
- `Ctrl+Alt+0` → Hold-Slate bei Unterbrechungen
- Optional: eigener Shortcut für `View → Multiview (Fullscreen)`

---

## T. Kundenpräsentation (Gedore) – OBS/Teams Playbook

### T1) Setup-Variation
- **Geräte:** Konftel Cam50 (siehe Abschnitt F1) + separater Laptop für OBS, zweiter Monitor als Program-Ausgang.
- **DSP-Animationen:** Zusätzliche Media Source (`GFX_DSP_Gedore`) mit kundenspezifischen SVG/MP4-Sequenzen (Edge xyz_2 → xyz_1/3 → Logo).
- **Szenen aus dem Standard-Set:**
   - `S5 - Hero + 2` (Intro/Wrap-up, rechtes Paneel mit kundenspezifischem Text oder KPI-Overlay).
   - `S3 - OSF Vollbild` (Volle OSF-Ansicht für Edge/Device/DSP-Story, Tabs bereits vorbereitet).
   - `S2 - Digital-Twin Vollbild` (Modulkameras + Process-Story im Digital Twin).
   - `S6 - OSF Hero` (Hero-Ansicht 960×1080 für KPI- oder Order-Screens).
   - `S4 - Kamera Vollbild` (Q&A bzw. Hardware-Showcase am Ende).
   - `View → Multiview (Fullscreen)` (Slot-Kombi aus `S1–S4` für Vier-Up Wrap-up).
- **Optional:** Falls Sie eine eigenständige DSP-Animation brauchen, legen Sie eine zusätzliche Scene Collection-Version mit `Media Source + VID_CAM_USB_Main (Picture-in-Picture)` an, behalten aber die Hotkeys aus Abschnitt N5 bei.

### T2) Ablauf (Empfehlung)
1. **Intro (`S5`)** – Kamera + Shopfloor + Portrait. Rechtes Textpaneel nutzt `TXT_SceneLabel` für Kunde/Agenda.
2. **DSP-Erklärung (`S3` + `GFX_DSP_Gedore`)** – Animation starten, Edge/Device/ERP-Linking erklären.
3. **Modul-Detail (`S2` oder `S6`)** – Auf Kundenmodul zoomen, Statusanzeigen hervorheben.
4. **Process-Story (Multiview aus `S1–S4` oder erneut `S3` mit Overlay)** – Schritte im Vierer-Layout oder Vollbild erläutern.
5. **Q&A (`S4 - Kamera Vollbild`)** – Kamera Vollbild für Fragen; optional zurück zu `S5` für Wrap-up.

### T3) OBS-spezifische Hinweise
- **Studio Mode** aktiv, Szenenwechsel erst nach Preview.
- **Hotkeys** entsprechen Abschnitt N5 (`Ctrl+Alt+1…6`). Zusätzliche DSP-Szene nur bei Bedarf auf freie Kombination (z. B. `Ctrl+Alt+7`).
- **Audio:** Headset als einzige Audio-Quelle, Kamera-Mic muted.
- **Teams:** Bildschirm „Monitor 2“ teilen, „Optimize“ aktiv; im Chat ankündigen, wenn Animationen starten.

### T4) Nachbereitung
- Aufzeichnung (`Ctrl+Alt+R`) lokal speichern, um Highlights später in kundenspezifische Clips zu schneiden.
- Feedback sofort in PROJECT_STATUS Todo-Liste spiegeln (z. B. fehlende Module-Tiles, neue Prozess-Sichten).

---

## 📚 Verwandte Dokumentation

- [OMF3 Project Structure](../../02-architecture/project-structure.md)
- [OMF3 Development Setup](../setup/project-setup.md)
- [OMF3 Routing](../../02-architecture/project-structure.md#routing)

---

**Letzte Aktualisierung:** 2025-12-21
