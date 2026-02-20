# Decision Record: TXT-Controller Deployment mit ROBO Pro Coding

**Datum:** 06.01.2026  
**Status:** ✅ **Accepted**  
**Kontext:** Task 18 (AIQS-Kamera-Integration) erfordert Deployment von modifiziertem Code auf TXT-Controller. Nach Tests verschiedener Methoden wurde ROBO Pro Coding als Deployment-Methode gewählt.

---

## Entscheidung

**ROBO Pro Coding** wird als primäre Methode für Deployment von Code auf TXT-Controller verwendet.

**Verzeichnis-Struktur:**
- `vendor/fischertechnik/` = Git-Submodul, Original `.ft` Archive, Workspace für ROBO Pro
- `integrations/TXT-{MODULE}/archives/` = Varianten als `.ft` Archive (für Deployment)
- `integrations/TXT-{MODULE}/workspaces/` = Entpackte Versionen (für Code-Analyse)

**Modus:** Grafischer Modus (Blockly) für visuelle Programmierung, Professional Modus (Python) für Code-Änderungen.

---

## Alternativen

### Alternative 1: SSH/SCP direkt
- **Beschreibung:** Code direkt über SSH/SCP auf Controller kopieren
- **Warum verworfen:** 
  - Permission-Problem: `ft` User kann nicht in `ftgui` Verzeichnis schreiben
  - `txtapi` läuft als `ftgui` User und benötigt Dateien in `ftgui` Workspace
  - Keine offizielle Methode, fehleranfällig
  - Keine visuelle Programmierung möglich

### Alternative 2: Externe Archiv-Manipulation
- **Beschreibung:** `.ft` Archive außerhalb von ROBO Pro entpacken, ändern, neu packen
- **Warum verworfen:**
  - Führt zu Funktionsverlust (z.B. `check_quality` funktioniert nicht mehr)
  - ROBO Pro hat interne Metadaten, die bei externer Manipulation gebrochen werden
  - Komprimierung und Pfade müssen exakt stimmen (unkomprimiert, führendes `/`)
  - Sehr fehleranfällig, nicht zuverlässig

### Alternative 3: HTTP-Endpoint für Kamera-Bilder
- **Beschreibung:** Kamera-Bilder über HTTP-Endpoint bereitstellen
- **Warum verworfen:**
  - Browser-Sicherheitsprobleme (Private Network Access)
  - Zusätzliche CORS-Konfiguration nötig
  - Komplexere Integration
  - MQTT ist bereits etabliert und funktioniert

---

## Konsequenzen

### Positiv
- ✅ **Offizielle Methode:** ROBO Pro Coding ist die offizielle IDE von Fischertechnik
- ✅ **Permission-Problem gelöst:** ROBO Pro verwendet `ftgui` User automatisch
- ✅ **Visuelle Programmierung:** Blockly-Programmierung möglich
- ✅ **Zuverlässig:** ROBO Pro verwaltet Archiv-Struktur korrekt
- ✅ **Einfach:** Grafische Oberfläche, keine Kommandozeile nötig
- ✅ **Deployment funktioniert:** Getestet und bestätigt

### Negativ
- ⚠️ **ROBO Pro Coding erforderlich:** Muss installiert sein (Mac/Windows)
- ⚠️ **Modus-Wechsel:** Für Python-Änderungen muss Professional Modus verwendet werden
- ⚠️ **API-Key:** Muss vom Controller-Display abgelesen werden (ändert sich ständig)
- ⚠️ **DHCP-Scan:** Controller-IP kann sich ändern (wird aber automatisch gescannt)

### Risiken
- **API-Key ändert sich:** Muss vor jeder Verbindung neu abgelesen werden
- **Modus-Konfusion:** Grafischer Modus zeigt Python-Code nicht direkt bearbeitbar
- **Externe Manipulation:** Archive sollten nicht außerhalb von ROBO Pro geändert werden

---

## Verzeichnis-Struktur

### Prinzip

**1. `vendor/fischertechnik/`** (Git-Submodul)
- **Zweck:** Original `.ft` Archive aus offiziellem Fischertechnik Repository
- **Inhalt:** Nur Original-Archive (z.B. `FF_AI_24V.ft`, `FF_DPS_24V.ft`)
- **Verwendung:** Workspace für ROBO Pro (Projekte öffnen)
- **Status:** Git-Submodul, keine Varianten

