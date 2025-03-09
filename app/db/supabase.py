import logging
from supabase import create_client, Client
from ..config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabaseクライアントの管理クラス"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                logger.debug(f"Initializing Supabase client with URL: {settings.SUPABASE_URL}")
                cls._instance = super(SupabaseClient, cls).__new__(cls)
                cls._instance.client = create_client(
                    settings.SUPABASE_URL, 
                    settings.SUPABASE_KEY
                )
                logger.debug("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        return cls._instance
    
    def get_client(self) -> Client:
        """Supabaseクライアントを取得"""
        return self.client

# シングルトンインスタンスを作成
supabase = SupabaseClient().get_client()

# 依存性注入用のファンクション
def get_supabase_client() -> Client:
    """依存性注入用のSupabaseクライアント取得関数"""
    return SupabaseClient().get_client()