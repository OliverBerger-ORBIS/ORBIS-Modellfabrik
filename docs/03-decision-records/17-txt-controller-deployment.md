# Decision Record: TXT-Controller Deployment mit ROBO Pro Coding

**Datum:** 06.01.2026  
**Status:** ✅ **Accepted**  
**Kontext:** Task 18 (AIQS-Kamera-Integration) erfordert Deployment von modifiziertem Code auf TXT-Controller. Nach Tests verschiedener Methoden wurde ROBO Pro Coding als Deployment-Methode gewählt.

---

## Entscheidung

**ROBO Pro Coding** wird als primäre Methode für Deployment von Code auf TXT-Controller verwendet.

**Verzeichnis-Struktur (Stand 18.02.2026 – ohne vendor):**
- `integrations/TXT-{MODULE}/archives/` = Alle OSF-Versionen (`.ft` Archive für ROBO Pro, Deployment)
- `integrations/TXT-{MODULE}/workspaces/` = Entpackte Versionen (für Code-Analyse, grep, diff)
- Originale/ältere Versionen bei Bedarf aus [Fischertechnik-Repo](https://github.com/fischertechnik/Agile-Production-Simulation-24V) besorgen

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

### Prinzip (ohne vendor – alle OSF-Versionen in integrations)

**1. `integrations/TXT-{MODULE}/archives/`**
- **Zweck:** Alle OSF-Versionen als `.ft` Archive (öffnen, ändern, speichern, deployen)
- **Inhalt:** z.B. `FF_AI_24V.ft`, `FF_AI_24V_wav.ft`, `FF_AI_24V_cam.ft`
- **Verwendung:** ROBO Pro öffnet von hier ODER vom Controller; „Speichern unter“ nach hier
- **Status:** Quelle of Truth für OSF

**2. `integrations/TXT-{MODULE}/workspaces/`**
- **Zweck:** Code-Analyse (grep, diff, IDE)
- **Inhalt:** Entpackte Projekte (`unzip …/archives/Variante.ft -d .`)
- **Verwendung:** Bei Bedarf aus archives/ extrahieren

**3. Fischertechnik-Repo (bei Bedarf)**
- **URL:** [Agile-Production-Simulation-24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V)
- **Zweck:** Originale oder ältere Versionen besorgen

### Beispiel-Struktur

```
integrations/TXT-AIQS/
├── archives/
│   ├── FF_AI_24V.ft          # Original
│   ├── FF_AI_24V_wav.ft
│   └── FF_AI_24V_cam.ft     # … weitere Varianten
└── workspaces/
    └── FF_AI_24V_cam/        # entpackt für Analyse
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

1. **Projekt öffnen:**
   - ROBO Pro Coding öffnen
   - Öffnen aus `integrations/TXT-*/archives/` ODER vom Controller
   - Für Python-Änderungen: Professional Modus aktivieren

2. **Umbenennen & speichern** (bei neuer Variante)

3. **Änderungen durchführen:**
   - Code direkt in ROBO Pro bearbeiten
   - ROBO Pro speichert automatisch

4. **Speichern** (Cmd+S)

5. **Deployment:**
   - TXT-Controller verbinden (DHCP-Scan, API-Key)
   - Projekt deployen
   - Testen

6. **Optional: Entpacken für Analyse:**
   ```bash
   cd integrations/TXT-AIQS/workspaces/ && unzip ../archives/FF_AI_24V_cam.ft -d .
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
