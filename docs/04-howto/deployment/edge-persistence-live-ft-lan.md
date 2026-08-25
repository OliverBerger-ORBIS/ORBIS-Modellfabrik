# Edge Persistence – Live im FT-LAN (Checkliste)

**Zielbetrieb:** Grafana + Persistence-Service auf dem **DSP-Edge** (Linux-VE `192.168.0.201`, Host Proxmox `.200`); **DB = SQL Server** auf bestehendem Container **`:1433`** (neues OSF-Schema). Lokal bis dahin Docker (Dev-Option B: SQL Server; Übergang: Postgres/Timescale). Siehe [wo läuft was](./dsp-edge-osf-persistence.md), [Netzwerk-Topologie](../setup/orbis-shopfloor-network-topology.md) und [DR-28](../../03-decision-records/28-edge-persistence-stack-and-metrics-model.md).

**Platte ist nicht der Engpass für einen RPi-Versuch.** Der APS-RPi (`192.168.0.100`) ist **armv7 / 32-bit** (CCU-Stack, [DR-23](../../03-decision-records/23-rpi-osf-ui-platform-armv7.md)). Offizielle `timescale/timescaledb` und aktuelle Grafana-Images sind **amd64/arm64**, nicht armv7. Timescale auf dem Shopfloor-Pi ist deshalb kein sinnvoller Zwischenstopp — CPU/Architektur, nicht GB.

| Wo | Rolle morgen |
|----|----------------|
| **Mac (Replay-Stack, `env.live`)** | Grafana `:3000` + DB + Persistence → MQTT `192.168.0.100:1883` |
| **RPi** | CCU / Broker / OSF-UI `:8080` / optional Intake-Bridge — **kein** Timescale |
| **DSP `.201`** | Nächster dauerhafter Host für denselben Compose-Stack |

---

## 1) Mac vor Ort (Live-Ingest)

Im FT-LAN, Persistence bleibt Replay-Container, Broker wird live:

```bash
cd osf-edge-persistence
cp env.live .env
```

**Docker Desktop + Dual-Homed (Gemini Wi‑Fi + FT-LAN Ethernet):** Container erreichen `192.168.0.100:1883` oft nicht (ECONNREFUSED). Lokal läuft zudem häufig Mosquitto auf `:1883` (Replay). Workaround:

```bash
# Tunnel RPi-Broker → Mac:1884 (Terminal offen lassen / -f im Hintergrund)
ssh -f -N -o ExitOnForwardFailure=yes -L 1884:127.0.0.1:1883 ff22@192.168.0.100

MQTT_HOST=host.docker.internal MQTT_PORT=1884 \
MQTT_USERNAME=default MQTT_PASSWORD=default \
SENSOR_INTERVAL_SECONDS=5 SENSOR_IDLE_INTERVAL_SECONDS=60 \
  docker compose up -d --force-recreate --no-deps persistence-service
```

Wenn Docker LAN-Zugriff hat und `:1883` frei ist:

```bash
MQTT_HOST=192.168.0.100 MQTT_PORT=1883 \
MQTT_USERNAME=default MQTT_PASSWORD=default \
SENSOR_INTERVAL_SECONDS=5 SENSOR_IDLE_INTERVAL_SECONDS=60 \
  docker compose up -d --force-recreate --no-deps persistence-service
```

Logs: `mode: live`, `mqttHost: host.docker.internal` (oder `.100`), `intervalSeconds: 5`, Subscribes inkl. `osf/workpiece/intake`.

Grafana: `http://localhost:3000` → **Systemstatus** → **MQTT Topics (raw)** und **Workpiece Trace**. Zeitfenster auf „jetzt“.

OSF-UI: Shopfloor `http://192.168.0.100:8080` **oder** lokales `nx serve` (`:4200`) mit Broker `ws://192.168.0.100:9001`.

Zurück ins Home-Office:

```bash
cp env.replay .env
MQTT_HOST=host.docker.internal SENSOR_INTERVAL_SECONDS=5 SENSOR_IDLE_INTERVAL_SECONDS=60 \
  docker compose up -d --force-recreate --no-deps persistence-service
```

---

## 2) OSF-UI auf den RPi (morgen)

Image vorher auf dem Mac bauen (armv7, Tag = `package.json`-Version):

```bash
npm run docker:osf-ui:armv7 -- 1.2.2
```

Lokal bereits gebaut (24.08.2026): `orbis-osf-ui:1.2.2` (linux/arm) und Tar  
`deploy/osf-ui/docker-images/osf-ui-arm32-1.2.2.tar` (~43 MB, nicht im Git). Schneller Fallback vor Ort:

```bash
scp deploy/osf-ui/docker-images/osf-ui-arm32-1.2.2.tar ff22@192.168.0.100:/tmp/
ssh ff22@192.168.0.100 "docker load -i /tmp/osf-ui-arm32-1.2.2.tar && cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml up -d osf-ui"
```

Vor Ort (baut erneut, lädt, startet Compose):

```bash
npm run docker:osf-ui:deploy -- ff22@192.168.0.100
```

Fallback Tar: [rpi-deployment.md](./rpi-deployment.md). CCU nicht mit aktualisieren, solange nur Persistenz/UI getestet wird.

---

## 3) Intake-Bridge (optional, Live-NFC-Facade)

Image `orbis-workpiece-intake-bridge:1.0.0` (armv7) ist lokal vorbereitet. Deploy: [workpiece-intake-bridge-rpi.md](./workpiece-intake-bridge-rpi.md).

Ohne Bridge kommt NFC weiter aus APS-Payloads (RGB_NFC / FTS `loadId` / CCU).

---

## 4) DSP-Edge (nächster Schritt, nicht RPi)

Persistence + Grafana auf **`.201`** (amd64); DB an SQL Server **`.201:1433`**. Grafana: `http://192.168.0.201:3000`. Architektur und VE-Inventar: [dsp-edge-osf-persistence.md](./dsp-edge-osf-persistence.md).
