# TXT-Controller Source-Zugriff und Projekt-Struktur

**Datum:** 23.12.2025  
**Status:** ✅ Source-Dateien erfolgreich kopiert und strukturiert

## 📁 Projekt-Struktur

Alle TXT-Controller-Sourcen sind unter `integrations/` organisiert, spiegeln die Struktur auf dem Controller wider:

```
integrations/
├── TXT-AIQS/
│   └── workspaces/
│       └── FF_AI_24V/          # Original-Sourcen vom Controller
│           ├── FF_AI_24V.py
│           ├── lib/
│           │   ├── camera.py
│           │   ├── machine_learning.py
│           │   └── ...
│           └── data/
├── TXT-DPS/
│   └── workspaces/
│       └── FF_DPS_24V/
├── TXT-FTS/
│   └── workspaces/
│       └── fts_main/
└── TXT-CGW/
    └── workspaces/
        └── FF_CGW/
```

**Prinzip:**
- `workspaces/` spiegelt die Struktur auf dem TXT-Controller (`/opt/ft/workspaces/`)
- Original-Sourcen werden **nicht** modifiziert
- Analysen und Refactoring in separaten Verzeichnissen (wenn nötig)

## 🔐 Zugangsdaten

### Standard-Credentials (alle TXT-Controller)
- **Username:** `ft`
- **Password:** `fischertechnik`
- **SSH Port:** `22` (muss aktiviert werden)
- **Web-Interface Port:** `80`

### IP-Adressbereich
- **DHCP-Bereich:** `192.168.0.101-199` (Router-Einstellungen der APS)
- **TXT-Controller:** Alle Controller im WLAN bekommen IPs aus diesem Bereich

**Wichtig:** 
- Im DPS-Modul gibt es **zwei** TXT-Controller:
  - **TXT-DPS:** Steuert DPS-Modul, liefert Sensordaten - **relevant**
  - **TXT-CGW:** Cloud Gateway, transportiert Topics in Fischertechnik-Cloud - **nicht relevant für lokale Fabrik-Prozesse**
- Beide werden im Configuration-Tab korrekt angezeigt (technisch richtig)
- Für Analyse und Integration nur TXT-DPS relevant

**IP-Adresse ermitteln:**
- Controller-Display: IP wird angezeigt
- Oder Netzwerk-Scan: `nmap -sn 192.168.0.101-199`

## 📥 Source-Dateien kopieren

### Voraussetzungen
1. **SSH aktivieren:** TXT-Controller → Settings → SSH aktivieren
2. **IP-Adresse ermitteln:** Controller-Display oder Netzwerk-Scan (`192.168.0.101-199`)

### Methode 1: SSH/SCP (Empfohlen)

**Schritte:**
1. **SSH-Verbindung:**
   ```bash
   ssh ft@<TXT-IP>
   # Password: fischertechnik
   ```

2. **Projekt-Verzeichnis finden:**
   ```bash
   cd ~/workspaces/
   ls -la
   # FF_AI_24V/     (AIQS)
   # FF_DPS_24V/    (DPS)
   # fts_main/      (FTS)
   # FF_CGW/        (CGW)
   ```

3. **Archiv erstellen:**
   ```bash
   cd ~/workspaces/FF_AI_24V
   tar -czf /tmp/ff_ai_24v_complete.tar.gz FF_AI_24V.py lib/ data/
   ```

4. **Archiv kopieren (neues Terminal auf Mac):**
   ```bash
   scp ft@<TXT-IP>:/tmp/ff_ai_24v_complete.tar.gz /tmp/
   ```

5. **Archiv entpacken:**
   ```bash
   cd integrations/TXT-AIQS/
   mkdir -p workspaces
   tar -xzf /tmp/ff_ai_24v_complete.tar.gz -C workspaces/
   mkdir -p workspaces/FF_AI_24V
   mv workspaces/FF_AI_24V.py workspaces/lib workspaces/data workspaces/FF_AI_24V/
   ```

### Methode 2: ROBO Pro Coding (Ziel-Methode, noch zu erarbeiten)

**Idealer Workflow:**
1. Projekt in ROBO Pro Coding öffnen
2. Python-Code direkt exportieren/kopieren
3. Oder direkt auf Controller deployen

**Status:** ⚠️ **Noch zu erarbeiten**
- Wie ändert man Sourcen in ROBO Pro Coding?
- Wie deployed man geänderte Sourcen auf den Controller?
- Welche Workflows gibt es für Development?

## 🔄 Sourcen ändern und deployen (Task 18 - Kamera-Bilder)

**Ziel:** Kamera-Bilder von AIQS über MQTT publizieren und in OSF-UI anzeigen

**Hinweis:** Nur relevante Controller werden angepasst (TXT-DPS, TXT-FTS, TXT-AIQS). TXT-CGW wird nicht angepasst, da er nur Cloud-Forwarding macht.

