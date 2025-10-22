Write-Host '=== Blue-Green Deployment Status ===' -ForegroundColor Cyan
Write-Host 'Deployments:' -ForegroundColor Yellow
kubectl get deployments -n blue-green
Write-Host 'Pods:' -ForegroundColor Yellow
kubectl get pods -n blue-green -o wide
Write-Host 'Services:' -ForegroundColor Yellow
kubectl get services -n blue-green
Write-Host 'Current Service Selector:' -ForegroundColor Yellow
kubectl describe service flask-app-service -n blue-green | Select-String 'Selector'
