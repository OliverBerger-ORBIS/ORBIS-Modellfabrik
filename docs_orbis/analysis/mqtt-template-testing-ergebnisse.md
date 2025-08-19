# 🎯 MQTT-Template Testing - Ergebnisse & Dokumentation

## 📋 **Testing-Übersicht**

**Datum:** 19. August 2025  
**Tester:** Oliver  
**Ziel:** Validierung der MQTT-Templates im Dashboard  
**Methode:** Manuelles Testing über Dashboard + Dokumentation  
**Status:** 🚨 **ORDER-ID Problem identifiziert** - Workflow-Templates benötigt  

---

## 🎯 **Testing-Anleitung**

### **Schritt 1: Dashboard vorbereiten**
1. **Dashboard öffnen:** http://localhost:8501
2. **MQTT-Verbindung** in der Sidebar herstellen
3. **Session auswählen** (z.B. `default_test_session`)
4. **MQTT Control Tab** öffnen

### **Schritt 2: Template Testing**
1. **Steuerungsmethode:** "Template Message" auswählen
2. **Template auswählen** aus der Dropdown-Liste
3. **Template Details** prüfen
4. **"Senden" Button** klicken
5. **Ergebnis beobachten** und dokumentieren

### **Schritt 3: Ergebnis-Dokumentation**
Für jedes Template:
- ✅ **Erfolg** oder ❌ **Fehler**
- **Fehlermeldung** (falls vorhanden)
- **Beobachtungen** (Module-Reaktion, Timing, etc.)
- **Screenshot** (optional)

---

## 📊 **Verfügbare Templates**

### **DRILL Module:**
- `DRILL_PICK_WHITE` - DRILL PICK für weißes Werkstück
- `DRILL_PICK_BLUE` - DRILL PICK für blaues Werkstück
- `DRILL_PICK_RED` - DRILL PICK für rotes Werkstück
- `DRILL_PROCESS_WHITE` - DRILL PROCESS für weißes Werkstück
- `DRILL_PROCESS_BLUE` - DRILL PROCESS für blaues Werkstück
- `DRILL_PROCESS_RED` - DRILL PROCESS für rotes Werkstück

### **MILL Module:**
- `MILL_PICK_WHITE` - MILL PICK für weißes Werkstück
- `MILL_PICK_BLUE` - MILL PICK für blaues Werkstück
- `MILL_PICK_RED` - MILL PICK für rotes Werkstück
- `MILL_PROCESS_WHITE` - MILL PROCESS für weißes Werkstück
- `MILL_PROCESS_BLUE` - MILL PROCESS für blaues Werkstück
- `MILL_PROCESS_RED` - MILL PROCESS für rotes Werkstück

### **HBW Module:**
- `HBW_STORE_WHITE` - HBW STORE für weißes Werkstück
- `HBW_STORE_BLUE` - HBW STORE für blaues Werkstück
- `HBW_STORE_RED` - HBW STORE für rotes Werkstück

### **DPS Module:**
- `DPS_INPUT_RGB` - DPS INPUT_RGB Befehl
- `DPS_RGB_NFC_WHITE` - DPS RGB_NFC für weißes Werkstück
- `DPS_RGB_NFC_BLUE` - DPS RGB_NFC für blaues Werkstück
- `DPS_RGB_NFC_RED` - DPS RGB_NFC für rotes Werkstück

### **AIQS Module:**
- `AIQS_CHECK_QUALITY_WHITE` - AIQS Qualitätsprüfung für weißes Werkstück

---

## 🚨 **KRITISCHES PROBLEM: ORDER-ID Management**

### **Identifiziertes Problem:**
```
MQTT Response Fehler:
{
  "actionState": {
    "state": "FAILED",
    "command": "PICK"
  },
  "errors": [
    {
      "errorType": "Validation",
      "errorMessage": "OrderUpdateId not valid"
    }
  ]
}
```

### **Root Cause Analysis:**
1. **ORDER-ID**: Wird korrekt generiert (UUID)
2. **orderUpdateId**: Bleibt immer `1` für alle Commands
3. **Workflow-Sequenz**: PICK → PROCESS → DROP benötigt inkrementelle orderUpdateId
4. **APS-Erwartung**: orderUpdateId muss für sequenzielle Commands steigen (1, 2, 3...)

### **Lösungsansatz:**
- **WorkflowOrderManager** implementieren
- **Workflow-Templates** mit ORDER-ID Tracking erstellen
- **PICK → PROCESS → DROP** Sequenzen mit korrekter orderUpdateId

