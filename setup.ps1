Write-Host "=== Smart Factory CV - Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Installing AI Inference dependencies..." -ForegroundColor Yellow
Set-Location services/ai-inference
pip install -r requirements.txt
Set-Location ../..

Write-Host ""
Write-Host "[2/3] Installing Stream Gateway dependencies..." -ForegroundColor Yellow
Set-Location services/stream-gateway
go mod download
Set-Location ../..

Write-Host ""
Write-Host "[3/3] Installing Dashboard dependencies..." -ForegroundColor Yellow
Set-Location services/dashboard
npm install
Set-Location ../..

Write-Host ""
Write-Host "Setup complete! Run .\start.ps1 to start all services." -ForegroundColor Green
