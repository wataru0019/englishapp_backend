from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Message(BaseModel):
    """チャットメッセージモデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    role: str  # 'user' または 'assistant'
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[Any, Any]] = None


class ChatSession(BaseModel):
    """チャットセッションモデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = []
    level: str = "intermediate"  # beginner, intermediate, advanced
    focus: str = "conversation"  # conversation, grammar, vocabulary
    metadata: Optional[Dict[Any, Any]] = None


class ChatRequest(BaseModel):
    """チャットリクエストモデル"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    level: Optional[str] = "intermediate"
    focus: Optional[str] = "conversation"


class ChatResponse(BaseModel):
    """チャットレスポンスモデル"""
    message: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    corrections: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[Dict[str, Any]]] = None


class SessionRequest(BaseModel):
    """新しいセッション作成リクエストモデル"""
    level: str = "intermediate"
    focus: str = "conversation"
    user_id: Optional[str] = None
    title: Optional[str] = None


class SessionResponse(BaseModel):
    """セッションレスポンスモデル"""
    session_id: str
    title: str
    created_at: datetime
