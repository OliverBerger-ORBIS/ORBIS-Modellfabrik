# Windows Präsentations-Setup – Desktops + Teams + OBS

Reproduzierbares Demo-Setup: **virtuelle Windows-Desktops**, **OBS nur für Kamera**, OSF-UI mit **Landscape/Hero-Profilen** (ab v1.1.8).

**Index:** [presentation/README.md](./README.md) · **Entscheidung:** [DR-29](../../03-decision-records/29-windows-desktops-presentation-without-fancyzones.md)

---

## Kurzüberblick

| Desktop | Rolle | Browser | Browser-Zoom | OSF-Diagramm | Inhalt |
|--------|--------|---------|--------------|--------------|--------|
| **1** | Working | — | — | — | OBS-Preview, Steuerung, VS Code, Teams optional |
| **2** | Landscape Fullscreen | **Edge** | **100 %** | UC **100 %** | Use-Cases UC-00…07 (Sidebar eingeklappt) |
| **3** | Hero | **Chrome** | **80 %** | DSP **100 %** | DSP → Accordion **Architektur**; Edge InPrivate Digital Twin; Kamera-Preview |

**Semantik OSF-Diagramm-Zoom:** 100 % = maximaler Fit ohne Scroll im Diagrammbereich (nicht literal 1920 px Canvas).

---

## External Links (OSF Settings ↔ Tab-Gruppen)

Quelle der Wahrheit für Klick-Ziele im **DSP-Architektur-Diagramm:**  
`osf/apps/osf-ui/public/assets/config/external-links.json` (Settings → **Export JSON** → deployen auf RPi).

| Feld (Settings) | Tab-Name (Empfehlung) | URL (MD1, Stand 14.07.2026) |
|-----------------|----------------------|-----------------------------|
| BP-Planning | **PT MD1** | `https://md1.orbis.de/sap/bc/ui5_ui5/omes/pt/index.html?sap-client=100&sap-ui-language=DE&sap-ui-xx-devmode=true#/OrderManagement/1010/SMARTFACTORY` |
| BP-MES | **MES MD1** | `https://md1.orbis.de/orbis(bD1kZSZjPTEwMA==)/web_mes/webviewer/index.htm#mppservice=orbis/mes&mpptimeout=60000&defaultlang=EN&maskid=ffb6098113c549bda9192b793dbb75ab&viewermenue=true&extensions=[%22controlinfo%22]&LAYOUT=LIGHT&Werk=1010` |
| BP-Supervisor | **SV MD1** (Supervisor) | `https://md1.orbis.de/sap/bc/ui5_ui5/omes/supervisor/index.html#/operation/1003442,0020,0` |
| BP-Analytics | **Grafana** | `http://192.168.0.201:3000/dashboards` (läuft auf **DSP-Edge-Knoten**, nicht RPi) |
| DSP Edge | *(Diagramm-Klick)* | **`TBD`** — ORBIS **DSP Edge** auf `192.168.0.201` (SSH `dsp-agent@192.168.0.201`); **≠ OSF-UI** (`192.168.0.100:8080`) |
| DSP SmartFactory | *(Diagramm-Klick)* | intern `/dsp-action` (OSF-UI auf RPi) |
| DSP Management Cockpit | *(Diagramm-Klick)* | `https://dspmcorbisprd.powerappsportals.com` |
| BP-ERP | *(Diagramm-Klick)* | intern `process` (OSF Process-Tab) |

**Hinweise**

- **MES CARD-ID:** Im MES-Viewer muss bei CARD-ID ein **Punkt (`.`)** eingegeben werden (ORBIS-Praxis).
- **Supervisor:** Operations-ID in der URL kann sich ändern — Feld **`bpSupervisorApplicationUrl`** in Settings/JSON anpassen.
- **Replay (localhost):** gleiche MD1-Links; OSF-URLs siehe Tab-Gruppe **OSF-LH** unten.

### Drei getrennte Systeme (nicht verwechseln)

