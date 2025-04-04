import json
import os

import boto3
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pymilvus import MilvusClient

# Global variables for reuse across invocations
client = None
openai_embeddings = None
text_splitter = None


def init_clients():
    """Initialize global clients if not already initialized"""
    global client, openai_embeddings, text_splitter

    if client is None:
        print("Initializing Milvus client...")
        client = MilvusClient(uri=os.getenv("ZILLIZ_CLOUD_URI"), token=os.getenv("ZILLIZ_TOKEN"))

    if openai_embeddings is None:
        print("Initializing OpenAI embeddings...")
        openai_embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    if text_splitter is None:
        print("Initializing text splitter...")
        text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=100)


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        # Initialize clients
        init_clients()

        # Validate event structure
        if "Records" not in event or not event["Records"]:
            print("No records found in event")
            return {"statusCode": 400, "body": json.dumps("No records found in event")}

        # Get bucket and file info from S3 event
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"Processing file {key} from bucket {bucket}")

        # Verify bucket
        expected_bucket = os.getenv("PDF_BUCKET_NAME")
        if bucket != expected_bucket:
            print(f"Invalid bucket. Expected {expected_bucket}, got {bucket}")
            return {
                "statusCode": 400,
                "body": json.dumps(f"Invalid bucket. Expected {expected_bucket}, got {bucket}"),
            }

        # Download PDF
        local_path = f"/tmp/{os.path.basename(key)}"
        print(f"Downloading file to {local_path}")
        s3 = boto3.client("s3")
        s3.download_file(bucket, key, local_path)

        # Process PDF
        print("Loading and splitting PDF...")
        documents = PyPDFLoader(local_path).load()
        chunks = text_splitter.split_documents(documents)
        print(f"Split PDF into {len(chunks)} chunks")

        # Prepare and insert data
        print("Generating embeddings and preparing data...")
        data = [
            {
                "pdf_text": chunk.page_content,
                "my_vector": openai_embeddings.embed_documents([chunk.page_content])[0],
            }
            for chunk in chunks
        ]

        print(f"Inserting {len(data)} records into collection {os.getenv('COLLECTION_NAME')}")
        client.insert(os.getenv("COLLECTION_NAME"), data)

        # Cleanup
        os.remove(local_path)
        print("Processing completed successfully")

        return {"statusCode": 200, "body": json.dumps(f"Successfully processed {key}")}

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        return {"statusCode": 500, "body": json.dumps(str(e))}
