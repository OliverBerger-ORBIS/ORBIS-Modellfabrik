# AIQS Quality-Check – DSP-Referenz (MQTT + OPC-UA)

**Zweck:** Informationen für DSP-Kollegen: Quality-Check-Status (PASSED/FAILED) auslesen – via MQTT (TXT-Erweiterung) oder OPC-UA.  
**Datum:** 2026-03-04

---

## 1. Empfohlene Quelle: MQTT Topic `quality_check` (TXT-Erweiterung)

**OSF hat eine TXT-Erweiterung vorgenommen:** Der TXT-AIQS-Controller sendet das Qualitätsergebnis direkt via MQTT – **ohne Umweg über Node-RED oder OPC-UA**.

| Eigenschaft | Wert |
|-------------|------|
| **Topic** | `/j1/txt/1/i/quality_check` |
| **Publisher** | TXT-AIQS (192.168.0.103), Varianten `_cam` oder `_cam_clfn` |
| **QoS** | 1, Retain: true |
| **Trigger** | Nach jedem Quality-Check (CHECK_QUALITY) |

**Payload (JSON):**

| Feld | Typ | Bedeutung |
|------|-----|-----------|
| `result` | string | `"PASSED"` oder `"FAILED"` |
| `ts` | string | ISO-8601 Timestamp |
| `num` | number | 1–4 (PASSED: 1/2/3, FAILED: 4) oder -1 |
| `classification` | string \| null | ML-Label (z.B. BOHO, MIPO2, CRACK) – nur `_cam_clfn` |
| `classificationDesc` | string | Lesbare Beschreibung – nur `_cam_clfn` |
| `data` | string | Base64-PNG (data URL) – Prüfbild |

**Für DSP:** Topic subscriben → `result` = PASSED/FAILED ist das Quality-Ergebnis. Vollständige Spec: [AIQS-CLASSIFICATION-REFERENCE.md](AIQS-CLASSIFICATION-REFERENCE.md).

---

## 2. Kontext: Woher kommt good/bad? (OPC-UA-Pfad)

Das AIQS-Modul prüft Werkstücke per Kamera und sortiert physisch:
- **PASSED (good):** Werkstück wird zurück zum FTS gefördert
- **FAILED (bad):** Werkstück wird zum NiO-Behälter (Not in Order) befördert

**Beteiligte Komponenten:**

| Komponente | Rolle |
|------------|-------|
| **TXT-AIQS** (192.168.0.103) | Kamera, ML-Klassifikation, sendet **`/j1/txt/1/i/quality_check`** (MQTT) und meldet an Node-RED |
| **AIQS SPS** (192.168.0.70) | Siemens S7-1200, OPC-UA Server, steuert Förderbänder und Sortiermechanik |
| **Node-RED** (RPi) | Liest TXT-Ergebnis (intern) → schreibt `cmd__good` oder `cmd__bad` an SPS → SPS setzt `stat__goodFinished` / `stat__badFinished` |

**Ablauf:**
1. CCU sendet CHECK_QUALITY-Befehl
2. TXT-Kamera klassifiziert → **TXT publiziert `quality_check` (result: PASSED/FAILED)**
3. Node-RED schreibt an OPC-UA: `cmd__good=true` (PASSED) oder `cmd__bad=true` (FAILED)
4. SPS führt Sortierung aus, setzt `stat__goodFinished` oder `stat__badFinished`

---

## 3. OPC-UA-Verbindung zum AIQS

| Parameter | Wert |
|-----------|------|
| **Endpoint** | `opc.tcp://192.168.0.70:4840` |
| **Modul-Serial** | SVR4H76530 (AIQS) |
| **Authentifizierung** | Typisch anonym (OPC-UA Standard) |
| **Netzwerk** | LAN 192.168.0.x, SPS statisch |

**Voraussetzung:** DSP muss im gleichen Netzwerk sein (192.168.0.x) oder per VPN/Routing die SPS erreichen können.

---

## 4. Relevante OPC-UA-Variablen (Good/Bad-Status)

Quelle: [Fischertechnik aiqs.md](../fischertechnik-official/06-modules/aiqs.md) – OPC UA Variables

| Variable (BrowseName) | Typ | Bedeutung |
|----------------------|-----|-----------|
| `stat__goodFinished` | BOOL | true = Good-Sortierung abgeschlossen (PASSED) |
| `stat__badFinished` | BOOL | true = Bad-Sortierung abgeschlossen (FAILED) |
| `stat__goodActive` | BOOL | true = Good-Prozess läuft |
| `stat__badActive` | BOOL | true = Bad-Prozess läuft |
| `cmd__good` | BOOL | Command: Good ausführen (Schreibzugriff, normalerweise von Node-RED) |
| `cmd__bad` | BOOL | Command: Bad ausführen |

