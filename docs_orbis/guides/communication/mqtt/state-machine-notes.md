# State Machine Notes für MQTT Message Templates

## FTS (Fahrerloses Transportsystem) - 5iO4

### Zustandsautomat-Verhalten

#### findInitialDockPosition
- **Verfügbarkeit**: Nur nach Initialisierung verfügbar
- **Verhalten**: Wird nach Ausführung deaktiviert
- **Zweck**: Initiale Positionsfindung für FTS
- **Fischertechnik-Dashboard**: Button wird nach Initialisierung deaktiviert

#### startCharging / stopCharging
- **Verhalten**: Gegenseitig ausschließend
- **Zustandsautomat**: 
  - Wenn `startCharging` aktiv → `stopCharging` verfügbar, `startCharging` deaktiviert
  - Wenn `stopCharging` aktiv → `startCharging` verfügbar, `stopCharging` deaktiviert
- **Zweck**: Verhindert gleichzeitige Ladung und Ladestopp

#### factsheetRequest
- **Verfügbarkeit**: Immer verfügbar
- **Zweck**: Status-Abfrage für dynamische Button-Aktivierung
- **Zukunft**: Wird für Status-Verwaltung verwendet

### Implementierungsnotizen

#### Aktueller Stand
- Alle FTS-Befehle sind immer verfügbar (einfache Implementierung)
- Keine Status-Verwaltung implementiert

#### Geplante Erweiterungen
- **Status-Verwaltung**: Dynamische Button-Aktivierung basierend auf FTS-Status
- **Zustandsautomat**: Implementierung der gegenseitigen Ausschließung
- **Initialisierung**: Automatische Deaktivierung nach `findInitialDockPosition`

## Module - Direkte vs. Event-getriggerte Befehle

### Direkte Befehle (DRILL, MILL, AIQS, FTS)
- **Standard-Sequenz**: PICK → PROCESS → DROP
- **orderUpdateId**: Inkrementell pro Modul
- **Verfügbarkeit**: Alle Befehle immer verfügbar
- **MQTT Control Tab**: ✅ Verfügbar

### Event-getriggerte Module (HBW, DPS)
- **HBW**: Wird durch Bestellungen getriggert (nicht direkte Befehle)
- **DPS**: Wird durch manuellen Wareneingang getriggert (nicht direkte Befehle)
- **MQTT Control Tab**: ❌ Nicht verfügbar (keine direkten Befehle)

### Nicht unterstützte Module (CHRG)
- **CHRG**: Befehle machen keinen Sinn
- **MQTT Control Tab**: ❌ Entfernt

### Implementierungsnotizen
- **Bewährte Methode**: `send_process_sequence_command`
- **MQTT-Integration**: Über bewährte `send_mqtt_message_direct`
- **UUID-Generierung**: Automatisch für orderId und action.id

## Factory Reset

### Verhalten
- **Verfügbarkeit**: Immer verfügbar
- **Optionen**: `withStorage` (HBW-Storage löschen/behalten)
- **Warnung**: Bei `withStorage=true` wird HBW-Storage gelöscht

### Implementierungsnotizen
- **Template-basiert**: Verwendet `message_template_manager`
- **MQTT-Integration**: Über bewährte `send_mqtt_message_direct`

## Zukunftsvision

### Status-basierte UI
- **Dynamische Buttons**: Basierend auf aktuellen Modul-Status
- **Zustandsautomat**: Implementierung für alle Module
- **Real-time Updates**: Live-Status-Updates im Dashboard

### Erweiterte Validierung
- **Befehl-Validierung**: Prüfung ob Befehle im aktuellen Zustand ausführbar sind
- **Sequenz-Validierung**: Prüfung der korrekten Befehlsreihenfolge
- **Fehlerbehandlung**: Verbesserte Fehlerbehandlung und -meldungen
