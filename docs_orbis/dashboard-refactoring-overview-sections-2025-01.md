# Dashboard Refactoring - Overview Sektionen Aufteilung

**Datum:** 04.01.2025  
**Status:** ✅ Abgeschlossen

## 🎯 **Ziel**
Aufteilung der ursprünglich 3 Sektionen aus `overview_inventory.py` in separate, spezialisierte Dateien für bessere Modularität und Wartbarkeit.

## 📋 **Durchgeführte Änderungen**

### **1. Sektionen-Aufteilung**

#### **Vorher: `overview_inventory.py` (3 Sektionen)**
```
overview_inventory.py:
├── 📚 Lagerbestand - HBW Übersicht (3x3 Raster)
├── 🛒 Bestellungen (3 Werkstück-Boxen)
└── 📊 Bestellung von Rohmaterial (Bedarfsberechnung)
```

#### **Nachher: Aufgeteilt in 3 Dateien**
```
overview_inventory.py:
├── 📚 Lagerbestand - HBW Übersicht
├── 🏗️ Lagerpositionen (A1-C3) - 3x3 Raster
└── 🔍 Debug-Info

overview_customer_order.py:
├── 📋 Kundenaufträge (Header)
├── 🛒 Kundenaufträge - 3 Werkstück-Boxen (ROT/BLUE/WHITE)
└── OrderManager mit MQTT-Integration

overview_purchase_order.py:
├── 📊 Rohmaterial-Bestellungen
├── 🔴 Rote Werkstücke (Bedarfsberechnung)
├── 🔵 Blaue Werkstücke (Bedarfsberechnung)
└── ⚪ Weiße Werkstücke (Bedarfsberechnung)
```

### **2. Technische Verbesserungen**

#### **OrderManager Integration**
- **Zentrale Datenquelle:** `OrderManager` in allen 3 Dateien
- **Echte MQTT-Integration:** `mqtt_client.drain()` für Live-Daten
- **Korrekte Berechnungen:** Keine hardcodierten Werte mehr
- **Konsistente Daten:** Alle Untertabs verwenden dieselben Daten

#### **Button-Key Management**
- **Eindeutige Keys:** Vermeidung von `StreamlitDuplicateElementKey` Fehlern
- **Strukturierte Namensgebung:**
  - `overview_inventory.py`: Keine Bestellungs-Buttons mehr
  - `overview_customer_order.py`: `order_inventory_order_*`
  - `overview_purchase_order.py`: `order_raw_*`

#### **UI-Verbesserungen**
- **Linksbündige Ausrichtung:** Werkstück-Boxen in `overview_customer_order.py`
- **HTML-Rendering:** Korrekte Darstellung leerer Buckets
- **Responsive Layout:** Flexbox-basierte Spalten

## 🔧 **Technische Details**

### **MQTT-Integration**
```python
# HBW-Nachrichten filtern
hbw_messages = [msg for msg in all_messages 
              if msg.get("topic", "").startswith("module/v1/ff/SVR3QA0022/state")]

# Neueste HBW-Nachricht verwenden
latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
```

### **Bedarfsberechnung**
```python
# Konstanten für maximale Kapazität
MAX_CAPACITY = 3

# Berechne Bedarf für jede Farbe
red_need = MAX_CAPACITY - red_count
blue_need = MAX_CAPACITY - blue_count  
white_need = MAX_CAPACITY - white_count
```

### **HTML-Templates für Buckets**
```html
<!-- Leere Buckets für fehlende Werkstücke -->
<div style="width: 60px; height: 40px; border: 2px solid #ccc; 
            border-top: none; background-color: #f9f9f9; 
            border-radius: 0 0 8px 8px; display: inline-block; margin: 2px;">
</div>
```

## 📊 **Erkannte Verbesserungsmöglichkeiten**

### **1. Topic-Dokumentation**
- **HBW-Topics:** `module/v1/ff/SVR3QA0022/state` für Lagerbestand
- **Zeitliche Abhängigkeiten:** Reihenfolge der MQTT-Nachrichten
- **yml-Dateien:** Ergänzung fehlender Dokumentation

### **2. HTML-Templates**
- **Wiederverwendbarkeit:** Zentrale Template-Definitionen
- **Konsistenz:** Einheitliche Darstellung von Werkstücken und Buckets
- **Wartbarkeit:** Änderungen nur an einer Stelle

## 🎯 **Nächste Schritte (TODOs)**

### **1. Bestellungs-Implementierung**
- **Direkter Versand:** Wie in `steering_factory`, aber ohne Bestätigung
- **MQTT-Integration:** Direkte Nachrichten an HBW-Modul
- **Status-Updates:** Echtzeit-Feedback

### **2. HTML-Templates**
- **Dummy-Templates:** Erst Definition, dann schrittweise Implementierung
- **Tab-Integration:** Aufruf in allen Tabs und Sub-Tabs
- **Wartbarkeit:** Zentrale Template-Verwaltung

### **3. Dokumentation**
- **Topic-Mapping:** Vollständige yml-Dateien
- **Zeitliche Abhängigkeiten:** Reihenfolge-Dokumentation
- **MQTT-Flows:** End-to-End Nachrichtenverfolgung

## ✅ **Erfolgreiche Tests**

- **Dashboard-Start:** Alle Tabs funktionieren
- **MQTT-Integration:** Live-Daten werden korrekt geladen
- **Button-Keys:** Keine Duplicate-Key-Fehler
- **Responsive Design:** Alle Layouts funktionieren
- **Debug-Info:** Vollständige Datenanzeige

## 🔄 **Backup-Strategie**

Alle Änderungen wurden mit Backups gesichert:
- `overview_inventory.py.backup`
- `overview_customer_order.py.backup`
- `overview_purchase_order.py.backup`

**Recovery-Befehle:**
```bash
cp src_orbis/omf/dashboard/components/overview_inventory.py.backup src_orbis/omf/dashboard/components/overview_inventory.py
cp src_orbis/omf/dashboard/components/overview_customer_order.py.backup src_orbis/omf/dashboard/components/overview_customer_order.py
cp src_orbis/omf/dashboard/components/overview_purchase_order.py.backup src_orbis/omf/dashboard/components/overview_purchase_order.py
```

---

**Status:** ✅ Refactoring erfolgreich abgeschlossen  
**Nächster Schritt:** Implementierung der Kundenauftrags-Funktionalität
