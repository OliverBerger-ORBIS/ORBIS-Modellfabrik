## npm & Node.js: Einfache Anleitung zum Einrichten der lokalen Entwicklungsumgebung

Dieses How‑To erklärt auf Deutsch, wie du Node.js / npm so einrichtest, dass du in allen PowerShell‑Sitzungen (z. B. VS Code Integrated Terminal) zuverlässig `npm` verwenden kannst. Es enthält mehrere Optionen (winget, non‑admin Install, nvm, Scoop) und konkrete PowerShell‑Befehle, die in dieser Projekt‑Umgebung funktionieren.

Zielgruppe: Entwickler*innen, die lokal an `ORBIS-Modellfabrik` arbeiten und die OSF (Angular/Nx) App `osf-ui` entwickeln oder testen wollen.

Kurzversion (für Fortgeschrittene)
- Überprüfen: `node --version` und `npm --version`
- Wenn Node fehlt: Installieren mit `winget` (Admin) oder eine non‑admin Installation in `%USERPROFILE%\tools` und den Ordner zur User‑PATH hinzufügen
- Terminal/VS Code neu starten
- Im Repo-Root: `.\scripts\run-omf3.ps1` oder `npx nx serve osf-ui --configuration=development`

1) Prüfen, ob Node / npm verfügbar sind

```powershell
node --version
npm --version
where.exe node
```

Wenn Versionen angezeigt werden, ist Node bereits verfügbar. Wenn nicht, weiter zu Schritt 2.

2) Installationsoptionen

a) Empfohlen (einfach, mit Admin): winget

```powershell
# Administrator-PowerShell
winget install OpenJS.NodeJS.LTS
```

b) Non‑Admin (manuell) — portable ZIP/EXE in %USERPROFILE%\tools

1. Lade Node.js LTS Windows ZIP oder das Windows Binary herunter (https://nodejs.org/)
2. Entpacke z. B. nach: `%USERPROFILE%\tools\node-v<version>-win-x64` (bei dir z.B. `C:\Users\beroli\tools\node-v18.20.0-win-x64`)
3. Füge den Ordner zur User‑PATH hinzu (siehe Schritt 3)

c) nvm-windows (empfohlen, wenn du mehrere Node‑Versionen benötigst)

1. Lade nvm‑windows von https://github.com/coreybutler/nvm-windows/releases herunter
2. Installiere und verwende z. B.: `nvm install 18.20.0` / `nvm use 18.20.0`

d) Scoop (alternative ohne Admin)

```powershell
# Ersteinrichtung (wenn noch nicht installiert)
iwr -useb get.scoop.sh | iex
scoop install nodejs-lts
```

3) Node dauerhaft in die User PATH eintragen (PowerShell)

Wenn du Node manuell nach `%USERPROFILE%\tools` entpackt hast, füge den Ordner zur User‑PATH hinzu:

```powershell
$nodeDir = "$env:USERPROFILE\tools\node-v18.20.0-win-x64"  # passe an
$current = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($current -notlike "*$nodeDir*") {
  [Environment]::SetEnvironmentVariable('Path', "$current;$nodeDir", 'User')
  Write-Host "Node-Pfad zur USER PATH hinzugefügt. Bitte alle PowerShell-/VSCode-Fenster neu starten."
} else {
  Write-Host "Node-Pfad ist bereits in der USER PATH vorhanden."
}
```

Nach dem Setzen: Schließe und öffne VS Code oder starte dein Terminal neu, damit neue Prozesse den aktualisierten PATH sehen.

4) Überprüfen nach Änderung

```powershell
where.exe node
node --version
npm --version
```

5) Projekt‑Abhängigkeiten installieren (im Repo Root)

Für reproduzierbare Builds (CI‑Lockfile) benutze `npm ci`. Bei älteren Lockfiles/Mono‑Repos kann `--legacy-peer-deps` nötig sein.

```powershell
# Sauberer, reproduzierbarer Install
npm ci --legacy-peer-deps

# Falls npm ci fehlschlägt, als Fallback:
npm install --legacy-peer-deps
```

6) Dev‑Server starten (OSF — osf-ui)

```powershell
# Einfache Variante
npx nx serve osf-ui --configuration=development

# Oder mit dem projektspezifischen Launcher (legt Logs an)
.\scripts\run-omf3.ps1

# Live-Log anschauen (in separatem Terminal)
Get-Content .\logs\omf3.log -Wait -Tail 50
```

7) Häufige Probleme & Lösungen

- "Node.js is not installed or not in PATH":
  - Prüfe `where.exe node` und die User‑PATH Variable. Meistens hilft ein Terminal/VSCode‑Neustart.
- Berechtigungsprobleme bei globalen Paketen: vermeide `npm install -g` ohne Notwendigkeit; nutze lokale node_modules oder ein Tool wie `nvm`.
- Peer‑Dependency‑Fehler bei `npm ci`: `--legacy-peer-deps` kann hier helfen.
- Antivirus/Defender blockiert node.exe? Ausnahmen prüfen.

8) Optional: npm aktualisieren

```powershell
# Lokal (global) aktualisieren
npm install -g npm@latest
```

9) Empfohlene Praxis für das ORBIS‑Repo

- Verwende die bereitgestellten Launcher‑Skripte (`scripts/run-omf3.ps1`) um konsistente Logs und konsistente Startbefehle zu haben.
- Nutze `npm ci` in CI und `npm install` lokal, wenn du Pakete hinzufügst.
- Committe keine node_modules in Git.

Wenn du willst, kann ich dieses Dokument als Wiki‑Seite oder Azure DevOps Wiki‑Markdown exportieren oder zusätzliche Checks in `run-omf3.ps1` aufnehmen (z. B. Auto‑Install von nvm/scoop). Sag mir einfach, welche Option du bevorzugst.

Falls du willst, führe ich die PATH‑Änderung hier in einem Patch automatisch für deine bisherige Node‑Installation (z. B. `C:\Users\beroli\tools\node-v18.20.0-win-x64`) aus — bestätige mit "PATH patch bitte" und ich schreibe ein kurzes PowerShell‑Skript oder eine README‑Ergänzung.

---
Letzte Aktualisierung: 2025-11-16
