# 📊 DPS & AIQS Session Analysis - Zusammenfassung

**Datum:** 2025-12-16  
**Status:** ✅ Alle Sessions analysiert

---

## 📈 Gesamt-Statistik

### Analysierte Sessions
- **Anzahl:** 13 Session-Dateien
- **DPS-Analysen:** 13 vollständige Analysen
- **AIQS-Analysen:** 13 vollständige Analysen

### DPS Gesamt-Statistik

**Commands gefunden:**
- `PICK`: 60x
- `DROP`: 61x
- `INPUT_RGB`: 18x (Farberkennung)
- `RGB_NFC`: 21x (NFC-Code auslesen)
- `startCalibration`: 45x
- `factsheetRequest`: 11x
- `reset`: 2x

**Order-Kontexte:**
- **STORAGE-ORDER Kontext:** 423 Messages (aus 3 Sessions: blue, red, white)
- **PRODUCTION-ORDER Kontext:** 532 Messages (aus 4 Sessions: blue, bwr, red, white)

### AIQS Gesamt-Statistik

**Commands gefunden:**
- `CHECK_QUALITY`: 53x (ML-basierte Qualitätsprüfung)
- `PICK`: 16x
- `DROP`: 18x
- `factsheetRequest`: 9x

**CHECK_QUALITY:**
- **Ergebnisse:** 53 (PASSED/FAILED)
- **Kontext-Messages:** 1,113 Messages (Photo, ML, Mustererkennung)

---

## 📁 Analysierte Session-Dateien

### Production Orders
1. ✅ `production_order_blue_20251110_180619.log`
   - DPS: 957 Messages, PRODUCTION-ORDER Kontext: 117 Messages
   - AIQS: 770 Messages, CHECK_QUALITY: 7 Ergebnisse

2. ✅ `production_order_bwr_20251110_182819.log`
   - DPS: 2,894 Messages, PRODUCTION-ORDER Kontext: 177 Messages
   - AIQS: 2,256 Messages, CHECK_QUALITY: 26 Ergebnisse

3. ✅ `production_order_red_20251110_180152.log`
   - DPS: 801 Messages, PRODUCTION-ORDER Kontext: 117 Messages
   - AIQS: 652 Messages, CHECK_QUALITY: 8 Ergebnisse

4. ✅ `production_order_white_20251110_184459.log`
   - DPS: 795 Messages, PRODUCTION-ORDER Kontext: 121 Messages
   - AIQS: 643 Messages, CHECK_QUALITY: 6 Ergebnisse

### Storage Orders
5. ✅ `storage_order_blue_20251110_181104.log`
   - DPS: 461 Messages, STORAGE-ORDER Kontext: 141 Messages (INPUT_RGB, RGB_NFC)
   - AIQS: 367 Messages, CHECK_QUALITY: 1 Ergebnis

6. ✅ `storage_order_red_20251110_181336.log`
   - DPS: 492 Messages, STORAGE-ORDER Kontext: 141 Messages (INPUT_RGB, RGB_NFC)
   - AIQS: 393 Messages, CHECK_QUALITY: 1 Ergebnis

7. ✅ `storage_order_white_20251110_181619.log`
   - DPS: 493 Messages, STORAGE-ORDER Kontext: 141 Messages (INPUT_RGB, RGB_NFC)
   - AIQS: 394 Messages, CHECK_QUALITY: 1 Ergebnis

### Weitere Sessions
8. ✅ `Start_20251110_175151.log`
   - DPS: 3,217 Messages (Startup/Initialisierung)
   - AIQS: 3,095 Messages

9. ✅ `calibrate_dps_1_20251202_101939.log`
   - DPS: 1,362 Messages (Calibration)
   - AIQS: 1,132 Messages

10. ✅ `default_test_session.log`
    - DPS: 153 Messages
    - AIQS: 137 Messages, CHECK_QUALITY: 2 Ergebnisse

11. ✅ `auftrag-blau_1.log`
    - DPS: 2 Messages
    - AIQS: 2 Messages, CHECK_QUALITY: 1 Ergebnis

12. ✅ `auftrag-rot_1.log`
    - DPS: 2 Messages
    - AIQS: 1 Message

13. ✅ `auftrag-weiss_1.log`
    - DPS: 1 Message
    - AIQS: 1 Message

---

## ✅ Erfasste Abläufe

### DPS Abläufe

#### ✅ STORAGE-ORDER Flow (vollständig erfasst)
- **Sessions:** storage_order_blue, storage_order_red, storage_order_white
- **Commands:** INPUT_RGB (18x), RGB_NFC (21x)
- **Kontext:** 423 Messages mit Farberkennung und NFC-Auslesen
- **Topics:** 
  - `module/v1/ff/SVR4H73275/order` (INPUT_RGB, RGB_NFC Commands)
  - `module/v1/ff/NodeRed/SVR4H73275/state` (State Updates mit Farbe und NFC-Code)
  - `ccu/order/request` (STORAGE Order Requests)

#### ✅ PRODUCTION-ORDER Flow (vollständig erfasst)
- **Sessions:** production_order_blue, production_order_bwr, production_order_red, production_order_white
- **Commands:** PICK (60x), DROP (61x), RGB_NFC (nach Produktion)
- **Kontext:** 532 Messages mit NFC-Auslesen nach Produktion
- **Topics:**
  - `module/v1/ff/SVR4H73275/order` (PICK, DROP Commands)
  - `module/v1/ff/SVR4H73275/state` (State Updates)
  - `ccu/order/completed` (PRODUCTION Order Completion)

