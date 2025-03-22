from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

from ..models.chat import ChatSession, Message


class LanguageChainUtil:
    """LangChain関連のユーティリティクラス"""
    
    @staticmethod
    def create_buffer_memory_from_session(session: ChatSession) -> ConversationBufferMemory:
        """セッションからConversationBufferMemoryを作成"""
        memory = ConversationBufferMemory(return_messages=True)
        
        # セッション内のメッセージをメモリに追加
        for msg in session.messages:
            if msg.role == "user":
                memory.chat_memory.add_user_message(msg.content)
            elif msg.role == "assistant":
                memory.chat_memory.add_ai_message(msg.content)
        
        return memory
    
    @staticmethod
    def convert_langchain_messages_to_models(messages: List[Any]) -> List[Message]:
        """LangChainのメッセージをアプリのメッセージモデルに変換"""
        result = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                result.append(Message(content=msg.content, role="user"))
            elif isinstance(msg, AIMessage):
                result.append(Message(content=msg.content, role="assistant"))
            # SystemMessageは保存しない
        
        return result
    
    @staticmethod
    def create_session_store() -> Dict[str, List[Any]]:
        """セッションストアを作成する（インメモリ）"""
        return {}
    
    @staticmethod
    def get_session_history(
        session_id: str, 
        session_store: Dict[str, List[Any]]
    ) -> List[Any]:
        """セッションストアからセッション履歴を取得"""
        if session_id not in session_store:
            session_store[session_id] = []
        return session_store[session_id]
    
    @staticmethod
    def create_chat_prompt_template(system_prompt: str) -> ChatPromptTemplate:
        """チャットプロンプトテンプレートを作成"""
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
    
    @staticmethod
    def setup_runnable_with_history(
        chain: Any, 
        session_store: Dict[str, List[Any]]
    ) -> RunnableWithMessageHistory:
        """履歴付きの実行可能オブジェクトを設定"""
        return RunnableWithMessageHistory(
            chain,
            lambda session_id: LanguageChainUtil.get_session_history(session_id, session_store),
            input_messages_key="input",
            history_messages_key="history"
        )
