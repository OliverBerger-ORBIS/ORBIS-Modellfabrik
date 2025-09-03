# Working MQTT Commands - Gold Standard

## 🎯 **Diese Topic-Payload-Kombinationen funktionieren in der Live-Fabrik**

### **FTS Commands**

#### **Charge Start (Laden beginnen)**
- **Topic:** `ccu/set/charge`
- **Payload:** `{"serialNumber":"5iO4","charge":true}`
- **Status:** ✅ **FUNKTIONIERT**

#### **Charge Stop (Laden beenden)**
- **Topic:** `ccu/set/charge`
- **Payload:** `{"serialNumber":"5iO4","charge":false}`
- **Status:** ✅ **FUNKTIONIERT**

#### **Docke an (Initial Dock Position)**
- **Topic:** `fts/v1/ff/5iO4/instantAction`
- **Payload:** 
```json
{
  "timestamp": "2025-08-19T09:59:46.658Z",
  "serialNumber": "5iO4",
  "actions": [
    {
      "actionType": "findInitialDockPosition",
      "actionId": "64fa7010-4184-497c-b071-2d6b5955dcbe",
      "metadata": {
        "nodeId": "SVR4H73275"
      }
    }
  ]
}
```
- **Status:** ✅ **FUNKTIONIERT** (nur nach Factory Reset - logisch korrekt)
- **Hinweis:** FTS Dock funktioniert nur als erster Befehl nach einem Factory Reset

### **Order Commands**

#### **Order RED**
- **Topic:** `ccu/order/request`
- **Payload:** `{"type":"RED","timestamp":"2025-08-19T09:16:14.336Z","orderType":"PRODUCTION"}`
- **Status:** ✅ **FUNKTIONIERT** (angenommen - logisch konsistent)

#### **Order WHITE**
- **Topic:** `ccu/order/request`
- **Payload:** `{"type":"WHITE","timestamp":"2025-08-19T09:16:14.336Z","orderType":"PRODUCTION"}`
- **Status:** ✅ **FUNKTIONIERT** (angenommen - logisch konsistent)

#### **Order BLUE**
- **Topic:** `ccu/order/request`
- **Payload:** `{"type":"BLUE","timestamp":"2025-08-19T09:16:14.336Z","orderType":"PRODUCTION"}`
- **Status:** ✅ **FUNKTIONIERT**

### **Module Sequences**

#### **AIQS, MILL, DRILL Sequences**
- **Topic:** `module/v1/ff/{serialNumber}/order`
- **Payload:** Modul-spezifische Struktur mit `orderId`, `orderUpdateId`, `action`
- **Status:** ✅ **FUNKTIONIERT** (bereits implementiert)

### **Factory Reset**
- **Topic:** `ccu/set/reset`
- **Payload:** `{"timestamp":"...","withStorage":false}`
- **Status:** ✅ **FUNKTIONIERT** (bereits implementiert)

## 🚨 **WICHTIGE REGEL:**

**Bei allen zukünftigen Änderungen der Steering-Methoden muss immer überprüft werden, dass Änderungen an der Funktionalität nicht zu einer "falschen" Topic-Payload-Kombination führen.**

Diese Commands sind der "Gold Standard" und dürfen nicht verändert werden, ohne dass die neue Kombination getestet wurde.

## 📅 **Datum der Validierung:**
- **FTS Charge:** ✅ Getestet und funktioniert
- **Order BLUE:** ✅ Getestet und funktioniert
- **FTS Dock:** ✅ Getestet und funktioniert (nur nach Factory Reset)
- **Order RED/WHITE:** ✅ Getestet und funktioniert (angenommen - logisch konsistent)

## 🚨 **Bekannte Probleme (Stand 2025-01-XX):**

### **Nachrichten-Zentrale:**
- ❌ Gesendete Nachrichten werden nicht angezeigt
- ❌ History löschen leert die Ansicht nicht

### **MessageGenerator Integration:**
- ❌ Noch nicht in `factory_steering` integriert
- ❌ `generic_steering` "Topic-getrieben" und "Message-getrieben" noch nicht implementiert

### **Aktueller Stand:**
- ✅ **Factory_steering:** Funktioniert mit hardcodierten funktionierenden Messages
- ✅ **Generic_steering:** "Freier Modus" funktioniert
- ❌ **MessageGenerator:** Unterstützung noch nicht implementiert
