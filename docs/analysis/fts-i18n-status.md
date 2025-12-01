# FTS Tab - I18n Status

## Übersicht

Dieses Dokument listet alle verwendeten i18n-Keys im FTS/AGV Tab auf und zeigt, welche Übersetzungen fehlen.

## Verwendete i18n-Keys

### Template (HTML) - 27 Keys

| Key | Englisch (Default) | Deutsch | Status |
|-----|-------------------|---------|--------|
| `@@ftsTabHeadline` | AGV Status | ❌ Fehlt | ⚠️ |
| `@@ftsTabDescription` | Real-time status, battery, and route information... | ❌ Fehlt | ⚠️ |
| `@@orderTabFixtureLabel` | Fixture | ✅ Vorhanden | ✅ |
| `@@ftsReplayHint` | Using replay environment - FTS data from MQTT broker | ❌ Fehlt | ⚠️ |
| `@@ftsStatusTitle` | AGV Status | ❌ Fehlt | ⚠️ |
| `@@ftsStatusDriving` | Status / Driving | ❌ Fehlt | ⚠️ |
| `@@ftsStatusStopped` | Stopped | ❌ Fehlt | ⚠️ |
| `@@ftsStatusPaused` | Paused | ❌ Fehlt | ⚠️ |
| `@@ftsStatusLoading` | Loading | ❌ Fehlt | ⚠️ |
| `@@ftsStatusLocation` | Current Location | ❌ Fehlt | ⚠️ |
| `@@ftsStatusOrder` | Active Order | ❌ Fehlt | ⚠️ |
| `@@ftsStatusLastUpdate` | Last Update | ❌ Fehlt | ⚠️ |
| `@@ftsCurrentAction` | Current Action | ❌ Fehlt | ⚠️ |
| `@@ftsRecentActions` | Recent Actions | ❌ Fehlt | ⚠️ |
| `@@ftsBatteryTitle` | Battery Status | ❌ Fehlt | ⚠️ |
| `@@ftsBatteryVoltage` | Current Voltage | ❌ Fehlt | ⚠️ |
| `@@ftsBatteryRange` | Voltage Range | ❌ Fehlt | ⚠️ |
| `@@ftsBatteryCharging` | Charging | ❌ Fehlt | ⚠️ |
| `@@ftsRouteTitle` | Route & Position | ❌ Fehlt | ⚠️ |
| `@@ftsRouteCurrentNode` | Current Node | ❌ Fehlt | ⚠️ |
| `@@ftsRouteStatus` | Status | ❌ Fehlt | ⚠️ |
| `@@ftsActionTimeline` | Action Timeline | ❌ Fehlt | ⚠️ |
| `@@ftsLoadsTitle` | Load Information | ❌ Fehlt | ⚠️ |
| `@@ftsLoadEmpty` | Empty | ❌ Fehlt | ⚠️ |
| `@@ftsNoData` | No FTS data available | ❌ Fehlt | ⚠️ |
| `@@ftsNoDataHint` | Connect to MQTT broker to receive FTS status updates. | ❌ Fehlt | ⚠️ |

### TypeScript - 9 Keys

| Key | Englisch (Default) | Deutsch | Status |
|-----|-------------------|---------|--------|
| `@@ftsLocationUnknown` | Unknown | ❌ Fehlt | ⚠️ |
| `@@ftsLocationIntersection` | Intersection ${nodeId} | ❌ Fehlt | ⚠️ |
| `@@ftsRouteStatusUnknown` | Unknown | ❌ Fehlt | ⚠️ |
| `@@ftsRouteStatusInTransit` | In Transit | ❌ Fehlt | ⚠️ |
| `@@ftsRouteStatusStationary` | Stationary | ❌ Fehlt | ⚠️ |
| `@@ftsStatusNoOrder` | None | ❌ Fehlt | ⚠️ |
| `@@commonYes` | Yes | ✅ Vorhanden | ✅ |
| `@@commonNo` | No | ✅ Vorhanden | ✅ |
| `@@fixtureLabelStartup` | Startup | ✅ Vorhanden | ✅ |
| `@@fixtureLabelMixed` | Mixed | ✅ Vorhanden | ✅ |

## Fehlende Übersetzungen

**Total: 32 Keys fehlen in der deutschen Übersetzung**

### Vorgeschlagene deutsche Übersetzungen

```json
{
  "@@ftsTabHeadline": "AGV Status",
  "@@ftsTabDescription": "Echtzeit-Status, Batterie- und Routeninformationen für das fahrerlose Transportsystem.",
  "@@ftsReplayHint": "Replay-Umgebung aktiv - FTS-Daten vom MQTT-Broker",
  "@@ftsStatusTitle": "AGV Status",
  "@@ftsStatusDriving": "Fahrend",
  "@@ftsStatusStopped": "Gestoppt",
  "@@ftsStatusPaused": "Pausiert",
  "@@ftsStatusLoading": "Ladevorgang",
  "@@ftsStatusLocation": "Aktuelle Position",
  "@@ftsStatusOrder": "Aktiver Auftrag",
  "@@ftsStatusLastUpdate": "Letzte Aktualisierung",
  "@@ftsCurrentAction": "Aktuelle Aktion",
  "@@ftsRecentActions": "Letzte Aktionen",
  "@@ftsBatteryTitle": "Batteriestatus",
  "@@ftsBatteryVoltage": "Aktuelle Spannung",
  "@@ftsBatteryRange": "Spannungsbereich",
  "@@ftsBatteryCharging": "Ladung",
  "@@ftsRouteTitle": "Route & Position",
  "@@ftsRouteCurrentNode": "Aktueller Knoten",
  "@@ftsRouteStatus": "Status",
  "@@ftsActionTimeline": "Aktions-Zeitlinie",
  "@@ftsLoadsTitle": "Ladeinformationen",
  "@@ftsLoadEmpty": "Leer",
  "@@ftsNoData": "Keine FTS-Daten verfügbar",
  "@@ftsNoDataHint": "Verbinden Sie sich mit dem MQTT-Broker, um FTS-Status-Updates zu erhalten.",
  "@@ftsLocationUnknown": "Unbekannt",
  "@@ftsLocationIntersection": "Kreuzung ${nodeId}",
  "@@ftsRouteStatusUnknown": "Unbekannt",
  "@@ftsRouteStatusInTransit": "Unterwegs",
  "@@ftsRouteStatusStationary": "Stationär",
  "@@ftsStatusNoOrder": "Keine"
}
```

## Nächste Schritte

1. ✅ **I18n-Keys dokumentiert** - Alle verwendeten Keys identifiziert
2. ⏳ **Deutsche Übersetzungen hinzufügen** - Fehlende Übersetzungen in `messages.de.json` ergänzen
3. ⏳ **Französische Übersetzungen prüfen** - `messages.fr.json` auf fehlende Keys prüfen
4. ⏳ **I18n-Extraktion ausführen** - `nx extract-i18n` ausführen, um sicherzustellen, dass alle Keys erfasst sind

## Refactoring-Status

- ✅ **FtsRouteService** - Routenberechnung ausgelagert (completed)
- ✅ **FtsAnimationService** - Animation-Logik ausgelagert (completed)
- ✅ **FtsTabComponent** - Von 1388 auf 684 Zeilen reduziert (50% Reduktion)

## Code-Qualität

- ✅ Keine Linter-Fehler
- ✅ Keine TypeScript-Fehler
- ✅ Services korrekt strukturiert
- ⚠️ I18n-Übersetzungen fehlen (32 Keys)

