import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import words, auth, chat
from .config import settings

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="FastAPI Supabase Lambda",
    description="FastAPIとSupabaseを連携するLambda用バックエンドAPI",
    version="0.1.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(words.router, prefix="/api/v1")
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Welcome to FastAPI Supabase Lambda API"}