# Original APS-Dashboard Analyse

## Ziel
Das Original APS-Dashboard (`central-control-frontend-prod`) analysieren, um die korrekten Commands, Topics und Payloads zu identifizieren.

## Container Details
- **Container:** `central-control-frontend-prod`
- **Image:** `ghcr.io/ommsolutions/ff-frontend-armv7:release-24v-v130`
- **Port:** 80 (extern) → 80 (intern)
- **URL:** `http://192.168.0.100/de/aps/`

## Analyse-Schritte

### 1. SSH-Zugang zum Raspberry Pi
```bash
ssh ff22@192.168.0.100
```

### 2. Container-Status prüfen
```bash
docker ps | grep frontend
```

### 3. In den Frontend Container
```bash
docker exec -it central-control-frontend-prod /bin/sh
```

### 4. Container-Inhalt analysieren
```bash
# Verzeichnisstruktur
ls -la /

# Web-Root finden
find / -name "*.html" -o -name "*.js" -o -name "*.css" 2>/dev/null | head -20

# Nginx/Apache Config
find / -name "nginx.conf" -o -name "httpd.conf" -o -name "*.conf" 2>/dev/null

# Package.json oder ähnliche Config-Dateien
find / -name "package.json" -o -name "*.json" 2>/dev/null | head -10
```

### 5. Web-Interface analysieren
- **URL:** `http://192.168.0.100/de/aps/`
- **Browser DevTools** → Network Tab
- **Commands identifizieren** die das Dashboard sendet

## Erwartete Ergebnisse
- Welche Commands das Original Dashboard anbietet
- Welche MQTT Topics es verwendet
- Welche Payload-Strukturen es sendet
- Welche UI-Elemente es hat

## Protokoll
*Wird während der Analyse gefüllt*

