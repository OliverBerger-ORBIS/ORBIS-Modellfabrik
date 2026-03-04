# Temporäre Analyse: CCU Quality-Fail Verhalten

**Erstellt:** 04.03.2026  
**Zweck:** Analyse und Planung für Sprint-17-Task "CCU: Quality-Fail ersetzt Order"  
**Status:** Vor Implementierung prüfen – Info behalten oder löschen/integrieren?

---

## Kontext

Bei `CHECK_QUALITY result=FAILED` erstellt die CCU aktuell automatisch einen neuen Production-Order (sofern Roh-Ware im HBW verfügbar). Das soll geändert werden können.

## Session-Analyse: `mixed-sw-pw-sw-pwnok-pw`

**Ablauf:** Production WHITE → AIQS CHECK_QUALITY NOT-OK → CCU erstellt Ersatzauftrag.

**Wer reagiert auf AIQS-Status?**

| System | Reaktion |
|--------|----------|
| **CCU** | Einziger Subscriber für Order-Logik. `handleActionUpdate` → `handleActionUpdateQualityCheckFailure` → `createOrder`. |
| **NodeRed/AIQS** | OPCUA good/bad für physische Sortierung. Keine Order-Logik. |
| **FTS** | Erhält nur Befehle von CCU. Reagiert nicht auf AIQS-Status. |
| **TXT-Controller** | Liest OPCUA. Keine MQTT-Order-Logik. |

**Fazit:** Änderung ausschließlich in CCU. Keine Anpassungen an FTS, NodeRed, anderen Modulen.

---

## Implementierungsoptionen (noch zu entscheiden)

### Option A: Config-Toggle

- `productionSettings.skipReplaceOrderOnQualityFailure`
- Frontend-UI, Env-Override
- **Nachteile:** Zusätzliche Komplexität, auf RPi kaum sinnvoll umschaltbar (nur neues Deployment), Toggle-Dokumentation nötig

### Option B: Verhaltensänderung ohne Toggle, alte Version tagen

- Neue Version: Immer "nur Order auf ERROR, kein Ersatzauftrag"
- Alte Version: Git-Tag (z.B. `ccu-quality-fail-auto-replace`) für Rollback
- **Vorteile:** Einfacher Code, klare Semantik, kein Toggle-Overhead
- **Nachteile:** Umschalten = neues Image deployen (aber bei Option A i.d.R. auch)

---

## Toggle-Bedenken & pragmatische Anwendung

**Bedenken (zutreffend):**
- Toggles erhöhen Codekomplexität (Branching, Defaults, Dokumentation)
- Toggles müssen irgendwo gesetzt werden (Config, Env, UI)
- Auf RPi: Kein praktischer Weg, Toggle zur Laufzeit zu ändern – typischerweise nur durch neues Deployment
- Wenn ohnehin Redeploy nötig ist: Version-Tag bringt dasselbe mit weniger Code

**Wann Toggles sinnvoll sind:**
- A/B-Tests, schrittweise Rollouts
- Unterschiedliche Deployments (z.B. Demo vs. Produktion) mit verschiedenem Verhalten
- Häufiges Umschalten ohne Redeploy
- Wenn MES/DSP später den QM-Check übernimmt und wir beide Modi parallel brauchen

**Wann Toggles unnötig sind:**
- Eindeutig gewünschtes neues Verhalten, altes ist Legacy
- Nur eine Deployment-Umgebung (RPi)
- Prozessentscheidung, die man nicht im Betrieb umschaltet

**Falls Toggles trotzdem gewählt werden – Dokumentation:**
- `integrations/APS-CCU/README.md` oder `docs/04-howto/` – Abschnitt "CCU-Konfiguration"
- Env-Variablen: In `docker-compose-prod.yml` bzw. `.env.example` dokumentieren
- Config-Optionen: In `GeneralConfig` (TypeScript) und ggf. Factory-Config-UI

