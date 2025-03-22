from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json

from ..models.chat import ChatSession, Message


class SessionService:
    """チャットセッション管理サービス"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """セッション管理サービスの初期化"""
        # インメモリストレージとして辞書を使用
        self.sessions: Dict[str, ChatSession] = {}
        
        # 永続ストレージのパス（オプション）
        self.storage_path = storage_path or os.environ.get("SESSION_STORAGE_PATH")
        
        # 永続ストレージが指定されている場合は初期化
        if self.storage_path and os.path.exists(self.storage_path):
            self._load_sessions()
    
    def _load_sessions(self) -> None:
        """永続ストレージからセッションを読み込む"""
        try:
            if not os.path.exists(self.storage_path):
                return
                
            with open(self.storage_path, 'r') as f:
                sessions_data = json.load(f)
                
            for session_id, session_dict in sessions_data.items():
                # メッセージのデシリアライズ
                messages = []
                for msg_dict in session_dict.get('messages', []):
                    messages.append(Message(
                        id=msg_dict.get('id'),
                        content=msg_dict.get('content'),
                        role=msg_dict.get('role'),
                        timestamp=datetime.fromisoformat(msg_dict.get('timestamp')),
                        metadata=msg_dict.get('metadata')
                    ))
                
                # セッションの作成
                self.sessions[session_id] = ChatSession(
                    id=session_id,
                    user_id=session_dict.get('user_id'),
                    title=session_dict.get('title', 'New Conversation'),
                    created_at=datetime.fromisoformat(session_dict.get('created_at')),
                    updated_at=datetime.fromisoformat(session_dict.get('updated_at')),
                    messages=messages,
                    level=session_dict.get('level', 'intermediate'),
                    focus=session_dict.get('focus', 'conversation'),
                    metadata=session_dict.get('metadata')
                )
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def _save_sessions(self) -> None:
        """永続ストレージにセッションを保存する"""
        if not self.storage_path:
            return
            
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # セッションをシリアライズ可能な形式に変換
            sessions_dict = {}
            for session_id, session in self.sessions.items():
                # メッセージをシリアライズ
                messages = []
                for msg in session.messages:
                    messages.append({
                        'id': msg.id,
                        'content': msg.content,
                        'role': msg.role,
                        'timestamp': msg.timestamp.isoformat(),
                        'metadata': msg.metadata
                    })
                
                # セッション全体をシリアライズ
                sessions_dict[session_id] = {
                    'user_id': session.user_id,
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'messages': messages,
                    'level': session.level,
                    'focus': session.focus,
                    'metadata': session.metadata
                }
            
            # ファイルに保存
            with open(self.storage_path, 'w') as f:
                json.dump(sessions_dict, f, indent=2)
                
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """セッションIDによるセッションの取得"""
        return self.sessions.get(session_id)
    
    def create_session(self, session: ChatSession) -> ChatSession:
        """新しいセッションの作成"""
        # セッションをストレージに追加
        self.sessions[session.id] = session
        
        # 永続ストレージに保存
        self._save_sessions()
        
        return session
    
    def update_session(self, session: ChatSession) -> ChatSession:
        """セッションの更新"""
        # 更新日時を設定
        session.updated_at = datetime.now()
        
        # セッションを更新
        self.sessions[session.id] = session
        
        # 永続ストレージに保存
        self._save_sessions()
        
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """セッションの削除"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # 永続ストレージに保存
            self._save_sessions()
            
            return True
        return False
    
    def add_message(self, session_id: str, message: Message) -> Optional[ChatSession]:
        """セッションにメッセージを追加"""
        session = self.get_session(session_id)
        if not session:
            return None
            
        # メッセージを追加
        session.messages.append(message)
        
        # 更新日時を設定
        session.updated_at = datetime.now()
        
        # セッションを更新
        self.update_session(session)
        
        return session
    
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """ユーザーのセッション一覧を取得"""
        return [s for s in self.sessions.values() if s.user_id == user_id]
    
    def get_recent_sessions(self, limit: int = 10) -> List[ChatSession]:
        """最近のセッション一覧を取得"""
        # 更新日時でソートして制限数だけ取得
        sorted_sessions = sorted(
            self.sessions.values(),
            key=lambda s: s.updated_at,
            reverse=True
        )
        return sorted_sessions[:limit]
