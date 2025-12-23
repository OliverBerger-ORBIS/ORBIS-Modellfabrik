# WebSocket-Verbindungsproblem - OSF Live-Modus

**Datum:** 23.12.2025  
**Problem:** OSF kann sich im Live-Modus nicht zu den WebSockets verbinden  
**Status:** APS läuft, Fischertechnik-UI funktioniert ✅

## 🚨 Problem-Beschreibung

**Symptom:**
- OSF kann sich im Live-Modus nicht zu den WebSockets verbinden
- APS läuft ✅
- Fischertechnik-UI funktioniert ✅
- Seit Umstellung von OMF3 zu OSF noch nicht getestet

**Konfiguration:**
- **Live Environment:** `192.168.0.100:9001`
- **Username:** `default`
- **Password:** `default`
- **WebSocket URL:** `ws://192.168.0.100:9001`

## 🔍 Mögliche Ursachen

**Wichtig:** Da die Fischertechnik-UI funktioniert, liegt das Problem **NICHT** in der Mosquitto-Konfiguration, sondern in der **OSF-Konfiguration oder im Code**.

### 1. OSF verwendet Authentifizierung, Fischertechnik-UI nicht

**Problem:** OSF versucht mit Username/Password zu verbinden (`default`/`default`), während die Fischertechnik-UI möglicherweise ohne Authentifizierung verbindet.

**Test:** Browser DevTools → Network-Tab → WebSocket-Verbindung der Fischertechnik-UI prüfen:
- Verwendet sie Authentifizierung?
- Welche Headers werden gesendet?
- Welche URL wird verwendet?

### 2. Unterschiedliche WebSocket-URL-Konstruktion

**Problem:** OSF baut die URL als `${mqttHost}:${mqttPort}${mqttPath || ''}` → `192.168.0.100:9001`

**Mögliche Probleme:**
- MQTT.js benötigt möglicherweise einen spezifischen WebSocket-Pfad (z.B. `/mqtt`)
- URL-Format könnte anders sein als erwartet

**Test:** In den Settings-Tab gehen und `mqttPath` auf `/mqtt` setzen

### 3. WebSocket-Pfad fehlt

**Problem:** MQTT.js benötigt manchmal einen spezifischen WebSocket-Pfad (z.B. `/mqtt`)

**Aktuelle Konfiguration:**
```typescript
mqttPath: ''  // Leer
```

**Mögliche Lösung:** Pfad hinzufügen:
```typescript
mqttPath: '/mqtt'  // Oder '/ws' oder '/websocket'
```

**Test:** In den Settings-Tab gehen und `mqttPath` auf `/mqtt` setzen

### 4. Browser-Sicherheitsrichtlinien (Private Network Access)

**Problem:** Moderne Browser blockieren WebSocket-Verbindungen zu privaten IP-Adressen

**Lösung:** Browser-Konsole prüfen auf Fehler wie:
- "Private Network Access"
- "Mixed Content"
- "CORS"

### 5. Port 9001 nicht erreichbar

**Problem:** Port 9001 könnte nicht geöffnet oder blockiert sein

**Test:**
```bash
# Port-Test
nc -vz 192.168.0.100 9001

# Oder mit telnet
telnet 192.168.0.100 9001
```

### 6. Unterschied zu Fischertechnik-UI (WICHTIG!)

**Da die Fischertechnik-UI funktioniert, sollten wir genau analysieren, wie sie sich verbindet:**

1. Browser DevTools → Network-Tab öffnen
2. Fischertechnik-UI öffnen (`http://192.168.0.100`)
3. WebSocket-Verbindung finden (Filter: WS)
4. **Notieren:**
   - WebSocket-URL (z.B. `ws://192.168.0.100:9001` oder `ws://192.168.0.100:9001/mqtt`)
   - Request Headers (besonders `Authorization` oder `Sec-WebSocket-Protocol`)
   - Response Headers
5. **Vergleichen mit OSF:**
   - Verwendet Fischertechnik-UI Authentifizierung?
   - Verwendet sie einen WebSocket-Pfad?
   - Welche Headers werden gesendet?

## 🚨 WICHTIG: Browser-spezifische Verbindungsprobleme (23.12.2025)

### Problem 1: Safari blockiert Zugriff auf `192.168.0.100`
**Problem:** Safari blockiert Zugriff auf `192.168.0.100` und fordert Router-Admin-Login

**Ursache:** Router-Sicherheitsrichtlinie oder Safari Private Network Access Policy

**Lösung:** 
1. Router-Admin-Login durchführen (wie vom User beschrieben)
2. Oder: OSF über lokale Netzwerk-IP statt `localhost` laden (`http://192.168.0.105:4200`)

### Problem 2: Chrome blockiert WebSocket-Verbindung (23.12.2025)
**Problem:** Chrome kann sich nicht zu `192.168.0.100:9001` verbinden, Safari funktioniert ✅

