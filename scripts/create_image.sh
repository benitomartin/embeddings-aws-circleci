#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

echo "Environment variables loaded."

# Check if the ECR repository exists, create it if it does not
if ! aws ecr describe-repositories --repository-names ${LAMBDA_ECR_REPOSITORY_NAME} --region ${AWS_REGION} 2>/dev/null; then
    echo "Repository ${LAMBDA_ECR_REPOSITORY_NAME} does not exist. Creating..."
    aws ecr create-repository --repository-name ${LAMBDA_ECR_REPOSITORY_NAME} --region ${AWS_REGION}
    echo "Repository ${LAMBDA_ECR_REPOSITORY_NAME} created."
else
    echo "Repository ${LAMBDA_ECR_REPOSITORY_NAME} already exists."
fi

# Build Docker image
# To make your image compatible with Lambda, you must use the --provenance=false option.
echo "Building Docker image ${LAMBDA_IMAGE_NAME}..."
docker buildx build --platform linux/amd64 --provenance=false -t ${LAMBDA_IMAGE_NAME}:latest .

# Authenticate Docker to your Amazon ECR registry
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag the Docker image
echo "Tagging Docker image..."
docker tag ${LAMBDA_IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${LAMBDA_ECR_REPOSITORY_NAME}:latest

# Push the Docker image to Amazon ECR
echo "Pushing Docker image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${LAMBDA_ECR_REPOSITORY_NAME}:latest

echo "Docker image pushed to ECR."
echo "Image created successfully."