**Empfehlung für diesen Fall:** Option B (ohne Toggle). Das gewünschte Verhalten ist eine klare Prozessänderung. Rollback bei Bedarf über `docker pull <image>:<alter-tag>`.

---

## Implementierungsplan (ToDos)

**Entscheidung:** Option B umsetzen. Kein automatischer Ersatzauftrag.

### ToDos

- [x] **T1** CCU-Code: In `handleActionUpdateQualityCheckFailure()` den Aufruf von `createOrder()` entfernen.
- [x] **T2** Unit-Test anpassen: "should NOT create replacement order when quality check fails (order remains ERROR)"
- [x] **T3** OSF-MODIFICATIONS.md: Modifikation 2 Status auf "✅ Umgesetzt"
- [ ] **T4** (optional) Git-Tag `ccu-quality-fail-auto-replace` vor dem Merge setzen (falls Rollback auf altes Verhalten nötig)
- [ ] **T5** E2E-Test: Nach Deploy auf RPi – Session mit mixed-sw-pw-sw-pwnok-pw reproduzieren, prüfen: Kein Ersatzauftrag nach AIQS FAILED

### Testbarkeit

| Testart | Was | Wann |
|---------|-----|------|
| **Unit-Test** | `handleActionUpdate` mit `State.FINISHED, QualityResult.FAILED` → `createOrder` nicht aufgerufen; Order state=ERROR, Steps CANCELLED | Sofort (lokal, CI) |
| **Integration** | CCU-Tests ausführen: `cd integrations/APS-CCU/central-control && npm test` | Sofort |
| **E2E (RPi)** | Reale Session: Production WHITE → AIQS NOT-OK → keine neue Order | Nach Deployment auf RPi |

E2E kann erst nach Deployment erfolgen – Unit-Tests sichern die Logik-Änderung ab.

---

## Deployment auf RPi (abarbeitbare Checkliste)

**Quelle:** [integrations/APS-CCU/DEPLOYMENT.md](../../integrations/APS-CCU/DEPLOYMENT.md)  
**RPi-Projektpfad:** `/home/ff22/fischertechnik/ff-central-control-unit` (vom Deploy-Skript verwendet)

### Voraussetzungen

- [ ] Docker Desktop mit buildx
- [ ] SSH-Zugang zum Raspberry Pi: `ff22@192.168.0.100` (Passwort: `ff22+`)
- [ ] Laptop und RPi im gleichen Netzwerk (192.168.0.x)
- [ ] Optional: SSH-Keys eingerichtet, um Passwort-Abfragen zu vermeiden

### Schritte

| Nr. | Aktion | Befehl / Hinweis |
|-----|--------|------------------|
| 1 | **Build** (nur CCU, schneller als Full-Build) | `cd integrations/APS-CCU && npm run docker:build -- userdev central` |
| 2 | **Deploy** (Images übertragen, laden, Compose aktualisieren, neu starten) | `npm run docker:deploy -- ff22@192.168.0.100 userdev central` |
| 3 | **Verifikation** – Container läuft | `ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml ps"` |
| 4 | **Verifikation** – Logs prüfen | `ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml logs central-control --tail 50"` |
| 5 | **E2E-Test** – Quality-Fail prüfen | Session `mixed-sw-pw-sw-pwnok-pw` reproduzieren: Production WHITE → AIQS NOT-OK → **kein** Ersatzauftrag, Order bleibt ERROR |

### Troubleshooting

| Problem | Lösung |
|---------|--------|
| SSH Host key verification failed | `ssh-keygen -R 192.168.0.100` |
| Build schlägt / No space | `docker system prune -a` |
| REMOTE_DIR falsch auf Pi | Pfad im Deploy-Skript prüfen: `integrations/APS-CCU/scripts/deploy-to-rpi.js` |

**Weitere Details:** [DEPLOYMENT.md](../../integrations/APS-CCU/DEPLOYMENT.md#troubleshooting)

---

*Siehe sprint_17.md für Task-Referenz. Nach letztem Commit: Dokument ggf. löschen oder in OSF-MODIFICATIONS.md integrieren.*
