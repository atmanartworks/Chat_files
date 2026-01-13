# Start Backend Server

Write-Host "=== Starting Backend Server ===" -ForegroundColor Cyan

Set-Location "backend"

# Activate virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Check if dependencies are installed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
python -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Start server
Write-Host "`nStarting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor White

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
