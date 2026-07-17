# Windows Präsentations-Setup – Desktops + Teams + OBS

Reproduzierbares Demo-Setup: **virtuelle Windows-Desktops**, **OBS nur für Kamera**, OSF-UI mit **Landscape/Hero-Profilen** (ab v1.1.8).

**Index:** [presentation/README.md](./README.md) · **Entscheidung:** [DR-29](../../03-decision-records/29-windows-desktops-presentation-without-fancyzones.md)

---

## Voraussetzungen

- [ ] **SmartFactory-Lesezeichen** in **Edge** und **Chrome** importiert ([Anhang Bookmarks](#anhang-smartfactory-bookmarks)).
- [ ] Favoritenordner **SmartFactory** mit Unterordnern (**OSF-RPi**, **OSF-LH**, **MES**, **DSP**, …) in beiden Browsern.
- [ ] OSF **External Links** auf dem RPi aktuell ([Deploy](../deployment/rpi-deployment.md)) — Details: [External Links](#external-links-osf-settings--tab-gruppen).
- [ ] Bei Beamer/Zweitmonitor: **Anzeige duplizieren** (`Win + P`) — siehe [Anzeige](#anzeige-beamer--monitor).

---

## Desktops – Kurzüberblick

| Desktop | Rolle | Browser | Browser-Zoom | OSF-Diagramm | Inhalt |
|--------|--------|---------|--------------|--------------|--------|
| **1** | Working | — | — | — | OBS-Preview, Steuerung, VS Code, Teams optional |
| **2** | Landscape Fullscreen | **Edge** | **100 %** | UC **100 %** | Use-Cases UC-00…07 (Sidebar eingeklappt) |
| **3** | Hero | **Chrome** | **80 %** | DSP **100 %** | DSP Architektur; Edge InPrivate Digital Twin; Kamera-Preview |

**Semantik OSF-Diagramm-Zoom:** 100 % = maximaler Fit ohne Scroll (nicht literal 1920 px Canvas).

### Anzeige (Beamer / Monitor)

Mit **virtuellen Desktops** (1–3) ist **Anzeige duplizieren** die einfachere Einstellung — **besser als „Erweitern“**: Laptop und Beamer zeigen dasselbe Bild; Desktop-Wechsel (`Win + Ctrl + ←/→`) bleibt nachvollziehbar.

| Einstellung | Empfehlung |
|-------------|------------|
| **Duplizieren** | ✅ Standard für Präsentation |
| **Erweitern** | Nur wenn bewusst zwei getrennte physische Arbeitsflächen nötig |

**Schnellwahl:** **`Win + P`** → **Duplizieren** (engl. *Duplicate*).

Alternativ: **Einstellungen** → **System** → **Anzeige** → **Mehrere Anzeigen** → **Duplizieren**.

---

## Live-Ablauf (Operator-Checkliste)

Reihenfolge vor der Demo am Shopfloor. Details → spätere Kapitel (Links in Klammern).

| # | Schritt | Check |
|---|---------|-------|
| **1** | **Shopfloor aktiv:** APS auf RPi, OSF auf RPi (`192.168.0.100:8080`), **DSP-Edge** — Strom/Netzwerk an | [ ] |
| **2** | **Konftel-20** per USB angeschlossen; Presets auf der Fernbedienung eingerichtet | [ ] → [Konftel-20 & OBS](#konftel-20--obs-kamera) |
| **3** | **OBS** starten (Scene Collection `osf-camera`); Kameraquelle erkannt; **zwei Camera-Preview-Fenster** (bleiben auf Desktop 1) | [ ] → [OBS-Einrichtung](#konftel-20--obs-kamera) |
| **4** | **Edge**, **Chrome** und **Edge InPrivate** starten; **Browser-Zoom** setzen; Tab-Gruppen **OSF-RPi**, **MES**, **DSP** öffnen | [ ] → [Tab-Gruppen](#tab-gruppen-live--replay), [Browser-Zoom & Layout](#browser-zoom--layout-desktop-23) |
| **5** | **Fenster auf Desktops verteilen** (Tastenkürzel unten) | [ ] |
| **6** | **Fenster innerhalb der Desktops anordnen** (Vollbild / Hero-Layout) | [ ] → [Browser-Zoom & Layout](#browser-zoom--layout-desktop-23) |
| **7** | **Kurztest:** Desktop-Wechsel; ggf. Konftel-Presets `0→1→…→6→0` | [ ] |

### Tastaturkürzel – virtuelle Desktops

| Aktion | Tastenkürzel |
|--------|----------------|
| **Desktop wechseln** (1 ↔ 2 ↔ 3) | **`Win + Ctrl + ←`** / **`Win + Ctrl + →`** |
| **Aktives Fenster auf anderen Desktop verschieben** | Fenster fokussieren → **`Win + Ctrl + ←`** / **`Win + Ctrl + →`** |
| **Task View** (Desktops + Fenster per Drag) | **`Win + Tab`** — Fenster auf Desktop-Thumbnails oben ziehen |
| Neuen Desktop anlegen | `Win + Ctrl + D` |
| Desktop schließen | `Win + Ctrl + F4` |

**Schritt 5 – Verteilen (Ziel):**

| Desktop | Fenster |
|---------|---------|
| **1** | OBS (Steuerung) + **beide** Camera-Preview-Fenster, VS Code, Teams optional |
| **2** | **Edge** mit Tab-Gruppe **OSF-RPi** (Vollbild) |
| **3** | **Chrome** (Hero/DSP), **Edge InPrivate** (Digital Twin), **zweites** OBS-Preview (Kamera) |

→ Fenster fokussieren, mit **`Win + Ctrl + ←/→`** auf Ziel-Desktop schieben; mit **`Win + Ctrl + ←/→`** prüfen, ob alles auf dem richtigen Desktop liegt.

### Tastaturkürzel – Fenster anordnen (Schritt 6)

| Aktion | Tastenkürzel |
|--------|----------------|
| Vollbild | **`Win + ↑`** |
| Fenster wiederherstellen | **`Win + ↓`** |
| Linke / rechte Bildschirmhälfte | **`Win + ←`** / **`Win + →`** |
| Browser-Zoom | **`Strg + 0`** (100 %), **`Strg + +`** / **`Strg + -`**, **`Strg + Mausrad`** |

Desktop **2:** Edge **`Win + ↑`** (Vollbild). Desktop **3:** Hero-Anordnung manuell oder per Snap — siehe [Browser-Zoom & Layout](#browser-zoom--layout-desktop-23).

### Tastaturkürzel – Konftel (Schritt 7)

| Aktion | Fernbedienung |
|--------|----------------|
| Preset speichern / abrufen | **`PRESET`** + Ziffer **0…6** |

Pflicht-Test: **`0 → 1 → 2 → 3 → 4 → 5 → 6 → 0`** in OBS-Preview (Desktop 1 und 3).

---

## Replay (Kurz)

Statt Schritt 1 (Shopfloor live): Mosquitto-Bridge + OSF lokal starten; Tab-Gruppe **OSF-LH** statt OSF-RPi; MES/DSP entfallen meist.

```powershell
.\scripts\start-mosquitto-ws-bridge.ps1
.\scripts\run-osf.ps1   # oder: npm run serve:osf-ui
```

→ [Tab-Gruppen – Replay](#replay-tab-gruppen)

---

## Tab-Gruppen (Live / Replay)

**Edge** und **Chrome:** Rechtsklick auf Unterordner unter **SmartFactory** → **Alle Tabs in Tabgruppe öffnen**.

| Modus | Tab-Gruppen (typisch) |
|-------|----------------------|
| **Live** | **OSF-RPi**, **MES**, **DSP** |
| **Live (lokal)** | **OSF-LH** statt OSF-RPi; optional MES/DSP |
| **Replay** | **OSF-LH** |

1. **SmartFactory** → **OSF-RPi** → **Alle Tabs in Tabgruppe öffnen**
2. **SmartFactory** → **MES** → **Alle Tabs in Tabgruppe öffnen**
3. **SmartFactory** → **DSP** → **Alle Tabs in Tabgruppe öffnen**
4. Browser: **Beim Start vorherige Sitzung fortsetzen** (Edge/Chrome)

### Replay – Tab-Gruppen

**SmartFactory** → **OSF-LH** → **Alle Tabs in Tabgruppe öffnen**

### Referenz-URLs (OSF)

| Tab | OSF-RPi (Live) | OSF-LH (Replay / lokal) |
|-----|----------------|-------------------------|
| OSF Dashboard | `http://192.168.0.100:8080/de/dsp` | `http://localhost:4200/de/dsp` |
| Track & Trace | `http://192.168.0.100:8080/de/dsp/use-case/track-trace?tab=live` | `http://localhost:4200/de/dsp/use-case/track-trace?tab=live` |
| Presentation (Digital Twin) | `http://192.168.0.100:8080/de/presentation` | `http://localhost:4200/de/presentation` |

MD1-URLs: [External Links](#external-links-osf-settings--tab-gruppen).

---

## Browser-Zoom & Layout (Desktop 2/3)

### Desktop 2 (Edge, Landscape)

- [ ] Browser-Zoom **100 %** (`Strg + 0`)
- [ ] UC-Diagramm **100 %** (↺ Reset in OSF, falls alter `sessionStorage`-Zoom)
- [ ] Sidebar auf UC-Routen **eingeklappt** (Toggle `⟩`)

### Desktop 3 (Hero)

| Fenster | Browser | Inhalt | Zoom |
|---------|---------|--------|------|
| Hero links | **Chrome** | DSP (`/de/dsp`), Accordion **Architektur** | Browser **80 %**, Diagramm **100 %** |
| Oben rechts | **Edge InPrivate** | `…/de/presentation` (Digital Twin) | — |
| Unten rechts | OBS Preview | Kamera (zweites Preview-Fenster von Schritt 3) | — |

Replay: RPi-URLs durch `localhost:4200` ersetzen.

---

## External Links (OSF Settings ↔ Tab-Gruppen)

Quelle: `osf/apps/osf-ui/public/assets/config/external-links.json` (Settings → **Export JSON** → deployen auf RPi).

| Feld (Settings) | Tab-Name | URL (MD1, Stand 14.07.2026) |
|-----------------|----------|-----------------------------|
| BP-Planning | **PT MD1** | `https://md1.orbis.de/sap/bc/ui5_ui5/omes/pt/index.html?sap-client=100&sap-ui-language=DE&sap-ui-xx-devmode=true#/OrderManagement/1010/SMARTFACTORY` |
| BP-MES | **MES MD1** | `https://md1.orbis.de/orbis(bD1kZSZjPTEwMA==)/web_mes/webviewer/index.htm#mppservice=orbis/mes&mpptimeout=60000&defaultlang=EN&maskid=ffb6098113c549bda9192b793dbb75ab&viewermenue=true&extensions=[%22controlinfo%22]&LAYOUT=LIGHT&Werk=1010` |
| BP-Supervisor | **SV MD1** | `https://md1.orbis.de/sap/bc/ui5_ui5/omes/supervisor/index.html#/operation/1003442,0020,0` |
| BP-Analytics | **Grafana** | `http://192.168.0.201:3000/dashboards` |
| DSP Edge | *(Diagramm)* | `https://192.168.0.200:8006` (Proxmox; VE/Runtime `.201`) — **≠ OSF-UI** |
| DSP Management Cockpit | *(Diagramm)* | `https://dspmcorbisprd.powerappsportals.com` |

**Hinweise:** MES CARD-ID mit **Punkt (`.`)**; Supervisor-URL ggf. in Settings anpassen.

### Drei Systeme (nicht verwechseln)

| System | Host | Tab-Gruppe / Tab |
|--------|------|-----------------|
| **OSF-UI** | `192.168.0.100:8080` | **OSF-RPi** / **OSF-LH** |
| **DSP Edge** | `192.168.0.200:8006` (Proxmox) | `dspEdgeUrl` — VE `.201` für SSH/SQL/Grafana |
| **Grafana** | `192.168.0.201:3000` | Tab in **DSP** |

**Deploy External Links:** Settings → Export JSON → [rpi-deployment.md](../deployment/rpi-deployment.md).

---

## Konftel-20 & OBS (Kamera)

> Validiert 09.07.2026 vor Ort bei ORBIS · Ergänzend: [obs-video-presentation-setup.md](./obs-video-presentation-setup.md)

**Vor OBS-Start:** Konftel-20 per USB verbinden.

| Modus | OBS-Kameraquelle |
|-------|------------------|
| Live (Normal) | `scn-01_Konftel-Cam20` |
| Replay | `scn-02_laptop-cam` |

**Zwei Preview-Fenster:** OBS → Rechtsklick Kameraquelle → **Windowed Projector (Preview)** — ein Fenster bleibt auf Desktop 1, das zweite wird später auf Desktop 3 gelegt (Schritt 5/6).

**OBS Transform (Kamera-Quelle):**

- Resolution: **Device Default**
- Bounding Box: **Scale to inner bounds (FIT)**, **1920 × 1080**
- Crop: Top/Bottom **10**, Left/Right **120**

**Presets (Fernbedienung):**

| Preset | Ziel |
|--------|------|
| 0 | Gesamtansicht |
| 1 | DRILL |
| 2 | HBW |
| 3 | MILL |
| 4 | AIQS |
| 5 | DPS |
| 6 | CHRG |

---

## Fallbacks

**Kein Konftel-20:** Built-in-Kamera, gleiche OBS-Transform-Werte, Verzerrungs-Check.

**Kein zweiter Monitor / nur Laptop:** Virtuelle Desktops 1–3 auf einem Display; optional Beamer per **Duplizieren** (siehe [Anzeige](#anzeige-beamer--monitor)).

**Teams-Aufzeichnung problematisch:** Windows Snipping Tool (Screen Recording).

---

## Anhang: SmartFactory Bookmarks

Einmalige Einrichtung in **Edge** und **Chrome**.

**Import:** [bookmarks/SmartFactory.html](./bookmarks/SmartFactory.html) — legt Ordner **SmartFactory** mit **OSF-RPi**, **OSF-LH**, **MES**, **DSP**, **fischertechnik**, **Dev** an.

| Browser | Import |
|---------|--------|
| **Edge** | **Favoriten verwalten** → **…** → **Favoriten importieren** |
| **Chrome** | **Lesezeichen-Manager** (`Strg + Umschalt + O`) → **⋮** → **Lesezeichen importieren** |

Tab-Gruppen: Unterordner → **Alle Tabs in Tabgruppe öffnen** ([Tab-Gruppen](#tab-gruppen-live--replay)).


