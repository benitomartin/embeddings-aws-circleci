#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

echo "Environment variables loaded."

# Check if the Lambda function exists
if ! aws lambda get-function --function-name ${LAMBDA_FUNCTION_NAME} --region ${AWS_REGION} 2>/dev/null; then
    echo "Lambda function ${LAMBDA_FUNCTION_NAME} does not exist. Creating..."
    aws lambda create-function \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --package-type Image \
        --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${LAMBDA_ECR_REPOSITORY_NAME}:latest \
        --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME} \
        --region ${AWS_REGION} \
        --timeout 900 \
        --memory-size 3072 \
        --environment "Variables={
            PDF_BUCKET_NAME=${PDF_BUCKET_NAME},
            OPENAI_API_KEY=${OPENAI_API_KEY},
            ZILLIZ_CLOUD_URI=${ZILLIZ_CLOUD_URI},
            ZILLIZ_TOKEN=${ZILLIZ_TOKEN},
            COLLECTION_NAME=${COLLECTION_NAME}
        }" \

else
    echo "Lambda function ${LAMBDA_FUNCTION_NAME} already exists. Updating..."
    aws lambda update-function-code \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${LAMBDA_ECR_REPOSITORY_NAME}:latest

    # Wait for role to propagate
    echo "Waiting lambda function to update code..."
    sleep 20

    aws lambda update-function-configuration \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --timeout 900 \
        --memory-size 3072 \
        --environment "Variables={
            PDF_BUCKET_NAME=${PDF_BUCKET_NAME},
            OPENAI_API_KEY=${OPENAI_API_KEY},
            ZILLIZ_CLOUD_URI=${ZILLIZ_CLOUD_URI},
            ZILLIZ_TOKEN=${ZILLIZ_TOKEN},
            COLLECTION_NAME=${COLLECTION_NAME}
        }"


fi

# Check and add S3 trigger to Lambda if it doesn't exist
if ! aws lambda get-policy --function-name ${LAMBDA_FUNCTION_NAME} 2>/dev/null | grep -q "S3InvokeFunction"; then
    echo "Adding S3 trigger permission to Lambda..."
    aws lambda add-permission \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --statement-id S3InvokeFunction \
        --action lambda:InvokeFunction \
        --principal s3.amazonaws.com \
        --source-arn arn:aws:s3:::${PDF_BUCKET_NAME} \
        --region ${AWS_REGION}
else
    echo "S3 trigger permission already exists for Lambda. Skipping..."
fi

# Check and configure S3 bucket notification if it doesn't exist
CURRENT_NOTIFICATIONS=$(aws s3api get-bucket-notification-configuration --bucket ${PDF_BUCKET_NAME} 2>/dev/null)
if ! echo "${CURRENT_NOTIFICATIONS}" | grep -q "${LAMBDA_FUNCTION_NAME}"; then
    echo "Configuring S3 bucket notification..."
    aws s3api put-bucket-notification-configuration \
        --bucket ${PDF_BUCKET_NAME} \
        --notification-configuration '{
            "LambdaFunctionConfigurations": [{
                "LambdaFunctionArn": "arn:aws:lambda:'${AWS_REGION}':'${AWS_ACCOUNT_ID}':function:'${LAMBDA_FUNCTION_NAME}'",
                "Events": ["s3:ObjectCreated:*"]
            }]
        }'
else
    echo "S3 bucket notification already configured. Skipping..."
fi
