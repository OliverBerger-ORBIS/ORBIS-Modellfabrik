# How-To: TXT-Controller Deployment mit ROBO Pro Coding

**Datum:** 06.01.2026  
**Status:** ✅ **Vollständig dokumentiert**

---

## 🎯 Übersicht

Dieses How-To beschreibt den vollständigen Workflow für Deployment von Code auf TXT-Controller mit ROBO Pro Coding.

**Ziel:** Code-Änderungen auf TXT-Controller deployen und testen.

---

## ⚠️ Wichtige Hinweise

| Punkt | Hinweis |
|------|---------|
| **Keine Änderungen im Repo** | Änderungen am TXT-Projekt erfolgen **ausschließlich in RoboPro Coding**. Die Quellen in `workspaces/` werden nicht direkt bearbeitet – sie dienen der Analyse (z.B. nach Entpacken des `.ft`-Archivs). |
| **RoboPro erforderlich** | RoboPro Coding muss installiert sein. *Aktuell:* nur auf **Mac** verfügbar. |
| **Blockly-Modus für Code** | Code-Anpassungen erfolgen im **Blockly-Editor** (grafischer Modus). Das Ergebnis wird über den generierten Python-Code verifiziert. |
| **Vorsicht bei Python-Edit** | Direktes Bearbeiten des Python-Codes im Professional-Modus kann **problematisch** sein: Der TXT reagiert extrem empfindlich auf Leerzeichen und Einrückungen. |

---

## 📋 Voraussetzungen

### Software
- ✅ **ROBO Pro Coding** installiert (*aktuell nur Mac*)
- ✅ **TXT-Controller** im WLAN (DHCP-Bereich `192.168.0.101-199`)
- ✅ **SSH optional:** Nur für direkten Controller-Zugriff (muss am Controller aktiviert werden)

### Netzwerk
- **DHCP-Bereich:** `192.168.0.101-199`
- **IP-Adresse:** Wird automatisch per DHCP vergeben
- **ROBO Pro Coding scannt automatisch** den DHCP-Bereich

### Zugangsdaten
- **Username:** `ft` (für SSH, falls aktiviert)
- **Password:** `fischertechnik` (für SSH, falls aktiviert)
- **API-Key:** Muss vom Controller-Display abgelesen werden (ändert sich ständig!)

---

## 📁 Verzeichnis-Struktur

### Prinzip

```
vendor/fischertechnik/              # Git-Submodul, Original .ft Archive
integrations/TXT-{MODULE}/
├── archives/                       # Varianten als .ft Archive (für Deployment)
│   └── FF_AI_24V_mod.ft
└── workspaces/                     # Entpackte Versionen (für Analyse)
    ├── FF_AI_24V/                  # Original (entpackt)
    └── FF_AI_24V_mod/              # Variante (entpackt)
```

### Bedeutung

- **`vendor/fischertechnik/`:** Original `.ft` Archive aus Git-Submodul, Workspace für ROBO Pro
- **`integrations/TXT-{MODULE}/archives/`:** Varianten als `.ft` Archive, werden deployed
- **`integrations/TXT-{MODULE}/workspaces/`:** Entpackte Versionen, für Code-Analyse

---

## 🔄 Workflow

### Phase 1: Original öffnen

1. **ROBO Pro Coding öffnen**
2. **Projekt öffnen:**
   - `Datei → Öffnen` oder `Cmd+O`
   - `vendor/fischertechnik/FF_AI_24V.ft` auswählen
   - Projekt wird geladen

3. **Modus wählen:**
   - **Grafischer Modus:** Für visuelle Programmierung (Blockly)
   - **Professional Modus:** Für Python-Code-Änderungen
     - `Ansicht → Art der Programmierung → Python-Programmierung`

### Phase 2: Änderungen durchführen

**Im Grafischen Modus:**
- ✅ Visuelle Änderungen mit Blockly-Blöcken
- ❌ Python-Code nicht direkt bearbeitbar
- ❌ Neue Python-Dateien können nicht erstellt werden

**Im Professional Modus:**
- ✅ Python-Code direkt bearbeiten
- ✅ Neue Dateien erstellen (z.B. `lib/camera_publisher.py`)
- ✅ Dateien modifizieren
- ✅ ROBO Pro speichert automatisch

**Hinweis:** Für Änderungen an **bestehendem Code** (z.B. AIQS Quality-Check): **Blockly-Modus** bevorzugen. Der TXT reagiert empfindlich auf Leerzeichen; Änderungen über Blockly vermeiden Formatierungsprobleme. Professional Modus für neue Python-Dateien.

### Phase 3: Variante speichern

1. **"Speichern unter..."** wählen (sofort nach Öffnen, damit das Original unverändert bleibt):
   - `Datei → Speichern unter...` oder `Cmd+Shift+S`
   - Pfad: `integrations/TXT-AIQS/archives/FF_AI_24V_mod.ft`
   - ROBO Pro erstellt `.ft` Archiv automatisch
   - **Projekt umbenennen** (falls gewünscht): Name in RoboPro auf den neuen Variantennamen setzen

2. **Optional: Entpacken für Analyse:**
   ```bash
   cd integrations/TXT-AIQS/workspaces/
   unzip ../archives/FF_AI_24V_mod.ft -d .
   ```

### Phase 4: TXT-Controller verbinden

1. **ROBO Pro Coding:**
   - `Controller → Verbinden` oder entsprechendes Menü
   - **WLAN-Verbindung** wählen

