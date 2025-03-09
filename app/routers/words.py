from fastapi import APIRouter, HTTPException, Query, Body, Path
from typing import List, Optional
from ..models.models import Word, WordCreate, WordUpdate, ErrorResponse
from ..db.supabase import supabase  # これで正しくインポートできます
from ..utils.helpers import handle_supabase_response, filter_none_values
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/words",
    tags=["words"],
    responses={404: {"model": ErrorResponse}},
)

@router.get("/", response_model=List[Word])
async def get_words(
    skip: int = Query(0, description="スキップする単語数"),
    limit: int = Query(100, description="取得する単語の最大数"),
):
    """
    単語のリストを取得する
    """
    try:
        # クエリの構築と実行
        query = supabase.table("words").select("*").range(skip, skip + limit - 1).order("id")
        logger.debug(f"Executing query on table: words")
        logger.debug(f"Range: {skip} to {skip + limit - 1}")
        
        # クエリの実行
        response = query.execute()
        logger.debug(f"Response status: {getattr(response, 'status_code', 'N/A')}")
        logger.debug(f"Response data type: {type(response.data)}")
        logger.debug(f"Response data: {response.data}")
        
        # レスポンスの処理
        result = handle_supabase_response(response, "Failed to fetch words")
        logger.debug(f"Processed result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error in get_words: {str(e)}", exc_info=True)
        raise

@router.get("/search", response_model=List[Word])
async def search_words(
    query: str = Query(..., description="検索クエリ"),
):
    """
    単語を検索する
    """
    response = supabase.table("words").select("*").ilike("word", f"%{query}%").execute()
    return handle_supabase_response(response, "Failed to search words")

@router.post("/", response_model=Word)
async def create_word(
    word: WordCreate = Body(..., description="作成する単語情報"),
):
    """
    新しい単語を登録する
    """
    response = supabase.table("words").insert(word.dict()).execute()
    return handle_supabase_response(response, "Failed to create word")[0]

@router.get("/{word_id}", response_model=Word)
async def get_word(
    word_id: int = Path(..., description="取得する単語のID"),
):
    """
    指定したIDの単語を取得する
    """
    response = supabase.table("words").select("*").eq("id", word_id).execute()
    data = handle_supabase_response(response, "Failed to fetch word")
    
    if not data:
        raise HTTPException(status_code=404, detail="Word not found")
    
    return data[0]

@router.put("/{word_id}", response_model=Word)
async def update_word(
    word_id: int = Path(..., description="更新する単語のID"),
    word: WordUpdate = Body(..., description="更新する単語情報"),
):
    """
    指定したIDの単語を更新する
    """
    # None値を持つフィールドを除外
    update_data = filter_none_values(word.dict())
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    response = supabase.table("words").update(update_data).eq("id", word_id).execute()
    data = handle_supabase_response(response, "Failed to update word")
    
    if not data:
        raise HTTPException(status_code=404, detail="Word not found")
    
    return data[0]

@router.delete("/{word_id}", response_model=dict)
async def delete_word(
    word_id: int = Path(..., description="削除する単語のID"),
):
    """
    指定したIDの単語を削除する
    """
    response = supabase.table("words").delete().eq("id", word_id).execute()
    handle_supabase_response(response, "Failed to delete word")
    
    return {"message": "Word deleted successfully"}

@router.post("/batch", response_model=List[Word])
async def create_words_batch(
    words: List[WordCreate] = Body(..., description="バッチで作成する単語リスト"),
):
    """
    複数の単語を一括で登録する
    """
    words_data = [word.dict() for word in words]
    response = supabase.table("words").insert(words_data).execute()
    return handle_supabase_response(response, "Failed to create words batch")