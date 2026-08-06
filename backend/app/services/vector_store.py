from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import (
    DefaultEmbeddingFunction,
)


VECTOR_DATABASE_PATH = Path("vector_database")
VECTOR_DATABASE_PATH.mkdir(exist_ok=True)

client = chromadb.PersistentClient(
    path=str(VECTOR_DATABASE_PATH)
)

embedding_function = DefaultEmbeddingFunction()

document_collection = client.get_or_create_collection(
    name="company_documents",
    embedding_function=embedding_function,
    metadata={
        "description": "Company knowledge-base document chunks"
    },
)


def store_document_chunks(
    document_id: int,
    document_name: str,
    chunks: list[str],
) -> int:
    if not chunks:
        raise ValueError("No document chunks are available")

    # Remove old chunks if this document was indexed before.
    document_collection.delete(
        where={"document_id": document_id}
    )

    chunk_ids = [
        f"document-{document_id}-chunk-{index}"
        for index in range(len(chunks))
    ]

    metadata = [
        {
            "document_id": document_id,
            "document_name": document_name,
            "chunk_number": index + 1,
        }
        for index in range(len(chunks))
    ]

    document_collection.add(
        ids=chunk_ids,
        documents=chunks,
        metadatas=metadata,
    )

    return len(chunks)
def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size"
        )

    chunks = []
    start_position = 0
    text_length = len(text)

    while start_position < text_length:
        end_position = min(
            start_position + chunk_size,
            text_length,
        )

        chunk = text[start_position:end_position].strip()

        if chunk:
            chunks.append(chunk)

        if end_position == text_length:
            break

        start_position = end_position - chunk_overlap

    return chunks

def delete_document_chunks(document_id: int) -> None:
    """Delete all vector chunks belonging to one document."""
    document_collection.delete(
        where={"document_id": document_id}
    )


def search_document_chunks(
    query: str,
    result_count: int = 5,
) -> list[dict]:
    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("Search query cannot be empty")

    collection_count = document_collection.count()

    if collection_count == 0:
        return []

    actual_result_count = min(
        result_count,
        collection_count,
    )

    results = document_collection.query(
        query_texts=[cleaned_query],
        n_results=actual_result_count,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    search_results = []

    for document_text, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        search_results.append(
            {
                "content": document_text,
                "document_id": metadata.get("document_id"),
                "document_name": metadata.get(
                    "document_name"
                ),
                "chunk_number": metadata.get(
                    "chunk_number"
                ),
                "distance": float(distance),
            }
        )

    return search_results
