# Legacy PNG Assets aus origin/main

## 📋 Übersicht

Diese PNG-Dateien wurden aus `omf/dashboard/assets/` des `origin/main` Branches kopiert, um die alten Symbole zu analysieren und mit den neuen SVG-Icons in `omf2/assets/` zu vergleichen.

## 🎨 Verfügbare Icons

### Module-Icons
- `aiqs_icon.png` - AIQS Modul Icon
- `dps_icon.png` - DPS Modul Icon  
- `drill_icon.png` - DRILL Modul Icon
- `fts_icon.jpeg` - FTS Modul Icon (94KB - großes JPEG)
- `hbw_icon.png` - HBW Modul Icon
- `mill_icon.png` - MILL Modul Icon

### System-Icons
- `chrg_icon.png` - Charger Icon
- `machine_icon.png` - Machine Icon (45KB - großes Icon)
- `mosquitto_icon.png` - Mosquitto MQTT Broker Icon (47KB - großes Icon)
- `orbis_logo.png` - ORBIS Logo (20KB)
- `pc-tablet_icon.png` - PC/Tablet Icon
- `platine_icon.png` - Platine Icon
- `router_icon.png` - Router Icon
- `rpi_icon.png` - Raspberry Pi Icon (klein)
- `rpi1_icon.png` - Raspberry Pi Icon (größer, 13KB)
- `txt_icon.png` - TXT Controller Icon

## 🔍 Analyse-Zweck

1. **Icon-Vergleich:** Alte PNG-Icons vs. neue SVG-Icons
2. **Design-Konsistenz:** Stil und Farbgebung prüfen
3. **Größen-Optimierung:** PNG vs. SVG Dateigrößen vergleichen
4. **Missing Icons:** Fehlende Icons identifizieren

## 📊 Dateigrößen-Analyse

- **Kleine Icons (1-4KB):** aiqs, chrg, dps, drill, hbw, mill, pc-tablet, platine, router, rpi, txt
- **Mittlere Icons (10-20KB):** orbis_logo, rpi1
- **Große Icons (40-50KB):** machine_icon, mosquitto_icon
- **Sehr große Icons (90KB+):** fts_icon.jpeg (94KB)

## 🎯 Nächste Schritte

1. Vergleich mit aktuellen SVG-Icons in `omf2/assets/`
2. Identifikation fehlender Icons
3. Entscheidung über Icon-Migration (PNG → SVG)
4. Update der Asset-Manager Konfiguration
