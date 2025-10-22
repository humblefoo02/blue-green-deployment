Write-Host 'Deploying GREEN Environment...' -ForegroundColor Green
kubectl apply -f ..\k8s\namespace.yaml
kubectl apply -f ..\k8s\green-deployment.yaml
kubectl apply -f ..\k8s\green-service.yaml

Write-Host 'Waiting for green deployment...' -ForegroundColor Cyan
kubectl wait --for=condition=available --timeout=120s deployment/green-deployment -n blue-green

Write-Host 'Green deployment status:' -ForegroundColor Cyan
kubectl get deployments -n blue-green
kubectl get pods -n blue-green

Write-Host 'GREEN environment deployed successfully!' -ForegroundColor Green
Write-Host 'Service still pointing to BLUE. Run switch-to-green.ps1 to switch' -ForegroundColor Yellow
