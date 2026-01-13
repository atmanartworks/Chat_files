# PowerShell script to test PDF generation

Write-Host "Testing PDF generation with chat endpoint..." -ForegroundColor Green

# Test 1: Chat with PDF generation
$chatResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
    -Method POST `
    -Headers @{
        "accept" = "application/json"
        "Content-Type" = "application/json"
    } `
    -Body (@{
        query = "tell me about python programming language"
        generate_pdf = $true
    } | ConvertTo-Json)

Write-Host "`nChat Response:" -ForegroundColor Yellow
$chatResponse | ConvertTo-Json -Depth 10

if ($chatResponse.pdf_url) {
    Write-Host "`nPDF URL: $($chatResponse.pdf_url)" -ForegroundColor Cyan
    Write-Host "You can download the PDF at: http://127.0.0.1:8000$($chatResponse.pdf_url)" -ForegroundColor Cyan
}

Write-Host "`n---`n" -ForegroundColor Gray

# Test 2: Direct PDF generation
Write-Host "Testing direct PDF generation endpoint..." -ForegroundColor Green

$pdfResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/generate-pdf" `
    -Method POST `
    -Headers @{
        "accept" = "application/json"
        "Content-Type" = "application/json"
    } `
    -Body (@{
        content = "This is a test document. Python is a high-level programming language known for its simplicity and readability."
        filename = "test_document.pdf"
    } | ConvertTo-Json)

Write-Host "`nPDF Generation Response:" -ForegroundColor Yellow
$pdfResponse | ConvertTo-Json

if ($pdfResponse.download_url) {
    Write-Host "`nDownload URL: http://127.0.0.1:8000$($pdfResponse.download_url)" -ForegroundColor Cyan
}
