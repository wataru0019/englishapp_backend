from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ルーターのインポート
from .routers import chat

# アプリケーションの作成
app = FastAPI(
    title="英語学習アプリ API",
    description="Geminiを活用した英語学習チャットアプリのバックエンドAPI",
    version="1.0.0"
)

# CORS設定
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://your-frontend-domain.com",
    "*"  # 開発中は全てのオリジンを許可（本番環境では適切に制限する）
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの追加
app.include_router(chat.router)

# 必要なディレクトリを作成
os.makedirs("data", exist_ok=True)

# ルートエンドポイント
@app.get("/")
async def root():
    return {
        "message": "英語学習アプリ API",
        "version": "1.0.0",
        "status": "running"
    }

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 環境変数チェック
@app.on_event("startup")
async def startup_event():
    required_env_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"警告: 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print("設定方法: .envファイルに追加するか、環境変数として設定してください。")
        
        # GOOGLE_API_KEYがない場合は特別な警告
        if "GOOGLE_API_KEY" in missing_vars:
            print("\nGOOGLE_API_KEYが必要です。Google AI Studioから取得してください。")
            print("https://makersuite.google.com/app/apikey")