**Für DSP-Read-Only:**
- `stat__goodFinished` und `stat__badFinished` sind die zentralen Status-Flags
- Sie werden von der SPS gesetzt, sobald die physische Sortierung fertig ist
- Typischer Ablauf: `stat__goodActive` oder `stat__badActive` → dann `stat__*Finished` = true

---

## 5. NodeIds (ns=4;i=X)

Die Fischertechnik-SPS verwendet das Schema `ns=4;i={number}`. Aus den Node-RED-Flows (AIQS-Tab, OPC-UA Read → Switch):

**Bekannte AIQS-NodeIds (aus Node-RED flows.json):**

| NodeId | Verwendung |
|--------|------------|
| ns=4;i=6 | cmd__good (Write) |
| ns=4;i=7 | cmd__bad (Write) |
| ns=4;i=35 | good_finished (Read) → PASSED |
| ns=4;i=36 | bad_finished (Read) → FAILED |
| ns=4;i=24 | badActive (Read) |
| ns=4;i=13 | goodActive (Read) |

*Vollständige Liste: Node-RED `integrations/APS-CCU/nodeRed/flows.json`, AIQS-Tab (flow `e811f976a7becb7c`), OPC-UA Read Switch-Node.*

**Für DSP-Quality-Status:** `ns=4;i=36` (stat__badFinished) und `ns=4;i=35` (stat__goodFinished) subscriben oder pollen. Bei `true` = Sortierung abgeschlossen (FAILED bzw. PASSED).

---

## 6. Übersicht: MQTT-Quellen für Quality-Status

| Topic | Quelle | Inhalt | Empfehlung für DSP |
|-------|--------|--------|--------------------|
| **`/j1/txt/1/i/quality_check`** | TXT-Controller (OSF-Erweiterung) | result, ts, num, classification, classificationDesc, data (Bild) | ✅ **Primär** – direkt vom TXT, früh im Ablauf |
| `module/v1/ff/NodeRed/SVR4H76530/state` | Node-RED (enriched) | OrderId, actionState.result: PASSED/FAILED | Mit Order-Kontext |
| `module/v1/ff/SVR4H76530/state` | TXT-Controller (VDA5050) | RAW-State | Alternative |

**Vorteil `quality_check`:** Direkt vom TXT, enthält Klassifikation und Prüfbild, keine OPC-UA- oder Node-RED-Abhängigkeit.  
**Vorteil OPC-UA:** Unabhängig von MQTT, SPS-Level-Status (physische Sortierung fertig).

---

## 7. Checkliste für DSP-Implementierung

**Option A: MQTT (empfohlen)**
| Nr. | Info/Aufgabe |
|-----|--------------|
| 1 | Topic subscriben: `/j1/txt/1/i/quality_check` |
| 2 | Payload parsen: `result` = `"PASSED"` oder `"FAILED"` |
| 3 | Optional: `classification`, `classificationDesc`, `data` (Bild) nutzen |
| 4 | Spec: [AIQS-CLASSIFICATION-REFERENCE.md](AIQS-CLASSIFICATION-REFERENCE.md) |

**Option B: OPC-UA**
| Nr. | Info/Aufgabe |
|-----|--------------|
| 1 | Endpoint: `opc.tcp://192.168.0.70:4840` |
| 2 | NodeIds lesen: `ns=4;i=35` (good_finished), `ns=4;i=36` (bad_finished) |
| 3 | Semantik: `stat__goodFinished=true` ↔ PASSED, `stat__badFinished=true` ↔ FAILED |

---

## 8. Referenzen

- [AIQS-CLASSIFICATION-REFERENCE.md](AIQS-CLASSIFICATION-REFERENCE.md) – **quality_check** Topic, Payload, Klassifikation
- [aiqs-quality-check-enumeration.md](../../04-howto/aiqs-quality-check-enumeration.md) – TXT-Erweiterung _cam_clfn
- [AIQS Modul-Doku (Fischertechnik)](../fischertechnik-official/06-modules/aiqs.md) – OPC UA Variables
- [Module Serial Mapping](../00-REFERENCE/module-serial-mapping.md) – AIQS IP 192.168.0.70, Serial SVR4H76530
- [Fischertechnik OPC-UA.md](https://github.com/fischertechnik/Agile-Production-Simulation-24V/blob/main/OPC-UA.md) – Screenshots Address Space AIQS
