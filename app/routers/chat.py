from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import google.generativeai as genai

from ..models.chat import (
    ChatRequest, 
    ChatResponse, 
    SessionRequest, 
    SessionResponse,
    ChatSession,
    Message
)
from ..services.gemini_service import GeminiService
from ..services.session_service import SessionService
from ..utils.langgraph_chatbot import process_message, convert_to_langchain_format, extract_assistant_message

# セッションサービスの作成
storage_path = os.environ.get("SESSION_STORAGE_PATH", "data/sessions.json")
session_service = SessionService(storage_path)

# GeminiサービスはAPIキーを必要とする
api_key = os.environ.get("GOOGLE_API_KEY")
gemini_service = GeminiService(api_key)

router = APIRouter(
    prefix="/api",
    tags=["chat"]
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """チャットメッセージを処理して、AIからの応答を返す"""
    # セッションIDがある場合はそのセッションを取得、なければ新しく作成
    session = None
    if request.session_id:
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Session with ID {request.session_id} not found"
            )
    else:
        # 新しいセッションを作成
        session = ChatSession(
            user_id=request.user_id,
            level=request.level, 
            focus=request.focus
        )
        session = session_service.create_session(session)
    
    # ユーザーメッセージをセッションに追加
    user_message = Message(
        content=request.message,
        role="user"
    )
    session = session_service.add_message(session.id, user_message)
    
    # 最初のメッセージの場合、タイトルを生成
    if len(session.messages) == 1:
        session.title = gemini_service.generate_title(request.message)
        session = session_service.update_session(session)
    
    # AIからの応答を生成
    try:
        ai_response = await gemini_service.generate_response(session, request.message)
        
        # AIメッセージをセッションに追加
        ai_message = Message(
            content=ai_response,
            role="assistant"
        )
        session = session_service.add_message(session.id, ai_message)
        
        # レスポンスを作成
        return ChatResponse(
            message=ai_response,
            session_id=session.id,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating AI response: {str(e)}"
        )

@router.post("/chat/langgraph", response_model=ChatResponse)
async def chat_with_langgraph(request: ChatRequest):
    """LangGraphを使用したチャットメッセージを処理して、AIからの応答を返す"""
    # セッションIDがある場合はそのセッションを取得、なければ新しく作成
    session = None
    if request.session_id:
        session = session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Session with ID {request.session_id} not found"
            )
    else:
        # 新しいセッションを作成
        session = ChatSession(
            user_id=request.user_id,
            level=request.level, 
            focus=request.focus
        )
        session = session_service.create_session(session)
    
    # ユーザーメッセージをセッションに追加
    user_message = Message(
        content=request.message,
        role="user"
    )
    session = session_service.add_message(session.id, user_message)
    
    # 最初のメッセージの場合、タイトルを生成
    if len(session.messages) == 1:
        session.title = gemini_service.generate_title(request.message)
        session = session_service.update_session(session)
    
    # LangGraphでの応答を生成
    try:
        # セッション履歴をLangChainフォーマットに変換
        history = convert_to_langchain_format(session.messages)
        
        # LangGraphで処理
        result = process_message(request.message, history)
        
        # 応答を抽出
        ai_response = extract_assistant_message(result)
        
        # AIメッセージをセッションに追加
        ai_message = Message(
            content=ai_response,
            role="assistant"
        )
        session = session_service.add_message(session.id, ai_message)
        
        # レスポンスを作成
        return ChatResponse(
            message=ai_response,
            session_id=session.id,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating AI response with LangGraph: {str(e)}"
        )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """新しいチャットセッションを作成"""
    # 新しいセッションを作成
    session = ChatSession(
        user_id=request.user_id,
        title=request.title or "New Conversation",
        level=request.level,
        focus=request.focus
    )
    
    # セッションをストアに保存
    session = session_service.create_session(session)
    
    # レスポンスを作成
    return SessionResponse(
        session_id=session.id,
        title=session.title,
        created_at=session.created_at
    )


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str):
    """指定されたIDのセッション情報を取得"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    return session


@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(user_id: Optional[str] = None, limit: int = 10):
    """セッション一覧を取得（ユーザーIDがある場合はそのユーザーのみ）"""
    if user_id:
        return session_service.get_user_sessions(user_id)
    else:
        return session_service.get_recent_sessions(limit)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """セッションを削除"""
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )


@router.put("/sessions/{session_id}/title", response_model=ChatSession)
async def update_session_title(session_id: str, title: str):
    """セッションのタイトルを更新"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    session.title = title
    session = session_service.update_session(session)
    return session


