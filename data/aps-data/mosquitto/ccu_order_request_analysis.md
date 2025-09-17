# CCU Order Request Analyse

## 📋 **ccu/order/request Message Flow**

### **Publishers (Wer sendet Auftragsbefehle):**

1. **`omf_dashboard_live`** (OMF Dashboard)
   - **IP:** 192.168.0.103
   - **Rolle:** OMF Dashboard sendet Auftragsbefehle
   - **Messages:** 2x Auftragsbefehle gesendet

2. **`mqttjs_1802b4e7`** (MQTT.js Dashboard)
   - **IP:** 172.18.0.5 (Docker Container)
   - **Rolle:** MQTT.js Dashboard sendet Auftragsbefehle
   - **Messages:** 3x Auftragsbefehle gesendet

### **Subscribers (Wer empfängt Auftragsbefehle):**

1. **`mqttjs_1802b4e7`** (MQTT.js Dashboard)
   - **IP:** 172.18.0.5 (Docker Container)
   - **Rolle:** MQTT.js Dashboard empfängt Auftragsbefehle
   - **Messages:** 5x Auftragsbefehle empfangen

2. **`omf_dashboard_live`** (OMF Dashboard)
   - **IP:** 192.168.0.103
   - **Rolle:** OMF Dashboard empfängt Auftragsbefehle (Echo/Confirmation)
   - **Messages:** 5x Auftragsbefehle empfangen

## 🔄 **Message Flow Pattern**

```
OMF Dashboard (192.168.0.103) ──┐
                                ├─→ MQTT Broker ──┐
MQTT.js Dashboard (172.18.0.5) ─┘                ├─→ OMF Dashboard (Echo)
                                                 ├─→ MQTT.js Dashboard (Echo)
                                                 └─→ [Weitere Subscriber]
```

## 📊 **Zusammenfassung**

**Auftragsbefehle werden gesendet von:**
- **OMF Dashboard** (192.168.0.103) - 2x
- **MQTT.js Dashboard** (172.18.0.5) - 3x

**Auftragsbefehle werden empfangen von:**
- **MQTT.js Dashboard** (172.18.0.5) - 5x
- **OMF Dashboard** (192.168.0.103) - 5x (Echo/Confirmation)

**Wichtige Erkenntnisse:**
- Beide Dashboard-Systeme senden Auftragsbefehle
- Beide Dashboard-Systeme empfangen auch die Auftragsbefehle (Echo-Pattern)
- Keine direkten Module (TXT, FTS, etc.) empfangen Auftragsbefehle
- Auftragsbefehle werden nur zwischen Dashboard-Systemen ausgetauscht

