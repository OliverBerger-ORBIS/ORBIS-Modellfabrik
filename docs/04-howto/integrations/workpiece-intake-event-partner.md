# Workpiece Intake Event — Partner-Hinweis

Für Apps, die nur das Signal „neues Werkstück an der Warenein-/ausgangsstation“ brauchen (z. B. Object Detection).

## Verbindung

| | |
|--|--|
| Broker (Browser) | `ws://192.168.0.100:9001` |
| User / Passwort | `default` / `default` |

Port **9001** = MQTT over **WebSocket** (für Browser-Apps). TCP-MQTT für native Tools: Port **1883** (nicht für Browser).

## Topic

`osf/workpiece/intake`

## Nachricht (JSON)

```json
{
  "productRaw": "WHITE",
  "nfc": "92e0ad91595f63",
  "timestamp": "2026-08-07T09:11:46.905Z"
}
```

| Feld | Bedeutung |
|------|-----------|
| `productRaw` | Farbe / Rohprodukt (`WHITE` \| `RED` \| `BLUE`) — Bridge publiziert erst, wenn die Farbe aus APS bekannt ist (kein `UNKNOWN`) |
| `nfc` | NFC-Tag-ID des Werkstücks |
| `timestamp` | Zeitpunkt (ISO-8601) |

Kein `orderId` in diesem Event (Storage-/Produktionsauftrag kommt später über APS; Track&Trace/Persistenz korrelieren über NFC).

