# Decision Record: MQTT Connection-Loop Prevention

**Datum:** 2025-09-25  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard hatte ein Problem mit mehrfachen MQTT-Verbindungen zum Replay-Broker, das zu "Client already connected, closing old connection" Fehlern führte.

---

## Problem

**Connection-Loop:** Ständige Neuverbindungen des MQTT-Clients ohne saubere Trennung alter Verbindungen, was zu:
- Mehrfachen Verbindungen zum gleichen Broker
- "Client already connected, closing old connection" Fehlern im Mosquitto-Log
- Instabiler MQTT-Verbindung
- Unerwarteten "received" Nachrichten durch Retained Messages

## Root Cause Analysis

Das Problem trat auf, weil:
1. **Fehlende strenge Prüfung** auf Environment-Wechsel
2. **Unvollständige Trennung** alter MQTT-Verbindungen
3. **Fehlender Fallback-Mechanismus** bei Reconnect-Fehlern

## Entscheidung

**Strenge Prüfung und saubere Verbindungsbehandlung** in `ensure_dashboard_client()` implementieren:

```python
def ensure_dashboard_client(env: str, store: MutableMapping) -> OmfMqttClient:
    """Singleton-Client für die Session mit strenger Environment-Prüfung"""
    cli = store.get("mqtt_client")
    stored_env = store.get("mqtt_env")
    
    if cli is None:
        # Erstinitialisierung
        cli = OmfMqttClient(cfg)
        cli.connect()
        store["mqtt_client"] = cli
        store["mqtt_env"] = env
        return cli

    # Strenge Prüfung auf Environment-Wechsel
    env_changed = stored_env != env
    
    if env_changed:
        # Umgebung gewechselt -> sauberer Reconnect statt Neuaufbau
        try:
            # Altes Objekt aus Session State entfernen (doppelte Handles vermeiden)
            old_cli = store.get("mqtt_client")
            if old_cli and hasattr(old_cli, 'client'):
                old_cli.client.loop_stop()
                old_cli.client.disconnect()
            
            cli.reconnect(cfg)
            store["mqtt_env"] = env
            
            # Optional: Verlauf leeren
            if hasattr(cli, "clear_history"):
                cli.clear_history()
        except Exception as e:
            # Fallback: Neuen Client erstellen
            cli = OmfMqttClient(cfg)
            cli.connect()
            store["mqtt_client"] = cli
            store["mqtt_env"] = env
    
    return cli
```

## Kritische Regeln

### 1. **MQTT-Client Singleton-Pattern**
- Der MQTT-Client darf **nur einmal pro Session und pro Umgebung (env)** aufgebaut werden
- `ensure_dashboard_client()` ist die **einzige** Funktion, die MQTT-Clients erstellt
- **Niemals** direkte `OmfMqttClient()` Instanzen in Komponenten erstellen

### 2. **Strenge Environment-Prüfung**
- **Immer** `stored_env != env` prüfen vor Reconnect
- **Nur bei echtem Environment-Wechsel** Reconnect durchführen
- **Bestehenden Client zurückgeben** wenn kein Wechsel

### 3. **Saubere Verbindungsbehandlung**
- **Alte Verbindung trennen:** `old_cli.client.loop_stop()` und `old_cli.client.disconnect()`
- **Reconnect statt Neuaufbau:** `cli.reconnect(cfg)` verwenden
- **Fallback-Mechanismus:** Bei Reconnect-Fehlern neuen Client erstellen

### 4. **Zentrale Verwendung**
- `ensure_dashboard_client()` **nur** in `omf_dashboard.py` aufrufen
- **Nicht** in Komponenten oder bei jedem Rendern
- Alle Komponenten verwenden `st.session_state.get("mqtt_client")`

### 5. **Verbotene Patterns**
- ❌ `OmfMqttClient(cfg)` in Komponenten
- ❌ `create_ephemeral()` in Komponenten  
- ❌ `get_omf_mqtt_client()` in Komponenten
- ❌ Mehrfache `ensure_dashboard_client()` Aufrufe

## Konsequenzen

### Positiv:
- **Stabile MQTT-Verbindung:** Keine Connection-Loops mehr
- **Ressourceneffizienz:** Nur eine Verbindung pro Environment
- **Robustheit:** Fallback-Mechanismus bei Fehlern
- **Konsistenz:** Einheitliche Verbindungsbehandlung
- **Debugging:** Klare Logging-Nachrichten

### Negativ:
- **Komplexität:** Zusätzliche Prüfungen und Fehlerbehandlung
- **Abhängigkeit:** Strikte Einhaltung der Regeln erforderlich

## Implementierung

- [x] Strenge Environment-Prüfung in `ensure_dashboard_client()`
- [x] Saubere Trennung alter Verbindungen
- [x] Fallback-Mechanismus bei Reconnect-Fehlern
- [x] Logging für Diagnose
- [x] Alle Komponenten verwenden Session State
- [x] Zentrale Verwendung in `omf_dashboard.py`

## Testing

**Verifiziert durch:**
1. **Connection-Loop Test:** Dashboard läuft stabil ohne "Client already connected" Fehler
2. **Environment-Switch Test:** Sauberer Wechsel zwischen Live/Replay ohne Verbindungsprobleme
3. **Logging-Verifikation:** Klare Nachrichten über Client-Status und Environment-Wechsel

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*  
*Problem gelöst durch: Strenge Prüfung und saubere Verbindungsbehandlung*
