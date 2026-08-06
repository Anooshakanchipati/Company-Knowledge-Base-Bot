from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_database
from app.security import require_admin
from app.services.document_processor import extract_document_text
from app.services.vector_store import (
    delete_document_chunks,
    search_document_chunks,
    split_text_into_chunks,
    store_document_chunks,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("/check")
def check_admin_access(
    current_admin: models.User = Depends(require_admin),
):
    return {
        "message": "Admin access confirmed",
        "admin": {
            "id": current_admin.id,
            "name": current_admin.name,
            "email": current_admin.email,
            "role": current_admin.role,
        },
    }


@router.post(
    "/documents/upload",
    response_model=list[schemas.DocumentResponse],
)
async def upload_documents(
    files: list[UploadFile] = File(...),
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one document",
        )

    uploaded_documents = []

    for file in files:
        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{original_name}: unsupported file type. "
                    "Only PDF, DOCX, and TXT files are allowed."
                ),
            )

        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=f"{original_name}: empty files are not allowed",
            )

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"{original_name}: file size must not exceed 10 MB",
            )

        stored_name = f"{uuid4().hex}{extension}"
        file_path = UPLOAD_DIRECTORY / stored_name
        document = None

        try:
            # Save the uploaded file.
            file_path.write_bytes(file_content)

            # Create the database record.
            document = models.Document(
                original_name=original_name,
                stored_name=stored_name,
                file_path=str(file_path),
                uploaded_by=current_admin.id,
            )

            database.add(document)
            database.commit()
            database.refresh(document)

            # Extract text from the document.
            extracted_text = extract_document_text(
                document.file_path
            )

            # Divide the extracted text into chunks.
            chunks = split_text_into_chunks(
                text=extracted_text,
                chunk_size=1000,
                chunk_overlap=200,
            )

            if not chunks:
                raise ValueError(
                    "No readable text was found in the document"
                )

            # Store chunks and embeddings in ChromaDB.
            store_document_chunks(
                document_id=document.id,
                document_name=document.original_name,
                chunks=chunks,
            )

            uploaded_documents.append(document)

        except Exception as error:
            database.rollback()

            # Remove vectors if any were created.
            if document is not None and document.id is not None:
                try:
                    delete_document_chunks(document.id)
                except Exception:
                    pass

                saved_document = (
                    database.query(models.Document)
                    .filter(models.Document.id == document.id)
                    .first()
                )

                if saved_document:
                    database.delete(saved_document)
                    database.commit()

            # Remove the saved file.
            if file_path.exists() and file_path.is_file():
                file_path.unlink()

            raise HTTPException(
                status_code=400,
                detail=f"{original_name}: {str(error)}",
            )

    return uploaded_documents
@router.get(
    "/documents",
    response_model=List[schemas.DocumentResponse],
)
def list_documents(
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    return (
        database.query(models.Document)
        .order_by(models.Document.created_at.desc())
        .all()
    )


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    document = (
        database.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    deleted_name = document.original_name
    file_path = Path(document.file_path)

    try:
        # Delete every related chunk and embedding.
        delete_document_chunks(document_id)

        # Delete the uploaded file.
        if file_path.exists() and file_path.is_file():
            file_path.unlink()

        # Delete the database record.
        database.delete(document)
        database.commit()

    except Exception as error:
        database.rollback()
        print(f"Document deletion error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to completely delete the document",
        )

    return {
        "message": "Document and all related chunks deleted successfully",
        "document_id": document_id,
        "document_name": deleted_name,
    }
@router.post(
    "/documents/{document_id}/extract",
    response_model=schemas.DocumentTextResponse,
)
def extract_uploaded_document(
    document_id: int,
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    document = (
        database.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        extracted_text = extract_document_text(
            document.file_path
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to read the document",
        )

    return {
        "document_id": document.id,
        "document_name": document.original_name,
        "character_count": len(extracted_text),
        "word_count": len(extracted_text.split()),
        "preview": extracted_text[:500],
    }
@router.post(
    "/documents/{document_id}/chunks",
    response_model=schemas.DocumentChunksResponse,
)
def create_document_chunks(
    document_id: int,
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    document = (
        database.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        extracted_text = extract_document_text(
            document.file_path
        )

        chunks = split_text_into_chunks(
            text=extracted_text,
            chunk_size=1000,
            chunk_overlap=200,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the document",
        )

    chunk_previews = [
        {
            "chunk_number": index + 1,
            "character_count": len(chunk),
            "content": chunk,
        }
        for index, chunk in enumerate(chunks[:5])
    ]

    return {
        "document_id": document.id,
        "document_name": document.original_name,
        "total_chunks": len(chunks),
        "chunks": chunk_previews,
    }
@router.post(
    "/documents/{document_id}/index",
    response_model=schemas.DocumentIndexResponse,
)
def index_document(
    document_id: int,
    current_admin: models.User = Depends(require_admin),
    database: Session = Depends(get_database),
):
    document = (
        database.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        extracted_text = extract_document_text(
            document.file_path
        )

        chunks = split_text_into_chunks(
            text=extracted_text,
            chunk_size=1000,
            chunk_overlap=200,
        )

        indexed_chunks = store_document_chunks(
            document_id=document.id,
            document_name=document.original_name,
            chunks=chunks,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print(f"Document indexing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to index the document",
        )

    return {
        "document_id": document.id,
        "document_name": document.original_name,
        "indexed_chunks": indexed_chunks,
        "message": "Document indexed successfully",
    }
@router.post(
    "/documents/search",
    response_model=schemas.DocumentSearchResponse,
)
def search_documents(
    search_request: schemas.SearchRequest,
    current_admin: models.User = Depends(require_admin),
):
    if search_request.result_count < 1:
        raise HTTPException(
            status_code=400,
            detail="Result count must be at least 1",
        )

    if search_request.result_count > 10:
        raise HTTPException(
            status_code=400,
            detail="Result count cannot exceed 10",
        )

    try:
        results = search_document_chunks(
            query=search_request.query,
            result_count=search_request.result_count,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        print(f"Document search error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to search the documents",
        )

    return {
        "query": search_request.query,
        "total_results": len(results),
        "results": results,
    }