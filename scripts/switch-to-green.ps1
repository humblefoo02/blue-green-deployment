Write-Host 'Switching traffic to GREEN environment...' -ForegroundColor Green
kubectl patch service flask-app-service -n blue-green -p '{\"spec\":{\"selector\":{\"version\":\"green\"}}}'

Start-Sleep -Seconds 3

Write-Host 'Current service configuration:' -ForegroundColor Cyan
kubectl describe service flask-app-service -n blue-green | Select-String 'Selector'

Write-Host 'Traffic switched to GREEN!' -ForegroundColor Green
Write-Host 'Access at: http://localhost:30080' -ForegroundColor Yellow
