import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_milvus_client():
    with patch("pymilvus.MilvusClient") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_env_vars():
    env_vars = {
        "ZILLIZ_CLOUD_URI": "fake-uri",
        "COLLECTION_NAME": "test_collection",
        "ZILLIZ_TOKEN": "fake-token",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


def test_drop_collection(mock_milvus_client, mock_env_vars):
    from src.drop_collection import drop_collection

    # Call drop collection
    drop_collection()

    # Verify the drop_collection method was called with correct parameters
    mock_milvus_client.drop_collection.assert_called_once_with(
        collection_name=mock_env_vars["COLLECTION_NAME"]
    )


@pytest.mark.parametrize("collection_exists", [True, False])
def test_collection_existence(mock_milvus_client, mock_env_vars, collection_exists):
    mock_milvus_client.list_collections.return_value = (
        [mock_env_vars["COLLECTION_NAME"]] if collection_exists else []
    )

    # Check if collection exists
    result = mock_milvus_client.list_collections()
    print(f" result: {result}")

    if collection_exists:
        assert mock_env_vars["COLLECTION_NAME"] in result
    else:
        assert mock_env_vars["COLLECTION_NAME"] not in result
