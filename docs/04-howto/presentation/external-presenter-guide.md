# Windows Präsentations-Setup – Desktops + Teams + OBS

Reproduzierbares Demo-Setup: **virtuelle Windows-Desktops**, **OBS nur für Kamera**, OSF-UI mit **Landscape/Hero-Profilen** (ab v1.1.8).
  
Diese Anleitung ist für Präsentierer gedacht, die die Live-Präsentation auf einem Windows-PC oder Laptop zeigen.
  
## Zielbild
  
Nach dem Setup sind die SmartFactory-Favoriten importiert, OBS zeigt nur die Kamera, und die Fenster sind auf die drei Präsentations-Desktops verteilt.
  
## 1) SmartFactory-Favoriten importieren
  
Import-Datei (ADO Wiki): [SmartFactory.html](https://dev.azure.com/ORBIS-AG-SAP/Modellfabrik/_wiki/wikis/Modellfabrik.wiki/8905/SmartFactory.html)


  
**Edge**: Favoriten öffnen → Favoriten verwalten → … → Favoriten importieren → `SmartFactory.html` auswählen.  
**Chrome**: Lesezeichen-Manager öffnen → … → Lesezeichen importieren → `SmartFactory.html` auswählen.
  
Nach dem Import ist der Ordner **SmartFactory** mit **OSF-RPi**, **OSF-LH**, **MES**, **DSP**, **fischertechnik** und **Dev** sichtbar.
  
## 2) OBS in 4 Schritten
  
1. OBS starten und die Scene Collection **osf-camera** öffnen.
2. Die **Konftel-20** als Kameraquelle wählen und das Kamerabild prüfen.
3. Über die Kameraquelle einen **Windowed Projector (Preview)** öffnen.
4. Zwei Preview-Fenster offen lassen: eins auf **Desktop 1**, eins später auf **Desktop 3**.
  
## 3) Setup in 7 Schritten
  
1. **Shopfloor aktivieren:** APS auf RPi, OSF auf RPi (`192.168.0.100:8080`), DSP-Edge starten.
2. **Konftel-20** per USB anschließen und Presets bereitlegen.
3. **Edge**, **Chrome** und **Edge InPrivate** starten; Browser-Zoom setzen und Tab-Gruppen öffnen.
4. Fenster auf die Desktops verteilen.
5. Fenster innerhalb der Desktops anordnen.
6. OBS-Preview-Fenster platzieren: eins auf Desktop 1, eins auf Desktop 3.
7. Kurztest: Desktop-Wechsel und Konftel-Presets durchschalten.
  
## 4) ShortCuts
  
**Virtuelle Desktops**
  
| Aktion | Tastenkürzel |
|--------|--------------|
| Desktop wechseln | **`Win + Ctrl + ←`** / **`Win + Ctrl + →`** |
| Aktives Fenster verschieben | Fenster fokussieren → **`Win + Ctrl + ←`** / **`Win + Ctrl + →`** |
| Task View öffnen | **`Win + Tab`** |
| Neuen Desktop anlegen | **`Win + Ctrl + D`** |
| Desktop schließen | **`Win + Ctrl + F4`** |
  
**Fenster anordnen**
  
| Aktion | Tastenkürzel |
|--------|--------------|
| Vollbild | **`Win + ↑`** |
| Fenster wiederherstellen | **`Win + ↓`** |
| Linke / rechte Bildschirmhälfte | **`Win + ←`** / **`Win + →`** |
| Browser-Zoom 100 % | **`Strg + 0`** |
| Browser-Zoom anpassen | **`Strg + +`**, **`Strg + -`**, **`Strg + Mausrad`** |
  
**Konftel-20**
  
| Aktion | Fernbedienung |
|--------|----------------|
| Preset abrufen / speichern | **`PRESET`** + Ziffer **0…6** |
  
Pflicht-Test: **`0 → 1 → 2 → 3 → 4 → 5 → 6 → 0`** in der OBS-Preview.
  
## 5) Tab-Gruppen und Zoom
  
- **OSF-RPi**: Live-Präsentation
- **MES**: Supervisor, PLT und MES-Ansicht
- **DSP**: DSP Management Cockpit, DSP Edge und Grafana
  
Zoom:
  
- **Desktop 2:** Edge **100 %**, UC-Diagramm **100 %**
- **Desktop 3:** Chrome **80 %**, DSP-Diagramm **100 %**
  
## 6) Zuordnung der Desktops
  
| Desktop | Inhalt |
|---------|--------|
| **1** | OBS-Steuerung, beide Camera-Preview-Fenster, VS Code, Teams optional |
| **2** | Edge mit Tab-Gruppe **OSF-RPi** |
| **3** | Chrome für DSP/Hero, Edge InPrivate für Digital Twin, zweites OBS-Preview |
  