### **Status:**
- 🚨 **KRITISCH**: PROCESS-Befehle funktionieren nicht ohne ORDER-ID Management
- 🔧 **In Entwicklung**: WorkflowOrderManager
- 📋 **Plan**: Workflow-Templates mit ORDER-ID Tracking

---

## 🔍 **Testing-Protokoll**

### **Template 1: DRILL_PICK_WHITE**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** DRILL_PICK_WHITE
2. **Template Details geprüft:**
   - Modul: DRILL
   - Befehl: PICK
   - Typ: WHITE
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

### **Template 2: DRILL_PICK_BLUE**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** DRILL_PICK_BLUE
2. **Template Details geprüft:**
   - Modul: DRILL
   - Befehl: PICK
   - Typ: BLUE
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

### **Template 3: DRILL_PICK_RED**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** DRILL_PICK_RED
2. **Template Details geprüft:**
   - Modul: DRILL
   - Befehl: PICK
   - Typ: RED
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

### **Template 4: MILL_PICK_WHITE**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** MILL_PICK_WHITE
2. **Template Details geprüft:**
   - Modul: MILL
   - Befehl: PICK
   - Typ: WHITE
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

### **Template 5: HBW_STORE_WHITE**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** HBW_STORE_WHITE
2. **Template Details geprüft:**
   - Modul: HBW
   - Befehl: STORE
   - Typ: WHITE
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

### **Template 6: AIQS_CHECK_QUALITY_WHITE**
**Datum:** ________  
**Zeit:** ________  
**Tester:** ________  

#### **Vorbereitung:**
- [ ] Dashboard geöffnet
- [ ] MQTT verbunden
- [ ] Session ausgewählt
- [ ] MQTT Control Tab aktiv

#### **Testing-Schritte:**
1. **Template ausgewählt:** AIQS_CHECK_QUALITY_WHITE
2. **Template Details geprüft:**
   - Modul: AIQS
   - Befehl: CHECK_QUALITY
   - Typ: WHITE
   - Erwartete Antwort: RUNNING
3. **Senden-Button geklickt:** ________

#### **Ergebnis:**
- **Status:** ✅ Erfolg / ❌ Fehler
- **Fehlermeldung:** ________
- **Module-Reaktion:** ________
- **Timing:** ________
- **Beobachtungen:** ________

#### **Screenshot:** ________

---

## 📈 **Zusammenfassung der Ergebnisse**

### **Erfolgsrate:**
- **Erfolgreiche Templates:** ________ / 6
- **Fehlgeschlagene Templates:** ________ / 6
- **Erfolgsrate:** ________%

### **Häufige Fehlermuster:**
1. **ORDER-ID Probleme:** ________
2. **Timing-Issues:** ________
3. **Modul-Verfügbarkeit:** ________
4. **MQTT-Verbindung:** ________

### **Funktionierende Templates:**
- ✅ ________
- ✅ ________
- ❌ ________
- ❌ ________

### **Kritische Beobachtungen:**
1. ________
2. ________
3. ________

---

## 🔧 **Technische Details**

### **Template-Struktur:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### **MQTT Topic Format:**
```
module/v1/ff/{serialNumber}/order
```

### **Erwartete Antworten:**
- **RUNNING:** Command wird ausgeführt
- **COMPLETED:** Command erfolgreich abgeschlossen
- **FAILED:** Command fehlgeschlagen
- **REJECTED:** Command abgelehnt

---

## 🎯 **Nächste Schritte**

### **Basierend auf den Ergebnissen:**
1. **ORDER-ID Management** implementieren (falls ORDER-ID Probleme)
2. **Modul-Status-Monitoring** verbessern (falls Timing-Issues)
3. **Error-Handling** implementieren (falls Fehlerbehandlung fehlt)
4. **Template-Optimierung** basierend auf Erkenntnissen

### **Weitere Testing:**
1. **Custom Order Testing** (manuelle ORDER-ID Eingabe)
2. **Module Overview Testing** (direkte Modul-Steuerung)
3. **MQTT Monitor Testing** (Nachrichten-Monitoring)

---

## 📝 **Notizen & Beobachtungen**

### **Dashboard-Verhalten:**
- ________
- ________
- ________

### **MQTT-Verbindung:**
- ________
- ________
- ________

### **Module-Reaktionen:**
- ________
- ________
- ________

---

**Status:** 📋 **TESTING-PROTOKOLL ERSTELLT** - Bereit für systematisches Template-Testing
