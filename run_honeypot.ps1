<#
.SYNOPSIS
    Honeypot Launch Script for Windows (PowerShell)
.DESCRIPTION
    Starts the HoneyPot Flask HTTP service and verifies connectivity.
#>

$banner = @"
  _    _                          _____      _   
 | |  | |                        |  __ \    | |  
 | |__| | ___  _ __   ___ _   _  | |__) |__ | |_ 
 |  __  |/ _ \| '_ \ / _ \ | | | |  ___/ _ \| __|
 | |  | | (_) | | | |  __/ |_| | | |  | (_) | |_ 
 |_|  |_|\___/|_| |_|\___|\__, | |_|   \___/ \__|
                           __/ |                 
                          |___/   Auth: @tanishqzope
"@
Write-Host $banner -ForegroundColor Cyan

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "MMM dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR"   { "Red" }
        "WARN"    { "Yellow" }
        default   { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Determine Python executable
$pythonExe = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonExe = ".\.venv\Scripts\python.exe"
    Write-Log "Using virtual environment: $pythonExe"
} elseif (Test-Path ".\honeypot-env\Scripts\python.exe") {
    $pythonExe = ".\honeypot-env\Scripts\python.exe"
    Write-Log "Using virtual environment: $pythonExe"
}

# Allow configuring port via argument or environment variable
$port = if ($env:PORT) { $env:PORT } else { "80" }
$env:PORT = $port

Write-Log "Starting Honeypot Flask application on port $port..."
$process = Start-Process -FilePath $pythonExe -ArgumentList "app.py" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 2

if ($process.HasExited) {
    Write-Log "Flask app exited unexpectedly. Checking if port was restricted (e.g., port 80 without admin)..." "WARN"
    Write-Log "Retrying on fallback port 5000..." "WARN"
    $env:PORT = "5000"
    $port = "5000"
    $process = Start-Process -FilePath $pythonExe -ArgumentList "app.py" -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

if (-not $process.HasExited) {
    Write-Log "Flask app running with Process ID: $($process.Id)" "SUCCESS"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Log "HTTP service is online on http://localhost:$port (HTTP $($response.StatusCode))" "SUCCESS"
        }
    } catch {
        Write-Log "Server is running, but initial probe returned: $_" "WARN"
    }

    Write-Host ""
    Write-Host "To monitor honeypot logs in real-time, run:" -ForegroundColor Yellow
    Write-Host "  $pythonExe monitor_honeypot.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop the honeypot, run:" -ForegroundColor Yellow
    Write-Host "  Stop-Process -Id $($process.Id)" -ForegroundColor Cyan
} else {
    Write-Log "Failed to start Honeypot service." "ERROR"
    exit 1
}

