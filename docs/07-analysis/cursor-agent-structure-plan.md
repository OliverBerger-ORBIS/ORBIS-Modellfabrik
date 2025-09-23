# 🧠 Modellfabrik – Doku-Struktur für CURSOR-Agent

Dieses Dokument dient als Leitfaden für die Dokumentationsstruktur der ORBIS-Modellfabrik innerhalb des Git-Projekts. Es unterstützt den CURSOR-Agenten dabei, Inhalte korrekt einzuordnen, bestehende Strukturen zu respektieren und neue Analyse- und Architektur-Informationen logisch abzulegen.

---

## 📁 Zielstruktur im Projekt

### Quellcode & Teststruktur

```bash
/omf/           # Python-Code (DSP, MQTT-Komponenten, Cloud-Anbindung)
/tests/         # Unit & Integration Tests
/logs/          # Nicht versionierte Log-Dateien (lokal)
/data/          # MQTT-Sessions für Replay-Tests ohne reale APS
/registry/      # MQTT-Kontrakte, Templates, Topic-Spezifikationen
/vendor/        # Submodul: Originalquellen Fischertechnik
```

### Alle APS-Komponenten/Systeme:  Sourcen und Scripte

```bash
/integrations/
├── mqtt/              # Technische Dateien zur MQTT-Analyse
├── node-red/          # Node-RED-Flows 
├── robo-pro/converted # Analysierte Inhalte der .ft-Module
├── docker/            # Docker Compose etc. vom APS-RPi
├── opcua/             # NodeMaps, Topologien, (noch nicht interesant, ggf spätrer mit einzelnen Unterordnern)
└── ccu/               # decompilat der APS-CCU 
└── txt/dps             # decompilat der ft-Module
txt/fts
txt/aiqs
txt/cgw               

```

### Dokumentation (Markdown)

```bash
/docs/
├── 01-strategy/         # Vision, Roadmap, Discover/Prepare
├── 02-architecture/     # Systemarchitektur, Layer-Modelle
├── 03-decision-records/ # ADRs – technische Entscheidungen
├── 04-howto/            # Technische Anleitungen
├── 05-reference/        # Datenformate, externe Links, Schnittstellen
├── 06-integrations/     # Beschreibung technischer Schnittstellen und Logik)
└── 08-extensions/       # Erweiterungen wie DSP, AI, Cloud, etc.
```

---

## 🔍 Inhalt von `/docs/07-analysis/` (neu!)

Dieser Ordner dient zur funktionalen und blackboxartigen Analyse bestehender Komponenten, z. B.:

| Datei                           | Inhalt |
|----------------------------------|--------|
| `mqtt-client-analysis.md`       | Welche Clients publizieren/subscriben was? |
| `ft-module-behavior.md`         | Analyse der TXT-Firmware-Module (.ft) |
| `ccu-ui-tabs.md`                | Funktionsweise der Tabs im APS-Web-Dashboard |
| `opcua-structure.md`            | Wie sind die OPC-UA-Knoten der TXT-Module aufgebaut? |
| `aps-docker-setup.md`           | Analyse der Container-Umgebung auf dem RPi |

---

## ✅ Aufgaben & ToDos

- [ ] Ordner `/docs/07-analysis/` anlegen
- [ ] Bestehende Analysen aus `/docs/06-integrations/` ggf. verschieben
- [ ] Markdown-Dateien pro Thema anlegen (siehe oben)
- [ ] TOC-Datei (`docs/07-analysis/TOC.md`) erstellen
- [ ] Bei jeder Analyse: Bezug zu Dateien aus `/integrations/` und `/vendor/` dokumentieren
- [ ] Agenten anweisen: Bei neuen Analysen → Inhalte in `/07-analysis/` ablegen

---

## 🧭 Hinweise für den CURSOR-Agent

- Diese Struktur ist verbindlich.
- `analysis/` ist für *funktionale Analyse*, `integrations/` für *technische Bindung*.
- Wenn unklar, wohin eine Info gehört: zuerst nachfragen oder `07-analysis/unsorted.md` nutzen.
