# Auftragssteuerung-Analyse

## Übersicht

Die Auftragssteuerung in der APS-Fabrik erfolgt über verschiedene Protokolle und Schnittstellen. Diese Dokumentation beschreibt den systematischen Ansatz zur Analyse der Auftragsverwaltung.

## Problemstellung

Die bisherige Analyse hat gezeigt, dass:
- Bestellungen über den Web-Server ausgelöst werden
- HTTP-POST Requests nicht die erwarteten Order-Requests enthalten
- Die Auftragssteuerung möglicherweise über andere Protokolle erfolgt

## Analyse-Ansatz

### 1. Erweiterte HTTP-Analyse

#### Enhanced HTTP Logger
- **Datei:** `src_orbis/mqtt/tools/enhanced_http_logger.py`
- **Funktion:** Testet alle HTTP-Methoden (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- **Endpunkte:** 
  - `/api/orders`
  - `/j1/txt/1/f/i/order`
  - `/fischertechnik/order/start`
  - `/order/start`
  - `/api/order/start`

#### Browser Proxy Logger
- **Datei:** `src_orbis/mqtt/tools/browser_proxy_logger.py`
- **Funktion:** Erfasst tatsächlichen Browser-Traffic
- **Voraussetzung:** mitmproxy Installation
- **Proxy:** 127.0.0.1:8080

### 2. WebSocket-Analyse

#### WebSocket-Monitoring
- **Endpunkte:**
  - `ws://192.168.0.100/ws`
  - `ws://192.168.0.100/websocket`
  - `ws://192.168.0.100/socket.io`
  - `wss://192.168.0.100/ws`

#### Mögliche WebSocket-Szenarien
- Real-time Order-Updates
- Live-Status-Updates
- Event-driven Order-Management

### 3. MQTT-Korrelation

#### Order-bezogene MQTT-Topics
- `ccu/order/request`
- `ccu/order/response`
- `module/v1/ff/*/order`
- `fischertechnik/order/start`

## Verwendung

### 1. Comprehensive Analysis Session starten

```bash
# Alle Logger starten
python src_orbis/mqtt/tools/start_comprehensive_analysis_session.py --session order_analysis_test

# Ohne Browser Proxy
python src_orbis/mqtt/tools/start_comprehensive_analysis_session.py --session order_analysis_test --no-browser-proxy
```

### 2. Enhanced HTTP Logger einzeln

```bash
# Enhanced HTTP Logger
python src_orbis/mqtt/tools/enhanced_http_logger.py --session order_test --duration 600
```

### 3. Browser Proxy Logger

```bash
# Browser Proxy Logger (erfordert mitmproxy)
python src_orbis/mqtt/tools/browser_proxy_logger.py --session order_test --port 8080
```

### 4. Analyse durchführen

```bash
# Enhanced HTTP Session analysieren
python src_orbis/mqtt/tools/analyze_enhanced_http_session.py order_analysis_test
```

## Erwartete Erkenntnisse

### HTTP-Methoden
- **POST:** Standard für Order-Erstellung
- **PUT:** Order-Updates
- **PATCH:** Teilweise Order-Updates
- **GET:** Order-Status-Abfragen

### WebSocket-Nachrichten
- Order-Status-Updates
- Real-time Notifications
- Event-Streams

### MQTT-Korrelation
- Order-Requests von Web-Server
- Order-Responses an Module
- Status-Updates

## Mögliche Auftragssteuerung-Szenarien

### Szenario 1: HTTP-basierte Steuerung
```
Browser → HTTP POST/PUT → Web-Server → MQTT → CCU → Module
```

### Szenario 2: WebSocket-basierte Steuerung
```
Browser → WebSocket → Web-Server → MQTT → CCU → Module
```

### Szenario 3: Hybrid-Ansatz
```
Browser → HTTP (Order-Creation) → WebSocket (Status-Updates) → MQTT (Module-Control)
```

## Analyse-Schritte

### Schritt 1: Baseline-Analyse
1. Enhanced HTTP Logger starten
2. Web-Server aufrufen
3. Bestellung durchführen
4. Logger stoppen und analysieren

### Schritt 2: Browser-Proxy-Analyse
1. mitmproxy installieren
2. Browser Proxy Logger starten
3. Browser für Proxy konfigurieren
4. Bestellung durchführen
5. Echten Traffic analysieren

### Schritt 3: MQTT-Korrelation
1. MQTT-Logs mit HTTP-Logs korrelieren
2. Order-bezogene Topics identifizieren
3. Timing-Analyse durchführen

### Schritt 4: WebSocket-Analyse
1. WebSocket-Verbindungen identifizieren
2. Nachrichten-Format analysieren
3. Order-bezogene Events finden

## Erwartete Order-Formate

### HTTP Order Request
```json
{
  "orderType": "WARE_EINGANG",
  "workpieceId": "R1",
  "targetModule": "HBW",
  "priority": "normal",
  "timestamp": "2025-08-25T16:30:00Z"
}
```

### WebSocket Order Update
```json
{
  "type": "order_update",
  "orderId": "uuid-123",
  "status": "processing",
  "module": "HBW",
  "timestamp": "2025-08-25T16:30:05Z"
}
```

### MQTT Order Command
```json
{
  "orderId": "uuid-123",
  "action": "PICK",
  "workpieceId": "R1",
  "targetModule": "HBW"
}
```

## Troubleshooting

### Keine Order-Requests gefunden
1. Browser Proxy Logger verwenden
2. Verschiedene HTTP-Methoden testen
3. WebSocket-Verbindungen prüfen
4. MQTT-Topics erweitern

### WebSocket nicht verfügbar
1. Verschiedene Ports testen
2. SSL/TLS-Verbindungen prüfen
3. Firewall-Einstellungen kontrollieren

### MQTT-Korrelation schwierig
1. Timing-Analyse durchführen
2. Order-IDs korrelieren
3. Topic-Patterns erweitern

## Nächste Schritte

1. **Comprehensive Analysis Session** starten
2. **Bestellung über Web-Server** durchführen
3. **Alle Protokolle** gleichzeitig erfassen
4. **Korrelation** zwischen HTTP, WebSocket und MQTT
5. **Order-Management-Protokoll** identifizieren

## Tools und Skripte

- `start_comprehensive_analysis_session.py` - Alle Logger starten
- `enhanced_http_logger.py` - Erweiterte HTTP-Analyse
- `browser_proxy_logger.py` - Browser-Traffic erfassen
- `analyze_enhanced_http_session.py` - HTTP-Logs analysieren
- `aps_session_logger.py` - MQTT-Logs erfassen

## Status

🔄 **In Entwicklung**
- Enhanced HTTP Logger implementiert
- Browser Proxy Logger implementiert
- Comprehensive Analysis Session implementiert
- Analyse-Tools implementiert

⏳ **Nächste Schritte**
- Comprehensive Analysis Session testen
- Bestellung über Web-Server durchführen
- Alle Protokolle korrelieren
- Order-Management-Protokoll identifizieren
