# Startet einen lokalen Mosquitto WebSocket-Bridge-Broker auf Port 9001
# Nutzung: .\start-mosquitto-ws-bridge.ps1

param(
    [string]$MosquittoExe = "C:\Program Files\mosquitto\mosquitto.exe",
    [string]$ConfigFile = "C:\Users\beroli\Projects\ORBIS-Modellfabrik\scripts\mosquitto-ws-bridge.conf"
)

function Wait-ForListenPort {
    param(
        [int]$Port,
        [int]$TimeoutSeconds = 10
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            return $true
        }
        Start-Sleep -Milliseconds 250
    }

    return $false
}

if (-not (Test-Path $MosquittoExe)) {
    Write-Host "❌ Mosquitto executable nicht gefunden: $MosquittoExe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "❌ Config nicht gefunden: $ConfigFile" -ForegroundColor Red
    exit 1
}

 $service = Get-Service mosquitto -ErrorAction SilentlyContinue
 if ($service) {
    if ($service.Status -ne 'Running') {
        try {
            Start-Service mosquitto -ErrorAction Stop
        } catch {
            Write-Host "⚠️ Mosquitto-Dienst konnte nicht gestartet werden: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "❌ Der lokale Mosquitto-TCP-Broker auf 1883 ist nicht verfuegbar." -ForegroundColor Red
            exit 1
        }
    }

    if (-not (Wait-ForListenPort -Port 1883 -TimeoutSeconds 10)) {
        Write-Host "⚠️ Mosquitto-Dienst startet nicht auf Port 1883." -ForegroundColor Yellow
        Write-Host "❌ Der lokale Mosquitto-TCP-Broker auf 1883 ist nicht verfuegbar." -ForegroundColor Red
        exit 1
    }
}

# Vorabcheck: 9001 frei?
$portInUse = Get-NetTCPConnection -LocalPort 9001 -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️ Port 9001 ist bereits belegt (PID(s): $($portInUse.OwningProcess -join ', '))." -ForegroundColor Yellow
    Write-Host "   Es läuft vermutlich bereits ein WebSocket-Broker." -ForegroundColor Yellow
    exit 0
}

Write-Host "▶ Starte WebSocket-Bridge auf ws://localhost:9001 ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $MosquittoExe -ArgumentList @('-c', $ConfigFile, '-v') -PassThru

if (Wait-ForListenPort -Port 9001 -TimeoutSeconds 10) {
    Write-Host "✅ WebSocket-Bridge läuft (PID $($proc.Id)) auf Port 9001" -ForegroundColor Green
    exit 0
}

Write-Host "❌ Bridge konnte nicht gestartet werden. Prüfe Logs/Terminalausgabe." -ForegroundColor Red
exit 1
