from fastapi import HTTPException
from typing import Any, Dict, List
from postgrest import APIResponse

def handle_supabase_response(response: APIResponse, error_message: str) -> List[Dict[str, Any]]:
    """
    Supabaseのレスポンスを処理し、データを取得するヘルパー関数

    Args:
        response: Supabaseからのレスポンス
        error_message: エラー時のメッセージ

    Returns:
        処理されたデータのリスト

    Raises:
        HTTPException: レスポンスにエラーがある場合
    """
    try:
        data = response.data
        
        if data is None:
            raise HTTPException(status_code=404, detail=f"{error_message}: No data found")
        
        # データが辞書の場合、リストに変換
        if isinstance(data, dict):
            return [data]
            
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"{error_message}: {str(e)}"
        )

def filter_none_values(data: dict) -> dict:
    """
    辞書からNone値を持つキーを除外する

    Args:
        data: 処理する辞書

    Returns:
        None値を除外した新しい辞書
    """
    return {k: v for k, v in data.items() if v is not None}