### Strategie

**MQTT-Topic publizieren (Bestätigt, analog zu TXT-DPS)**
1. **Referenz-Implementierung (TXT-DPS):**
   - TXT-DPS publiziert bereits Kamera-Bilder über MQTT: `/j1/txt/1/i/cam`
   - Format: `{"ts":"...","data":"data:image/jpeg;base64,..."}`
   - Implementierung: `integrations/TXT-DPS/workspaces/FF_DPS_24V/lib/SSC_Publisher.py`
     - `publish_camera()` Funktion (Zeilen 78-87)
     - `frame_to_base64()` Helper (Zeilen 171-176)
     - `image_callback()` Event-Handler (Zeilen 100-102)

2. **TXT-AIQS Anpassung:**
   - `lib/machine_learning.py` erweitern oder `lib/camera_publisher.py` erstellen
   - Kamera-Frames abrufen: `TXT_SLD_M_USB1_1_camera.read_frame()` (bereits vorhanden)
   - Base64-Kodierung: Analog zu TXT-DPS `frame_to_base64()` Funktion
   - MQTT-Publikation: Topic `aiqs/camera` (eigenes Topic mit `aiqs/*` Präfix zur Kennzeichnung als "nicht-Standard" Erweiterung)
   - Format: `{"ts":"...","data":"data:image/jpeg;base64,..."}`

3. **OSF-UI Integration (pausiert bis TXT-Controller Deployment erfolgreich):**
   - Gateway `aiqsCameraFrames$` Stream muss erstellt werden (analog zu `cameraFrames$`)
   - Topic-Abonnement `aiqs/#` muss hinzugefügt werden
   - Anzeige im AIQS-Tab oder als Detail im Shopfloor-Tab (bei AIQS-Station-Auswahl)
   - **WICHTIG:** OSF-UI Änderungen werden erst nach erfolgreichem TXT-Controller Deployment durchgeführt

**HTTP-Endpoint (Verworfen)**
- ❌ Browser-Sicherheitsprobleme (Private Network Access)
- ❌ Zusätzliche CORS-Konfiguration nötig
- ❌ Komplexere Integration
- ❌ `AiqsCameraService` wurde gelöscht (nicht verwendet)

### Workflow (Noch zu erarbeiten)

1. **Sourcen lokal ändern:**
   - In `integrations/TXT-AIQS/workspaces/FF_AI_24V/` arbeiten
   - Änderungen vornehmen (z.B. MQTT-Topic hinzufügen)

2. **ROBO Pro Coding Workflow:**
   - Wie lädt man geänderte Sourcen in ROBO Pro Coding?
   - Wie deployed man auf den Controller?
   - Gibt es einen direkten Upload-Mechanismus?

3. **Testing:**
   - Änderungen auf Controller testen
   - MQTT-Topic prüfen
   - OSF-UI Integration testen

**Status:** ⚠️ **ROBO Pro Coding Workflow muss noch erarbeitet werden**

## 🚨 Troubleshooting

### SSH-Verbindung fehlgeschlagen
- **SSH aktivieren:** TXT-Controller → Settings → SSH
- **IP prüfen:** Controller-Display oder `nmap -sn 192.168.0.101-199`
- **Port-Test:** `nc -zv <TXT-IP> 22`
- **Credentials:** `ft` / `fischertechnik`

### Dateien nicht gefunden
- **Projekt-Verzeichnis:** `~/workspaces/` auf Controller
- **Pfad prüfen:** `cd ~/workspaces/ && ls -la`

## 📚 Verwandte Dokumentation

- [TXT-AIQS README](./TXT-AIQS/README.md) - AIQS-spezifische Details
- [ROBO_PRO_TROUBLESHOOTING.md](./ROBO_PRO_TROUBLESHOOTING.md) - ROBO Pro Coding Probleme

## 📝 Konsolidierte Dokumente

**Diese Dokumentation konsolidiert:**
- ✅ `TXT-ACCESS_GUIDE.md` → Zugriffsmethoden integriert
- ✅ `TXT-SOURCE-COPY-PROCESS.md` → Source-Copy-Prozess integriert
- ✅ `TXT-AIQS/FIND_CONTROLLER_GUIDE.md` → Controller finden integriert
- ✅ `TXT-AIQS/USB_CONNECTION_GUIDE.md` → USB-Verbindung integriert
- ✅ `TXT-AIQS/CAMERA_ENDPOINT_DISCOVERY.md` → HTTP-Ansatz nicht gewählt
- ✅ `TXT-AIQS/COPY_FROM_SSH.md` → SSH-Prozess integriert
- ✅ `TXT-AIQS/ENDPOINT_TEST_RESULTS.md` → HTTP-Ansatz nicht gewählt
- ✅ `TXT-AIQS/TEST_HTTP_ENDPOINTS.md` → HTTP-Ansatz nicht gewählt

