import os

from pymilvus import DataType, MilvusClient


def create_schema(dimension: int = 1536) -> MilvusClient.create_schema:
    """Create a schema for the Milvus collection.

    Args:
        dimension (int): Dimension of the vector field. Defaults to 1536 (OpenAI embeddings).

    Returns:
        MilvusClient.Schema: Schema object for collection creation.
    """
    schema = MilvusClient.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )

    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="pdf_text", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="my_vector", datatype=DataType.FLOAT_VECTOR, dim=dimension)

    return schema


def create_collection(
    collection_name: str | None = None,
    uri: str | None = None,
    token: str | None = None,
    dimension: int = 1536,
) -> None:
    """Create a new Milvus collection with the specified parameters.

    Args:
        collection_name (str, optional): Name of the collection. Defaults to env var COLLECTION_NAME.
        uri (str, optional): Zilliz Cloud URI. Defaults to env var ZILLIZ_CLOUD_URI.
        token (str, optional): Zilliz token. Defaults to env var ZILLIZ_TOKEN.
        dimension (int, optional): Vector dimension. Defaults to 1536.
    """
    # Use environment variables as fallback
    collection_name = collection_name or os.getenv("COLLECTION_NAME")
    uri = uri or os.getenv("ZILLIZ_CLOUD_URI")
    token = token or os.getenv("ZILLIZ_TOKEN")

    if not all([collection_name, uri, token]):
        raise ValueError("Missing required parameters: collection_name, uri, or token")

    # Connect to Zilliz Cloud (Milvus)
    client = MilvusClient(uri=uri, token=token)

    # Create schema
    schema = create_schema(dimension)

    # Prepare index parameters
    index_params = client.prepare_index_params()
    index_params.add_index(field_name="my_vector", index_type="AUTOINDEX", metric_type="COSINE")

    # Create collection
    client.create_collection(collection_name=collection_name, schema=schema, index_params=index_params)


if __name__ == "__main__":
    # Create collection
    print("Creating collection...")
    create_collection()
    print("Collection created successfully.")
