import os

from aws_lambda.lambda_function import lambda_handler

# Set up test event
TEST_BUCKET = os.getenv("PDF_BUCKET_NAME")
TEST_FILE = "1706.03762v7.pdf"

test_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": TEST_BUCKET},
                "object": {"key": TEST_FILE},
            }
        }
    ]
}

def test_lambda_handler():
    """Test the lambda_handler function with an actual S3 file."""
    response = lambda_handler(test_event, None)

    assert response["statusCode"] == 200, f"Unexpected response: {response}"
    assert "Successfully processed" in response["body"]