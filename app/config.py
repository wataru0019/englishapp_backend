import os
from typing import List
from pydantic import BaseSettings
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()

class Settings(BaseSettings):
    """アプリケーション設定"""
    # Supabase設定
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # アプリケーション設定
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS設定
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name, raw_val):
            if field_name == "CORS_ORIGINS" and raw_val:
                return raw_val.split(",")
            return raw_val

# 設定のインスタンス化
settings = Settings()