# 🎯 MESSAGE PROCESSING PATTERN - Standard für alle Manager

**Status: KRITISCH - MUSS BEIM JEDEN MANAGER BEFOLGT WERDEN**  
**Datum: 2025-10-04**  
**Problem: Immer wieder die gleichen Fehler bei Message-Verarbeitung**

---

## ❌ **HÄUFIGE FEHLER (NIEMALS WIEDER):**

### **Fehler 1: Falsche Message-Struktur Annahme**
```python
# ❌ FALSCH - Annahme dass payload ein Dictionary ist
payload = message_data.get("payload", {})
temperature = payload.get("temperature", 0.0)

# ❌ FALSCH - Annahme dass Felder in payload sind
connection_state = payload.get("connectionState")
```

### **Fehler 2: Falsche Feld-Namen**
```python
# ❌ FALSCH - Erfundene Feld-Namen
temperature = sensor_data.get("temperature", 0.0)
light = sensor_data.get("light", 0.0)
```

### **Fehler 3: Fehlende Debug-Logs**
```python
# ❌ FALSCH - Keine Sichtbarkeit der Message-Struktur
sensor_data = json.loads(payload)
temperature = sensor_data.get("t", 0.0)
```

---

## ✅ **KORREKTES MESSAGE PROCESSING PATTERN:**

### **Schritt 1: Message-Struktur analysieren (MANDATORY)**
```python
def _extract_entity_data(self, topic: str, messages: List[Dict]) -> Dict[str, Any]:
    """Extract entity data from messages - ALWAYS follow this pattern"""
    if not messages:
        return {}
    
    latest_message = messages[-1]
    
    # STEP 1: ALWAYS log message structure FIRST
    logger.info(f"🔍 DEBUG: Raw message keys: {list(latest_message.keys())}")
    logger.info(f"🔍 DEBUG: Message structure: {latest_message}")
    
    # STEP 2: Check if data is in payload (String) or message_data (Direct)
    payload = latest_message.get("payload", "{}")
    if isinstance(payload, str):
        try:
            import json
            parsed_data = json.loads(payload)
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse JSON payload: {e}")
            parsed_data = {}
    else:
        parsed_data = payload
    
    # STEP 3: Check BOTH locations for data
    # Option A: Data is in parsed payload (String format from MQTT)
    if parsed_data and any(key in parsed_data for key in ["t", "h", "p", "connectionState", "available"]):
        logger.info(f"🔍 DEBUG: Data found in payload: {parsed_data}")
        data_source = parsed_data
    # Option B: Data is directly in message_data (Direct format)
    elif any(key in latest_message for key in ["t", "h", "p", "connectionState", "available"]):
        logger.info(f"🔍 DEBUG: Data found in message_data: {latest_message}")
        data_source = latest_message
    else:
        logger.warning(f"⚠️ No data found in payload or message_data")
        return {}
    
    return data_source
```

### **Schritt 2: Schema-basierte Feld-Extraktion (MANDATORY)**
```python
def _extract_specific_fields(self, topic: str, data_source: Dict) -> Dict[str, Any]:
    """Extract specific fields based on topic - ALWAYS use REAL field names"""
    
    # ALWAYS check real MQTT data first:
    # Example: find data/aps-data -name "*bme680*" | xargs cat
    # Example: find data/aps-data -name "*connection*" | xargs cat
    
    if "/bme680" in topic:
        # REAL fields from MQTT data: {"t": 25.4, "h": 31.6, "p": 1003.8, "iaq": 48}
        return {
            "temperature": data_source.get("t", 0.0),      # ✅ REAL field name
            "humidity": data_source.get("h", 0.0),         # ✅ REAL field name
            "pressure": data_source.get("p", 0.0),         # ✅ REAL field name
            "air_quality": data_source.get("iaq", 0.0),    # ✅ REAL field name (not "aq")
            "timestamp": data_source.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    elif "/ldr" in topic:
        # REAL fields from MQTT data: {"br": 97.1, "ldr": 1853}
        return {
            "light": data_source.get("ldr", 0.0),          # ✅ REAL field name (not "l")
            "brightness": data_source.get("br", 0.0),      # ✅ REAL field name
            "timestamp": data_source.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    elif "/connection" in topic:
        # REAL fields from MQTT data: {"connectionState": "ONLINE"}
        return {
            "connection_state": data_source.get("connectionState", ""),  # ✅ REAL field name
            "timestamp": data_source.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    elif "/state" in topic:
        # REAL fields from MQTT data: {"available": "READY"}
        return {
            "available": data_source.get("available", ""),  # ✅ REAL field name
            "timestamp": data_source.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    else:
        logger.warning(f"⚠️ Unknown topic pattern: {topic}")
        return {}
```

