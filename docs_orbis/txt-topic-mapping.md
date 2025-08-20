# TXT Topic Mapping Documentation

## Übersicht

Das ORBIS Dashboard unterstützt jetzt vollständige friendly-topic Mappings für alle TXT-Controller Topics.

## TXT Topic Struktur

### Grundstruktur
```
/j1/txt/1/{type}/{direction}/{action}
```

### Topic-Typen

#### 1. F-Topics (Function Topics)
**Format:** `/j1/txt/1/f/{direction}/{action}`

**Beispiele:**
- `/j1/txt/1/f/i/stock` → `TXT : f : i : stock`
- `/j1/txt/1/f/o/order` → `TXT : f : o : order`
- `/j1/txt/1/f/i/order` → `TXT : f : i : order`
- `/j1/txt/1/f/i/config/hbw` → `TXT : f : i : config : hbw`

**Richtungen:**
- `i` = Input (Eingang)
- `o` = Output (Ausgang)

#### 2. C-Topics (Control Topics)
**Format:** `/j1/txt/1/c/{sensor}`

**Beispiele:**
- `/j1/txt/1/c/bme680` → `TXT : c : bme680`
- `/j1/txt/1/c/cam` → `TXT : c : cam`
- `/j1/txt/1/c/ldr` → `TXT : c : ldr`

#### 3. I-Topics (Input Topics)
**Format:** `/j1/txt/1/i/{sensor}`

**Beispiele:**
- `/j1/txt/1/i/bme680` → `TXT : i : bme680`
- `/j1/txt/1/i/broadcast` → `TXT : i : broadcast`
- `/j1/txt/1/i/cam` → `TXT : i : cam`
- `/j1/txt/1/i/ldr` → `TXT : i : ldr`

#### 4. O-Topics (Output Topics)
**Format:** `/j1/txt/1/o/{action}`

**Beispiele:**
- `/j1/txt/1/o/broadcast` → `TXT : o : broadcast`

## Implementierung

### Statische Mappings
```python
TXT_TOPIC_MAPPINGS = {
    # F-Topics (Function topics)
    "/j1/txt/1/f/i/stock": "TXT : f : i : stock",
    "/j1/txt/1/f/o/order": "TXT : f : o : order",
    # ... weitere Mappings
}
```

### Dynamische Pattern-Erkennung
```python
# F-Topics (Function topics)
match = re.match(r"/j1/txt/1/f/([io])/([^/]+)", topic)
if match:
    direction, action = match.groups()
    return f"TXT : f : {direction} : {action}"

# F-Topics with config
match = re.match(r"/j1/txt/1/f/([io])/config/([^/]+)", topic)
if match:
    direction, config = match.groups()
    return f"TXT : f : {direction} : config : {config}"

# C-Topics (Control topics)
match = re.match(r"/j1/txt/1/c/([^/]+)", topic)
if match:
    sensor = match.group(1)
    return f"TXT : c : {sensor}"

# I-Topics (Input topics)
match = re.match(r"/j1/txt/1/i/([^/]+)", topic)
if match:
    sensor = match.group(1)
    return f"TXT : i : {sensor}"

# O-Topics (Output topics)
match = re.match(r"/j1/txt/1/o/([^/]+)", topic)
if match:
    action = match.group(1)
    return f"TXT : o : {action}"
```

## Gefundene TXT Topics in Sessions

### Aktuelle Sessions (26 Datenbanken)
```
📋 Found 12 unique TXT topics:
  /j1/txt/1/c/bme680
  /j1/txt/1/c/cam
  /j1/txt/1/c/ldr
  /j1/txt/1/f/i/config/hbw
  /j1/txt/1/f/i/order
  /j1/txt/1/f/i/stock
  /j1/txt/1/f/o/order
  /j1/txt/1/i/bme680
  /j1/txt/1/i/broadcast
  /j1/txt/1/i/cam
  /j1/txt/1/i/ldr
  /j1/txt/1/o/broadcast
```

## Dashboard Integration

### Filter-Komponente
- Alle TXT-Topics werden in der Topic-Auswahl als friendly names angezeigt
- Alphabetische Sortierung der Topics
- Konsistente Darstellung im gesamten Dashboard

### MQTT-Analyse
- TXT-Topics werden benutzerfreundlich in Tabellen angezeigt
- Filterung nach TXT-Topics möglich
- Zeitstempel-Analyse für TXT-Nachrichten

## Erweiterbarkeit

### Neue TXT-Topics hinzufügen
1. **Statisches Mapping:** Fügen Sie das Topic zu `TXT_TOPIC_MAPPINGS` hinzu
2. **Dynamisches Pattern:** Neue Topics werden automatisch erkannt, wenn sie dem bestehenden Pattern folgen

### Beispiel für neue Topics
```python
# Neue F-Topic
"/j1/txt/1/f/i/status": "TXT : f : i : status"

# Neue C-Topic
"/j1/txt/1/c/temperature": "TXT : c : temperature"

# Neue I-Topic
"/j1/txt/1/i/button": "TXT : i : button"

# Neue O-Topic
"/j1/txt/1/o/led": "TXT : o : led"
```

## Vorteile

1. **Benutzerfreundlichkeit:** Verständliche Topic-Namen statt technischer Pfade
2. **Konsistenz:** Einheitliche Namensgebung für alle TXT-Topics
3. **Erweiterbarkeit:** Automatische Erkennung neuer Topics
4. **Wartbarkeit:** Zentrale Konfiguration in `topic_mapping.py`
5. **Filterung:** Einfache Filterung nach Topic-Typen im Dashboard

## Status

✅ **Vollständig implementiert**
- Alle bekannten TXT-Topics werden unterstützt
- Dynamische Pattern-Erkennung funktioniert
- Dashboard-Integration abgeschlossen
- Tests erfolgreich durchgeführt
