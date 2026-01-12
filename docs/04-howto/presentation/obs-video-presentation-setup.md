# OBS Setup: ORBIS SmartFactory (OSF) Präsentation

Diese Anleitung beschreibt das standardisierte Setup für OSF-Präsentationen mittels OBS Studio. Ziel ist eine einheitliche, vereinfachte Struktur ohne Overengineering.

## 🎯 Konzept & Layout
Das Setup nutzt verschiedene Browser, um OBS die Unterscheidung der Fenster zu erleichtern. Die Hauptszene („Hero +2“) kombiniert die wichtigsten Ansichten.

- **Auflösung:** 
  - Standard-Fenster (Edge, Firefox): **1920x1080**
  - Hero-Fenster (Chrome): **1040x1080** (nutzen Sie die Resizer-Einstellung `S6_Hero`)
- **Bedienung:** Der Präsentator steuert primär den **Chrome-Browser** (Hero).
- **Multiview:** Die ersten 4 Szenen (S1-S4) sind für die Multiview-Übersicht optimiert.

---

## 1. Szenen & Quellen (Scenes & Sources)

### Die Basis-Quellen (Browser & Kamera)
Bitte starten Sie diese Anwendungen **vor** OBS:

| Anwendung | Browser-Wahl | Zweck | Tabs | OBS Source Name |
| :--- | :--- | :--- | :--- | :--- |
| **Hero + 2** | Chrome | Aktive Steuerung (Hero) | ~8 (Alle Demo-relevante) | `chrome_hero` |
| **Digital Twin** | Firefox | Shopfloor/Ansicht | 1 (`de/presentation`) | `firefox_presentation` |
| **OSF Secondary** | Edge (Standard) | Vollbild-Fallback / Übersicht | 8 | `msedge_osf` |
| **OSF Orders** | Edge (InPrivate) | Auftragseingang/Logistik | 1+ | `msedge_priv_orders` |
| **Kamera** | - | fabrik Video | - | `cam_usb` |

> **Hinweis:** Durch die unterschiedlichen Browser/Profile kann OBS die Fenster eindeutig zuordnen.

---

### Die Szenen-Struktur (Reihenfolge einhalten!)

Legen Sie die Szenen exakt in dieser Reihenfolge an, damit der Multiview (Ansicht -> Multiview) logisch aufgebaut ist.

#### 1) S1: OSF-Main
- **Inhalt:** `msedge_osf` (Window Capture)
- **Beschreibung:** Edge mit 8 Tabs. Dient als Backup oder Detailansicht.

#### 2) S2: Digit-Twin
- **Inhalt:** `firefox_presentation` (Window Capture)
- **Beschreibung:** Firefox mit Digital Twin.

#### 3) S3: OSF-Orders
- **Inhalt:** `msedge_priv_orders` (Window Capture)
- **Beschreibung:** Edge Private. Zeigt eingehende Bestellungen.

#### 4) S4: Camera Vollbild
- **Inhalt:** `cam_usb` (Video Capture Device)
- **Beschreibung:** Vollbild-Kamera mit Abb der Fabrik.

---

#### 5) S5: Hero +2 (Haupt-Präsentations-Szene)
Dies ist die **Master-Szene**, die während der Präsentation hauptsächlich gezeigt wird. Sie komponiert Inhalte aus den anderen Szenen.
- **Layout:**
  - **Hintergrund:** Dezent/Branding.
  - **Hauptbereich (Links):** Szene `S6: Hero OSF` (Zoom ca. 66%).
  - **Seitenleiste (Rechts Oben):** Szene `S2: Digit-Twin`.
  - **Seitenleiste (Rechts Unten):** Szene `S4: Camera`.
- **Wichtig:** Das Hero-Element (`S6`) muss so skaliert werden, dass es optimal in das Layout passt.

#### 6) S6: Hero-OSF (Container)
- **Inhalt:** `chrome_hero` (Window Capture)
- **Beschreibung:** Roh-Input des Chrome-Browsers.
- **Funktion:** Dient als Quellexport für S5. Hier kann das Bild bei Bedarf zugeschnitten (Cropping) werden, ohne S5 zu zerstören.

#### 7) S7: Hold-Slate
- **Inhalt:** Image Source (z.B. `holding-slate.png` oder Logo).
- **Beschreibung:** "Gleich geht es los" / Pause-Screen.

---

## 2. Vorbereitung & Ablauf (Checkliste)

### Vorbereitung (ca. 10 Min vor Termin)
1. [ ] **Fenster anordnen:** 
   - Edge & Firefox auf **1920x1080** skalieren.
   - Chrome (Hero) über Resizer auf **`Se_Hero` (1040x1080)** einstellen.
2. [ ] **Tabs & Szenen laden (Wichtig!):**
   - Schalten Sie in OBS alle Szenen (S1-S6) einmal durch.
   - Klicken Sie in den Browsern (besonders Chrome Hero) **alle** für die Demo geplanten Tabs einmal an.
   - *Check:* Sidebar wegklicken, Umgebung auf "live" stellen, Logins prüfen.
3. [ ] **OBS starten:** Prüfen, ob alle Window-Captures greifen.
   - *Falls schwarz:* Eigenschaften der Source öffnen -> Fenstertitel neu auswählen.
4. [ ] **Zoom-Check (S5):** Prüfen, ob die Chrome-Ansicht (Hero) in der "Hero +2" Szene korrekt eingepasst ist (ggf. Zoom-Faktor ~66% prüfen).

### Während der Präsentation
1. **Start:** `S7 Hold-Slate` -> `S4 Camera Vollbild` (Intro).
2. **Demo:** Wechsel auf `S5 Hero +2`.
3. **Steuerung:** 
   - Der Präsentator arbeitet fast ausschließlich im **Chrome-Browser**.
   - OBS überträgt das komponierte Bild (S5), in dem der Zuschauer Chrome + Digital Twin + Fabrik sieht.
4. **Spezialfälle:** Bei Bedarf via Multiview direkt auf `S2` (nur 3D) oder `S3` (Orders) schalten.

---

## 3. Fehlerbehebung

- **Browser-Fenster schwarz im OBS?**
  - Stellen Sie "Capture Method" in den Source-Eigenschaften auf **Windows 10 (1903 and up)**.
  - Alternativ: Hardwarebeschleunigung im Browser deaktivieren.
- **Fenstergröße ändert sich?**
  - Nutzen Sie Tools wie *Sizer* oder *FancyZones*, um 1920x1080 exakt wiederherzustellen.