**2. `integrations/TXT-{MODULE}/archives/`** (Varianten als `.ft` Archive)
- **Zweck:** Varianten für Deployment auf TXT-Controller
- **Inhalt:** Modifizierte `.ft` Archive (z.B. `FF_AI_24V_mod.ft`)
- **Verwendung:** Wird von ROBO Pro erstellt (über "Speichern unter...")
- **Status:** Wird auf TXT Controller deployed

**3. `integrations/TXT-{MODULE}/workspaces/`** (Entpackte Versionen)
- **Zweck:** Code-Analyse außerhalb von ROBO Pro
- **Inhalt:** Entpackte Projekte (z.B. `FF_AI_24V/`, `FF_AI_24V_mod/`)
- **Verwendung:** Für Code-Analyse, Git-Diff, externe Tools
- **Status:** Wird aus `.ft` Archiven extrahiert

### Beispiel-Struktur

```
vendor/fischertechnik/
├── FF_AI_24V.ft              # Original (Git-Submodul)
└── FF_DPS_24V.ft             # Original (Git-Submodul)

integrations/TXT-AIQS/
├── archives/
│   └── FF_AI_24V_mod.ft      # Variante (für Deployment)
└── workspaces/
    ├── FF_AI_24V/             # Original (entpackt)
    └── FF_AI_24V_mod/         # Variante (entpackt für Analyse)
```

---

## Grafischer Modus vs. Professional Modus

### Grafischer Modus (Blockly)
- ✅ Visuelle Programmierung mit Blöcken
- ✅ Deployment funktioniert
- ❌ Python-Code nicht direkt bearbeitbar
- ❌ Neue Python-Dateien können nicht erstellt werden
- **Verwendung:** Visuelle Programmierung, einfache Änderungen

### Professional Modus (Python)
- ✅ Python-Code direkt bearbeitbar
- ✅ Neue Dateien können erstellt werden
- ✅ Vollständige Kontrolle über Code
- ✅ Deployment funktioniert
- **Verwendung:** Python-Code-Änderungen, neue Module

**Entscheidung:** Professional Modus für Code-Änderungen, Grafischer Modus für visuelle Programmierung.

---

## Implementierung

### Workflow

1. **Original öffnen:**
   - ROBO Pro Coding öffnen
   - `vendor/fischertechnik/FF_AI_24V.ft` öffnen
   - Für Python-Änderungen: Professional Modus aktivieren

2. **Änderungen durchführen:**
   - Code direkt in ROBO Pro bearbeiten
   - ROBO Pro speichert automatisch

3. **Variante speichern:**
   - "Speichern unter..." → `integrations/TXT-AIQS/archives/FF_AI_24V_mod.ft`
   - ROBO Pro erstellt `.ft` Archiv automatisch

4. **Deployment:**
   - TXT-Controller verbinden (DHCP-Scan, API-Key)
   - Projekt deployen
   - Testen

5. **Optional: Entpacken für Analyse:**
   ```bash
   unzip integrations/TXT-AIQS/archives/FF_AI_24V_mod.ft -d integrations/TXT-AIQS/workspaces/
   ```

### Voraussetzungen

- ✅ ROBO Pro Coding installiert (Mac/Windows)
- ✅ TXT-Controller im WLAN (DHCP-Bereich `192.168.0.101-199`)
- ✅ API-Key vom Controller-Display ablesen
- ✅ SSH optional (nur für direkten Controller-Zugriff)

---

## Verwandte Dokumentation

- [How-To: TXT-Controller Deployment](../04-howto/txt-controller-deployment.md) - Schritt-für-Schritt Anleitung
- [ROBO Pro Final Conclusion](../../06-integrations/TXT-AIQS/ROBO_PRO_FINAL_CONCLUSION.md) - Test-Ergebnisse
- [ROBO Pro Workflow Final](../../06-integrations/TXT-AIQS/ROBO_PRO_WORKFLOW_FINAL.md) - Finaler Workflow

---

*Entscheidung getroffen von: Projektteam*  
*Basierend auf Tests und Analysen vom 05.01.2026 - 06.01.2026*