#### ✅ Calibration Flow (erfasst)
- **Session:** calibrate_dps_1_20251202_101939.log
- **Commands:** startCalibration (45x)
- **Topics:** `ccu/state/calibration/SVR4H73275`, `ccu/set/calibration`

### AIQS Abläufe

#### ✅ CHECK_QUALITY Flow (vollständig erfasst)
- **Sessions:** Alle Production Orders + Storage Orders + Test Sessions
- **Commands:** CHECK_QUALITY (53x), PICK (16x), DROP (18x)
- **Ergebnisse:** 53 CHECK_QUALITY Ergebnisse (PASSED/FAILED)
- **Kontext:** 1,113 Messages mit Photo, ML, Mustererkennung
- **Topics:**
  - `module/v1/ff/SVR4H76530/order` (CHECK_QUALITY Commands)
  - `module/v1/ff/NodeRed/SVR4H76530/state` (CHECK_QUALITY Ergebnisse)
  - `ccu/order/completed` (Production Steps mit CHECK_QUALITY)

#### ✅ Production Flow Integration (vollständig erfasst)
- **Sessions:** Alle Production Orders
- **Integration:** CHECK_QUALITY als Teil des Production-Order-Flows
- **Ergebnisse:** PASSED (Order fortgesetzt) oder FAILED (Order abgebrochen)

---

## 📊 Datenverfügbarkeit für GitHub

### DPS-Daten
**Verzeichnis:** `data/osf-data/dps-analysis/`

**Verfügbare Dateien pro Session:**
- `{session_name}_metadata.json` - Metadaten und Statistiken
- `{session_name}_all_dps_messages.json` - Alle DPS-relevanten Messages
- `{session_name}_dps_state.json` - DPS State Updates
- `{session_name}_dps_order.json` - DPS Order Commands
- `{session_name}_storage_order_context.json` - STORAGE-ORDER Kontext (wenn vorhanden)
- `{session_name}_production_order_context.json` - PRODUCTION-ORDER Kontext (wenn vorhanden)
- Weitere kategorisierte Dateien (connection, instantAction, etc.)

**Wichtige Sessions für GitHub:**
- `storage_order_*_storage_order_context.json` - STORAGE-ORDER Flow mit INPUT_RGB und RGB_NFC
- `production_order_*_production_order_context.json` - PRODUCTION-ORDER Flow mit NFC-Auslesen

### AIQS-Daten
**Verzeichnis:** `data/osf-data/aiqs-analysis/`

**Verfügbare Dateien pro Session:**
- `{session_name}_metadata.json` - Metadaten und Statistiken
- `{session_name}_all_aiqs_messages.json` - Alle AIQS-relevanten Messages
- `{session_name}_aiqs_state.json` - AIQS State Updates
- `{session_name}_aiqs_order.json` - AIQS Order Commands
- `{session_name}_check_quality_results.json` - CHECK_QUALITY Ergebnisse (PASSED/FAILED)
- `{session_name}_check_quality_context.json` - CHECK_QUALITY Kontext (Photo, ML, Mustererkennung)
- Weitere kategorisierte Dateien (connection, instantAction, etc.)

**Wichtige Sessions für GitHub:**
- `production_order_*_check_quality_context.json` - CHECK_QUALITY Flow mit Photo/ML
- `production_order_*_check_quality_results.json` - CHECK_QUALITY Ergebnisse

---

## ✅ Vollständigkeit

### DPS
- ✅ **STORAGE-ORDER:** Vollständig erfasst (3 Sessions, alle Farben: blue, red, white)
- ✅ **PRODUCTION-ORDER:** Vollständig erfasst (4 Sessions, alle Farben: blue, bwr, red, white)
- ✅ **INPUT_RGB:** 18x erfasst (Farberkennung)
- ✅ **RGB_NFC:** 21x erfasst (NFC-Code auslesen)
- ✅ **PICK/DROP:** Vollständig erfasst (60x PICK, 61x DROP)
- ✅ **Calibration:** Erfasst (calibrate_dps_1 Session)

### AIQS
- ✅ **CHECK_QUALITY:** Vollständig erfasst (53 Ergebnisse aus 13 Sessions)
- ✅ **PASSED/FAILED:** Beide Ergebnisse vorhanden
- ✅ **Photo/ML:** Kontext-Messages erfasst (1,113 Messages)
- ✅ **Production Integration:** Vollständig erfasst (alle Production Orders)
- ✅ **PICK/DROP:** Vollständig erfasst (16x PICK, 18x DROP)

---

## 🎯 Für GitHub bereit

**Alle Daten sind:**
- ✅ Vollständig analysiert (13 Sessions)
- ✅ Strukturiert (JSON-Format)
- ✅ Kategorisiert (nach Topics und Abläufen)
- ✅ Dokumentiert (README-Dateien)
- ✅ GitHub-ready (keine großen Binärdaten)

**GitHub kann:**
- ✅ Alle JSON-Dateien verwenden
- ✅ Alle Abläufe nachvollziehen (STORAGE-ORDER, PRODUCTION-ORDER, CHECK_QUALITY)
- ✅ Beispiel-Apps erstellen basierend auf echten Daten
- ✅ Alle Commands und States verstehen
