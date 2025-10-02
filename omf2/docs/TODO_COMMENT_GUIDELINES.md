# TODO-Kommentar Richtlinien

## 🎯 **Zweck**
TODO-Kommentare markieren temporäre Lösungen und hardcodierte Payloads, die später durch Schema-driven Approach ersetzt werden sollen.

## 📋 **TODO-Kommentar Format**

### **Standard-Format:**
```python
# TODO: Replace hardcoded payload with schema-driven approach
# TODO: Use PayloadGenerator.generate_example_payload(topic) instead
# TODO: Integrate with Registry Manager for proper schema validation
```

### **Spezifische TODO-Kommentare:**
```python
# TODO: Replace hardcoded payload with schema-driven approach
# TODO: Use PayloadGenerator.generate_example_payload("ccu/set/reset") instead
# TODO: Integrate with Registry Manager for proper schema validation
```

## 🔍 **Wann TODO-Kommentare verwenden?**

### **✅ TODO-Kommentare ERFORDERLICH bei:**
- Hardcodierte Payloads in `factory_steering_subtab.py`
- Temporäre Lösungen für schnelle Entwicklung
- Code, der Schema-driven werden soll
- Kurz-Hacks, die später refactored werden

### **❌ KEINE TODO-Kommentare bei:**
- Bereits Schema-driven Code
- Korrekte Gateway-Verwendung
- Registry-basierte Implementierungen

## 📝 **TODO-Kommentar Best Practices**

### **1. Spezifische Topics angeben:**
```python
# ✅ GUT: Spezifisches Topic
# TODO: Use PayloadGenerator.generate_example_payload("ccu/set/reset") instead

# ❌ SCHLECHT: Generisch
# TODO: Use PayloadGenerator instead
```

### **2. Drei-stufige TODO-Struktur:**
```python
# TODO: Replace hardcoded payload with schema-driven approach
# TODO: Use PayloadGenerator.generate_example_payload(topic) instead  
# TODO: Integrate with Registry Manager for proper schema validation
```

### **3. Vor hardcodierten Payloads:**
```python
def _send_factory_reset(admin_gateway):
    """Send Factory Reset Command"""
    try:
        from datetime import datetime
        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload("ccu/set/reset") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {
            "timestamp": datetime.now().isoformat(),
            "withStorage": False
        }
```

## 🎯 **Refactoring-Plan**

### **Phase 1: TODO-Kommentare hinzufügen**
- ✅ Alle hardcodierten Payloads markieren
- ✅ Spezifische Topics angeben
- ✅ Drei-stufige TODO-Struktur verwenden

### **Phase 2: Schema-driven Migration**
- 🔄 PayloadGenerator implementieren
- 🔄 Registry Manager Integration
- 🔄 Schema-Validierung hinzufügen

### **Phase 3: TODO-Kommentare entfernen**
- 🔄 Hardcodierte Payloads ersetzen
- 🔄 TODO-Kommentare entfernen
- 🔄 Tests aktualisieren

## 📊 **TODO-Status Tracking**

### **Aktuelle TODO-Kommentare:**
- `_send_factory_reset()` - Factory Reset Command
- `_send_emergency_stop()` - Emergency Stop Command  
- `_send_fts_dock()` - FTS Dock Command
- `_send_fts_load()` - FTS Load Command
- `_send_fts_unload()` - FTS Unload Command
- `_send_order()` - Production Order

### **Refactoring-Priorität:**
1. **Hoch:** `_send_order()` - Häufig verwendet
2. **Mittel:** `_send_factory_reset()` - Admin-Funktion
3. **Niedrig:** FTS-spezifische Commands

## 🚀 **Migration-Strategie**

### **Schritt 1: Registry-Schemas erstellen**
```yaml
# omf2/registry/schemas/ccu_set_reset.json
{
  "type": "object",
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "withStorage": {"type": "boolean"}
  },
  "required": ["timestamp", "withStorage"]
}
```

### **Schritt 2: PayloadGenerator erweitern**
```python
def generate_example_payload(self, topic: str) -> Optional[Dict[str, Any]]:
    """Generates schema-compliant payload for topic"""
    # Schema-basierte Payload-Generierung
```

### **Schritt 3: Hardcodierte Payloads ersetzen**
```python
# Vorher (mit TODO):
# TODO: Replace hardcoded payload with schema-driven approach
payload = {"timestamp": datetime.now().isoformat(), "withStorage": False}

# Nachher (Schema-driven):
payload = payload_generator.generate_example_payload("ccu/set/reset")
```

## ✅ **Erfolgskriterien**

### **TODO-Kommentare erfolgreich wenn:**
- ✅ Alle hardcodierten Payloads markiert
- ✅ Spezifische Topics angegeben
- ✅ Drei-stufige Struktur verwendet
- ✅ Refactoring-Pfad klar definiert

### **Migration erfolgreich wenn:**
- ✅ PayloadGenerator verwendet
- ✅ Registry Manager integriert
- ✅ Schema-Validierung funktioniert
- ✅ TODO-Kommentare entfernt

## 🎯 **Zusammenfassung**

TODO-Kommentare sind **essentiell** für:
- **Saubere Entwicklung** - Markieren temporäre Lösungen
- **Refactoring-Plan** - Klare Migration-Strategie
- **Code-Qualität** - Vermeiden von vergessenen Hardcodierungen
- **Team-Kommunikation** - Zeigen was noch zu tun ist

**Jeder hardcodierte Payload MUSS TODO-Kommentare haben!** 🎯
