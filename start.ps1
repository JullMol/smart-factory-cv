$jobs = @()

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "services/ai-inference/src"
    python main.py
}
Start-Sleep -Seconds 3

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "services/stream-gateway"
    go run cmd/server/main.go
}
Start-Sleep -Seconds 2

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "services/dashboard"
    npx vite --host
}

Write-Host ""
Write-Host "=== Smart Factory CV - Services Started ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "  AI Inference:    http://localhost:8000 (REST), :50051 (gRPC)" -ForegroundColor Green
Write-Host "  Stream Gateway:  http://localhost:8080 (HTTP/WS)" -ForegroundColor Green
Write-Host "  Dashboard:       http://localhost:3000" -ForegroundColor Green
Write-Host "  Metrics:         http://localhost:9090 (AI), :9091 (Gateway)" -ForegroundColor Yellow
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