**Symptome:**
- OSF lädt korrekt über `http://192.168.0.105:4200`
- Keine WebSocket-Verbindung zu `192.168.0.100:9001`
- Safari funktioniert ohne Probleme

**Ursache:** Chrome's striktere Private Network Access Policy

**Wer hat das geändert?**
- ❌ **NICHT** unser Code (letzte Änderung: OSF Rebranding am 20.12.2025)
- ✅ **Wahrscheinlich:** Chrome-Update mit strikteren Sicherheitsrichtlinien
- ✅ **Mögliche Ursache:** Chrome's Private Network Access Policy ist strikter als Safari

## 🔧 Debugging-Schritte

### Schritt 1: Browser-Konsole prüfen

1. OSF im Browser öffnen
2. Chrome DevTools → Console öffnen
3. Live-Modus aktivieren
4. Fehlermeldungen notieren

**Erwartete Logs:**
```
[WebSocketMqttAdapter] Attempting to connect to: ws://192.168.0.100:9001
[WebSocketMqttAdapter] Original wsUrl parameter: 192.168.0.100:9001
[WebSocketMqttAdapter] Using authentication with username: default
```

### Schritt 2: Diagnostic Mode aktivieren

1. **Vor dem Laden der App** in der Browser-Konsole:
   ```javascript
   window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true
   ```
2. Seite neu laden
3. Live-Modus aktivieren
4. Alle Logs kopieren

**Was wird getestet:**
- Raw WebSocket-Verbindung (ohne MQTT.js)
- MQTT.js-Verbindungsparameter
- Browser-Informationen

### Schritt 3: Raw WebSocket-Test

**Tool:** `tools/mqtt-debug.html`

1. Tool öffnen: `tools/mqtt-debug.html`
2. URL eingeben: `ws://192.168.0.100:9001`
3. "Test Connection" klicken
4. Ergebnis notieren

**Erwartetes Ergebnis:**
- ✅ Erfolg: "WebSocket connection opened successfully"
- ❌ Fehler: "WebSocket error occurred" oder "Connection timeout"

### Schritt 4: Port-Test

```bash
# Port 9001 testen
nc -vz 192.168.0.100 9001

# Oder mit curl (falls WebSocket-Support)
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://192.168.0.100:9001
```

### Schritt 5: Mosquitto-Logs prüfen

**Auf dem APS-Server (192.168.0.100):**

```bash
# SSH-Verbindung
ssh ff22@192.168.0.100

# Mosquitto-Logs prüfen
tail -f /mosquitto/log/mosquitto.log

# Oder Docker-Logs
docker logs mosquitto
```

**Was zu prüfen:**
- Verbindungsversuche von OSF
- Authentifizierungsfehler
- WebSocket-Upgrade-Fehler

## 🔧 Lösungsansätze

**Wichtig:** Da die Fischertechnik-UI funktioniert, sollten wir **zuerst** analysieren, wie sie sich verbindet, bevor wir Änderungen vornehmen.

### Lösung 1: Vergleich mit Fischertechnik-UI (EMPFOHLEN)

**Schritt 1:** Browser DevTools → Network-Tab → WebSocket-Verbindung analysieren

**Schritt 2:** Unterschiede identifizieren:
- URL-Format
- Authentifizierung
- Headers
- WebSocket-Pfad

**Schritt 3:** OSF-Konfiguration entsprechend anpassen

### Lösung 2: Authentifizierung deaktivieren (nur zum Testen)

**Nur zum Testen, nicht für Produktion!**

**OSF-Konfiguration anpassen:**

```typescript:osf/apps/osf-ui/src/app/services/environment.service.ts
live: {
  mqttHost: '192.168.0.100',
  mqttPort: 9001,
  mqttPath: '',
  mqttUsername: undefined,  // ← Entfernen zum Testen
  mqttPassword: undefined,  // ← Entfernen zum Testen
},
```

**Oder in Settings-Tab:** Username/Password leeren

### Lösung 3: WebSocket-Pfad hinzufügen

**In OSF Settings-Tab:**
- `mqttPath` auf `/mqtt` setzen
- Oder `/ws` oder `/websocket` testen

**Oder in Code ändern:**

```typescript:osf/apps/osf-ui/src/app/services/environment.service.ts
live: {
  mqttHost: '192.168.0.100',
  mqttPort: 9001,
  mqttPath: '/mqtt',  // ← Hinzufügen
  mqttUsername: 'default',
  mqttPassword: 'default',
},
```

**Aber:** Mosquitto benötigt normalerweise keinen Pfad für WebSocket!

### Lösung 4: Browser-Konsole prüfen

**Wichtigster Schritt:** Die Browser-Konsole zeigt die tatsächliche Fehlermeldung!

1. OSF im Browser öffnen
2. Chrome DevTools → Console öffnen
3. Live-Modus aktivieren
4. **Fehlermeldungen notieren:**
   - WebSocket-Verbindungsfehler?
   - Authentifizierungsfehler?
   - Timeout?
   - CORS-Fehler?
   - Private Network Access-Fehler?