@router.post("/grammar", response_model=Dict[str, Any])
async def check_grammar(text: str):
    """文法チェックを実行して結果を返す"""
    try:
        # GeminiモデルでGrammarチェックを行う実装
        # ここでは簡易的な実装
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Please analyze the following English text for grammar errors. 
        For each error, provide:
        1. The incorrect part
        2. The correct version
        3. A brief explanation of the grammar rule

        Return as a JSON array of objects with fields:
        - original: the original incorrect text
        - correction: the corrected text
        - explanation: explanation of the grammar rule
        - type: the type of error (e.g., "verb tense", "article", etc.)

        TEXT: {text}
        """
        
        response = model.generate_content(prompt)
        
        # 応答をJSONとして解析（エラー処理を追加）
        try:
            import json
            corrections = json.loads(response.text)
        except:
            # JSONとして解析できない場合は、テキスト応答をそのまま返す
            return {
                "original_text": text,
                "corrections": [],
                "message": response.text
            }
        
        return {
            "original_text": text,
            "corrections": corrections
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking grammar: {str(e)}"
        )


@router.get("/vocabulary", response_model=Dict[str, Any])
async def get_vocabulary(topic: str, level: str = "intermediate"):
    """特定のトピックに関連する語彙を提供"""
    try:
        # Geminiモデルを使用して語彙推奨を取得
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Generate a list of useful English vocabulary for {level} level students related to the topic "{topic}".
        
        For each word, provide:
        1. The word itself
        2. Part of speech (noun, verb, adj, etc.)
        3. Definition (simple and clear)
        4. Example sentence using the word
        5. Any common collocations or phrases with this word
        
        Return as a JSON array of objects with fields:
        - word: the vocabulary word
        - partOfSpeech: the part of speech
        - definition: a simple definition
        - example: an example sentence
        - collocations: array of common phrases/collocations
        
        Include 10 words that would be appropriate for {level} level English learners.
        """
        
        response = model.generate_content(prompt)
        
        # 応答をJSONとして解析（エラー処理を追加）
        try:
            import json
            vocabulary = json.loads(response.text)
        except:
            # JSONとして解析できない場合は、テキスト応答をそのまま返す
            return {
                "topic": topic,
                "level": level,
                "vocabulary": [],
                "message": response.text
            }
        
        return {
            "topic": topic,
            "level": level,
            "vocabulary": vocabulary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating vocabulary: {str(e)}"
        )


@router.get("/topics", response_model=List[Dict[str, Any]])
async def get_conversation_topics(category: Optional[str] = None, count: int = 5):
    """会話トピックの推奨を提供"""
    try:
        # カテゴリがある場合はそれに関連するトピックを、なければ一般的なトピックを提供
        category_prompt = f"related to {category}" if category else "for general conversation practice"
        
        # Geminiモデルを使用してトピックを取得
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Generate {count} interesting conversation topics {category_prompt} for English language learners.
        
        For each topic, provide:
        1. A title/question for the topic
        2. A brief description of the topic
        3. 3 sample questions to get the conversation started
        
        Return as a JSON array of objects with fields:
        - title: the conversation topic title/question
        - description: a brief description of why this is a good conversation topic
        - questions: array of 3 starter questions
        - category: the category this topic belongs to
        """
        
        response = model.generate_content(prompt)
        
        # 応答をJSONとして解析（エラー処理を追加）
        try:
            import json
            topics = json.loads(response.text)
        except:
            # JSONとして解析できない場合は、空のトピックリストを返す
            return []
        
        return topics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating conversation topics: {str(e)}"
        )
