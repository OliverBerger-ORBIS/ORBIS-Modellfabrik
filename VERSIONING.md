# Versionsnummer – Single Source of Truth

**Es gibt genau eine Stelle, an der die Versionsnummer gepflegt wird.**

## Source of Truth

**Datei:** `package.json` (Projektroot)  
**Feld:** `"version"`

```json
{
  "name": "osf-workspace",
  "version": "0.7.8",
  ...
}
```

## Änderung der Version

**Nur hier anpassen:** `package.json` → Feld `"version"`

Alle anderen Stellen werden daraus abgeleitet:
- `osf/apps/osf-ui/src/environments/version.ts` wird bei jedem Build aus `package.json` generiert (Skript: `scripts/update-ui-version.js`)
- Die in der UI angezeigte Version kommt aus `version.ts`

## Ablauf

1. Version in `package.json` ändern
2. Build ausführen (z.B. `nx build osf-ui` oder `npm run build:github-pages`) → `version.ts` wird automatisch aktualisiert
3. Keine weiteren manuellen Schritte nötig

## Für KI-Assistenten

- **Suchbegriff:** `"version"` in `package.json` (root)
- **Nicht:** `version.ts` oder andere Dateien manuell ändern – sie sind abgeleitet
