from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
class DocumentResponse(BaseModel):
    id: int
    original_name: str
    uploaded_by: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
class DocumentTextResponse(BaseModel):
    document_id: int
    document_name: str
    character_count: int
    word_count: int
    preview: str
    
class ChunkPreview(BaseModel):
    chunk_number: int
    character_count: int
    content: str


class DocumentChunksResponse(BaseModel):
    document_id: int
    document_name: str
    total_chunks: int
    chunks: list[ChunkPreview]    

class DocumentIndexResponse(BaseModel):
    document_id: int
    document_name: str
    indexed_chunks: int
    message: str
class SearchRequest(BaseModel):
    query: str
    result_count: int = 5


class SearchResult(BaseModel):
    content: str
    document_id: int
    document_name: str
    chunk_number: int
    distance: float


class DocumentSearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResult]

class ChatQuestionRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class ChatSource(BaseModel):
    document_id: int
    document_name: str
    chunk_number: int


class ChatAnswerResponse(BaseModel):
    conversation_id: int
    question: str
    answer: str
    model_provider: str
    sources: list[ChatSource]

class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: int
    title: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: list[MessageResponse]

    model_config = ConfigDict(from_attributes=True)