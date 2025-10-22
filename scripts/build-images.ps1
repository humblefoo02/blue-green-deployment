Write-Host 'Building Blue-Green Deployment Images...' -ForegroundColor Cyan
Set-Location -Path '..\app'

Write-Host 'Building BLUE image...' -ForegroundColor Blue
docker build -t flask-app:blue --build-arg APP_VERSION=1.0 --build-arg APP_COLOR=blue .
if ($LASTEXITCODE -eq 0) { Write-Host 'Blue image built successfully' -ForegroundColor Green } else { Write-Host 'Blue build failed' -ForegroundColor Red; exit 1 }

Write-Host 'Building GREEN image...' -ForegroundColor Green
docker build -t flask-app:green --build-arg APP_VERSION=2.0 --build-arg APP_COLOR=green .
if ($LASTEXITCODE -eq 0) { Write-Host 'Green image built successfully' -ForegroundColor Green } else { Write-Host 'Green build failed' -ForegroundColor Red; exit 1 }

Write-Host 'Docker Images:' -ForegroundColor Cyan
docker images | Select-String 'flask-app'
Set-Location -Path '..\scripts'
