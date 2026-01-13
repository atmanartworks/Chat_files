# Script to fix venv permission issues

Write-Host "=== Fixing venv Permission Issues ===" -ForegroundColor Cyan

# Step 1: Check for running Python processes
Write-Host "`n1. Checking for running Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Found Python processes. Please close them first:" -ForegroundColor Red
    $pythonProcesses | Format-Table ProcessName, Id, Path
    Write-Host "`nClose these processes and run this script again." -ForegroundColor Yellow
    exit
} else {
    Write-Host "No Python processes found. Good!" -ForegroundColor Green
}

# Step 2: Try to remove venv
Write-Host "`n2. Attempting to remove existing venv..." -ForegroundColor Yellow
if (Test-Path "venv") {
    try {
        # Deactivate if active
        if ($env:VIRTUAL_ENV) {
            Write-Host "Deactivating virtual environment..." -ForegroundColor Yellow
            deactivate
        }
        
        # Remove with retry
        $maxRetries = 3
        $retryCount = 0
        $removed = $false
        
        while ($retryCount -lt $maxRetries -and -not $removed) {
            try {
                Remove-Item -Path "venv" -Recurse -Force -ErrorAction Stop
                $removed = $true
                Write-Host "venv removed successfully!" -ForegroundColor Green
            } catch {
                $retryCount++
                if ($retryCount -lt $maxRetries) {
                    Write-Host "Retry $retryCount/$maxRetries..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 2
                } else {
                    Write-Host "Could not remove venv. Try these steps:" -ForegroundColor Red
                    Write-Host "  1. Close all terminals/IDEs using this venv" -ForegroundColor Yellow
                    Write-Host "  2. Close VS Code or other editors" -ForegroundColor Yellow
                    Write-Host "  3. Restart your computer if needed" -ForegroundColor Yellow
                    Write-Host "  4. Or use a different venv name: python -m venv venv_new" -ForegroundColor Yellow
                    exit
                }
            }
        }
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "venv folder does not exist. Good!" -ForegroundColor Green
}

# Step 3: Create new venv
Write-Host "`n3. Creating new virtual environment..." -ForegroundColor Yellow
try {
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host "`nTo activate:" -ForegroundColor Cyan
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
} catch {
    Write-Host "Error creating venv: $_" -ForegroundColor Red
    Write-Host "`nTry running as Administrator or use:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv_new" -ForegroundColor White
}
