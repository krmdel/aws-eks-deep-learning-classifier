#!/bin/bash

# Configuration - Update these variables
AWS_REGION="us-east-1"  # Change to your preferred region
ECR_REPOSITORY="clothing-classifier"  # Your ECR repository name
IMAGE_TAG="v1"  # Docker image tag (matches deployment.yaml)
AWS_ACCOUNT_ID=""  # AWS Account ID (or leave empty to auto-detect)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Get AWS Account ID if not set
if [ -z "$AWS_ACCOUNT_ID" ]; then
    print_info "Detecting AWS Account ID..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        print_error "Failed to get AWS Account ID. Make sure AWS CLI is configured."
        exit 1
    fi
    print_info "AWS Account ID: $AWS_ACCOUNT_ID"
fi

# Set ECR repository URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

print_info "ECR Repository URI: ${ECR_URI}"

# Step 1: Build Docker image
print_info "Step 1: Building Docker image for Kubernetes/EKS (amd64 architecture)..."
print_info "Using --platform linux/amd64 for EKS compatibility"
docker build --platform linux/amd64 -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    print_error "Docker build failed!"
    exit 1
fi
print_info "Docker image built successfully!"

# Verify image architecture (EKS compatibility check)
print_info "Verifying image architecture for EKS compatibility..."
IMAGE_ARCH=$(docker inspect ${ECR_REPOSITORY}:${IMAGE_TAG} --format='{{.Architecture}}' 2>/dev/null)
IMAGE_OS=$(docker inspect ${ECR_REPOSITORY}:${IMAGE_TAG} --format='{{.Os}}' 2>/dev/null)

# Check if architecture is amd64 compatible (most common for EKS)
if [ "$IMAGE_ARCH" = "amd64" ] || [ "$IMAGE_ARCH" = "x86_64" ]; then
    print_info "✓ Architecture verified: $IMAGE_ARCH (amd64 compatible)"
    if [ "$IMAGE_OS" = "linux" ]; then
        print_info "✓ OS verified: $IMAGE_OS"
        print_info "Image is compatible with EKS amd64 nodes ✓"
    else
        print_warning "OS is: $IMAGE_OS (expected: linux)"
    fi
else
    print_warning "⚠ Architecture is: $IMAGE_ARCH"
    print_warning "Most EKS nodes use amd64. If your nodes are arm64, this is fine."
    print_info "Image OS: $IMAGE_OS"
fi

# Step 2: Authenticate Docker to ECR
print_info "Step 2: Authenticating Docker with ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

if [ $? -ne 0 ]; then
    print_error "ECR authentication failed!"
    exit 1
fi
print_info "ECR authentication successful!"

# Step 3: Create ECR repository if it doesn't exist
print_info "Step 3: Checking if ECR repository exists..."
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} &> /dev/null

if [ $? -ne 0 ]; then
    print_warning "Repository does not exist. Creating it..."
    aws ecr create-repository \
        --repository-name ${ECR_REPOSITORY} \
        --region ${AWS_REGION} \

    if [ $? -ne 0 ]; then
        print_error "Failed to create ECR repository!"
        exit 1
    fi
    print_info "ECR repository created successfully!"
else
    print_info "ECR repository already exists."
fi

# Step 4: Tag the image
print_info "Step 4: Tagging Docker image..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    print_error "Docker tagging failed!"
    exit 1
fi
print_info "Docker image tagged successfully!"

# Step 5: Push image to ECR
print_info "Step 5: Pushing Docker image to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    print_error "Docker push failed!"
    exit 1
fi
print_info "Docker image pushed successfully!"

# Step 6: Verify image in ECR
print_info "Step 6: Verifying image in ECR..."
IMAGE_DIGEST=$(aws ecr describe-images \
    --repository-name ${ECR_REPOSITORY} \
    --image-ids imageTag=${IMAGE_TAG} \
    --region ${AWS_REGION} \
    --query 'imageDetails[0].imageDigest' \
    --output text 2>/dev/null)

if [ -n "$IMAGE_DIGEST" ] && [ "$IMAGE_DIGEST" != "None" ]; then
    print_info "Image verified in ECR ✓"
    print_info "Image Digest: ${IMAGE_DIGEST}"
else
    print_warning "Could not verify image digest (this is usually fine)"
fi

# Check image size
print_info "Checking image size..."
IMAGE_SIZE=$(docker images ${ECR_REPOSITORY}:${IMAGE_TAG} --format "{{.Size}}" 2>/dev/null)
if [ -n "$IMAGE_SIZE" ]; then
    print_info "Image size: ${IMAGE_SIZE}"
fi

print_info "=========================================="
print_info "SUCCESS! Docker image pushed to ECR!"
print_info "=========================================="
print_info "Image URI: ${ECR_URI}:${IMAGE_TAG}"
if [ -n "$IMAGE_DIGEST" ] && [ "$IMAGE_DIGEST" != "None" ]; then
    print_info "Image Digest: ${ECR_URI}@${IMAGE_DIGEST}"
fi
print_info ""
print_info "Next steps for Kubernetes/EKS deployment:"
print_info "  1. Update your deployment.yaml to use the ECR image:"
print_info "     image: ${ECR_URI}:${IMAGE_TAG}"
print_info "     imagePullPolicy: Always"
print_info ""
print_info "  2. Apply the updated deployment:"
print_info "     kubectl apply -f k8s/deployment.yaml"
print_info ""
print_info "  3. Verify the deployment:"
print_info "     kubectl get pods -l app=clothing-classifier-deployment"
print_info "     kubectl logs -l app=clothing-classifier-deployment"
print_info ""
print_info "This image can be used in:"
print_info "  - EKS clusters (Kubernetes)"
print_info "  - ECS tasks"
print_info "  - EC2 instances"
print_info ""
print_info "To update the deployment image, run:"
print_info "  kubectl set image deployment/clothing-classifier-deployment \\"
print_info "    clothing-classifier-deployment=${ECR_URI}:${IMAGE_TAG}"
