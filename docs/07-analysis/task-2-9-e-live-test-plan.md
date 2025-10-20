# Task 2.9-E: Live-Modus Test Plan

## 🎯 **ZIEL**
End-to-End Test der MessageManager-Integration in **Replay Environment** ohne echte Fabrik-Verbindung.

## 🧪 **TEST-SZENARIEN**

### **1. Generic Steering - Topic-driven Mode**
- **Ziel:** Direkte Topic-Auswahl mit MessageManager-Validierung
- **Test:** Topic auswählen → Payload eingeben → MessageManager validieren → Admin Gateway senden
- **Erwartung:** Schema-Validierung funktioniert, QoS/Retain aus Registry

### **2. Generic Steering - Schema-driven Mode**  
- **Ziel:** Schema-basierte Payload-Generierung mit PayloadGenerator
- **Test:** Topic auswählen → PayloadGenerator → MessageManager validieren → Admin Gateway senden
- **Erwartung:** PayloadGenerator erstellt gültige Payloads, Schema-Validierung funktioniert

### **3. Generic Steering - Schema Test Mode**
- **Ziel:** Systematische Schema-Validierung aller Topics
- **Test:** Alle Topics testen → PayloadGenerator → MessageManager validieren
- **Erwartung:** Konsistente Ergebnisse, keine Race Conditions

### **4. CCU Domain Controls**
- **Ziel:** CCU Gateway publish_message Funktionalität
- **Test:** CCU-spezifische Topics → Schema-Validierung → CCU Gateway senden
- **Erwartung:** CCU Domain-spezifische Validierung funktioniert

## 🔧 **TEST-IMPLEMENTIERUNG**

### **Replay Environment Setup**
```python
# Test ohne echte MQTT-Verbindung
# Mock MQTT Client für Replay-Tests
# Schema-Validation ohne echte Message-Übertragung
```

### **Test-Kriterien**
- ✅ **Schema-Validation:** Alle Topics validieren korrekt
- ✅ **PayloadGenerator:** Generiert gültige Payloads für alle Schemas
- ✅ **MessageManager:** Konsistente Validierung in beiden Domains
- ✅ **Registry Integration:** QoS/Retain Parameter korrekt geladen
- ✅ **Error Handling:** Graceful Fallbacks bei Validierungsfehlern

## 📊 **ERFOLGS-KRITERIEN**

### **Must-Have (Kritisch)**
- [ ] **0 ERROR-LOGS** in omf2/omf.py
- [ ] **Schema-Validation** funktioniert für alle Topics
- [ ] **PayloadGenerator** erstellt gültige Payloads
- [ ] **MessageManager** konsistent in beiden Domains

### **Should-Have (Wichtig)**
- [ ] **Performance:** < 1 Sekunde pro Topic-Validierung
- [ ] **UI-Responsiveness:** Keine Blocking-Operations
- [ ] **Error-Messages:** Benutzerfreundliche Fehlermeldungen

### **Nice-to-Have (Optional)**
- [ ] **Batch-Validation:** Mehrere Topics gleichzeitig
- [ ] **Progress-Indicators:** UI-Feedback für lange Operationen

## 🚀 **NÄCHSTE SCHRITTE**

1. **Test-Environment Setup** - Replay Environment konfigurieren
2. **Test-Implementation** - Automatisierte Tests erstellen
3. **Test-Execution** - Alle Szenarien durchlaufen
4. **Result-Analysis** - Ergebnisse dokumentieren
5. **Task 2.9-F** - Factory Steering umstellen (nur wenn Tests erfolgreich)

## 📝 **NOTIZEN**

- **Fallback-Strategy:** Hardcodierte Messages bleiben als Fallback
- **Replay Environment:** Test ohne echte Fabrik-Verbindung
- **SchemaTester Race Condition:** Nach hinten verschoben (nicht kritisch)
- **Live-Test:** Echte Fabrik-Verbindung durch User getestet
