from fastapi import APIRouter, Depends, HTTPException
from app.security import get_current_user
from app.services.ai_service import generate_rag_answer
from app.services.vector_store import search_document_chunks
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_database




router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)
@router.post(
    "/ask",
    response_model=schemas.ChatAnswerResponse,
)
def ask_question(
    request: schemas.ChatQuestionRequest,
    current_user: models.User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    conversation = None

    if request.conversation_id is not None:
        conversation = (
            database.query(models.Conversation)
            .filter(
                models.Conversation.id
                == request.conversation_id,
                models.Conversation.user_id
                == current_user.id,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

    else:
        conversation = models.Conversation(
            title=question[:100],
            user_id=current_user.id,
        )

        database.add(conversation)
        database.commit()
        database.refresh(conversation)

    try:
        search_results = search_document_chunks(
            query=question,
            result_count=5,
        )

        answer, model_provider = generate_rag_answer(
            question=question,
            search_results=search_results,
        )

        user_message = models.ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )

        assistant_message = models.ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )

        database.add_all([
            user_message,
            assistant_message,
        ])

        database.commit()

    except ValueError as error:
        database.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        database.rollback()
        print(f"RAG answer error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate the answer",
        )

    sources = []
    seen_sources = set()

    for result in search_results:
        source_key = (
            result["document_id"],
            result["chunk_number"],
        )

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            sources.append(
                {
                    "document_id": result["document_id"],
                    "document_name": result["document_name"],
                    "chunk_number": result["chunk_number"],
                }
            )

    return {
        "conversation_id": conversation.id,
        "question": question,
        "answer": answer,
        "model_provider": model_provider,
        "sources": sources,
    }
@router.get("/conversations")
def get_conversations(
    current_user: models.User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    conversations = (
        database.query(models.Conversation)
        .filter(
            models.Conversation.user_id == current_user.id
        )
        .order_by(
            models.Conversation.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
        }
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: models.User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    conversation = (
        database.query(models.Conversation)
        .filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        database.query(models.ChatMessage)
        .filter(
            models.ChatMessage.conversation_id
            == conversation.id
        )
        .order_by(
            models.ChatMessage.created_at.asc()
        )
        .all()
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: models.User = Depends(get_current_user),
    database: Session = Depends(get_database),
):
    conversation = (
        database.query(models.Conversation)
        .filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    database.delete(conversation)
    database.commit()

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id,
    }

