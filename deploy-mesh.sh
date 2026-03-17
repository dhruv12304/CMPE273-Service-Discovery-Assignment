#!/bin/bash
set -e

echo "==> Starting Minikube..."
minikube start --memory=4096 --cpus=2

echo "==> Installing Istio (demo profile)..."
istioctl install --set profile=demo -y

echo "==> Enabling Istio sidecar injection on default namespace..."
kubectl label namespace default istio-injection=enabled --overwrite

echo "==> Building Docker image inside Minikube..."
eval $(minikube docker-env)
docker build -t service-discovery:latest .

echo "==> Deploying service registry..."
kubectl apply -f k8s/registry.yaml
kubectl rollout status deployment/service-registry

echo "==> Deploying hello-service (2 replicas)..."
kubectl apply -f k8s/hello-service.yaml
kubectl rollout status deployment/hello-service

echo "==> Applying Istio traffic rules..."
kubectl apply -f k8s/istio-traffic.yaml

echo "==> Running discovery client job..."
kubectl apply -f k8s/client-job.yaml

echo ""
echo "Deployment complete. Check client output with:"
echo "  kubectl logs -l job-name=discovery-client --tail=50"
echo ""
echo "Verify Istio sidecar injection:"
echo "  kubectl get pods -o wide"
echo "  kubectl describe pod -l app=hello-service | grep istio-proxy"
echo ""
echo "View Istio mesh dashboard:"
echo "  istioctl dashboard kiali"
