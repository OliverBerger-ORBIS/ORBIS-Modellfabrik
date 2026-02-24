# Advanced Deployment Guide

This guide covers all deployment scenarios, from quick automated updates to manual installation and hybrid development.

## Prerequisites

- Docker Desktop with buildx support
- SSH access to Raspberry Pi (user: `ff22`, password: `ff22+`)
- Sufficient disk space (images are ~500MB each compressed)
- Node.js 18.x for local development

**Note:** During deployment, you'll be prompted to enter the SSH password multiple times.

## Standard Deployment Options

### Option 1: Automated Deployment (Recommended)

This automatically handles all steps: build, save, transfer, load, and restart.

**Full Deployment:**
```bash
npm run docker:build
npm run docker:deploy -- ff22@192.168.0.100
# Enter password when prompted: ff22+
```

**Selective Deployment (Faster):**
If you only changed specific services, you can deploy just those:
```bash
# Build only frontend
npm run docker:build -- userdev frontend

# Deploy only central-control and nodered
npm run docker:deploy -- ff22@192.168.0.100 userdev central nodered
```
Available services: `central`, `frontend`, `nodered`

### Option 2: Manual Step-by-Step

**1. Build images:**
```bash
npm run docker:build v1.3.0
```

**2. Save to files:**
```bash
npm run docker:save v1.3.0
```

Creates tar files in `docker-images/`:
- `ff-ccu-armv7-v1.3.0.tar.gz`
- `ff-frontend-armv7-v1.3.0.tar.gz`
- `ff-nodered-armv7-v1.3.0.tar.gz`

**3. Transfer to Raspberry Pi:**
```bash
scp docker-images/*.tar.gz ff22@192.168.0.100:/tmp/
# Enter password when prompted: ff22+
```

**4. Load images on Pi:**
```bash
ssh ff22@192.168.0.100
# Enter password when prompted: ff22+
cd /tmp
gunzip -c ff-ccu-armv7-v1.3.0.tar.gz | docker load
gunzip -c ff-nodered-armv7-v1.3.0.tar.gz | docker load
gunzip -c ff-frontend-armv7-v1.3.0.tar.gz | docker load
```

**5. Update docker-compose.yml:**
```bash
cd /path/to/project
# Edit docker-compose-prod.yml to use new tag
nano docker-compose-prod.yml
```

**6. Restart services:**
```bash
docker compose -f docker-compose-prod.yml down
docker compose -f docker-compose-prod.yml up -d
```

**7. Clean up:**
```bash
docker image prune -a
rm /tmp/*.tar.gz
```

### Option 3: Container Registry (Alternative)

Push images to GitHub Container Registry for easier distribution:

```bash
# Login to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push images
docker push ghcr.io/ommsolutions/ff-ccu-armv7:v1.3.0
docker push ghcr.io/ommsolutions/ff-nodered-armv7:v1.3.0
docker push ghcr.io/ommsolutions/ff-frontend-armv7:v1.3.0
```

Then on Raspberry Pi:
```bash
docker compose -f docker-compose-prod.yml pull
docker compose -f docker-compose-prod.yml up -d
```

## Verification

**Check running containers:**
```bash
ssh ff22@192.168.0.100
docker ps
```

**View logs:**
```bash
docker compose -f docker-compose-prod.yml logs -f
```

**Access services:**
- Web UI: http://raspberrypi.local or http://\\<rpi-ip\\>
- Node-RED: http://raspberrypi.local:1880

## Hybrid Development (Local + Remote MQTT)

### Autostart make Permanent
Enable automatic startup on Raspberry Pi boot:

```bash
ssh ff22@raspberrypi.local
# Password: ff22+
sudo cp raspberrypi/fischer-techik.service /etc/systemd/system/
sudo systemctl enable fischer-techik.service
sudo systemctl start fischer-techik.service
```

## Hybrid Development (Local + Remote MQTT)

Develop services locally while using the MQTT broker on Raspberry Pi.

### Setup

