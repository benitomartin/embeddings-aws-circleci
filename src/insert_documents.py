import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pymilvus import MilvusClient


def process_pdf(pdf_path: str, chunk_size: int = 512, chunk_overlap: int = 100) -> list[dict]:
    """Process a PDF file and generate embeddings for its content.

    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int, optional): Size of text chunks. Defaults to 512.
        chunk_overlap (int, optional): Overlap between chunks. Defaults to 100.

    Returns:
        List[dict]: List of dictionaries containing text and embeddings.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    # Load and process PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split text
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)

    # Generate embeddings
    openai_embeddings = OpenAIEmbeddings()

    # Prepare data for insertion
    data = []
    for chunk in chunks:
        text = chunk.page_content
        embedding = openai_embeddings.embed_documents([text])[0]
        data.append({"pdf_text": text, "my_vector": embedding})

    return data


def insert_documents(
    pdf_path: str,
    collection_name: str | None = None,
    uri: str | None = None,
    token: str | None = None,
    chunk_size: int = 512,
    chunk_overlap: int = 100,
) -> None:
    """Insert documents from a PDF file into a Milvus collection.

    Args:
        pdf_path (str): Path to the PDF file.
        collection_name (str, optional): Name of the collection. Defaults to env var COLLECTION_NAME.
        uri (str, optional): Zilliz Cloud URI. Defaults to env var ZILLIZ_CLOUD_URI.
        token (str, optional): Zilliz token. Defaults to env var ZILLIZ_TOKEN.
        chunk_size (int, optional): Size of text chunks. Defaults to 512.
        chunk_overlap (int, optional): Overlap between chunks. Defaults to 100.
    """
    # Use environment variables as fallback
    collection_name = collection_name or os.getenv("COLLECTION_NAME")
    uri = uri or os.getenv("ZILLIZ_CLOUD_URI")
    token = token or os.getenv("ZILLIZ_TOKEN")

    if not all([collection_name, uri, token]):
        raise ValueError("Missing required parameters: collection_name, uri, or token")

    # Connect to Zilliz Cloud (Milvus)
    client = MilvusClient(uri=uri, token=token)

    # Process PDF and get data
    data = process_pdf(pdf_path, chunk_size, chunk_overlap)

    # Insert data
    client.insert(collection_name, data)

    # Verify collection load state
    load_state = client.get_load_state(collection_name=collection_name)
    print(f"Collection load state: {load_state}")


if __name__ == "__main__":
    # Insert documents
    print("Inserting documents...")
    insert_documents("data/1706.03762v7.pdf")
    print("Documents inserted successfully.")
