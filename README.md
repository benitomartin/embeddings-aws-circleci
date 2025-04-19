# Update Vector Database Pipeline with AWS Lambda

This project implements an automated pipeline that processes PDF documents uploaded to S3, extracts text, generates embeddings using OpenAI, and stores them in a Zilliz Cloud (Milvus) vector database using AWS Lambda.

The project has been developed as part of the following [blog](XXXX)

## Project Structure

```.
.
├── .circleci/
│   └── config.yml
├── data/
│   └── 1706.03762v7.pdf
├── src/
│   ├── create_collection.py
│   ├── drop_collection.py
│   ├── insert_documents.py
│   └── __init__.py
├── aws_lambda/
|   ├── __init__.py
│   └── lambda_function.py
├── scripts/
│   ├── build_deploy.sh
│   ├── create_roles.sh
│   ├── create_image.sh
│   └── create_lambda.sh
├── tests/
│   ├── test_collection_exists.py
│   ├── test_lambda_function.py
│   └── test_collection_mock.py
├── Dockerfile
└── pyproject.toml
```

## Prerequisites

- Python 3.12+
- AWS Account with appropriate permissions
- OpenAI API key
- Zilliz Cloud account and credentials
- Docker installed locally
- CircleCI account (for CI/CD)
- [UV package manager](https://github.com/astral/uv)

## Environment Variables

Create a `.env` file with the following variables:

```bash
ZILLIZ_CLOUD_URI=your-zilliz-uri
ZILLIZ_TOKEN=your-zilliz-token
COLLECTION_NAME=your-collection-name
PDF_BUCKET_NAME=your-bucket-name
OPENAI_API_KEY=your-openai-key
AWS_REGION=your-aws-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_ACCOUNT_ID=your-account-id
LAMBDA_ECR_REPOSITORY_NAME=your-ecr-repo-name
LAMBDA_IMAGE_NAME=your-image-name
LAMBDA_FUNCTION_NAME=your-lambda-name
ROLE_NAME=your-role-name
ROLE_POLICY_NAME=your-policy-name
```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd embeddings-aws-circleci
   ```

1. Install dependencies using UV and activate the virtual environment:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync --all-extras
   source .venv/bin/activate
   ```

## Deployment

### Manual Deployment

1. Create S3 bucket:

   ```bash
   aws s3api create-bucket \
       --bucket embeddings-$(uuidgen | tr -d - | tr '[:upper:]' '[:lower:]' ) \
       --region eu-central-1 \
       --create-bucket-configuration LocationConstraint=eu-central-1
   ```

   Don't forget to update the `.env` file with the bucket name.

1. Deploy using the build script:

   ```bash
   chmod +x ./scripts/build_deploy.sh
   ./scripts/build_deploy.sh
   ```

### CI/CD with CircleCI

The project includes a CircleCI configuration that:

- Installs dependencies
- Runs tests and linting
- Builds Docker image
- Deploys to AWS Lambda

Required CircleCI environment variables:

- All variables from the `.env` file must be added to CircleCI project settings

## Testing the Milvus Collection

```bash
# Run all tests
uv run pytest
```

## Testing the Pipeline

1. Upload a PDF to the S3 bucket:

   ```bash
   aws s3 cp data/your-file.pdf s3://your-bucket-name/
   ```

1. Monitor Lambda execution:

   ```bash
   aws logs tail /aws/lambda/your-lambda-function --follow
   ```

## Contributing

1. Fork the repository
1. Create a feature branch
1. Commit your changes
1. Push to the branch
1. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
