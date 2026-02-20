# OSF Vision – Konzept & MQTT-First

> **📋 Entwicklungsphasen:** [Roadmap](roadmap.md)  
> **Glossary:** [99-glossary.md](../99-glossary.md)

---

## 🎯 Konzept

### OSF (ORBIS-SmartFactory)
Konzept und Vision – unsere Produkte (DSP, MES, …) und Leistungen demonstrierbar machen. Use Cases, Demos, Messeauftritte. OSF ist kein produktives System, sondern Demonstrator.

### Fischertechnik APS 24V
Produkt von Fischertechnik – physische Modellfabrik + Software. Wir nutzen es als Testumgebung.

| Begriff | Bedeutung |
|--------|-----------|
| **FMF** (Fischertechnik-ModellFabrik) | Physische Komponenten – Shopfloor (HBW, DRILL, MILL, AIQS, DPS, FTS, …) |
| **APS** | Software-Teil – CCU, Node-RED, Frontend, mosquitto, TXT-, PLC-Programme |

### OSF-UI
Unser Dashboard zur Visualisierung. Angular (`osf/`), ehemals OMF3.

### Parallelbetrieb
MQTT-Entkopplung ermöglicht: **APS-CCU** und **ORBIS-DSP** nebeneinander; **APS-Frontend** und **OSF-UI** nebeneinander. Bei Demonstrationen: nur ORBIS-Komponenten zeigen.

### Projekt-Scope (dieses Repo)
| Bereich | Änderung? |
|---------|-----------|
| ORBIS-DSP, ORBIS-MES | ❌ Nein (extern) |
| OSF-UI | ✅ Ja |
| FMF-Komponenten (z.B. AIQS-TXT) | ✅ Ja |
| APS-CCU | ✅ Temporär (z.B. ERP-ID in MQTT) |

Nicht: Alle APS-Komponenten ersetzen. Ziel: selektive Übernahme durch ORBIS (insbesondere CCU durch DSP).

---

## 🏗️ Leitidee: MQTT-First

**Steuerung über MQTT-Kommandos, Node-RED vermittelt zu OPC-UA**

Das OSF-System basiert auf der Prämisse, dass Steuerungslogik über MQTT läuft. Node-RED vermittelt zwischen MQTT und OPC-UA zu den physischen Modulen (FMF).

## 🏗️ System-Namenskonvention

### APS (As-Is) – Fischertechnik
- **FMF** – physische Komponenten
- **APS-CCU**, **APS-NodeRED**, **APS-Frontend**

### OSF (To-Be) – Unser System
- **OSF-UI** – Angular-Dashboard
- **Session Manager** – Replay Helper-App

> **Namenskonvention:** Groß-Schreibweise mit Bindestrich (z.B. APS-CCU, OSF-UI)

---

## 🏗️ Architektur-Prinzipien

### 1. MQTT als Steuerungsebene
- Befehle über `module/v1/ff/{serial}/order`
- Status über `module/v1/ff/{serial}/state`
- Keine direkte OPC-UA-Steuerung aus der OSF-UI

### 2. Node-RED als Vermittler
- MQTT → OPC-UA, OPC-UA → MQTT
- Modul-spezifische Logik (State-Machine, Error-Handling)

### 3. Templates & Mappings
- Templates definieren Nachrichtenstrukturen (topic-frei)
- Mappings verbinden Topics mit Templates

---

## 🎯 Erfolgskriterien

- ✅ OSF-UI kann DRILL mit `PICK → DRILL → DROP` anweisen
- ✅ HBW-Verwaltung, AIQS-Bewertung über MQTT
- ✅ Tests via Replay stabil

---

## 🔄 Message-Flow

```
User (OSF-UI) → MQTT Order → Node-RED → OPC-UA → Modul (FMF)
Modul → OPC-UA → Node-RED → MQTT State → OSF-UI
```

---

## 💡 Warum MQTT-First?

**Vorteile:** Entkopplung, Skalierbarkeit, Testbarkeit (Replay).  
**Trade-offs:** Zusätzliche Schicht (Node-RED), Latenz, Abhängigkeiten.

---

*"MQTT-First bedeutet: Alles was steuerbar ist, ist über MQTT steuerbar."*