## 📋 Checkliste (Priorität)

**Wichtig:** Da die Fischertechnik-UI funktioniert, liegt das Problem in OSF, nicht in Mosquitto!

### Erste Schritte (WICHTIG):
- [ ] **Browser-Konsole prüfen:** Fehlermeldungen bei WebSocket-Verbindung notieren
- [ ] **Fischertechnik-UI analysieren:** Browser DevTools → Network-Tab → WebSocket-Verbindung prüfen
  - [ ] URL notieren
  - [ ] Headers notieren (besonders Authentifizierung)
  - [ ] WebSocket-Pfad prüfen
- [ ] **Vergleich:** OSF-Konfiguration mit Fischertechnik-UI vergleichen

### Weitere Debugging-Schritte:
- [ ] Diagnostic Mode aktivieren: `window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true`
- [ ] Raw WebSocket-Test durchführen (`tools/mqtt-debug.html`)
- [ ] Port 9001 testen (`nc -vz 192.168.0.100 9001`)
- [ ] WebSocket-Pfad testen (`/mqtt`, `/ws`, `/websocket`) - **nur wenn Fischertechnik-UI einen verwendet**
- [ ] Authentifizierung deaktivieren (nur zum Testen) - **nur wenn Fischertechnik-UI keine verwendet**

## 🔗 Verwandte Dokumentation

- [MQTT WebSocket Debug Guide](../../docs/04-howto/mqtt-websocket-debug-guide.md)
- [Mosquitto Setup Guide](../../docs/04-howto/setup/mosquitto/README.md)
- [APS-Mosquitto Integration](./mosquitto/README.md)

## 🔧 Chrome-spezifische Lösungen (23.12.2025)

**Problem:** Chrome blockiert WebSocket-Verbindung, Safari funktioniert ✅

### Lösung 1: Chrome mit deaktivierter Private Network Access starten

**macOS:**
```bash
# Chrome mit deaktivierter PNA starten
open -a "Google Chrome" --args --disable-features=BlockInsecurePrivateNetworkRequests
```

**Windows:**
```bash
# Chrome mit deaktivierter PNA starten
"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-features=BlockInsecurePrivateNetworkRequests
```

**Linux:**
```bash
google-chrome --disable-features=BlockInsecurePrivateNetworkRequests
```

### Lösung 2: Chrome-Flags prüfen

1. Chrome öffnen: `chrome://flags/`
2. Suche nach: `Private Network Access`
3. Deaktiviere: `Block insecure private network requests`
4. Chrome neu starten

### Lösung 3: Chrome DevTools prüfen

1. Chrome DevTools öffnen (F12)
2. Console-Tab → Fehlermeldungen prüfen:
   - `Private Network Access`
   - `CORS`
   - `Mixed Content`
   - `WebSocket connection failed`
3. Network-Tab → Filter "WS" → WebSocket-Verbindung prüfen:
   - Status-Code (z.B. 101 Switching Protocols oder Fehler)
   - Request Headers
   - Response Headers

### Lösung 4: Vergleich Safari vs Chrome

**Da Safari funktioniert, sollten wir prüfen:**

1. **Browser DevTools → Network-Tab:**
   - Safari: WebSocket-Verbindung zu `192.168.0.100:9001` prüfen
   - Chrome: WebSocket-Verbindung zu `192.168.0.100:9001` prüfen
   - Unterschiede notieren (URL, Headers, Status)

2. **Browser-Konsole:**
   - Safari: Fehlermeldungen prüfen
   - Chrome: Fehlermeldungen prüfen
   - Unterschiede notieren

## 📝 Notizen

**Wichtig:**
- ✅ **Safari funktioniert** → **Problem ist Chrome-spezifisch!**
- ✅ Fischertechnik-UI funktioniert → **Problem ist OSF-spezifisch, NICHT Mosquitto!**
- ⚠️ Seit Umstellung von OMF3 zu OSF noch nicht getestet → Möglicherweise Konfigurationsänderung nötig
- ✅ APS läuft → Netzwerk-Verbindung funktioniert grundsätzlich

**Chrome-spezifisches Problem (23.12.2025):**
- OSF lädt korrekt über `http://192.168.0.105:4200`
- Keine WebSocket-Verbindung zu `192.168.0.100:9001` in Chrome
- Safari funktioniert ohne Probleme ✅

**Nächste Schritte (Priorität):**
1. **Chrome DevTools prüfen:** Console- und Network-Tab → Fehlermeldungen notieren
2. **Chrome-Flags testen:** `--disable-features=BlockInsecurePrivateNetworkRequests`
3. **Vergleich Safari vs Chrome:** Browser DevTools → Network-Tab → WebSocket-Verbindung prüfen
4. **Diagnostic Mode aktivieren:** `window.__MQTT_RAW_WEBSOCKET_DIAGNOSTIC = true`
5. **Raw WebSocket-Test:** `tools/mqtt-debug.html` mit `ws://192.168.0.100:9001`

