# Testet MQTT End-to-End (Publish/Subscribe) mit festem Timeout
# Verwendung: .\test-mqtt-e2e.ps1 -TimeoutSeconds 10

param(
    [string]$BrokerHost = "localhost",
    [int]$BrokerPort = 1883,
    [string]$Topic = "orbis/test",
    [int]$TimeoutSeconds = 10,
    [string]$MosquittoBinDir = ""
)

$ErrorActionPreference = "Stop"

function Resolve-MosquittoBinDir {
    param([string]$Preferred)

    $candidates = @()

    if ($Preferred -and $Preferred.Trim().Length -gt 0) {
        $candidates += $Preferred
    }

    $candidates += @(
        "C:\Program Files\mosquitto",
        "C:\Program Files (x86)\mosquitto",
        "$env:USERPROFILE\mosquitto"
    )

    foreach ($dir in $candidates) {
        if ((Test-Path (Join-Path $dir "mosquitto_sub.exe")) -and (Test-Path (Join-Path $dir "mosquitto_pub.exe"))) {
            return $dir
        }
    }

    return $null
}

$binDir = Resolve-MosquittoBinDir -Preferred $MosquittoBinDir
if (-not $binDir) {
    Write-Host "❌ mosquitto_pub.exe / mosquitto_sub.exe nicht gefunden." -ForegroundColor Red
    exit 1
}

$subExe = Join-Path $binDir "mosquitto_sub.exe"
$pubExe = Join-Path $binDir "mosquitto_pub.exe"
$msg = "ping-" + [guid]::NewGuid().ToString()

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  MQTT E2E Test" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Broker:  $BrokerHost`:$BrokerPort" -ForegroundColor Gray
Write-Host "Topic:   $Topic" -ForegroundColor Gray
Write-Host "Timeout: $TimeoutSeconds s" -ForegroundColor Gray
Write-Host "BinDir:  $binDir" -ForegroundColor Gray

$job = Start-Job -ScriptBlock {
    param($exe, $brokerHost, $port, $topic)
    & $exe -h $brokerHost -p $port -t $topic -C 1
} -ArgumentList $subExe, $BrokerHost, $BrokerPort, $Topic

Start-Sleep -Milliseconds 700
& $pubExe -h $BrokerHost -p $BrokerPort -t $Topic -m $msg | Out-Null

$completed = Wait-Job -Job $job -Timeout $TimeoutSeconds
if (-not $completed) {
    Stop-Job $job -ErrorAction SilentlyContinue | Out-Null
    Remove-Job $job -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Host "❌ Timeout nach $TimeoutSeconds s (keine Nachricht empfangen)." -ForegroundColor Red
    exit 2
}

$received = Receive-Job -Job $job -ErrorAction SilentlyContinue
Remove-Job $job -Force -ErrorAction SilentlyContinue | Out-Null

Write-Host "SENT: $msg" -ForegroundColor Gray
Write-Host "RECV: $received" -ForegroundColor Gray

if ($received -eq $msg) {
    Write-Host "✅ MQTT_E2E_OK" -ForegroundColor Green
    exit 0
}

Write-Host "❌ MQTT_E2E_FAIL (Nachricht stimmt nicht überein)." -ForegroundColor Red
exit 3
