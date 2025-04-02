import os

import pytest
from pymilvus import MilvusClient


@pytest.fixture
def milvus_client():
    # Initialize Milvus client with environment variables for URI and token
    client = MilvusClient(uri=os.getenv("ZILLIZ_CLOUD_URI"), token=os.getenv("ZILLIZ_TOKEN"))
    yield client
    client.close()  # Close the connection after the test


def test_check_collection_existence(milvus_client):
    collection_name = os.getenv("COLLECTION_NAME")

    # Step 1: Get list of all collections in the Milvus instance
    collections = milvus_client.list_collections()

    # Step 2: Assert that the collection name exists in the list of collections
    assert collection_name in collections, f"Collection '{collection_name}' does not exist in Milvus."
