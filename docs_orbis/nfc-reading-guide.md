# 📱 NFC-Code Auslesung Guide

## 📋 Übersicht

Dieser Guide beschreibt die Schritte zur physischen Auslesung der restlichen 14 NFC-Codes von den Werkstücken.

## 🎯 Ziel

**Aktueller Stand:** 10 von 24 NFC-Codes gefunden (41.7%)
**Ziel:** Alle 24 NFC-Codes auslesen und zuordnen

## 📊 Aktuelle Zuordnung

### ✅ Gefundene Codes (10/24)

#### 🔴 Rote Werkstücke (8/8 - Vollständig!)
- **R1:** `040a8dca341291` ✅
- **R2:** `04158cca341291` ✅
- **R3:** `047389ca341291` ✅
- **R4:** `047c8bca341291` ✅
- **R5:** `047f8cca341290` ✅
- **R6:** `04808dca341291` ✅
- **R7:** `04ab8bca341290` ✅
- **R8:** `04c489ca341290` ✅

#### ⚪ Weiße Werkstücke (2/8 - 6 fehlen)
- **W1:** `04798eca341290` ✅
- **W2:** `048989ca341290` ✅
- **W3:** ❓ Zu finden
- **W4:** ❓ Zu finden
- **W5:** ❓ Zu finden
- **W6:** ❓ Zu finden
- **W7:** ❓ Zu finden
- **W8:** ❓ Zu finden

#### 🔵 Blaue Werkstücke (0/8 - Alle fehlen)
- **B1:** ❓ Zu finden
- **B2:** ❓ Zu finden
- **B3:** ❓ Zu finden
- **B4:** ❓ Zu finden
- **B5:** ❓ Zu finden
- **B6:** ❓ Zu finden
- **B7:** ❓ Zu finden
- **B8:** ❓ Zu finden

## 🔧 Auslesung-Schritte

### 1. Vorbereitung
- [ ] **NFC-Reader** bereitstellen (Smartphone mit NFC-App)
- [ ] **Werkstück-Set** identifizieren (24 Werkstücke)
- [ ] **Farb-Kategorisierung** bestätigen (8 Rot, 8 Weiß, 8 Blau)
- [ ] **Auslesung-Tabelle** vorbereiten

### 2. NFC-Reader Setup
```bash
# Android: NFC Tools Pro oder ähnliche App
# iOS: NFC Tools oder Shortcuts App
# Alternative: USB NFC-Reader mit PC
```

### 3. Auslesung-Prozess
1. **Werkstück identifizieren** (Farbe + Nummer)
2. **NFC-Reader aktivieren**
3. **Werkstück an Reader halten**
4. **NFC-Code notieren**
5. **In Tabelle eintragen**

### 4. Auslesung-Tabelle

| Werkstück | Farbe | NFC-Code | Status |
|-----------|-------|----------|--------|
| R1 | 🔴 Rot | `040a8dca341291` | ✅ Gefunden |
| R2 | 🔴 Rot | `04158cca341291` | ✅ Gefunden |
| R3 | 🔴 Rot | `047389ca341291` | ✅ Gefunden |
| R4 | 🔴 Rot | `047c8bca341291` | ✅ Gefunden |
| R5 | 🔴 Rot | `047f8cca341290` | ✅ Gefunden |
| R6 | 🔴 Rot | `04808dca341291` | ✅ Gefunden |
| R7 | 🔴 Rot | `04ab8bca341290` | ✅ Gefunden |
| R8 | 🔴 Rot | `04c489ca341290` | ✅ Gefunden |
| W1 | ⚪ Weiß | `04798eca341290` | ✅ Gefunden |
| W2 | ⚪ Weiß | `048989ca341290` | ✅ Gefunden |
| W3 | ⚪ Weiß | | 🔍 Zu finden |
| W4 | ⚪ Weiß | | 🔍 Zu finden |
| W5 | ⚪ Weiß | | 🔍 Zu finden |
| W6 | ⚪ Weiß | | 🔍 Zu finden |
| W7 | ⚪ Weiß | | 🔍 Zu finden |
| W8 | ⚪ Weiß | | 🔍 Zu finden |
| B1 | 🔵 Blau | | 🔍 Zu finden |
| B2 | 🔵 Blau | | 🔍 Zu finden |
| B3 | 🔵 Blau | | 🔍 Zu finden |
| B4 | 🔵 Blau | | 🔍 Zu finden |
| B5 | 🔵 Blau | | 🔍 Zu finden |
| B6 | 🔵 Blau | | 🔍 Zu finden |
| B7 | 🔵 Blau | | 🔍 Zu finden |
| B8 | 🔵 Blau | | 🔍 Zu finden |

