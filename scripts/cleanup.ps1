Write-Host 'Cleaning up Blue-Green deployment...' -ForegroundColor Red
kubectl delete namespace blue-green
docker rmi flask-app:blue flask-app:green
Write-Host 'Cleanup complete!' -ForegroundColor Green
