# Factory Reset und Order Trigger Features

## Übersicht

Neue Features für die direkte Steuerung der APS-Fabrik über MQTT:
1. **Factory Reset** - Zurücksetzen der gesamten Fabrik über Dashboard
2. **Order Trigger Script** - Auftragsauslösung über MQTT ohne Dashboard

## 1. Factory Reset im Dashboard

### Funktion
- **Ort:** Module Overview Tab
- **Zweck:** Zurücksetzen der gesamten APS-Fabrik
- **MQTT Topic:** `ccu/set/reset`

### Verwendung
1. **MQTT-Verbindung herstellen** über Sidebar
2. **Module Overview Tab** öffnen
3. **"Fabrik zurücksetzen"** expandieren
4. **Option wählen:**
   - ☐ Mit Storage (HBW-Storage löschen)
   - ☑ Ohne Storage (HBW-Storage beibehalten)
5. **Bestätigung:**
   - ✅ **JA - Zurücksetzen** (führt Reset aus)
   - ❌ **NEIN - Abbrechen** (bricht ab)

### MQTT-Nachricht
```json
{
  "timestamp": "2025-08-25T07:39:05.581Z",
  "withStorage": false
}
```

### Sicherheitshinweise
- ⚠️ **WARNUNG:** Stoppt alle laufenden Module
- ⚠️ **WARNUNG:** Bricht laufende Aufträge ab
- ⚠️ **WARNUNG:** Mit Storage löscht HBW-Daten

## 2. Order Trigger System

### Dashboard Integration
- **Ort:** MQTT Control Tab → Steuerungsmethode "Bestellung"
- **Zweck:** Direkte Bestellung über Dashboard
- **MQTT Topic:** `/j1/txt/1/f/o/order` (Browser Format)

### Verwendung im Dashboard
1. **MQTT-Verbindung herstellen** über Sidebar
2. **MQTT Control Tab** öffnen
3. **Steuerungsmethode:** "Bestellung" auswählen
4. **Zwei Optionen:**
   - **🚀 Bestellung-Trigger:** Alle Buttons aktiv (ohne HBW-Status)
   - **📦 Bestellung (mit HBW-Status):** Nur verfügbare Werkstücke

### Browser Order Format
**MQTT Topic:** `/j1/txt/1/f/o/order`
**Payload:**
```json
{
  "type": "COLOR",
  "ts": "2024-01-01T12:00:00.000Z"
}
```

**Farben:** RED, WHITE, BLUE

### Orchestrierung
- **CCU koordiniert** automatisch alle Module
- **Keine manuelle Steuerung** einzelner Module nötig
- **Automatische Produktionskette** wird gestartet

### Order Trigger Script (Legacy)
- **Datei:** `src_orbis/mqtt/tools/test_order_trigger.py` (gelöscht)
- **Zweck:** Auftragsauslösung über MQTT ohne Dashboard
- **MQTT Topics:** 
  - `/j1/txt/1/f/i/order` (TXT Controller)
  - `ccu/order/active` (CCU)

### Verwendung

#### Basis-Kommando:
```bash
python src_orbis/mqtt/tools/test_order_trigger.py
```

#### Mit Parametern:
```bash
python src_orbis/mqtt/tools/test_order_trigger.py \
  --broker 192.168.1.100 \
  --order-type WARE_EINGANG \
  --color WHITE \
  --workpiece-id W1
```

#### CCU Order:
```bash
python src_orbis/mqtt/tools/test_order_trigger.py \
  --order-type AUFTRAG \
  --ccu
```

### Parameter

| Parameter | Beschreibung | Standard | Optionen |
|-----------|--------------|----------|----------|
| `--broker` | MQTT Broker Host | 192.168.1.100 | IP-Adresse |
| `--port` | MQTT Broker Port | 1883 | Port-Nummer |
| `--order-type` | Auftragstyp | WARE_EINGANG | WARE_EINGANG, AUFTRAG, AI_NOT_OK |
| `--color` | Werkstück-Farbe | WHITE | WHITE, RED, BLUE |
| `--workpiece-id` | Werkstück-ID | W1 | Beliebige ID |
| `--ccu` | Via CCU senden | False | Flag |

### MQTT-Nachrichten

#### TXT Controller Order:
```json
{
  "ts": "2025-08-25T07:39:05.662Z",
  "state": "WAITING_FOR_ORDER",
  "orderType": "WARE_EINGANG",
  "workpieceColor": "WHITE",
  "workpieceId": "W1",
  "orderId": "uuid-here"
}
```

#### CCU Order:
```json
{
  "orderId": "uuid-here",
  "orderType": "WARE_EINGANG",
  "timestamp": "2025-08-25T07:39:05.662Z",
  "metadata": {
    "priority": "NORMAL",
    "timeout": 300
  }
}
```

## 3. Test-Szenarien

### Szenario 1: Factory Reset
1. **Dashboard öffnen** und MQTT verbinden
2. **Module Overview** Tab wählen
3. **"Fabrik zurücksetzen"** expandieren
4. **"Mit Storage"** aktivieren
5. **"JA - Zurücksetzen"** klicken
6. **MQTT-Explorer** beobachten für `ccu/set/reset`

### Szenario 2: Wareneingang Order
```bash
python src_orbis/mqtt/tools/test_order_trigger.py \
  --order-type WARE_EINGANG \
  --color WHITE \
  --workpiece-id W1
```

### Szenario 3: Auftrag Order
```bash
python src_orbis/mqtt/tools/test_order_trigger.py \
  --order-type AUFTRAG \
  --color RED \
  --workpiece-id R1
```

### Szenario 4: CCU Order
```bash
python src_orbis/mqtt/tools/test_order_trigger.py \
  --order-type AI_NOT_OK \
  --ccu
```

## 4. Monitoring

### MQTT-Explorer Topics
- `ccu/set/reset` - Reset-Befehle
- `ccu/order/active` - Aktive Aufträge
- `ccu/order/completed` - Abgeschlossene Aufträge
- `/j1/txt/1/f/i/order` - TXT Controller Orders
- `module/v1/ff/+/state` - Module Status

### Dashboard Monitoring
- **Module Overview:** Zeigt Reset-Status
- **MQTT Monitor:** Zeigt gesendete Nachrichten
- **MQTT Analyse:** Zeigt Nachrichten-Historie

## 5. Fehlerbehebung

### Häufige Probleme

#### MQTT-Verbindung fehlgeschlagen
```bash
# Broker-Adresse prüfen
ping 192.168.1.100

# Port prüfen
telnet 192.168.1.100 1883
```

#### Order wird nicht verarbeitet
1. **MQTT-Explorer** öffnen
2. **Topic** `/j1/txt/1/f/i/order` beobachten
3. **Nachricht** auf korrekte Struktur prüfen
4. **TXT Controller** Status prüfen

#### Reset funktioniert nicht
1. **CCU Status** prüfen
2. **Topic** `ccu/set/reset` beobachten
3. **Payload** auf korrekte Struktur prüfen

## 6. Nächste Schritte

### Geplante Erweiterungen
- [ ] **Reset-Status Monitoring** im Dashboard
- [ ] **Order-Status Tracking** für gesendete Aufträge
- [ ] **Batch-Orders** für mehrere Werkstücke
- [ ] **Order-Templates** für häufige Szenarien
- [ ] **Integration** in Template Message Manager

### Verbesserungen
- [ ] **Bessere Fehlerbehandlung** für MQTT-Verbindungen
- [ ] **Retry-Mechanismus** für fehlgeschlagene Orders
- [ ] **Order-Validierung** vor dem Senden
- [ ] **Logging** für alle Aktionen
