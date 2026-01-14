# Smart Factory CV - Setup Script
Write-Host "=== Smart Factory CV - Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Installing AI Inference dependencies..." -ForegroundColor Yellow
Set-Location services/ai-inference
pip install -r requirements.txt
Set-Location ../..

Write-Host ""
Write-Host "[2/2] Installing Dashboard dependencies..." -ForegroundColor Yellow
Set-Location services/dashboard
npm install
Set-Location ../..

Write-Host ""
Write-Host "Setup complete! Run .\start.ps1 to start all services." -ForegroundColor Green
