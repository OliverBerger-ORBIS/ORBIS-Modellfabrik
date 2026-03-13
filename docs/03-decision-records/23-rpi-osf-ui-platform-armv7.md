# 23 – RPi OSF-UI: Plattform armv7 (32-bit)

**Datum:** 2026-03-12  
**Status:** Accepted  
**Kontext:** OSF-UI-Container crashte mit Exit 159 – falsche Architektur (arm64 statt armv7).

---

## Entscheidung

**OSF-UI auf dem RPi (192.168.0.100) muss als armv7 (32-bit) gebaut werden.**

| Plattform | Docker | CCU/Node-RED/Frontend | OSF-UI |
|-----------|--------|------------------------|--------|
| RPi mit CCU-Stack | linux/arm/v7 (32-bit) | ff-*-armv7 | orbis-osf-ui:armv7 |

**Begründung:** Der RPi läuft mit 32-bit OS. CCU, Node-RED und Frontend nutzen `ff-*-armv7`. OSF-UI steht in derselben `docker-compose-prod.yml` und **muss dieselbe Architektur** nutzen. Ein arm64-Image führt zu Container-Crash (Exit 159).

---

## Fehlersymptom

- `Restarting (159) 1 second ago`
- `WARNING: requested platform (linux/arm64) does not match detected host (linux/arm/v8)`
- http://192.168.0.100:8080 nicht erreichbar

---

## Implementierung

- Deploy-Skript: Default `PLATFORM=armv7` (nicht arm/arm64)
- Env-Var `OSF_UI_RPI_PLATFORM=arm` nur für 64-bit RPi (wenn vorhanden)
- Build: `node scripts/build-osf-ui-docker.js armv7`

---

## Referenzen

- [rpi-deployment.md](../04-howto/deployment/rpi-deployment.md)
- [deploy-osf-ui-to-rpi.js](../../scripts/deploy-osf-ui-to-rpi.js) – Konstante `PLATFORM`
- [DR-19: OSF-UI Deployment-Strategie](19-osf-ui-deployment-strategy.md)
