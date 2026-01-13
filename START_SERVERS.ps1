# Script to start both Frontend and Backend servers

Write-Host "=== Starting Chat with Files Application ===" -ForegroundColor Cyan

# Check if backend venv is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "`n[Backend] Activating virtual environment..." -ForegroundColor Yellow
    Set-Location "backend"
    & ".\venv\Scripts\Activate.ps1"
    Set-Location ".."
}

# Start Backend
Write-Host "`n[Backend] Starting FastAPI server..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "backend"
    & ".\venv\Scripts\Activate.ps1"
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "`n[Frontend] Starting React development server..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "frontend"
    npm run dev
}

Write-Host "`n=== Servers Starting ===" -ForegroundColor Cyan
Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop both servers" -ForegroundColor White

# Wait for jobs
try {
    Wait-Job -Job $backendJob, $frontendJob
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
}
