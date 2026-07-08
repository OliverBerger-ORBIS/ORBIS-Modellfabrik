# Decision Record: Windows-Praesentation ueber virtuelle Desktops (ohne FancyZones, OBS nur Kamera)

**Datum:** 2026-07-08  
**Status:** Accepted  
**Kontext:** Der bisherige Praesentationspfad mit FancyZones/PowerToys und teils OBS-basierter Layoutlogik war im Betrieb nicht robust genug. FancyZones-Layouts wurden zwischen Desktops inkonsistent uebernommen, und der Aufbau war fuer wiederholbare Demo-Sessions zu fehleranfaellig. Ziel war ein schlanker, reproduzierbarer Operator-Workflow nach Windows-Neustart mit moeglichst wenigen beweglichen Teilen.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird -> [README - Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

1. **Praesentationslayout erfolgt ausschliesslich ueber Windows-Bordmittel (virtuelle Desktops).**  
   Es wird **kein FancyZones/PowerToys** mehr als Pflichtbestandteil genutzt.

2. **OBS wird nur fuer Kamera verwendet.**  
   Keine OBS-basierte Praesentationskomposition/Window-Capture-Logik. OBS liefert nur Kameraquelle + Preview-Fenster.

3. **Desktop-Modell ist verbindlich:**
   - Desktop 1: `Working` (Steuerung, OBS, VS Code)
   - Desktop 2: `Fullscreen` (Edge)
   - Desktop 3: `Hero` (Chrome + Edge InPrivate Digital Twin + Kamera-Preview)

4. **Navigation waehrend Demo erfolgt ueber `WIN + Ctrl + ←/→`.**

5. **Replay-Start bleibt skriptbasiert fuer Kernkomponenten:**
   - `scripts/start-mosquitto-ws-bridge.ps1`
   - `scripts/run-osf.ps1` (oder `npm run serve:osf-ui`)

---

## Alternativen

- **FancyZones/PowerToys als Pflicht-Layoutsteuerung:** verworfen wegen instabiler/inkonsistenter Layout-Uebernahme zwischen Desktops.
- **OBS als zentraler Praesentations-Orchestrator:** verworfen wegen erhoehter Komplexitaet und geringerer Reproduzierbarkeit.
- **Vollautomatischer Start inkl. Desktop-Window-Placement:** verworfen, da Windows Virtual Desktops keine stabile, verlassliche API fuer dieses Placement bereitstellen.

---

## Konsequenzen

- **Positiv:**
  - Klarer, kurzer Operator-Workflow (6 Aktionen)
  - Weniger Fehlerquellen durch Wegfall von FancyZones- und OBS-Layoutlogik
  - Nach Neustart reproduzierbar testbar

- **Negativ:**
  - Teilweise manuelle Fensterverteilung bleibt notwendig
  - Zoom/Groesseneinstellungen muessen vor Demo kurz geprueft werden

- **Risiken:**
  - Kamera-Feintuning (Konftel) ist hardwareabhaengig und muss vor Ort final validiert werden

---

## Implementierung (Soll/Status)

- [x] Setup-Doku auf Desktop-Workflow umgestellt (`windows-desktops-teams-obs-setup-checklist.md`)
- [x] FancyZones- und OBS-Praesentationsbezug aus dem operativen Ablauf entfernt
- [x] Replay-Startkommandos in den Operator-Ablauf integriert
- [x] Nicht mehr benoetigte Praesentations-Automationsskripte entfernt
- [ ] Konftel-Feineinstellung (Crop/Transform/Resolution) vor Ort bei ORBIS final nachpflegen

---
*Entscheidung getroffen von: Team OSF / ORBIS SmartFactory*
