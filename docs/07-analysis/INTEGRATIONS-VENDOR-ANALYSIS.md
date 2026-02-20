# Analyse: integrations/ vs. vendor/ – Doppeltes Haushalten?

**Datum:** 18.02.2026  
**Aktualisiert:** 18.02.2026 (Quelle-of-Truth = TXT-Controller)  
**Kontext:** Prüfung auf Redundanz zwischen `integrations/` und `vendor/` unter Berücksichtigung des [TXT-Controller How-To](../04-howto/txt-controller-deployment.md).

---

## 1. Korrekter Workflow

**Projekt öffnen** (zwei Quellen möglich):
- Aus `integrations/TXT-{MODULE}/archives/` – unsere gespeicherten `.ft` Archive
- Vom TXT-Controller – aktuelle Live-Version

**Vorgehensweise:**
1. ROBO Pro starten
2. Projekt öffnen: aus `integrations/…/archives/` ODER vom Controller
3. Umbenennen → speichern (ins Repo unter `archives/`)
4. Ändern → speichern
5. Mit Controller verbinden → zurück auf Controller downloaden

**Struktur in integrations:**
- `archives/` = `.ft` Archive (für ROBO Pro öffnen/deployen)
- `workspaces/` = entpackte Versionen (für Code-Analyse, grep, diff)

**Alle OSF-Versionen liegen in integrations.** Das Submodul `vendor/` ist nicht nötig; Originale oder ältere Versionen bei Bedarf aus dem [Fischertechnik-Repository](https://github.com/fischertechnik/Agile-Production-Simulation-24V) besorgen.

---

## 2. FF_AI_24V – Erwartete Varianten

| Suffix | Beschreibung |
|--------|--------------|
| *(keins)* | Original (Basis) |
| `_wav` | Ton in sorting_line bei result passed/failed (unterschiedliche Töne) |
| `_cam` | Ton + MQTT-Nachricht Topic `quality_check` |
| `_cam_clfn` | Wie _cam, Topic um `classification` erweitert |

**Wenn im Repo nur _wav vorhanden ist** → Workflow wurde nicht eingehalten oder funktioniert nicht korrekt.

---

## 3. Ist-Zustand

### vendor/fischertechnik (Git-Submodul)

| Datei | Herkunft |
|-------|----------|
| FF_AI_24V.ft, FF_AI_24V_wav.ft | Fischertechnik Agile-Production-Simulation-24V |
| FF_DPS_24V.ft, FF_CGW.ft, fts_main.ft, ServoCalib_DPS.ft | Fischertechnik |

**Bewertung:** Redundant, wenn Workflow „vom Controller öffnen“ konsequent genutzt wird. Original bei Bedarf aus Fischertechnik-Repo wiederherstellbar.

### integrations/TXT-AIQS/archives/

| Datei | Status |
|-------|--------|
| FF_AI_24V_cam.ft | ✅ vorhanden |
| FF_AI_24V_cam_clfn.ft | ✅ vorhanden |
| FF_AI_24V_wav.ft | ✅ vorhanden |
| FF_AI_24V.ft (Original) | ❌ fehlt – ggf. vom Controller sichern |

### integrations/TXT-*/workspaces/

Entpackte Versionen für Code-Analyse (z.B. grep, diff). Können bei Bedarf aus `archives/` regeneriert werden (`unzip`).

---

## 4. Empfehlung: Auf ein Verzeichnis konsolidieren

### 4.1 vendor/ entfernen

- **Originale** bei Bedarf aus [Fischertechnik Agile-Production-Simulation-24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V) holen
- **Quelle of Truth** = TXT-Controller bzw. `integrations/archives/`
- **Workflow:** Controller → ROBO Pro → „Speichern unter“ nach `integrations/TXT-*/archives/` → Download auf Controller

### 4.2 Schritte (nach Freigabe)

1. **Submodul vendor entfernen** (`.gitmodules`, `git submodule deinit`, Verzeichnis)
2. **How-To + DR-17 anpassen:** Workflow ohne vendor dokumentieren
3. **Fischertechnik-Repo dokumentieren:** [Agile-Production-Simulation-24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V) – dort Originale oder ältere Versionen bei Bedarf besorgen
4. **FF_AI_24V.ft (Original)** ins Repo aufnehmen, wenn noch nicht vorhanden (aus Controller oder Fischertechnik-Repo)

### 4.3 workspaces/

- **Option A:** Beibehalten für Code-Analyse (grep, IDE, Dokumentation)
- **Option B:** Bei Bedarf aus archives/ entpacken, nicht versionieren (`.gitignore`)

---

## 5. Referenzen

- [How-To: TXT-Controller Deployment](../04-howto/txt-controller-deployment.md)
- [Decision Record 17: TXT-Controller Deployment](../03-decision-records/17-txt-controller-deployment.md)
- [TXT-AIQS README](../06-integrations/TXT-AIQS/README.md)
