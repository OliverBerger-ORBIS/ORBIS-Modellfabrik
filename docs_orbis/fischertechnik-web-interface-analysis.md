# Fischertechnik Web Interface Analysis

## 🎯 **Ziel**
Das Fischertechnik Web-Interface unter `http://192.168.0.100/de/aps/factory/dashboard` analysieren, um zu verstehen, wie Orders und Module-Befehle funktionieren.

## 🔍 **Analyse-Methoden**

### **1. MQTT-Traffic Analyse**
- **Session Logger starten:** `fischertechnik_web_test`
- **Web-Interface verwenden** für Order-Erstellung
- **MQTT-Traffic aufzeichnen** und analysieren

### **2. Browser Developer Tools**
- **F12** drücken um Developer Tools zu öffnen
- **Network Tab** aktivieren
- **Rotes Werkstück beauftragen** über Web-Interface
- **HTTP-Requests** analysieren

## 📋 **Schritt-für-Schritt Anleitung**

### **Schritt 1: Session Logger starten**
```bash
python src_orbis/mqtt/loggers/aps_session_logger.py --session-label fischertechnik_web_test --process-type custom --auto-start
```

### **Schritt 2: Browser Developer Tools**
1. **Browser öffnen:** http://192.168.0.100/de/aps/factory/dashboard
2. **F12** drücken für Developer Tools
3. **Network Tab** auswählen
4. **"Preserve log"** aktivieren
5. **"XHR"** Filter aktivieren

### **Schritt 3: Order über Web-Interface**
1. **Rotes Werkstück auswählen**
2. **"Beauftragen"** oder "Order" Button klicken
3. **HTTP-Requests** im Network Tab beobachten
4. **Request/Response Details** analysieren

### **Schritt 4: MQTT-Traffic beobachten**
1. **Session Logger** läuft parallel
2. **MQTT-Traffic** wird aufgezeichnet
3. **Module-Reaktionen** beobachten

### **Schritt 5: Analyse**
1. **Session Logger stoppen** mit 'q'
2. **Analyse-Script ausführen:**
   ```bash
   python src_orbis/mqtt/tools/analyze_fischertechnik_web_session.py
   ```

## 🔍 **Was wir suchen**

### **HTTP-Requests:**
- **POST/PUT Requests** für Order-Erstellung
- **Request Headers** und Authentication
- **Request Body** mit Order-Daten
- **Response Codes** und Daten

### **MQTT-Topics:**
- **Order-Topics** die verwendet werden
- **Module-Befehle** die gesendet werden
- **Status-Updates** von Modulen
- **Workflow-Sequenzen**

### **Order-Formate:**
- **Exakte JSON-Struktur** der Orders
- **Required Fields** und Validierung
- **Module-spezifische Parameter**
- **Timing und Sequenzen**

## 📊 **Erwartete Erkenntnisse**

### **Order-Workflow:**
1. **HTTP-Request** an Fischertechnik-Server
2. **MQTT-Order** wird generiert
3. **Module-Befehle** werden gesendet
4. **Status-Updates** werden empfangen

### **Module-Kontrolle:**
- **Welche Topics** für Module-Befehle
- **Welche Parameter** erforderlich sind
- **Welche Sequenzen** ausgeführt werden

### **Integration:**
- **Wie unser Dashboard** die gleichen Befehle senden kann
- **Welche Unterschiede** es gibt
- **Welche Verbesserungen** möglich sind

## 🚀 **Nächste Schritte**

Nach der Analyse können wir:
1. **Exakte Order-Formate** in unser Dashboard integrieren
2. **Module-Befehle** entsprechend anpassen
3. **Workflow-Sequenzen** implementieren
4. **Fehlerbehandlung** verbessern

## 📝 **Notizen**

- **Session Logger** läuft parallel zum Browser
- **Developer Tools** zeigen HTTP-Traffic
- **MQTT-Traffic** wird in SQLite gespeichert
- **Analyse-Script** wertet beide aus
