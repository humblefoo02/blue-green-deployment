Write-Host 'Deploying BLUE Environment...' -ForegroundColor Blue
kubectl apply -f ..\k8s\namespace.yaml
kubectl apply -f ..\k8s\blue-deployment.yaml
kubectl apply -f ..\k8s\blue-service.yaml
kubectl apply -f ..\k8s\service.yaml

Write-Host 'Waiting for blue deployment...' -ForegroundColor Cyan
kubectl wait --for=condition=available --timeout=120s deployment/blue-deployment -n blue-green

Write-Host 'Blue deployment status:' -ForegroundColor Cyan
kubectl get deployments -n blue-green
kubectl get pods -n blue-green
kubectl get services -n blue-green

Write-Host 'BLUE environment deployed successfully!' -ForegroundColor Green
Write-Host 'Access at: http://localhost:30080' -ForegroundColor Yellow
