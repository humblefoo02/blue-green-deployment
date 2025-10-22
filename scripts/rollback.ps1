Write-Host 'Rolling back to BLUE environment...' -ForegroundColor Yellow
kubectl patch service flask-app-service -n blue-green -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'

Write-Host 'Rollback complete!' -ForegroundColor Green
kubectl get all -n blue-green
