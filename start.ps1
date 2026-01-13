$jobs = @()

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "ai-engine/src"
    python server.py
}
Start-Sleep -Seconds 2

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "backend-streamer"
    go run cmd/main.go
}
Start-Sleep -Seconds 2

$jobs += Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "frontend-dashboard"
    npm run dev
}

Write-Host "Services started:"
Write-Host "AI Engine:  http://localhost:8000"
Write-Host "Backend:    ws://localhost:8080"
Write-Host "Frontend:   http://localhost:3000"
Write-Host "`nPress Ctrl+C to stop"

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
