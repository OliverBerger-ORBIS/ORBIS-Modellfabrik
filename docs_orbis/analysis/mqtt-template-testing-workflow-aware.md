# 🎯 MQTT-Template Testing - Workflow-Aware Strategie

## 🚨 **Kritisches Problem bestätigt**

### **Alle MQTT-Commands sind werkstück-abhängig:**
**Keine "sicheren" Produktions-Commands verfügbar!**

#### **Kritische Produktions-Commands:**
- ❌ `DRILL_PICK_WHITE` - **Werkstück + FTS erforderlich**
- ❌ `MILL_PICK_WHITE` - **Werkstück + FTS erforderlich**
- ❌ `HBW_STORE_WHITE` - **Werkstück erforderlich**
- ❌ `AIQS_CHECK_QUALITY_WHITE` - **Werkstück erforderlich**

#### **Nur FTS-Commands sind "sicher":**
- ✅ `FTS_LADEN` - **Ohne Werkstück möglich**
- ✅ `FTS_LADEN_BEENDEN` - **Ohne Werkstück möglich**
- ✅ `FTS_DOCK_DPS` - **Ohne Werkstück möglich**

---

## 🎯 **Korrekte Testing-Strategie**

### **Phase 1: FTS-Commands Testing (Sicher)**
**Ziel:** Nur FTS-Commands ohne Werkstück-Abhängigkeit testen

#### **1.1 Verfügbare FTS-Templates:**
```bash
# Diese Templates sollten verfügbar sein:
- FTS_LADEN
- FTS_LADEN_BEENDEN  
- FTS_DOCK_DPS
```

#### **1.2 FTS-Template Testing:**
```bash
# Voraussetzungen für FTS-Commands:
1. FTS verfügbar? ✅/❌
2. Keine anderen aktiven Commands? ✅/❌
3. FTS nicht in kritischem Zustand? ✅/❌
```

### **Phase 2: Produktions-Commands (Nur mit Workflow)**
**Ziel:** Produktions-Commands nur mit korrekten Workflow-Voraussetzungen

#### **2.1 Workflow-Voraussetzungen für DRILL_PICK_WHITE:**
```bash
1. FTS an DRILL angedockt? ✅/❌
2. Weißes Werkstück im FTS? ✅/❌
3. DRILL verfügbar? ✅/❌
4. Keine anderen aktiven Commands? ✅/❌
```

#### **2.2 Workflow-Voraussetzungen für andere Commands:**
```bash
# MILL_PICK_WHITE:
1. FTS an MILL angedockt? ✅/❌
2. Weißes Werkstück im FTS? ✅/❌
3. MILL verfügbar? ✅/❌

# HBW_STORE_WHITE:
1. Werkstück verfügbar? ✅/❌
2. HBW verfügbar? ✅/❌
3. Lagerplatz frei? ✅/❌

# AIQS_CHECK_QUALITY_WHITE:
1. Werkstück verfügbar? ✅/❌
2. AIQS verfügbar? ✅/❌
```

---

## 📊 **Korrigiertes Testing-Protokoll**

### **Template 1: FTS_LADEN (Sicher)**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Voraussetzungen prüfen:**
- [ ] **FTS verfügbar:** ✅/❌
- [ ] **Keine anderen aktiven Commands:** ✅/❌
- [ ] **FTS nicht in kritischem Zustand:** ✅/❌

#### **Testing-Schritte:**
1. **Voraussetzungen erfüllt:** ✅/❌
2. **Template ausgewählt:** FTS_LADEN
3. **Template Details geprüft:**
   - Modul: FTS
   - Befehl: LADEN
   - Erwartete Antwort: RUNNING
4. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **FTS Status nach Test:** Available/Busy/Blocked/Error
- **Weitere Commands möglich:** ✅/❌
- **Beobachtungen:** ________

---

### **Template 2: DRILL_PICK_WHITE (Kritisch - Nur mit Workflow)**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Workflow-Voraussetzungen prüfen:**
- [ ] **FTS an DRILL angedockt:** ✅/❌
- [ ] **Weißes Werkstück im FTS:** ✅/❌
- [ ] **DRILL verfügbar:** ✅/❌
- [ ] **Keine anderen aktiven Commands:** ✅/❌

#### **Testing-Schritte:**
1. **Workflow-Voraussetzungen erfüllt:** ✅/❌
2. **Template ausgewählt:** DRILL_PICK_WHITE
3. **Template Details geprüft:**
   - Modul: DRILL
   - Befehl: PICK
   - Typ: WHITE
   - Erwartete Antwort: RUNNING
4. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **DRILL Status nach Test:** Available/Busy/Blocked/Error
- **Weitere Commands möglich:** ✅/❌
- **Beobachtungen:** ________

#### **Workflow-Impact:**
- **DRILL blockiert:** ✅/❌
- **FTS Status geändert:** ✅/❌
- **Werkstück verbraucht:** ✅/❌

---

## 🎯 **Empfohlene Testing-Reihenfolge**

### **1. FTS-Commands (Sicher):**
1. `FTS_LADEN` - Ohne Werkstück möglich
2. `FTS_LADEN_BEENDEN` - Ohne Werkstück möglich
3. `FTS_DOCK_DPS` - Ohne Werkstück möglich

### **2. Produktions-Commands (Nur mit Workflow):**
4. `DRILL_PICK_WHITE` - **Nur wenn FTS + Werkstück bereit**
5. `MILL_PICK_WHITE` - **Nur wenn FTS + Werkstück bereit**
6. `HBW_STORE_WHITE` - **Nur wenn Werkstück verfügbar**
7. `AIQS_CHECK_QUALITY_WHITE` - **Nur wenn Werkstück verfügbar**

### **3. Workflow-Sequenzen:**
8. **Komplette Wareneingang-Sequenz**
9. **Komplette Auftrag-Sequenz**

---

## 🚨 **Kritische Erkenntnis**

### **Alle Produktions-Commands benötigen Workflow-Management:**
- ❌ **Keine "sicheren" Produktions-Commands**
- ❌ **Alle Commands werkstück-abhängig**
- ❌ **Workflow-Voraussetzungen kritisch**

### **Nur FTS-Commands sind "sicher":**
- ✅ **FTS-Commands ohne Werkstück möglich**
- ✅ **Grundlegende FTS-Steuerung verfügbar**
- ✅ **Workflow-Vorbereitung möglich**

---

## 🚀 **Nächste Schritte**

### **Sofort:**
1. **FTS-Commands** zuerst testen (sicher)
2. **Workflow-Voraussetzungen** für Produktions-Commands prüfen
3. **Modul-Status-Monitoring** implementieren

### **Parallel:**
1. **ORDER-ID Management** implementieren
2. **Workflow-Engine** entwickeln
3. **Error-Recovery** implementieren

### **Langfristig:**
1. **Komplette Workflow-Sequenzen** implementieren
2. **Automatisierte Workflow-Validierung**
3. **Workflow-Visualisierung** im Dashboard

---

**Status:** 🚨 **ALLE PRODUKTIONS-COMMANDS KRITISCH** - Nur FTS-Commands sicher testbar
