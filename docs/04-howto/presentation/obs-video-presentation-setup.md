# OBS Setup: ORBIS SmartFactory (OSF) Präsentation

Diese Anleitung beschreibt den **vereinfachten Zielstandard** fuer Messe- und Videokonferenz-Setups.

Schneller Operator-Pfad (Checkliste):
- [Windows Präsentations-Setup – Desktops + Teams + OBS (Normal/Replay)](windows-desktops-teams-obs-setup-checklist.md)

## Geltender Standard (ab 06.05.2026)

- **OBS wird nur fuer die Kamera-Quelle verwendet** (Kamera aktiv, Kamera-Rotation).
- **Bildschirm-Layout wird nicht mehr in OBS gebaut**, sondern ueber **FancyZones**.
- **Shopfloor-Rotation erfolgt ueber OSF-UI-Settings**.
- **Konftel-20 Zoom-Szenen pro Station werden lokal gespeichert**.
- Dasselbe Setup gilt fuer **Praesentation vor Ort** und **Videokonferenzen**.

---

## Verworfen (nicht mehr verwenden)

Die frueheren OBS-Ansatze mit komplexer Szenen-Regie sind fuer den Regelbetrieb verworfen:

- Mehrere Browser-Captures als Hauptlogik in OBS (`S1..S7`, Hero+2 als OBS-Komposition)
- OBS-Multiview als zentraler Navigationspfad
- OBS als Orchestrator fuer gesamte Bildschirm-Layouts

Diese Ansatze sind zu fragil und zu fehleranfaellig fuer den produktiven Demo-Betrieb.

---

## 1) Zielarchitektur

### 1.1 OBS (nur Kamera)

- Eine Kamera-Quelle (`cam_usb`) als Video-Capture-Device
- Fallback erlaubt: Built-in-Laptop-Kamera, wenn Konftel-20 nicht angeschlossen ist
- Optional wenige Kamera-Szenen (z. B. `CAM_WIDE`, `CAM_STATION`, `CAM_DETAIL`) fuer schnelle Umschaltung
- Keine Browser-Window-Captures als Pflichtbestandteil der Hauptpraesentation
- Wichtig: **USB-Kamera immer anschliessen, bevor OBS geoeffnet wird** (sonst fehlerhafte oder fehlende Source-Zuordnung)

### 1.2 Desktop-Layout (FancyZones)

- **Desktop 1:** Fullscreen (Hauptansicht)
- **Desktop 2:** Hero + 2 (fester Split fuer parallele Ansichten)
- Fensterpositionierung und Groessen werden ueber FancyZones reproduzierbar gesetzt
- Der **Hero+2-Schnitt orientiert sich an der Kamera-Projektion**, sodass moeglichst keine schwarzen Bereiche entstehen
- Im Hero+2-Layout:
  - **oberhalb der Kamera:** Digital Twin (`dsp/en/presentation`) in **Firefox**
  - **restliche Flaeche:** Hero in **Chrome**

### 1.3 Applikationsrotation

- **Shopfloor-Rotation:** ueber OSF-UI-Settings
- **Kamera-Rotation:** ueber OBS-Szenen/Hotkeys

### 1.4 Konftel-20

- Zoom-Modus je Station als Szene/Presets auf dem Geraet speichern
- Abrufbar ohne Eingriff in die Demo-Pipeline

### 1.5 Konftel Preset-Matrix (verbindlich)

| Preset | Ziel |
|---|---|
| `0` | Gesamtansicht (moeglichst gross, ohne unnoetigen Rand) |
| `1` | DRILL |
| `2` | HBW |
| `3` | MILL |
| `4` | AIQS |
| `5` | DPS |
| `6` | CHRG |

Qualitaetskriterium fuer Preset `0`:
- Fabrik moeglichst gross im Bild
- keine unnoetigen schwarzen Randraeume
- stabil nutzbar als Start-/Rueckfallansicht

---

## 2) Checkliste vor Termin

1. [ ] FancyZones aktiv; Layouts `Desktop 1 = Fullscreen`, `Desktop 2 = Hero + 2` geladen
2. [ ] USB-Kamera angeschlossen, **danach** OBS starten; Kamera-Quelle sichtbar (`cam_usb`)
3. [ ] OSF-UI geoeffnet, Umgebung korrekt, noetige Tabs vorbereitet
4. [ ] OBS-Kamera-Rotation getestet (Wide/Station/Detail)
5. [ ] Shopfloor-Rotation ueber UI-Settings verifiziert
6. [ ] Konftel-20 Szenen je Station abrufbar
7. [ ] Bedienung geprueft: Desktop-Wechsel (`Win + Tab` oder schnell `Win + Ctrl + Left/Right`), Fenster-Wechsel (`Alt + Tab`)
8. [ ] Freigabemodus geprueft (Messe = Duplizieren, Videokonferenz = Erweitern)

---

## 2a) Kurzanleitung Presets (Konftel Remote)

- **Preset speichern:** Kamera ausrichten -> `PRESET` -> Ziffer (`0-9`)
- **Preset abrufen:** Ziffer (`0-9`) druecken
- **Preset loeschen:** `RESET` + Ziffer (`0-9`)
- **Mittelposition:** `HOME`

Empfehlung:
- Presets `0-6` nach obiger Matrix belegen
- nach jeder Aenderung kurz `0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 0` durchtesten

---

## 3) Ablauf waehrend Praesentation

1. Start in Fullscreen (Desktop 1) fuer Einfuehrung
2. Wechsel zu Hero + 2 (Desktop 2) fuer parallele Darstellung
3. Shopfloor-Rotation ausschliesslich in OSF-UI steuern
4. Kamerawechsel ausschliesslich in OBS steuern
5. Bei Station-Fokus Konftel-20 Zoom-Preset nutzen

---

## 4) Videokonferenz-Nutzung

Das gleiche Grund-Setup wird fuer remote Termine verwendet, mit angepasstem Monitor-Modus:

- **Messe-Betrieb:** Monitor **duplizieren**
- **Videokonferenz-Betrieb:** Monitor **erweitern** und den grossen Praesentationsmonitor in Teams/Zoom teilen
- Layout bleibt FancyZones-basiert
- OBS liefert nur Kamera-/Bildausschnitt
- Keine OBS-Kompositionslogik als Voraussetzung fuer die Demo

Damit ist Vor-Ort- und Remote-Betrieb konsistent.