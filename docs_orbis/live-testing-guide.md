# 🚀 Live Testing Guide - Template Message Manager

## 📋 Übersicht

Dieser Guide beschreibt die Schritte für das Live-Testing des Template Message Managers mit der echten APS-Anlage im Büro.

## ✅ Voraussetzungen

- ✅ Dashboard läuft auf Port 8501
- ✅ Template Message Manager vollständig implementiert
- ✅ 9 Templates für alle Workflow-Typen verfügbar
- ✅ MQTT-Verbindung zu APS (192.168.0.100:1883) konfiguriert

## 🎯 Live-Test Schritte

### 1. Dashboard Zugriff
```
URL: http://localhost:8501
Status: ✅ Läuft
```

### 2. Template Control Tab
Navigieren Sie zum **"🚀 Wareneingang Control"** Tab im Dashboard.

### 3. Wareneingang Test
1. **Werkstück-Farbe auswählen:** RED, WHITE oder BLUE
2. **Werkstück-ID eingeben:** NFC-gelesene ID oder Test-ID
3. **"🚀 Wareneingang starten"** Button klicken

### 4. Order Tracking
- Wechseln Sie zum **"📊 Order Tracking"** Tab
- Überwachen Sie die ORDER-ID Generierung
- Verfolgen Sie den Workflow-Status

### 5. Template Library
- Wechseln Sie zum **"📚 Template Library"** Tab
- Überprüfen Sie alle 9 verfügbaren Templates

## 🔧 MQTT-Verbindung

### Broker-Konfiguration
```yaml
# config/credentials.yml
mqtt_brokers:
  - name: "APS Local"
    host: "192.168.0.100"
    port: 1883
    username: "default"
    password: "default"
```

### Verbindung testen
```bash
# MQTT-Verbindung testen
mosquitto_pub -h 192.168.0.100 -p 1883 -u default -P default -t "test/topic" -m "test"
```

## 📊 Erwartete Ergebnisse

### Wareneingang Workflow
1. **Template gesendet:** Wareneingang Trigger
2. **CCU Response:** ORDER-ID generiert
3. **Workflow Start:** HBW → Lagerung
4. **Status Update:** Order Tracking aktiv

### Order Tracking
- **Aktive Orders:** 1-3 Orders pro Session
- **Farb-Verteilung:** ROT/WEISS/BLAU
- **Workflow-Status:** PICK → PROCESS → PLACE

## 🚨 Troubleshooting

### MQTT-Verbindung fehlschlägt
1. **APS-Netzwerk prüfen:** 192.168.0.100 erreichbar?
2. **MQTT-Broker Status:** Port 1883 offen?
3. **Credentials:** default/default korrekt?

### Template nicht gesendet
1. **MQTT Client Status:** Verbunden?
2. **Template Parameter:** Alle erforderlichen Felder ausgefüllt?
3. **Topic Format:** Korrektes MQTT-Topic?

### Order Tracking funktioniert nicht
1. **CCU Response:** ORDER-ID generiert?
2. **Message Handler:** CCU Responses registriert?
3. **Database:** Session-Daten gespeichert?

## 📈 Erfolgs-Metriken

### Phase 1 Ziele
- [ ] Wareneingang Template erfolgreich gesendet
- [ ] CCU generiert ORDER-ID
- [ ] Order Tracking funktional
- [ ] Dashboard zeigt aktive Orders

### Phase 2 Ziele
- [ ] Alle 9 Templates getestet
- [ ] Workflow-Status Updates
- [ ] Error-Handling validiert
- [ ] Performance-Monitoring aktiv

## 🔗 Nächste Schritte

Nach erfolgreichem Live-Test:
1. **Auftrag Templates** testen (Produktions-Workflows)
2. **AI-not-ok Templates** testen (Fehler-Szenarien)
3. **Batch Processing** implementieren
4. **Advanced Analytics** aktivieren

---

**Status:** ✅ **Bereit für Live-Test** - Dashboard läuft, Templates implementiert, MQTT konfiguriert! 🚀
