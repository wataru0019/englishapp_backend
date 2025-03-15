from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WordBase(BaseModel):
    """単語の基本モデル"""
    word: str = Field(..., title="word", description="単語")
    mean: str = Field(..., title="mean", description="意味")
    example_sentence: Optional[str] = Field(None, title="example_sentence", description="例文")

    class Config:
        orm_mode = True

class WordCreate(WordBase):
    """単語作成モデル"""
    pass

class WordUpdate(WordBase):
    """単語更新モデル - すべてのフィールドをオプショナルにする"""
    word: Optional[str] = None
    mean: Optional[str] = None
    example_sentence: Optional[str] = None

class WordInDB(WordBase):
    """データベース内の単語モデル"""
    id: int = Field(..., title="id")
    created_at: datetime = Field(..., title="created_at")

    class Config:
        orm_mode = True

class Word(WordInDB):
    """API応答用の単語モデル"""
    pass

class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    detail: str