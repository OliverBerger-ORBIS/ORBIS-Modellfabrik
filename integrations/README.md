# Integrations – TXT Controller, Arduino, NodeRED

Dieses Verzeichnis enthält Hardware-Integrationen für das OSF (ORBIS SmartFactory) Projekt.

---

## Arduino

| Ort | Zweck | Inhalt |
|-----|-------|--------|
| `integrations/Arduino/` | **Sketchbook** – Arduino IDE öffnet diesen Ordner | Sketches (z. B. `Vibrationssensor_SW420/`) |

**Setup:** Arduino IDE → Einstellungen → Sketchbook-Speicherort = `integrations/Arduino` (absoluter Pfad).

**Doku:** [Arduino Vibrationssensor](../docs/05-hardware/arduino-vibrationssensor.md) | [Arduino IDE Setup](../docs/04-howto/setup/arduino-ide-setup.md)

---

## TXT Controller Modules

Structure follows [DR-17](../docs/03-decision-records/17-txt-controller-deployment.md) and [How-To: TXT-Controller Deployment](../docs/04-howto/txt-controller-deployment.md).

### Structure

| Ort | Zweck | Inhalt |
|-----|-------|--------|
| `integrations/TXT-{MODULE}/archives/` | **Alle OSF-Versionen** – für ROBO Pro und Deployment | `.ft` Archive (öffnen, ändern, speichern, deployen) |
| `integrations/TXT-{MODULE}/workspaces/` | Code-Analyse | Entpackte Versionen (`unzip …/archives/Variante.ft -d .`) |

**Workflow:** Projekt öffnen (aus `archives/` oder vom Controller) → umbenennen → speichern → ändern → speichern → mit Controller verbinden → zurück auf Controller downloaden. Originale/ältere Versionen bei Bedarf aus [Fischertechnik-Repo](https://github.com/fischertechnik/Agile-Production-Simulation-24V) holen.

### TXT-{MODULE} Verzeichnisstruktur

```
integrations/TXT-{MODULE}/
├── archives/                # Varianten (nur wo modifiziert, z.B. TXT-AIQS)
│   └── FF_AI_24V_cam.ft
└── workspaces/              # Entpackt für Analyse
    └── {PROJEKT_NAME}/      # FF_AI_24V/, FF_DPS_24V/, fts_main/, FF_CGW/
        ├── {PROJEKT_NAME}.py
        ├── lib/
        └── data/
```

**Detaillierte Anleitung:** [How-To: TXT-Controller Deployment](../docs/04-howto/txt-controller-deployment.md) | [DR-17](../docs/03-decision-records/17-txt-controller-deployment.md)

## TXT Modules

### 1. **TXT-DPS** - DPS TXT Controller (Haupt-Controller)
- **Source:** `FF_DPS_24V` from TXT-Controller
- **IP:** `192.168.0.101` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-p0F4`
- **Role:** DPS-Modul-Steuerung und Sensordaten
- **Key Files:** `FF_DPS_24V.py`, `lib/DPS.py`, `lib/mqtt_utils.py`
- **Features:** Order management, MQTT integration, VDA5050, NFC-Reader, Sensoren
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

### 2. **TXT-CGW** - Cloud Gateway Controller (Nicht relevant)
- **Source:** `FF_CGW` from TXT-Controller
- **IP:** `192.168.0.102` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-WiY4`
- **Role:** Cloud Gateway - transportiert MQTT-Topics in Fischertechnik-Cloud
- **Key Files:** `FF_CGW.py`, `lib/RemoteGateway.py`
- **Features:** MQTT-Forwarding zu Fischertechnik-Cloud
- **Status:** ⚠️ **Nicht relevant für lokale Fabrik-Prozesse** - Nur Cloud-Forwarding

**Hinweis:** Im DPS-Modul (`SVR4H73275`) gibt es zwei TXT-Controller. Der TXT-DPS steuert das Modul und liefert die Sensordaten, der TXT-CGW dient nur als Cloud-Gateway. Beide werden im Configuration-Tab korrekt angezeigt, aber nur TXT-DPS ist für die Fabrik-Prozesse relevant.

### 3. **TXT-FTS** - FTS TXT Controller
- **Source:** `fts_main` from TXT-Controller
- **IP:** `192.168.0.107` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-5iO4`
- **Role:** Transport system control
- **Key Files:** `fts_main.py`, `lib/line_follower.py`, `lib/charger.py`
- **Features:** Line following, battery management, collision detection
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

### 4. **TXT-AIQS** - AIQS TXT Controller
- **Source:** `FF_AI_24V` from TXT-Controller
- **IP:** `192.168.0.158` (aktuell, DHCP-assigned, war `192.168.0.103`)
- **Controller-ID:** `TXT4.0-Q0Y4`
- **Role:** Quality control and AI image recognition
- **Key Files:** `FF_AI_24V.py`, `lib/machine_learning.py`, `lib/camera.py`
- **Features:** Image recognition, quality control, sorting line
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

## Extraction (Optional)

Workspaces bei Bedarf aus `.ft` Archiven erzeugen:

```bash
cd integrations/TXT-AIQS/workspaces/
unzip ../archives/FF_AI_24V_cam.ft -d .
```

## Analysis Status

- ✅ **TXT-DPS**: Extracted and ready for analysis (relevant für Fabrik-Prozesse)
- ✅ **TXT-FTS**: Extracted and ready for analysis (relevant)
- ✅ **TXT-AIQS**: Extracted and ready for analysis (relevant)
- ✅ **TXT-CGW**: Extracted (nicht relevant für Fabrik-Prozesse, nur Cloud-Gateway)

## Next Steps

1. **Order ID Logic**: Analyze `TXT-DPS/FF_DPS_24V.py` for order management
2. **MQTT Topics**: Extract topic patterns from `mqtt_utils.py` files
3. **VDA5050 Integration**: Study `vda5050.py` for AGV communication
4. **Module Communication**: Map inter-module message flows

## Related Documentation

- [APS Architecture](../../docs/02-architecture/)
- [MQTT Analysis](../../docs/06-integrations/mosquitto/)
- [System Context](../../docs/02-architecture/system-context.md)
