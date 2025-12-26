# Clothing Classification Service

A FastAPI-based microservice for clothing classification using ONNX Runtime and Xception model. Deployed on AWS EKS (Elastic Kubernetes Service).

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Docker Build](#docker-build)
- [AWS Setup](#aws-setup)
  - [ECR Setup](#ecr-setup)
  - [EKS Cluster Setup](#eks-cluster-setup)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

This service classifies clothing items from images into 10 categories:
- dress, hat, longsleeve, outwear, pants, shirt, shoes, shorts, skirt, t-shirt

**Tech Stack:**
- FastAPI (Python web framework)
- ONNX Runtime (model inference)
- Docker (containerization)
- Kubernetes (orchestration)
- AWS EKS (managed Kubernetes)
- AWS ECR (container registry)

## Prerequisites

### Required Software

1. **Python 3.13+**
   ```bash
   python --version  # Should be 3.13 or higher
   ```

2. **Pipenv** (for dependency management)
   ```bash
   pip install pipenv
   ```

3. **Docker**
   ```bash
   docker --version
   ```

4. **AWS CLI** (configured with credentials)
   ```bash
   aws --version
   aws configure  # Set up your AWS credentials
   ```

5. **kubectl** (Kubernetes CLI)
   ```bash
   kubectl version --client
   ```

6. **eksctl** (for EKS cluster management)
   ```bash
   eksctl version
   # Install: https://eksctl.io/introduction/installation/
   ```

### AWS Account Requirements

- AWS Account with appropriate permissions
- IAM permissions for:
  - ECR (Elastic Container Registry)
  - EKS (Elastic Kubernetes Service)
  - EC2 (for EKS worker nodes)
  - IAM (for service roles)

## Local Setup

### 1. Clone/Navigate to Project Directory

```bash
cd /path/to/tutorial/cloth_predictions
```

### 2. Install Dependencies

```bash
# Install Python dependencies using Pipenv
pipenv install

# Activate virtual environment
pipenv shell
```

### 3. Verify Local Setup

```bash
# Test the application locally
python app.py

# In another terminal, test the health endpoint
curl http://localhost:8080/health
```

## Docker Build

### 1. Build Docker Image

```bash
# Build the image
docker build -t clothing-classifier:v1 .

# Verify the image
docker images | grep clothing-classifier
```

### 2. Test Docker Image Locally

```bash
# Run the container
docker run -p 8080:8080 clothing-classifier:v1

# Test in another terminal
curl http://localhost:8080/health
```

## AWS Setup

### ECR Setup

#### Step 1: Configure AWS Region and Account

Update the variables in `deploy-to-ecr.sh` or set environment variables:

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="your-account-id"  # Or leave empty to auto-detect
```

#### Step 2: Build and Push to ECR

```bash
# Make script executable
chmod +x deploy-to-ecr.sh

# Run the deployment script
./deploy-to-ecr.sh
```

The script will:
1. Build the Docker image for amd64 architecture
2. Authenticate with ECR
3. Create ECR repository if it doesn't exist
4. Tag the image
5. Push to ECR
6. Verify the push

#### Step 3: Verify Image in ECR

```bash
# List images in ECR
aws ecr describe-images \
  --repository-name clothing-classifier \
  --region us-east-1
```

### EKS Cluster Setup

#### Step 1: Create EKS Cluster

```bash
# Create cluster using eksctl
eksctl create cluster -f k8s/eks-config.yaml

# This will take 15-20 minutes
# The cluster name is: test-k8s-cluster
# Region: us-east-1
```

#### Step 2: Verify Cluster Access

```bash
# Update kubeconfig
aws eks update-kubeconfig --name test-k8s-cluster --region us-east-1

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

#### Step 3: Configure EKS Nodes to Pull from ECR

EKS nodes need permission to pull images from ECR. This is usually handled automatically by eksctl, but verify:

```bash
# Check node IAM role
kubectl describe node | grep "ProviderID"

# Verify ECR access (should work automatically with eksctl)
```

## Deployment

### Step 1: Update Deployment Image

Update `k8s/deployment.yaml` with your ECR image URI:

```yaml
image: <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clothing-classifier:v1
```

Or use the image digest (more secure):
```yaml
image: <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clothing-classifier@sha256:<digest>
```

### Step 2: Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Apply service
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get deployments
kubectl get pods
kubectl get services
```

### Step 3: Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=clothing-classifier-deployment

# Check pod logs
kubectl logs -l app=clothing-classifier-deployment

# Check service endpoints
kubectl get endpoints clothing-classifier
```

### Step 4: Get Service Endpoint

#### Option A: LoadBalancer (Recommended)

The service is configured as LoadBalancer type. Get the endpoint:

```bash
# Get LoadBalancer endpoint
kubectl get svc clothing-classifier -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Wait 2-5 minutes for DNS propagation
```

#### Option B: Port Forward (For Local Testing)

```bash
# Port forward to local machine
kubectl port-forward service/clothing-classifier 8080:80

# Access at: http://localhost:8080
```

#### Option C: NodePort (If LoadBalancer not available)

```bash
# Get node IP
kubectl get nodes -o wide

# Access at: http://<NODE_IP>:30080
# Note: Requires security group to allow port 30080
```

## Testing

### 1. Test Health Endpoint

```bash
# Using LoadBalancer
curl http://<LOADBALANCER_ENDPOINT>/health

# Using port-forward
curl http://localhost:8080/health

# Using NodePort
curl http://<NODE_IP>:30080/health
```

### 2. Test Prediction Endpoint

#### Using Python Script

```bash
# Update test.py with your endpoint
python test.py
```

The `test.py` script automatically detects the LoadBalancer endpoint.

#### Using curl

```bash
curl -X POST http://<ENDPOINT>/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://bit.ly/mlbookcamp-pants"}'
```

### 3. Load Testing

```bash
# Run load test
python load_test.py
```

## Troubleshooting

### Issue: Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Check ECR permissions
# - Resource limits: Check deployment resources
# - Health check failures: Check app logs
```

### Issue: Cannot Pull Image from ECR

```bash
# Verify ECR repository exists
aws ecr describe-repositories --repository-name clothing-classifier

# Check image exists
aws ecr describe-images --repository-name clothing-classifier

# Verify node IAM role has ECR permissions
# eksctl should handle this automatically
```

### Issue: Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints clothing-classifier

# Verify pods are running
kubectl get pods -l app=clothing-classifier-deployment

# Check service configuration
kubectl describe svc clothing-classifier

# For LoadBalancer: Wait 2-5 minutes for DNS
# For NodePort: Check security group allows port 30080
```

### Issue: LoadBalancer DNS Not Resolving

```bash
# Wait a few minutes for DNS propagation
# Verify LoadBalancer is created
kubectl get svc clothing-classifier

# Check AWS Console → EC2 → Load Balancers
# Use port-forward as temporary solution
kubectl port-forward service/clothing-classifier 8080:80
```

### Common Commands

```bash
# View all resources
kubectl get all

# Describe deployment
kubectl describe deployment clothing-classifier-deployment

# View events
kubectl get events --sort-by='.lastTimestamp'

# Restart deployment
kubectl rollout restart deployment/clothing-classifier-deployment

# Scale deployment
kubectl scale deployment/clothing-classifier-deployment --replicas=2

# Delete and recreate
kubectl delete -f k8s/deployment.yaml
kubectl apply -f k8s/deployment.yaml
```

## Project Structure

```
cloth_predictions/
├── app.py                 # FastAPI application
├── clothing-model.onnx    # ONNX model file
├── Dockerfile            # Docker image definition
├── Pipfile              # Python dependencies
├── Pipfile.lock         # Locked dependencies
├── deploy-to-ecr.sh     # ECR deployment script
├── test.py              # Test script
├── load_test.py         # Load testing script
└── k8s/                 # Kubernetes manifests
    ├── deployment.yaml  # Deployment configuration
    ├── service.yaml     # Service configuration
    ├── hpa.yaml         # Horizontal Pod Autoscaler
    ├── eks-config.yaml  # EKS cluster configuration
    └── components.yaml  # Additional components
```

## Environment Variables

You can set these environment variables:

```bash
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="your-account-id"
export SERVICE_URL="http://your-endpoint/predict"
```

## Cleanup

### Delete EKS Cluster

```bash
eksctl delete cluster --name test-k8s-cluster --region us-east-1
```

### Delete ECR Repository

```bash
aws ecr delete-repository \
  --repository-name clothing-classifier \
  --force \
  --region us-east-1
```

### Delete Kubernetes Resources

```bash
kubectl delete -f k8s/
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Kubernetes events: `kubectl get events`
3. Check application logs: `kubectl logs -l app=clothing-classifier-deployment`