2. **Controller-Scan:**
   - ROBO Pro Coding scannt automatisch DHCP-Bereich `192.168.0.101-199`
   - Controller erscheint in Liste

3. **API-Key eingeben:**
   - **API-Key vom Controller-Display ablesen** (wird angezeigt)
   - API-Key in ROBO Pro Coding eingeben
   - **Wichtig:** API-Key ändert sich ständig, muss vor jeder Verbindung neu abgelesen werden!

4. **Verbindung herstellen:**
   - Controller aus Liste auswählen
   - Verbindung wird hergestellt

### Phase 5: Deployment

1. **Projekt deployen:**
   - `Controller → Download` oder entsprechendes Menü
   - Projekt wird auf den TXT-Controller übertragen

2. **Auf dem TXT-Controller:**
   - Deploytes Programm in der Programmliste auswählen (**Load**)
   - Als aktives Programm festlegen
   - **Autostart** aktivieren (Programm startet beim Booten des Controllers)

3. **Testen:**
   - Funktionalität prüfen
   - MQTT-Topics prüfen (falls relevant)
   - Logs prüfen (falls verfügbar)

---

---

## 📦 Original entpacken (einmalig)

Falls Original aus `vendor/` für Analyse entpackt werden soll:

```bash
# Original aus vendor/ entpacken
cd integrations/TXT-AIQS/workspaces/
unzip ../../../vendor/fischertechnik/FF_AI_24V.ft -d .
```

**Ergebnis:**
```
integrations/TXT-AIQS/workspaces/FF_AI_24V/
├── FF_AI_24V.py
├── lib/
└── data/
```

---

## 🔍 Troubleshooting

### Problem: Controller wird nicht gefunden

**Lösung:**
- Prüfen ob Controller im WLAN ist
- Prüfen ob Controller im DHCP-Bereich `192.168.0.101-199` ist
- ROBO Pro Coding Scan erneut starten

### Problem: Verbindung schlägt fehl

**Lösung:**
- API-Key vom Controller-Display neu ablesen
- API-Key kann sich geändert haben (bei Neustart)
- Controller neu starten und API-Key erneut ablesen

### Problem: Falscher API-Key

**Lösung:**
- API-Key muss vom Controller-Display abgelesen werden
- API-Key ändert sich ständig, nicht speichern!
- Bei jedem Verbindungsversuch neu ablesen

### Problem: Python-Code nicht bearbeitbar

**Lösung:**
- Professional Modus aktivieren: `Ansicht → Art der Programmierung → Python-Programmierung`
- Oder: `FF_AI_24V_orig_py.ft` direkt öffnen (bereits im Professional Modus)

### Problem: Programm funktioniert nicht nach Deployment

**Lösung:**
- Prüfen ob alle Dateien korrekt deployed wurden
- Prüfen ob `.blockly` Dateien vorhanden sind (falls nötig)
- Prüfen ob Programm-Modus korrekt ist (Professional vs. Grafisch)
- **Wichtig:** Externe Archiv-Manipulation kann zu Funktionsverlust führen!

---

## 📝 Best Practices

### ✅ DO

- ✅ Änderungen direkt in ROBO Pro durchführen
- ✅ ROBO Pro für alle Archiv-Operationen verwenden
- ✅ Original-Archiv als Basis verwenden
- ✅ Neue Versionen über "Speichern unter..." erstellen
- ✅ Professional Modus für Python-Code-Änderungen verwenden
- ✅ API-Key vor jeder Verbindung neu ablesen

### ❌ DON'T

- ❌ Archive außerhalb von ROBO Pro modifizieren
- ❌ Dateien manuell umbenennen
- ❌ Scripts für Archiv-Manipulation verwenden (außer einfache Fälle)
- ❌ ZIP-Archive direkt bearbeiten
- ❌ API-Key speichern (ändert sich ständig)

---

## 🔗 Verwandte Dokumentation

- [Decision Record: TXT-Controller Deployment](../03-decision-records/17-txt-controller-deployment.md) - Entscheidungsgrundlagen
- [ROBO Pro Connection Guide](../../06-integrations/TXT-AIQS/ROBO_PRO_CONNECTION_GUIDE.md) - Verbindungsanleitung
- [ROBO Pro Troubleshooting](../../06-integrations/ROBO_PRO_TROUBLESHOOTING.md) - Problembehandlung

---

## 📚 Beispiel: Kamera-MQTT-Publikation

**Ziel:** Kamera-Bilder von AIQS über MQTT publizieren.

### Schritt 1: Original öffnen

1. ROBO Pro Coding öffnen
2. `vendor/fischertechnik/FF_AI_24V.ft` öffnen
3. Professional Modus aktivieren: `Ansicht → Art der Programmierung → Python-Programmierung`

### Schritt 2: Neue Datei erstellen

1. `lib/camera_publisher.py` erstellen
2. Code einfügen (analog zu TXT-DPS `SSC_Publisher.py`)
3. ROBO Pro speichert automatisch

### Schritt 3: Integration

1. `lib/sorting_line.py` öffnen
2. `camera_publisher` importieren und starten
3. ROBO Pro speichert automatisch

### Schritt 4: Variante speichern

1. `Datei → Speichern unter...` → `integrations/TXT-AIQS/archives/FF_AI_24V_camera.ft`
2. ROBO Pro erstellt Archiv automatisch

### Schritt 5: Deployment

1. TXT-Controller verbinden (API-Key ablesen)
2. Projekt deployen
3. Programm starten und testen

---

*Letzte Aktualisierung: 06.01.2026*

