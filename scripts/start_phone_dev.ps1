# Start backend + public tunnel (no ngrok required)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/start_phone_dev.ps1

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Starting FastAPI on port 8000..."
Start-Process -FilePath "$Root\.venv\Scripts\uvicorn.exe" `
  -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000" `
  -WorkingDirectory $Root `
  -WindowStyle Minimized

Start-Sleep -Seconds 3

Write-Host "Starting LocalTunnel (public HTTPS)..."
Write-Host "Copy the https://....loca.lt URL into .env as API_PUBLIC_URL"
Write-Host "Then run: python scripts/export_elevenlabs_setup.py"
Write-Host ""

npx --yes localtunnel --port 8000
