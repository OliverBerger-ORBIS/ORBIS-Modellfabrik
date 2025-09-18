# Integration Guide - Fischertechnik APS

## Overview

Dieser Guide beschreibt die Integration und Verwaltung der Fischertechnik APS Node-RED Flows.

## Backup and Restore

### Creating Backups

1. **SSH Access**
   ```bash
   ssh ff22@192.168.0.100
   # Password: ff22+
   ```

2. **Backup flows.json**
   ```bash
   cp ~/.node-red/flows.json ~/.node-red/backups/flows_$(date +%Y%m%d_%H%M%S).json
   ```

3. **Backup settings.js**
   ```bash
   cp ~/.node-red/settings.js ~/.node-red/backups/settings_$(date +%Y%m%d_%H%M%S).js
   ```

### Restoring Backups

1. **Stop Node-RED**
   ```bash
   sudo systemctl stop nodered
   ```

2. **Restore files**
   ```bash
   cp ~/.node-red/backups/flows_YYYYMMDD_HHMMSS.json ~/.node-red/flows.json
   cp ~/.node-red/backups/settings_YYYYMMDD_HHMMSS.js ~/.node-red/settings.js
   ```

3. **Start Node-RED**
   ```bash
   sudo systemctl start nodered
   ```

## SSH and Admin API

### SSH Access

- **Host**: 192.168.0.100
- **User**: ff22
- **Password**: ff22+

### Admin API

- **URL**: http://192.168.0.100:1880/admin
- **Authentication**: Basic Auth (ff22/ff22+)

## Troubleshooting

### Common Issues

1. **Node-RED not starting**
   - Check logs: `journalctl -u nodered -f`
   - Verify flows.json syntax
   - Check file permissions

2. **OPC-UA connection issues**
   - Verify module IP addresses
   - Check OPC-UA server status
   - Test with OPC-UA client

3. **MQTT communication problems**
   - Check MQTT broker status
   - Verify topic subscriptions
   - Monitor MQTT traffic

### Maintenance

1. **Regular Backups**
   - Daily automated backups
   - Weekly manual verification
   - Monthly archive cleanup

2. **System Updates**
   - Update Node-RED packages
   - Update system packages
   - Test after updates

3. **Performance Monitoring**
   - Monitor CPU usage
   - Check memory consumption
   - Monitor network traffic
