$trainChoice = Read-Host "Train model now? (y/n)"

if ($trainChoice -eq "y") {
    Set-Location "ai-engine/scripts"
    python train.py --model n --epochs 100 --batch 16 --device 0
    Set-Location "../.."
}

Set-Location "ai-engine"
pip install -r requirements.txt -q
Set-Location ".."

Set-Location "backend-streamer"
go mod download
Set-Location ".."

Set-Location "frontend-dashboard"
npm install --silent
Set-Location ".."

Write-Host "Setup complete. Run start.ps1 to launch services."
