# Versionsnummer – Single Source of Truth

**Es gibt genau eine Stelle, an der die Versionsnummer gepflegt wird.**

## Source of Truth

**Datei:** `package.json` (Projektroot)  
**Feld:** `"version"`

```json
{
  "name": "osf-workspace",
  "version": "0.7.10",
  ...
}
```

## Änderung der Version

**Nur hier anpassen:** `package.json` → Feld `"version"`

Alle anderen Stellen werden daraus abgeleitet:
- **`osf/apps/osf-ui/src/environments/version.ts`** – wird bei jedem Build generiert (Skript: `scripts/update-ui-version.js`)
- **`VERSION`** – wird von `scripts/update-ui-version.js` aus `package.json` geschrieben
- **`pyproject.toml` (orbis-smartfactory)** – liest Version aus `VERSION` zur Installationszeit

Session Manager teilt dieselbe Version mit OSF (u.a. für Docker-Deployment und Replay-Umgebung).

## Ablauf

1. Version in `package.json` ändern
2. Build ausführen (z.B. `nx build osf-ui` oder `npm run build:github-pages`) → `version.ts` wird automatisch aktualisiert
3. `pip install -e ".[dev]"` verwendet die Version aus `package.json` automatisch
4. Keine weiteren manuellen Schritte nötig

## Für KI-Assistenten

- **Suchbegriff:** `"version"` in `package.json` (root)
- **Nicht:** `version.ts`, `setup.py` oder andere Dateien manuell ändern – sie sind abgeleitet
