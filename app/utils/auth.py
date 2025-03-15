from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
import os
from typing import Optional
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# Supabaseクライアントの初期化
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# OAuth2スキーマ
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    現在のユーザーを取得する関数。
    トークンが有効であれば、ユーザー情報を返す。
    無効であれば、HTTPExceptionを発生させる。
    """
    try:
        # トークンからユーザー情報を取得
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 認証が必要なエンドポイントで使用する依存関係
def get_current_active_user(current_user = Depends(get_current_user)):
    """
    アクティブなユーザーを取得する関数。
    将来的には、ユーザーのステータスに応じて処理を分岐させることができる。
    """
    # ここで、必要に応じてユーザーのステータスチェックなどを行う
    # 例: if current_user.disabled: raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
