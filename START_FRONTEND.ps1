# Start Frontend Server

Write-Host "=== Starting Frontend Server ===" -ForegroundColor Cyan

Set-Location "frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start server
Write-Host "`nStarting React development server on http://localhost:5173" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor White

npm run dev
