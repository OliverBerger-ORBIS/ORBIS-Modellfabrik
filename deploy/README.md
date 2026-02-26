# Deployment Configurations

This directory contains Docker Compose configurations for deploying the ORBIS SmartFactory infrastructure.

## Available Configurations

### `docker-compose.osf-ui.yml` - OSF-UI Dashboard

Deploys the OSF (ORBIS Shopfloor) Dashboard – Port **8080**.

#### Build

```bash
# ARM64 (Raspberry Pi 4/5, 64-bit OS)
npm run docker:osf-ui:arm

# ARM32/armv7 (Raspberry Pi mit 32-bit OS, z.B. ff-ccu-armv7)
npm run docker:osf-ui:armv7

# AMD64 (lokal testen)
npm run docker:osf-ui:local
```

#### Lokal starten

```bash
docker compose -f deploy/docker-compose.osf-ui.yml up -d
# → http://localhost:8080
```

#### RPi-Integration

Auf dem RPi parallel zu Fischertechnik-Dashboard (Port 80):
- Fischertechnik: `http://192.168.0.100`
- OSF-UI: `http://192.168.0.100:8080`

**RPi Deployment (Image + Compose gemeinsam übertragen):**

```bash
# 1. Image bauen – ARM64 ODER ARM32 je nach RPi-OS
#    RPi 64-bit: npm run docker:osf-ui:arm
#    RPi 32-bit (armv7): npm run docker:osf-ui:armv7
mkdir -p deploy/osf-ui/docker-images
# Für ARM64:
docker save orbis-osf-ui:latest -o deploy/osf-ui/docker-images/osf-ui-arm64.tar
# Für ARM32:
docker save orbis-osf-ui:latest -o deploy/osf-ui/docker-images/osf-ui-arm32.tar

# 2. Auf RPi kopieren (Dateiname anpassen: arm64 oder arm32)
scp deploy/osf-ui/docker-images/osf-ui-arm32.tar deploy/docker-compose.osf-ui.yml ff22@192.168.0.100:~/

# 3. Auf RPi: Image laden und starten
ssh ff22@192.168.0.100
docker compose -f ~/docker-compose.osf-ui.yml down
docker load -i ~/osf-ui-arm32.tar
docker compose -f ~/docker-compose.osf-ui.yml up -d
# → http://192.168.0.100:8080
```

Dockerfile: `deploy/osf-ui/Dockerfile`

---

### `docker-compose.metrics.yml` - Metrics Stack

Deploys the metrics collection and visualization infrastructure:
- **InfluxDB 2.7** - Time-series database for storing metrics
- **Grafana 10.2.2** - Visualization and dashboarding platform

#### Quick Start

```bash
# Start the metrics stack
docker compose -f docker-compose.metrics.yml up -d

# Check status
docker compose -f docker-compose.metrics.yml ps

# View logs
docker compose -f docker-compose.metrics.yml logs -f

# Stop the stack
docker compose -f docker-compose.metrics.yml down
```

#### Access

Once started, the services are available at:
- **InfluxDB**: http://localhost:8086
  - Username: `admin`
  - Password: `adminpassword`
  - Organization: `orbis`
  - Bucket: `omf-metrics`
  - Token: `dev-token-please-change`

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

#### Configuration

Default credentials are for development only. For production:
1. Use environment variables:
   ```bash
   export INFLUX_ADMIN_TOKEN="your-secure-token"
   docker compose -f docker-compose.metrics.yml up -d
   ```

2. Or modify the docker-compose file to use `.env` file:
   ```yaml
   environment:
     - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUX_TOKEN}
   ```

#### Data Persistence

By default, data is persisted in Docker volumes:
- `influxdb-data` - InfluxDB time-series data
- `influxdb-config` - InfluxDB configuration
- `grafana-data` - Grafana dashboards and settings

To reset all data:
```bash
docker compose -f docker-compose.metrics.yml down -v
```

#### Metrics Service Integration

The metrics service (`backend/metrics-service`) connects to InfluxDB to write data. Configure it with:

```bash
cd ../backend/metrics-service
cp .env.example .env
# Edit .env to set INFLUX_URL, INFLUX_TOKEN, etc.
npm run dev
```

For containerized deployment, uncomment the `metrics-service` section in `docker-compose.metrics.yml`.

## Network Configuration

The compose file creates a `omf-metrics-network` bridge network for service communication. Services can be accessed:
- From host: Use `localhost` and mapped ports
- Between containers: Use service names (e.g., `http://influxdb:8086`)

## Troubleshooting

### InfluxDB not starting
```bash
# Check logs
docker compose -f docker-compose.metrics.yml logs influxdb

# Ensure no port conflicts
lsof -i :8086
```

### Grafana not connecting to InfluxDB
- Verify InfluxDB is running: `curl http://localhost:8086/health`
- Check network connectivity: `docker network inspect omf-metrics-network`
- Verify token and organization in Grafana data source configuration

### Permission issues with volumes
```bash
# Fix volume permissions (Linux)
sudo chown -R $(id -u):$(id -g) /var/lib/docker/volumes/
```
