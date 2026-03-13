# RPi Docker Update – Schritt-für-Schritt

**Ziel:** CCU (und optional OSF-UI) auf dem Raspberry Pi aktualisieren.  
**Voraussetzung:** SSH-Zugang zum Pi (User `ff22`, Passwort `ff22+`).  
**IP:** 192.168.0.100 (anpassen, falls anders)

---

## Schnellüberblick

| Schritt | CCU | OSF-UI |
|--------|-----|--------|
| 1. Version prüfen | `integrations/APS-CCU/package.json` | `package.json` (Repo-Root) |
| 2. Build | `npm run docker:build <TAG> central` | in `docker:osf-ui:deploy` enthalten |
| 3. Deploy | `npm run docker:deploy -- ff22@192.168.0.100 <TAG> central` | `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` |

---

## 1. CCU aktualisieren

### 1.1 Version festlegen

Aktuelle Version in `integrations/APS-CCU/package.json` (z.B. `1.3.0-osf.2`). Für den Deploy verwenden wir den Tag `v1.3.0-osf.2`.

### 1.2 CCU-Image bauen

```bash
cd integrations/APS-CCU
npm run docker:build v1.3.0-osf.2 central
```

- Baut nur die CCU (`central`), nicht Frontend oder Node-RED.
- Plattform: `linux/arm/v7` (RPi 32-bit).
- Dauer: ca. 2–5 Minuten.

**Mögliche Fehler:**
- `No space left`: `docker system prune -a`
- `buildx not available`: Docker Desktop prüfen / Buildx aktivieren

### 1.3 Auf den Pi deployen

```bash
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.2 central
```

Das Skript macht:
1. Image als Tar speichern  
2. Mit SCP auf den Pi kopieren (`/tmp/`)  
3. Per SSH: Image laden, `docker-compose-prod.yml` anpassen, Container neu starten  

**Passwort:** Bei Aufforderung `ff22+` eingeben (oder SSH-Key nutzen: `ssh-copy-id ff22@192.168.0.100`).

### 1.4 Verifikation (CCU)

```bash
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml ps"
```

```bash
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml logs central-control --tail 30"
```

---

## 2. OSF-UI aktualisieren (optional)

### 2.1 Version

OSF-UI verwendet die Version aus `package.json` (Repo-Root, z.B. `0.8.8`). Das Deploy-Skript nutzt sie automatisch.

### 2.2 Deploy (Build + Transfer + Start)

```bash
cd /Users/oliver/Projects/ORBIS-Modellfabrik   # Repo-Root
npm run docker:osf-ui:deploy -- ff22@192.168.0.100
```

Das Skript:
- Baut OSF-UI (Angular + Docker)
- Speichert und überträgt das Image
- Startet den Container neu

**Andere Version:**
```bash
npm run docker:osf-ui:deploy -- ff22@192.168.0.100 0.8.9
```

### 2.3 Verifikation (OSF-UI)

- Browser: http://192.168.0.100:8080

---

## 3. Vollständiger Update (CCU + OSF-UI)

```bash
# 0. Compose-Datei auf den Pi (nur bei Änderungen nötig)
scp integrations/APS-CCU/docker-compose-prod.yml ff22@192.168.0.100:/home/ff22/fischertechnik/ff-central-control-unit/

# 1. CCU
cd integrations/APS-CCU
npm run docker:build v1.3.0-osf.2 central
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.2 central

# 2. OSF-UI (aus Repo-Root)
cd ../..
npm run docker:osf-ui:deploy -- ff22@192.168.0.100
```

---

## 4. Fehlerbehebung

### Port 8080 belegt

```bash
ssh ff22@192.168.0.100 "docker stop osf-ui osf-ui-prod 2>/dev/null; docker rm osf-ui osf-ui-prod 2>/dev/null"
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml up -d"
```

### Host-Key-Veränderung („Host key verification failed“)

```bash
ssh-keygen -R 192.168.0.100
```

### Alte Images aufräumen (Platzmangel)

```bash
docker system prune -a
```

---

## 5. Referenzen

- [rpi-deployment.md](./rpi-deployment.md) – Übersicht
- [integrations/APS-CCU/DEPLOYMENT.md](../../../integrations/APS-CCU/DEPLOYMENT.md) – CCU-Deployment
- [deploy/README.md](../../../deploy/README.md) – Docker-Setup
