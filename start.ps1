# Smart Factory CV - Start Script
$jobs = @()

Write-Host "=== Smart Factory CV - Starting Services ===" -ForegroundColor Cyan
Write-Host ""

# Start AI Inference
Write-Host "Starting AI Inference server..." -ForegroundColor Yellow
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "services/ai-inference"
    python src/main.py
}
Start-Sleep -Seconds 3

# Start Dashboard
Write-Host "Starting Dashboard..." -ForegroundColor Yellow
$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "services/dashboard"
    npm run dev
}

Write-Host ""
Write-Host "=== Services Started ===" -ForegroundColor Green
Write-Host ""
Write-Host "  AI Inference:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Dashboard:     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor DarkGray
Write-Host ""

try {
    while ($true) {
        Start-Sleep -Seconds 1
        Receive-Job -Job $jobs
    }
}
finally {
    Stop-Job -Job $jobs
    Remove-Job -Job $jobs
}