**1. Stop the service you want to develop locally:**
```bash
ssh ff22@192.168.0.100
# Enter password if prompted: ff22+
cd /path/to/project
docker compose -f docker-compose-prod.yml stop central-control
# or: docker compose -f docker-compose-prod.yml stop frontend
```

**2. Configure local environment:**

For central-control, create `.env`:
```bash
cd central-control
cat > .env << EOF
MQTT_URL=mqtt://192.168.0.100:1883
MQTT_USER=admin
MQTT_PASS=<password>
EOF
```

For frontend, update `src/environments/environment.ts` with the Pi's MQTT broker URL.

**3. Run locally:**
```bash
# Central Control
cd central-control
npm start            # Or: npm run start:debug

# Frontend
cd frontend
npm start            # Access at http://localhost:4200
```

### Test MQTT Connection

```bash
# Install MQTT clients
# Ubuntu/Debian: apt-get install mosquitto-clients
# macOS: brew install mosquitto

# Subscribe to topics
mosquitto_sub -h 192.168.0.100 -p 1883 -u admin -P <password> -t 'ccu/#' -v

# Publish test message
mosquitto_pub -h 192.168.0.100 -p 1883 -u admin -P <password> -t 'ccu/test' -m 'Hello'
```

### Development Scenarios

**Scenario 1: Develop Backend Only**
```bash
# On Pi: Stop only backend
docker compose -f docker-compose-prod.yml stop central-control

# Locally: Run backend
cd central-control
npm start

# Access frontend at http://192.168.0.100
```

**Scenario 2: Develop Frontend Only**
```bash
# On Pi: Stop only frontend
docker compose -f docker-compose-prod.yml stop frontend

# Locally: Run frontend
cd frontend
npm start

# Access at http://localhost:4200
```

**Scenario 3: Develop Both Locally**
```bash
# On Pi: Keep only MQTT running
docker compose -f docker-compose-prod.yml stop frontend central-control

# Terminal 1
cd central-control && npm start

# Terminal 2
cd frontend && npm start

# Access at http://localhost:4200
```

### Return to Production

Restart stopped containers on Pi:
```bash
docker compose -f docker-compose-prod.yml start central-control frontend
```

## Troubleshooting

### Build Errors

**No space left:**
```bash
docker system prune -a
```

**ARM build fails:**
```bash
# Ensure buildx is installed
docker buildx version

# Create builder if needed
docker buildx create --name multiarch --use
```

### Deployment Issues

**SSH connection refused:**
```bash
ssh ff22@192.168.0.100 "sudo systemctl status ssh"
```

**Host key verification failed:**
If you see this error when `npm start` tries to connect to the Pi, it means the Pi's identity key has changed (e.g., OS reinstall).
- **Fix:** Remove the old key from your known hosts file:
    - **Windows:** Open `~/.ssh/known_hosts` and delete the line starting with `192.168.0.100` or `172...`
    - **Command:** `ssh-keygen -R 192.168.0.100`

**Images not loading:**
```bash
# Verify tar files
gunzip -t docker-images/*.tar.gz
```

**Containers not starting:**
```bash
# Check logs
docker compose -f docker-compose-prod.yml logs

# Verify config syntax
docker compose -f docker-compose-prod.yml config
```

### Network Issues

**MQTT connection fails:**
- Ensure firewall allows port 1883
- Check MQTT broker is running: `docker ps | grep mosquitto`
- Verify credentials in .env file

**Frontend can't connect:**
- Check that frontend container is running
- Verify port 80 (or 4200 for dev) is not blocked
- Check browser console for connection errors

## Best Practices

1. **Version your images:** Use semantic versioning (v1.3.0) instead of just `latest`
2. **Test locally first:** Always test builds with `npm start` before deploying
3. **Backup before update:** Save current docker-compose-prod.yml before changes
4. **Monitor logs:** Use `docker compose logs -f` during deployment
5. **Clean up regularly:** Run `docker image prune` to remove old images

## Additional Resources

- [README.md](README.md) - Quick start and basic usage
- [central-control/README.md](central-control/README.md) - MQTT protocol documentation
- [nodeRed/readme.md](nodeRed/readme.md) - Node-RED configuration
