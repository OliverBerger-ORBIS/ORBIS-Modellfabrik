# MQTT Client Connection – Canonical Guide

Diese Anleitung beschreibt die verbindliche Implementierung und Bedienlogik für die MQTT-Verbindung im OMF2-Dashboard. Sie ersetzt ältere, widersprüchliche Dokumente.

## Komponenten
- Admin MQTT Client: `omf2/admin/admin_mqtt_client.py`
- CCU MQTT Client: `omf2/ccu/ccu_mqtt_client.py`
- Environment-Switch Utility: `omf2/ui/utils/environment_switch.py`
- Sidebar-Anzeige: `omf2/ui/main_dashboard.py` (Connection Status)

## Grundprinzipien
- Verbindung wird stringent über die Sidebar gesteuert.
- Ein Environment-Switch triggert einen sauberen Disconnect, aber keinen Auto-Reconnect.
- Ein (Re-)Connect erfolgt über den Sidebar-Button „Refresh Dashboard“, und nur wenn noch keine Verbindung besteht.
- Admin und CCU verhalten sich identisch in der Connect-Reihenfolge und Anzeige-Initialisierung.

## Initialisierung vor dem ersten Render
- Direkt nach Client-Erzeugung (ohne Verbindung):
  - `self._current_environment = <env>`
  - `cfg = _load_config(<env>)`
  - `self._host = cfg['host']`, `self._port = cfg['port']`
- Effekt: Die Sidebar zeigt bereits beim ersten Render einen deterministischen `Broker: host:port` (nie "unknown"), auch ohne aktive Verbindung oder laufenden Broker.

## Verbindungsaufbau (paho-mqtt)
- Einheitliche Reihenfolge (Admin und CCU):
  - `client.connect_async(host, port, keepalive)`
  - `client.loop_start()`
- Disconnect stets sauber:
  - `client.loop_stop()` und `client.disconnect()`

## Environment-Switch
- Utility: `switch_all_environments(new_env)` ruft `switch_ccu_environment()` und `switch_admin_environment()` auf.
- Verhalten:
  - Sauberer Disconnect und Neuerstellung der Clients.
  - Unmittelbar nach Neuerstellung werden `current_environment` und `host/port` gesetzt (aus Config), damit die Sidebar korrekt rendert.
  - Kein Auto-Reconnect; die UI wird via `request_refresh()` aktualisiert.

## Sidebar-Verhalten (Connection Status)
- Anzeige bezieht sich auf `get_connection_info()` der jeweiligen Clients:
  - Wenn verbunden: Host/Port aus tatsächlichen Client-Parametern.
  - Wenn nicht verbunden: Host/Port aus der Umgebungskonfiguration (nie "unknown").
- „Refresh Dashboard“:
  - Führt einen Connect nur aus, wenn keine aktive Verbindung besteht.
  - Client-ID ändert sich beim Environment-Switch und wird im Status angezeigt.

## Do / Don’t
- Do: Connect ausschließlich über die Sidebar („Refresh Dashboard“), nicht implizit an anderer Stelle.
- Do: `connect_async()` vor `loop_start()` verwenden (beide Clients identisch).
- Do: Vor Connect `current_environment` und `host/port` aus `_load_config()` setzen.
- Don’t: Auto-Connect direkt im Environment-Switch auslösen.
- Don’t: UI-Render starten, bevor `host/port` gesetzt sind (führt zu "unknown").

## Hinweise zu Plattformunterschieden
- Unter Windows führt früheres Rendern häufiger zu Race-Conditions. Durch die oben beschriebene Initialisierung vor dem Render wird `unknown` zuverlässig vermieden.

## Referenzen im Code
- Admin: `get_connection_info()` liefert bei Nicht-Verbindung Werte aus `_load_config(current_env)`.
- CCU: identisches Verhalten.
- Environment-Switch setzt `_current_environment` und `_host/_port` direkt nach Neuerstellung der Clients.


