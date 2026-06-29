# Session Manager Release Checkliste

Diese Checkliste gilt fuer Releases der Helper-App `session_manager/`.

## 1) Version festlegen (SemVer)
- Patch (`X.Y.Z+1`): Bugfix
- Minor (`X.Y+1.0`): neues Feature
- Major (`X+1.0.0`): Breaking Change

## 2) Versionskonsistenz herstellen
- `session_manager/__init__.py` -> `__version__ = "X.Y.Z"`
- `session_manager/app.py` -> Sidebar-Footer auf `vX.Y.Z`
- `docs/04-howto/helper_apps/session-manager/README.md` -> Navigation-Version auf `vX.Y.Z`

Pruefkommando:

```bash
rg "__version__|v[0-9]+\\.[0-9]+\\.[0-9]+" \
  session_manager/__init__.py \
  session_manager/app.py \
  docs/04-howto/helper_apps/session-manager/README.md
```

## 3) Validierung
- Session Manager lokal startbar: `streamlit run session_manager/app.py`
- Betroffene Workflows kurz smoke-testen (z. B. Replay/Recorder/Object Detection)

## 4) Commit erstellen
- Nur relevante Dateien stagen.
- Commit-Message mit Release-Bezug (z. B. `release(session-manager): vX.Y.Z`).

## 5) Tag setzen (verbindlich namespaced)

```bash
git tag session-manager-vX.Y.Z
```

## 6) Push

```bash
git push origin <branch>
git push origin session-manager-vX.Y.Z
```

## 7) Nachkontrolle

```bash
git tag --list "session-manager-v*"
```

## Retrospektive Tags (ohne Historie zu brechen)
Wenn ein frueheres Release keinen Namespaced Tag hat:

```bash
git tag session-manager-vX.Y.Z <release-commit-sha>
git push origin session-manager-vX.Y.Z
```

Wichtig:
- Bestehende Tags nicht verschieben oder loeschen.
- Nur fehlende Zusatz-Tags setzen.
