from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# Supabaseクライアントの初期化
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# ルーターの設定
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# OAuth2のスキーマ設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# リクエスト/レスポンスモデルの定義
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str

# ユーザー登録エンドポイント
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        # 登録情報をログ出力
        print(f"Attempting to register user: {user.email}")
        
        # Supabaseでユーザーを作成
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
        
        # 詳細なレスポンス情報をログ出力
        print(f"Supabase registration response: {response}")
        print(f"User data: {response.user}")
        
        user_id = response.user.id
        user_email = response.user.email
        
        # 作成した後、データが存在するかごく強制的に確認
        try:
            check_user = supabase.auth.get_user(response.session.access_token)
            print(f"Confirmation - User exists: {check_user.user.email}")
        except Exception as check_error:
            print(f"Warning: Could not verify user after creation: {str(check_error)}")
        
        return {
            "id": user_id,
            "email": user_email
        }
    except Exception as e:
        # 詳細なエラー情報をログ出力
        print(f"Registration error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

# ログインエンドポイント
@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    try:
        # ログ出入力値
        print(f"Login attempt for: {user.email}")
        
        # Supabaseでログイン
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        
        # レスポンスの詳細なログ
        print(f"Supabase login response: {response}")
        
        # アクセストークンとリフレッシュトークンを取得
        access_token = response.session.access_token
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # 詳細なエラー情報をログ出力
        print(f"Login error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# トークン取得エンドポイント (OAuth2互換)
@router.post("/token", response_model=Token)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Supabaseでログイン
        response = supabase.auth.sign_in_with_password({
            "email": form_data.username,  # OAuth2では、emailがusernameフィールドに入る
            "password": form_data.password
        })
        
        # アクセストークンを取得
        access_token = response.session.access_token
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ログアウトエンドポイント
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        # Supabaseでログアウト
        supabase.auth.sign_out()
        return {"detail": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed: {str(e)}"
        )

# 現在のユーザー情報を取得するエンドポイント
@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # トークンからユーザー情報を取得
        user = supabase.auth.get_user(token)
        
        return {
            "id": user.user.id,
            "email": user.user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# パスワードリセットメール送信エンドポイント
@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(email: EmailStr):
    try:
        # パスワードリセットメールを送信
        supabase.auth.reset_password_email(email)
        return {"detail": "Password reset email sent"}
    except Exception as e:
        # エラーが発生してもユーザーにはエラーを表示しない（セキュリティのため）
        return {"detail": "If the email exists, a password reset link has been sent"}
