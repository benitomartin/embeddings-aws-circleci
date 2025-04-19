#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

echo "Environment variables loaded."


# Create a new IAM role with Lambda and S3 full access
echo "Checking IAM role..."

# Check if the role exists
if ! aws iam get-role --role-name ${ROLE_NAME} --region ${AWS_REGION} 2>/dev/null; then
    echo "Creating new IAM role for Lambda with S3 access..."

    # Fix: Remove space after = and use proper JSON formatting
    ASSUME_ROLE_POLICY='{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }'

    # Create the IAM role
    aws iam create-role \
        --role-name ${ROLE_NAME} \
        --assume-role-policy-document "${ASSUME_ROLE_POLICY}" \
        --region ${AWS_REGION}


    # Add Lambda execution policy. Provides Put, Get access to S3 and full access to CloudWatch Logs.
    aws iam attach-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/AWSLambdaExecute  \
        --region ${AWS_REGION}

    echo "IAM role created and policy attached."

    # Wait for role to propagate
    echo "Waiting for role to propagate..."
    sleep 20

else
    echo "IAM role ${ROLE_NAME} already exists. Skipping role creation."
fi
