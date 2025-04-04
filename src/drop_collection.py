import os

from pymilvus import MilvusClient


def drop_collection(
    collection_name: str | None = None,
    uri: str | None = None,
    token: str | None = None,
) -> None:
    """Drop a Milvus collection.

    Args:
        collection_name (str, optional): Name of the collection. Defaults to env var COLLECTION_NAME.
        uri (str, optional): Zilliz Cloud URI. Defaults to env var ZILLIZ_CLOUD_URI.
        token (str, optional): Zilliz token. Defaults to env var ZILLIZ_TOKEN.
    """
    # Use environment variables as fallback
    collection_name = collection_name or os.getenv("COLLECTION_NAME")
    uri = uri or os.getenv("ZILLIZ_CLOUD_URI")
    token = token or os.getenv("ZILLIZ_TOKEN")

    if not all([collection_name, uri, token]):
        raise ValueError("Missing required parameters: collection_name, uri, or token")

    # Connect to Zilliz Cloud (Milvus)
    client = MilvusClient(uri=uri, token=token)

    # Drop the collection
    client.drop_collection(collection_name=collection_name)


if __name__ == "__main__":
    # Drop collection
    print("Dropping collection...")
    drop_collection()
    print("Collection dropped successfully.")
