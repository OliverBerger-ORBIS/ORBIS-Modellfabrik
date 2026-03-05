# Decision Record: CCU OSF-Versionierung

**Datum:** 2026-03-04  
**Status:** Accepted  
**Kontext:** Die APS-CCU stammt von ommsolutions/Fischertechnik; OSF nimmt Modifikationen vor (OSF-MODIFICATIONS.md). Eine klare Versionierungsstrategie ermöglicht Nachverfolgbarkeit, reproduzierbare Deployments und Zuordnung von Änderungen zu Releases.

> **Vorgehensweise:** Wann/Wie ein Decision Record erstellt wird → [README – Vorgehensweise](README.md#vorgehensweise-wann-wird-ein-decision-record-erstellt)

---

## Entscheidung

**Wir versionieren die OSF-CCU konsequent:**

1. **package.json als Source of Truth** – `integrations/APS-CCU/package.json` und `central-control/package.json` (synchron gehalten)
2. **Pre-Release-Suffix `-osf.N`** – Trennung von ommsolutions-Releases: `1.3.0-osf.1` = Fork basierend auf ommsolutions 1.3.0, OSF-Release 1. Vermeidet Kollision (z.B. ommsolutions 1.3.1 vs. OSF 1.3.1).
3. **Semantic Versioning (SemVer)** – Basisversion von Upstream; `-osf.N` inkrementiert pro OSF-Release. Bei Merge von Upstream 1.3.1: `1.3.1-osf.0` oder `1.3.1-osf.1`.
4. **Docker-Tags an Version koppeln** – Releases: `v1.3.0-osf.1`; Entwicklung: `userdev`
5. **Selektives Build/Deploy als Standard** – Bei CCU-Änderungen nur `central` bauen und deployen (siehe [DEPLOYMENT.md](../../integrations/APS-CCU/DEPLOYMENT.md))
6. **OSF-MODIFICATIONS mit Version verknüpfen** – Jede Modifikation referenziert die Version, ab der sie aktiv ist

---

## Nebenwirkungen (Analyse)

| Bereich | Verhalten | Risiko |
|---------|-----------|--------|
| **CCU-Version (package.json)** | Wird zur Laufzeit gelesen, nur in UI angezeigt ("Version der zentralen Steuerung") | Keines – keine technische Abhängigkeit |
| **Modul-Versionen (TXT, FTS)** | Module melden ihre eigene Firmware-Version; CCU prüft gegen `required-versions.json` | Keines – Modul-Versionen sind unabhängig von CCU-Version |
| **Container untereinander** | Kein Versionsaustausch zwischen central-control, frontend, nodered | Keines |
| **required-versions.json** | Definiert erlaubte Modul-Firmware-Ranges; nicht verwechseln mit CCU-Version | Nur ändern bei neuer Modul-Firmware-Unterstützung |

**Fazit:** Eine Erhöhung der CCU-Version hat keine funktionalen Nebenwirkungen.

---

## Versionierungs-Workflow

### OSF-Releases (`1.3.0-osf.1` → `1.3.0-osf.2`)
- Nächste OSF-Änderung auf gleicher Upstream-Basis: `-osf.N` inkrementieren
- Beispiele: Quality-Fail = `1.3.0-osf.1`; nächste Modifikation = `1.3.0-osf.2`

### Upstream-Merge (z.B. ommsolutions 1.3.1)
- Nach Merge: `1.3.1-osf.0` (ohne eigene Änderungen) oder `1.3.1-osf.1` (mit OSF-Änderungen)
- Basisversion reflektiert Upstream-Stand

### Build & Deploy (empfohlen: selektiv)

```bash
# Nur CCU bauen und deployen (Standard bei OSF-CCU-Änderungen)
npm run docker:build v1.3.0-osf.1 central
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.1 central
```

Full-Build (alle drei Images) nur bei Änderungen an Frontend oder Node-RED.

---

## Alternativen

- **Keine Versionierung:** Verworfen – keine Nachverfolgbarkeit von Releases
- **Reines SemVer (1.3.1) ohne Suffix:** Verworfen – Kollisionsrisiko mit ommsolutions 1.3.1
- **Eigene Minor-Linie (1.4.x):** Verworfen – verliert Bezug zu Upstream-Basis
- **Eigener Registry-Namespace (ghcr.io/orbis-modellfabrik):** Option für spätere Abgrenzung; aktuell nicht erforderlich

---

## Konsequenzen

- **Positiv:** Klare Zuordnung Änderung↔Release; reproduzierbare Deployments; OSF-MODIFICATIONS nachvollziehbar
- **Negativ:** Manueller Version-Bump bei Releases (kein automatisches Bump)
- **Risiken:** Keine – Analyse bestätigt keine Nebenwirkungen

---

## Implementierung

- [x] DR-21 anlegen
- [x] package.json auf 1.3.0-osf.1 (Quality-Fail Release)
- [x] OSF-MODIFICATIONS: Version-Referenz für Mod 2
- [x] DEPLOYMENT.md: Selektives CCU-Build/Deploy als Standard
- [ ] Bei jeder CCU-Release: `-osf.N` inkrementieren (z.B. 1.3.0-osf.1 → 1.3.0-osf.2)

---

## Referenzen

- [DR-20: APS-CCU OSF-Modifikationen](20-aps-ccu-osf-modifications-documentation.md)
- [OSF-MODIFICATIONS.md](../../integrations/APS-CCU/OSF-MODIFICATIONS.md)
- [DEPLOYMENT.md](../../integrations/APS-CCU/DEPLOYMENT.md)
- [DR-15: Semver Versioning](15-semver-versioning.md) (OSF-UI; Konzept übertragen)

---
*Entscheidung getroffen von: OSF-Entwicklung*
