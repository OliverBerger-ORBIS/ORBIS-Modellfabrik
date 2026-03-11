# Versionsnummer – Single Source of Truth

**Eine einzige Datei: `package.json` → `"version"`**

---

## 🎯 Release-Version setzen (empfohlen)

**Ein Befehl für alles:**

```bash
npm run version:bump -- 0.8.8
```

Das aktualisiert: `package.json` → `version.ts` → `VERSION`

---

## Manuell (falls nötig)

1. **Nur** `package.json` → Feld `"version"` ändern
2. `npm run update-version` ausführen
3. **Nicht** `version.ts` oder `VERSION` manuell anfassen – die werden generiert

---

## Abgeleitete Dateien (nicht manuell ändern)

| Datei | Wird geschrieben von |
|-------|----------------------|
| `version.ts` | `update-ui-version.js` |
| `VERSION` | `update-ui-version.js` |
| GitHub Pages Build | Deploy-Workflow liest `package.json` direkt |

---

## Ablauf bei Release

1. `npm run version:bump -- 0.8.8`
2. CHANGELOG.md Eintrag ergänzen
3. Commit, Push → Deploy nutzt package.json automatisch

## Für KI-Assistenten / Cursor

- **Version ändern:** Nur `package.json` → `"version"`, danach `npm run update-version`
- **Oder:** `npm run version:bump -- X.Y.Z` (macht beides)
- **Nie:** `version.ts` oder `VERSION` manuell editieren