## 📱 NFC-Reader Apps

### Android
- **NFC Tools Pro** (Empfohlen)
- **NFC TagInfo**
- **NFC TagWriter**

### iOS
- **NFC Tools**
- **Shortcuts** (mit NFC-Action)
- **NFC TagReader**

### Desktop
- **ACR122U NFC Reader**
- **USB NFC-Reader**

## 🔍 Muster-Analyse

### Bekannte Muster
- **Format:** 12-stellige Hex-Codes
- **Präfix:** `04` (konsistent)
- **Suffix:** `ca34129x` (x = 0 oder 1)
- **Farb-Erkennung:** Letzte Ziffer
  - `0` = Weiß/Blau
  - `1` = Rot

### Erwartete Codes
Basierend auf dem Muster sollten die fehlenden Codes folgendes Format haben:
- **Weiße Werkstücke:** `04xxxxca341290`
- **Blaue Werkstücke:** `04xxxxca341290`

## 📝 Aktualisierung der Mapping-Datei

Nach der Auslesung muss die Datei `src_orbis/mqtt/tools/nfc_workpiece_mapping.py` aktualisiert werden:

```python
NFC_WORKPIECE_MAPPING = {
    # 🔴 Rote Werkstücke (8/8 - Vollständig!)
    "R1": "040a8dca341291",
    "R2": "04158cca341291", 
    "R3": "047389ca341291",
    "R4": "047c8bca341291",
    "R5": "047f8cca341290",
    "R6": "04808dca341291",
    "R7": "04ab8bca341290",
    "R8": "04c489ca341290",
    
    # ⚪ Weiße Werkstücke (2/8 - 6 zu finden)
    "W1": "04798eca341290",
    "W2": "048989ca341290",
    "W3": "NEUER_NFC_CODE",  # Zu finden
    "W4": "NEUER_NFC_CODE",  # Zu finden
    "W5": "NEUER_NFC_CODE",  # Zu finden
    "W6": "NEUER_NFC_CODE",  # Zu finden
    "W7": "NEUER_NFC_CODE",  # Zu finden
    "W8": "NEUER_NFC_CODE",  # Zu finden
    
    # 🔵 Blaue Werkstücke (0/8 - Alle zu finden)
    "B1": "NEUER_NFC_CODE",  # Zu finden
    "B2": "NEUER_NFC_CODE",  # Zu finden
    "B3": "NEUER_NFC_CODE",  # Zu finden
    "B4": "NEUER_NFC_CODE",  # Zu finden
    "B5": "NEUER_NFC_CODE",  # Zu finden
    "B6": "NEUER_NFC_CODE",  # Zu finden
    "B7": "NEUER_NFC_CODE",  # Zu finden
    "B8": "NEUER_NFC_CODE",  # Zu finden
}
```

## 🚀 Nächste Schritte

### Nach der Auslesung
1. **Mapping-Datei aktualisieren**
2. **Dashboard testen** (neue Werkstücke verfügbar)
3. **Template Messages testen** (alle 24 Werkstücke)
4. **Live-Test im Büro** durchführen

### Dashboard Integration
- ✅ **Dropdown-Menü** mit benutzerfreundlichen IDs
- ✅ **Farb-Visualisierung** (🔴⚪🔵)
- ✅ **NFC-Code Anzeige** für Debugging
- ✅ **Statistiken** (24/24 = 100%)

---

**Status:** 🔍 **Bereit für physische Auslesung** - 14 NFC-Codes fehlen noch! 📱
