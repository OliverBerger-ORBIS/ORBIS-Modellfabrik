<#
.SYNOPSIS
  Fügt den Ordner von node.exe zur USER PATH Variable hinzu, falls noch nicht vorhanden.

.DESCRIPTION
  - Ermittelt den ersten in PATH sichtbaren node.exe Pfad (via where.exe)
  - Fügt dessen Ordner zur User PATH Umgebungsvariable hinzu (keine Duplikate)
  - Schreibt eine kurze Anleitung zum Neustart der Shell

.NOTES
  Ausführen in einer normalen PowerShell-Sitzung (keine Admin-Rechte nötig für USER PATH).
#>

# Versuche node.exe zu finden
$nodeExe = (where.exe node 2>$null | Select-Object -First 1)

if (-not $nodeExe) {
  Write-Error 'node.exe wurde nicht gefunden. Bitte installiere Node.js oder starte eine Shell, in der "node --version" funktioniert, und versuche es erneut.'
  exit 1
}

$nodeDir = Split-Path -Path $nodeExe -Parent
Write-Host "Gefundene node.exe: $nodeExe"
Write-Host "Node-Verzeichnis: $nodeDir"

# Hole aktuelle User PATH (oder leeren String)
$current = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not $current) { $current = '' }

# Normiere und prüfe auf Duplikate (case-insensitive)
$entries = $current -split ';' | Where-Object { $_ -ne '' } | ForEach-Object { $_.Trim() }
if ($entries -contains $nodeDir) {
  Write-Host 'Node-Verzeichnis ist bereits in der User PATH vorhanden. Keine Änderung nötig.'
  exit 0
}

# Füge am Ende hinzu
$newPath = if ($current -eq '') { $nodeDir } else { $current + ';' + $nodeDir }
[Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

Write-Host 'Erfolgreich: Node-Pfad zur USER PATH hinzugefügt.'
Write-Host 'Bitte alle PowerShell-/VSCode-Fenster neu starten, damit die Änderung wirksam wird.'
Write-Host 'Prüfe anschließend mit: where.exe node und node --version'

exit 0