| System | Host (FT-/ORBIS-LAN) | Rolle | Präsentations-Tab |
|--------|----------------------|-------|-------------------|
| **OSF-UI** | `192.168.0.100:8080` | Shopfloor-Dashboard (Angular), MQTT/CCU-Anbindung | Tab-Gruppe **OSF-RPi** / **OSF-LH** |
| **DSP Edge** | `192.168.0.201` (SSH `dsp-agent`) | ORBIS-Produkt Edge-Runtime — **eigenes System** | **`dspEdgeUrl`** in Settings — **HTTP-URL noch klären** |
| **Grafana / Persistence** | `192.168.0.201:3000` | Analytics auf dem Edge-Knoten ([DR-28](../../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) | Tab **Grafana** |

**`dspEdgeUrl`:** Im Repo derzeit **leer** (`""`), bis vor Ort die HTTP-Oberfläche des DSP Edge (Port/Pfad) verifiziert ist. Frühere Werte waren falsch: Marketing-URL (`main`) bzw. fälschlich OSF-UI (`:8080/de/dsp`).

**Vor Ort prüfen (wenn im ORBIS-Netz):** `ssh dsp-agent@192.168.0.201` → welche Ports/UI? Ergebnis in Settings → Export JSON → deployen.

---

## Tab-Gruppen & Favoriten (Edge + Chrome)

Zwei **Favoritenordner** anlegen (in **Edge** und **Chrome** jeweils):

### Ordner `OSF-RPi` (Live / Normal-Modus, Desktop 2 Edge)

| Tab | URL |
|-----|-----|
| OSF Dashboard | `http://192.168.0.100:8080/de/dsp` |
| OSF Use Cases | `http://192.168.0.100:8080/de/dsp/use-case` |
| OSF Presentation (Digital Twin) | `http://192.168.0.100:8080/de/presentation` |
| PT MD1 | siehe Tabelle External Links |
| MES MD1 | siehe Tabelle External Links |
| SV MD1 Supervisor | siehe Tabelle External Links |
| Grafana | `http://192.168.0.201:3000/dashboards` |
| *(optional)* DSP Edge UI | Settings **`dspEdgeUrl`** — **TBD** vor Ort klären |

**Edge Desktop 2:** Tab-Gruppe **OSF-RPi** im Vollbild; Start-Tab typisch Use-Case oder DSP.

### Ordner `OSF-LH` (Replay / localhost, Desktop 2 oder Dev)

| Tab | URL |
|-----|-----|
| OSF Dashboard | `http://localhost:4200/de/dsp` |
| OSF Use Cases | `http://localhost:4200/de/dsp/use-case` |
| OSF Presentation | `http://localhost:4200/de/presentation` |
| PT MD1 / MES MD1 / SV MD1 | identisch zu **OSF-RPi** (MD1-Server) |

### Desktop 3 (Hero) — Chrome

| Fenster | Browser | Tab / Inhalt |
|---------|---------|--------------|
| Hero links | Chrome | Tab-Gruppe oder einzelner Tab: `http://192.168.0.100:8080/de/dsp` (Browser-Zoom **80 %**) |
| Digital Twin oben rechts | Edge **InPrivate** | `http://192.168.0.100:8080/de/presentation` |
| Kamera unten rechts | OBS Projector Preview | siehe Konftel-Abschnitt unten |

### Tab-Gruppen anlegen (Edge / Chrome)

1. Tabs der jeweiligen Gruppe öffnen (URLs aus Tabellen oben).
2. Rechtsklick auf einen Tab → **Zu neuer Gruppe hinzufügen** / **Add tab to new group**.
3. Gruppe benennen: `OSF-RPi` bzw. `OSF-LH`.
4. Farbe wählen (z. B. Blau = RPi, Grün = LH).
5. Browser: **Beim Start vorherige Sitzung fortsetzen** aktivieren.

### Favoriten exportieren (Übergabe an Kollegen)

| Browser | Export |
|---------|--------|
| **Edge** | `…` → **Favoriten** → **Favoriten verwalten** → **…** → **Favoriten exportieren** → HTML-Datei |
| **Chrome** | **Lesezeichen-Manager** (`Strg+Umschalt+O`) → **⋮** → **Lesezeichen exportieren** → HTML-Datei |

Kollegen: Import über dieselben Menüs (**Favoriten importieren** / **Lesezeichen importieren**). Tab-Gruppen müssen einmalig manuell aus den Favoriten-Tabs neu gruppiert werden (Export enthält keine Gruppen-Metadaten).

**OSF External Links (RPi):** Settings → External links → **Export JSON** → Datei ins Repo unter `public/assets/config/external-links.json` → Deploy ([rpi-deployment.md](../deployment/rpi-deployment.md)).

---

## Runbook (Schrittfolge)

### 1) Modus wählen

- [ ] **Normal (Live):** APS + OSF auf RPi (`192.168.0.100:8080`); Tab-Gruppe **OSF-RPi**
- [ ] **Replay:** Mosquitto-Bridge + OSF lokal:
  - `.\scripts\start-mosquitto-ws-bridge.ps1`
  - `.\scripts\run-osf.ps1` (oder `npm run serve:osf-ui`)
  - Tab-Gruppe **OSF-LH**
- [ ] Erst wenn OSF läuft, Browser-Tabs öffnen

### 2) Desktop 1 — Working starten

- [ ] OBS (Scene Collection `osf-camera`); Kamera **vor** OBS-Start per USB verbinden
- [ ] Kameraquelle: Normal = `scn-01_Konftel-Cam20`, Replay = `scn-02_laptop-cam`
- [ ] Zwei **Camera Preview**-Projektoren (Fenster) öffnen
- [ ] Edge + Chrome starten; Teams optional

### 3) Fenster auf Desktops verteilen (`Win + Tab`)

- [ ] Desktop 1: OBS-Preview + Steuerung + VS Code
- [ ] Desktop 2: Edge Vollbild (Tab-Gruppe **OSF-RPi** oder **OSF-LH**)
- [ ] Desktop 3: Chrome Hero + Edge InPrivate (Digital Twin) + OBS-Preview (Kamera)

### 4) Zoom & Layout prüfen

- [ ] Desktop 2: Browser **100 %**, UC-Diagramm **100 %** (↺ Reset falls alter `sessionStorage`-Zoom)
- [ ] Desktop 3 Chrome: Browser **80 %**, DSP-Architektur **100 %**, Accordion **Architektur** geöffnet
- [ ] Sidebar auf UC-Routen eingeklappt (Toggle `⟩` zum Aufklappen)
- [ ] Konftel/OBS: Verzerrungs-Check (siehe unten)

### 5) Navigation testen

- [ ] `Win + Ctrl + ←/→` zwischen Desktop 1/2/3 — Zoom und Fensterpositionen stabil

### 6) Optional: Teams

- [ ] Präsentationsmonitor teilen; Aufnahme Teams oder Snipping Tool

---

## Konftel-20 & OBS (Kamera)

> Validiert 09.07.2026 vor Ort bei ORBIS

**OBS Transform (Kamera-Quelle):**

- Resolution: **Device Default**
- Bounding Box: **Scale to inner bounds (FIT)**, **1920 × 1080**
- Crop: Top/Bottom **10**, Left/Right **120**

**Presets (Fernbedienung):** `PRESET` + Ziffer speichern / Ziffer abrufen

| Preset | Ziel |
|--------|------|
| 0 | Gesamtansicht |
| 1 | DRILL |
| 2 | HBW |
| 3 | MILL |
| 4 | AIQS |
| 5 | DPS |
| 6 | CHRG |

**Pflicht-Test:** `0 → 1 → 2 → 3 → 4 → 5 → 6 → 0` in OBS-Preview (Desktop 1 + 3).

---

## Fallbacks

**Kein Konftel-20:** Built-in-Kamera, gleiche OBS-Transform-Werte zuerst, dann Verzerrungs-Check.

**Kein zweiter Monitor:** Desktops 1–3 auf einem Display; Monitor duplizieren.

**Teams-Aufzeichnung problematisch:** Windows Snipping Tool (Screen Recording).

---

## HTML-Export (Drucken / PDF)

Standalone-HTML für Browser-Druck (`Cmd+P` / `Strg+P`):

```bash
bash scripts/export-presentation-checklist-html.sh
```

Erzeugt: `docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.html` — lokal öffnen, **Drucken** oder **Als PDF speichern**. Kein Internet nötig (kein Mermaid). Footer wird beim Druck ausgeblendet.
