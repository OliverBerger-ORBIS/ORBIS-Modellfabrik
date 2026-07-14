# Windows Präsentations-Setup – Desktops + Teams + OBS (Normal/Replay)

Ziel: Reproduzierbares Demo-Setup auf Windows mit **virtuellen Desktops** als Layout-Basis und **OBS für Kamera**.

## Ultra-Kurz (6 Aktionen)
- Modus wählen: **Normal (Live)** oder **Replay**.
- In Desktop 1 (`Working`) alle nötigen Apps in Reihenfolge starten (bei Replay zuerst Mosquitto + OSF; Browser-Tabs erst nach laufendem OSF).
- Apps auf Desktop 1/2/3 verteilen.
- Apps in den Desktops anordnen und Zoom-/Größeneinstellungen prüfen (siehe [Referenz-Zoom](#referenz-zoom-verifiziert-14072026)).
- Mit `WIN + Ctrl + ←/→` kurz testen, ob alles stabil funktioniert.
- Optional Teams teilen und mit/ohne Aufnahme starten.

## Scope
- Teams teilt den Präsentationsmonitor im Vollbild und zeichnet auf.
- Bei Problemen mit Teams-Meeting-Aufzeichnung wird das **Windows Snipping Tool** für Videoaufnahme verwendet.
- Es gibt zwei Modi:
  - **Normal-Modus:** APS + Konftel-20 + OSF (bevorzugt über RPi/APS)
  - **Replay-Modus:** ohne APS, mit Laptop-Kamera + lokalem Mosquitto-Broker + OSF auf localhost
- OBS wird für Kamera-Preview betrieben.
- Kamera liegt auf Desktop 1 (Working) im OBS-Projector-Preview und zusätzlich auf Desktop 3 (rechts unten) als Gegenpart zum Digital Twin.
- Für Object Detection bleibt OBS-Recording der Kamera möglich.
- **Desktop 2 (Landscape Fullscreen):** **Edge**, Browser-Zoom **100 %**, Use-Case-Diagramm **100 %** (OSF-Zoom), Sidebar eingeklappt.
- **Desktop 3 (Hero):** **Chrome**, Browser-Zoom **80 %**, DSP-Architektur-Diagramm **100 %** (OSF-Zoom) + **Edge InPrivate** für Digital Twin (rechts oben) + Kamera-Preview (rechts unten).

---

## Referenz-Zoom (verifiziert 14.07.2026)

| Desktop | Auflösung (typ.) | Browser | OSF-Diagramm-Zoom | Inhalt | Hinweise |
|--------|-------------------|---------|-------------------|--------|----------|
| **2 – Landscape Fullscreen** | 1920×1200 (Prio 1) | **100 %** | **100 %** (UC) | Use-Case UC-00…07 | Sidebar standardmäßig eingeklappt; per Toggle aufklappbar. |
| **3 – Hero** | ~1040×1080 | **80 %** | **100 %** (DSP Architektur) | DSP → Accordion **Architektur** | Accordion normal scrollbar; Diagramm ohne Scroll bei ≤ **100 %** OSF-Zoom; Scroll erst bei OSF-Zoom **> 100 %**. |

**Semantik OSF-Diagramm-Zoom:** 100 % = maximaler Fit in den sichtbaren Diagrammbereich (nicht literal 1920 px Canvas).

**Nach Browser-Update / Hard-Reload:** UC- und DSP-Zoom ggf. einmal **Reset** (↺), falls alter `sessionStorage`-Wert (`OSF.viewScale`) noch aktiv ist.

---

## A) Schnell-Checkliste (operatorfähig)

### Preflight (2 Minuten)
- [ ] Windows-Desktop gestartet, externer Monitor erkannt (falls vorhanden)
- [ ] Anzeigeeinstellung geprüft: Desktop-Rechtsklick → Anzeigeeinstellungen → **Diese Anzeigen duplizieren** (Laptop-Monitor)
- [ ] Modus gewählt: **Normal** oder **Replay**
- [ ] VS Code gestartet (optional im Normal-Modus, erforderlich im Replay-Modus)
- [ ] Normal-Modus: APS gestartet (optional zusätzlich OSF auf localhost)
- [ ] Replay-Modus: Mosquitto-Bridge läuft, OSF läuft auf localhost
- [ ] Teams angemeldet und testweise monitor-share verfügbar
- [ ] OBS installiert und startet fehlerfrei (scene collection osf-camera)
- [ ] Browser vorhanden: Edge + Chrome (InPrivate für Digital Twin)
- [ ] URL-Persistenz eingerichtet: Favoriten-Ordner `OSF-LH` + `OSF-RPi`, Browser-Start auf „Vorherige Sitzung fortsetzen“

### Layout & Kamera
- [ ] Desktop 1: Working (OBS-Preview + Steuerungs-Apps + VS Code)
- [ ] Desktop 2: Fullscreen (Edge, Browser **100 %**, Use-Case-Diagramm **100 %**)
- [ ] Desktop 3: Hero (Chrome Browser **80 %**, DSP-Architektur **100 %** + Edge InPrivate Digital Twin rechts oben + Kamera-Preview rechts unten)
- [ ] Kameraquelle gewählt: Konftel-20 (Normal) oder Laptop-Cam (Replay/Fallback)
- [ ] Konftel-20 Presets eingerichtet (0 = Gesamtansicht, 1 = DRILL, 2 = HBW, 3 = MILL, 4 = AIQS, 5 = DPS, 6 = CHRG) 
- [ ] OBS-Preview auf Desktop 1 offen + zweites Preview auf Desktop 3 (rechts unten)
- [ ] Kamera-Verzerrungs-Check bestanden (OBS + Teams)
- [ ] Preset-Test bestanden (0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 0, Positionen korrekt)

### Teams-Pfad
- [ ] In Teams den Präsentationsmonitor im Vollbild teilen
- [ ] Optional: Desktop 1 (`Working`) teilen, wenn Kamera-Vollbild im Fokus stehen soll
- [ ] Recording-Pfad festlegen:
  - Primär: Teams-Aufzeichnung (Meeting)
  - Fallback: Windows Snipping Tool (Screen Recording)


---

## B) Erprobung – Schrittfolge (stabil, komplett händisch)

### Aktion 1) Modus wählen (Normal oder Replay)
- [ ] **Normal (Live):** APS starten und Datenpfad prüfen
- [ ] **Replay:** (VS Code starten)
  - Mosquitto-Bridge starten: `.\scripts\start-mosquitto-ws-bridge.ps1`
  - OSF starten: `.\scripts\run-osf.ps1` (alternativ `npm run serve:osf-ui`)
- [ ] Erst wenn OSF läuft, Browser-Tabs öffnen

### Aktion 2) Apps in Desktop 1 (`Working`) starten
- [ ] OBS starten (Scene Collection: `osf-camera`)
- [ ] Kameraquelle wählen:
  - Normal-Modus: `scn-01_Konftel-Cam20`
  - Replay-Modus: `scn-02_laptop-cam`
- [ ] Zwei Camera-Preview-Projektoren als eigene Fenster öffnen
- [ ] Edge + Chrome starten (sowie Edge InPrivate für Digital Twin)
- [ ] Teams nur bei Bedarf starten (optional)

### Aktion 3) Apps auf Desktops verteilen (WIN + TAB in Desktop 1)
- [ ] Desktop 1: OBS-Preview + Steuerungs-Apps + VS Code
- [ ] Desktop 2: Edge (Fullscreen)
- [ ] Desktop 3: Chrome (Hero) + Edge InPrivate (Digital Twin) + OBS-Preview (Kamera)

### Aktion 4) In den Desktops anordnen und Werte prüfen
- [ ] Desktop 2 (Edge): Browser-Zoom **100 %**, Use-Case-Diagramm **100 %** (Reset ↺ falls nötig)
- [ ] Desktop 3 (Chrome): Browser-Zoom **80 %**, DSP-Architektur **100 %** (Accordion **Architektur** geöffnet)
- [ ] Desktop 3 (rechts oben): Edge InPrivate mit Digital Twin
- [ ] Desktop 3 (rechts unten): OBS-Kamera-Preview
- [ ] Kamera-Verzerrungs-Check (OBS + Teams) durchführen

> **Konftel-20 OBS-Einstellungen (validiert 09.07.2026 vor Ort bei ORBIS):**
> - **Resolution:** Device Default
> - **Zoom:** mit Fernbedienung auf korrekten Ausschnitt einstellen
> - **Edit Transform:**
>   - Bounding Box Type: **Scale to inner bounds (FIT)**
>   - Bounding Box Size: **1920 × 1080**
>   - Crop – Top: **10**, Bottom: **10**, Left: **120**, Right: **120**
> - Preview Desktop 1 + Desktop 3 verifiziert: ✓
>
> **Konftel-20 Presets einrichten (Fernbedienung):**
> - Kamera auf Zielausschnitt ausrichten -> **PRESET** -> Ziffer (**0-6**) speichern
> - Empfohlene Belegung: **0 Gesamtansicht**, **1 DRILL**, **2 HBW**, **3 MILL**, **4 AIQS**, **5 DPS**, **6 CHRG** (OBS Cam-View zeigt erfolgreiche Tastenbelegung links oben)
>
> **Preset-Test (Pflicht):**
> - Sequenz drücken: **0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 0**
> - In OBS-Preview Desktop 1 und Desktop 3 prüfen: korrekter Ausschnitt, reproduzierbare Position, keine Verzerrung

### Aktion 5) Kurztest Navigation
- [ ] Mit `WIN + Ctrl + ←/→` kurz zwischen Desktop 1/2/3 wechseln
- [ ] Prüfen, ob Fensterpositionen, Zoom und Inhalte stabil bleiben

### Aktion 6) Optional: Teams teilen und aufnehmen
- [ ] Gewünschten Desktop/Monitor in Teams teilen
- [ ] Optional Desktop 1 teilen, wenn Kamera-Vollbild im Fokus stehen soll
- [ ] Aufnahme starten:
  - Primär: Teams-Aufzeichnung
  - Fallback: Snipping Tool

### Optional: Object Detection
- [ ] OBS-Kameraaufnahme kann parallel zur Teams-Aufnahme laufen

---

## C) Fallbacks

### Kein Konftel-20 angeschlossen
- Built-in-Kamera verwenden.
- **Identische OBS-Einstellungen wie bei Konftel-20 verwenden** (Crop/Transform zuerst gleich lassen).
- Danach Kamera-Verzerrungs-Check durchführen (OBS Preview + Teams-Share).
- Weiterhin 4:3 bevorzugen (z. B. 800x600).
- Wenn nur 16:9 verfügbar: Crop/Letterbox bewusst prüfen, keine Geometrieverzerrung.

### Zweiter Monitor fehlt
- Setup A nutzen (Laptop-Monitor teilen/duplizieren).
- Desktop 1/2/3 weiterhin verwenden, nur auf einem Display.