### **Schritt 3: Manager-Implementierung (MANDATORY)**
```python
class EntityManager:
    """Business Logic Manager - ALWAYS follow this pattern"""
    
    def process_entity_messages(self, gateway) -> Dict[str, Any]:
        """Process entity messages from Gateway buffers"""
        try:
            entity_data = {}
            
            # Get all buffers via Gateway (Gateway-Pattern)
            all_buffers = gateway.get_all_message_buffers()
            
            for topic, messages in all_buffers.items():
                if not messages:
                    continue
                
                # Check if this is our entity topic
                if self._is_entity_topic(topic):
                    logger.debug(f"📡 Processing entity topic: {topic}")
                    
                    # ALWAYS use the standard extraction pattern
                    processed_data = self._extract_entity_data(topic, messages)
                    if processed_data:
                        entity_data[topic] = processed_data
            
            return entity_data
            
        except Exception as e:
            logger.error(f"❌ Failed to process entity messages: {e}")
            return {}
    
    def _is_entity_topic(self, topic: str) -> bool:
        """Check if topic is our entity topic - ALWAYS implement"""
        entity_patterns = ["/bme680", "/ldr", "/connection", "/state"]
        return any(pattern in topic for pattern in entity_patterns)
```

---

## 🔍 **DEBUG-PROZESS (MANDATORY vor jeder Implementierung):**

### **Schritt 1: Echte MQTT-Daten analysieren**
```bash
# ALWAYS check real data first:
find data/aps-data -name "*bme680*" | head -3 | xargs cat
find data/aps-data -name "*ldr*" | head -3 | xargs cat
find data/aps-data -name "*connection*" | head -3 | xargs cat
```

### **Schritt 2: Message-Struktur verstehen**
```python
# ALWAYS log message structure:
logger.info(f"🔍 DEBUG: Raw message keys: {list(message.keys())}")
logger.info(f"🔍 DEBUG: Message structure: {message}")
logger.info(f"🔍 DEBUG: Payload: {message.get('payload', 'NO_PAYLOAD')}")
```

### **Schritt 3: Feld-Namen aus echten Daten extrahieren**
```python
# ALWAYS use REAL field names from MQTT data:
# BME680: {"t": 25.4, "h": 31.6, "p": 1003.8, "iaq": 48}
# LDR: {"br": 97.1, "ldr": 1853}
# Connection: {"connectionState": "ONLINE"}
```

---

## 🚨 **KRITISCHE REGELN (NIEMALS VERLETZEN):**

1. **ALWAYS log message structure FIRST** - keine Annahmen über Struktur
2. **ALWAYS check real MQTT data** - keine erfundenen Feld-Namen
3. **ALWAYS check BOTH payload and message_data** - Daten können in beiden sein
4. **ALWAYS implement debug logging** - Sichtbarkeit ist kritisch
5. **ALWAYS use Gateway-Pattern** - UI → Manager → Gateway

---

## 📋 **CHECKLISTE vor jeder Manager-Implementierung:**

- [ ] Echte MQTT-Daten analysiert (`find data/aps-data -name "*topic*" | xargs cat`)
- [ ] Message-Struktur geloggt (`logger.info(f"Message structure: {message}")`)
- [ ] Feld-Namen aus echten Daten extrahiert (nicht erfundene Namen)
- [ ] Beide Datenquellen geprüft (payload UND message_data)
- [ ] Debug-Logging implementiert
- [ ] Gateway-Pattern verwendet
- [ ] Business Logic Manager Pattern verwendet
- [ ] Schema-basierte Feld-Extraktion implementiert

---

## 🎯 **BEISPIEL: Korrekte Implementierung**

```python
# ✅ KORREKT - SensorManager
def _extract_sensor_data(self, topic: str, messages: List[Dict]) -> Dict[str, Any]:
    if not messages:
        return {}
    
    latest_message = messages[-1]
    
    # STEP 1: Log message structure (MANDATORY)
    logger.info(f"🔍 DEBUG: Raw message keys: {list(latest_message.keys())}")
    logger.info(f"🔍 DEBUG: Message structure: {latest_message}")
    
    # STEP 2: Check data location (MANDATORY)
    payload = latest_message.get("payload", "{}")
    if isinstance(payload, str):
        try:
            import json
            parsed_data = json.loads(payload)
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse JSON payload: {e}")
            parsed_data = {}
    else:
        parsed_data = payload
    
    # STEP 3: Check BOTH locations (MANDATORY)
    if parsed_data and any(key in parsed_data for key in ["t", "h", "p", "iaq"]):
        data_source = parsed_data
        logger.info(f"🔍 DEBUG: Data found in payload: {parsed_data}")
    elif any(key in latest_message for key in ["t", "h", "p", "iaq"]):
        data_source = latest_message
        logger.info(f"🔍 DEBUG: Data found in message_data: {latest_message}")
    else:
        logger.warning(f"⚠️ No data found in payload or message_data")
        return {}
    
    # STEP 4: Extract with REAL field names (MANDATORY)
    if "/bme680" in topic:
        return {
            "temperature": data_source.get("t", 0.0),      # ✅ REAL field from MQTT
            "humidity": data_source.get("h", 0.0),         # ✅ REAL field from MQTT
            "pressure": data_source.get("p", 0.0),         # ✅ REAL field from MQTT
            "air_quality": data_source.get("iaq", 0.0),    # ✅ REAL field from MQTT
            "timestamp": latest_message.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    return {}
```

**DIESES PATTERN MUSS BEI JEDEM MANAGER BEFOLGT WERDEN!**
