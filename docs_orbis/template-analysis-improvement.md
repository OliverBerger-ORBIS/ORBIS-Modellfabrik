# 🔧 Template Analysis Improvement

## 📋 Problem

Die **Beispiel-Nachrichten** in der TXT Template Analyse zeigten **Template-Platzhalter** anstelle von echten Nachrichten:

### **❌ Falsches Beispiel (vor der Verbesserung):**
```json
{
  "ts": "2025-08-19T09:13:34.583Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "<nfcCode>",
        "type": "<workpieceType: RED, WHITE, BLUE>",
        "state": "<state: RAW>"
      },
      "location": "A3",
      "hbw": "SVR3QA0022"
    }
  ]
}
```

Diese Platzhalter wie `<nfcCode>`, `<workpieceType: RED, WHITE, BLUE>` gehören in das **Template**, nicht in die **Beispiele**.

## ✅ Lösung

### **🔍 Template vs. Beispiele unterscheiden:**

#### **📋 Template (soll Platzhalter zeigen):**
```json
{
  "workpiece": {
    "id": "<nfcCode>",
    "type": "<workpieceType: RED, WHITE, BLUE>",
    "state": "<state: RAW>"
  }
}
```

#### **📄 Beispiele (sollen echte Nachrichten zeigen):**
```json
{
  "workpiece": {
    "id": "040a8dca341291",
    "type": "RED",
    "state": "RAW"
  }
}
```

### **🛠️ Implementierung:**

#### **1. `is_real_message()` Methode (verbessert):**
```python
def is_real_message(self, payload: Dict) -> bool:
    """Check if a payload is a real message (not a template placeholder)"""
    def contains_template_placeholders(obj):
        if isinstance(obj, str):
            # Erweiterte Liste aller Template-Platzhalter
            placeholder_patterns = [
                '<nfcCode>', '<workpieceType:', '<state:', '<location:', '<hbwId>',
                '<RED>', '<WHITE>', '<BLUE>', '<RAW>', '<timestamp>', '<status:',
                '<workpieceType: RED, WHITE, BLUE>', '<state: RAW>', 
                '<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>',
                '<workpieceType: BLUE, RED, WHITE>', '<status: IN_PROCESS, WAITING_FOR_ORDER>'
            ]
            return any(pattern in obj for pattern in placeholder_patterns)
        # ... rekursive Prüfung für dict und list
    return not contains_template_placeholders(payload)
```

#### **2. Filterung in der Analyse:**
```python
# Only add as example if it's a real message (not template placeholder)
if self.is_real_message(payload):
    examples.append({
        'session': msg['session'],
        'timestamp': msg['timestamp'],
        'payload': payload
    })
```

## 🎯 Ergebnis

### **✅ Vorher:**
- **Beispiele** zeigten Template-Platzhalter
- **Verwirrend** für Benutzer
- **Falsche** Daten als Beispiele

### **✅ Nachher:**
- **Template** zeigt Platzhalter (korrekt)
- **Beispiele** zeigen echte Nachrichten
- **Klarer** Unterschied zwischen Template und Beispielen

## 📊 Betroffene Topics

### **📥 Function Input Topics:**
- `/j1/txt/1/f/i/stock` - Lagerbestand
- `/j1/txt/1/f/i/order` - Aufträge
- `/j1/txt/1/f/i/config/*` - Konfigurationen

### **📤 Function Output Topics:**
- `/j1/txt/1/f/o/order` - Auftragsausgaben
- `/j1/txt/1/f/o/stock` - Lagerausgaben

## 🔗 Verwandte Dokumentation

- **[TXT Template Analyzer](txt-template-analyzer-guide.md)**
- **[MQTT Control Dashboard](mqtt-control-summary.md)**
- **[Template Message Manager](template-message-manager-implementation.md)**
