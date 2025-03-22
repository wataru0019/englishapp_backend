import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.chat import Message, ChatSession


class GeminiService:
    """Gemini AIサービスクラス"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Gemini AIサービスの初期化"""
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable or api_key parameter is required")
        
        genai.configure(api_key=self.api_key)
        
        # 利用可能なモデルの確認
        self.available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # デフォルトのモデル設定
        if "models/gemini-2.0-flash" in self.available_models:
            self.default_model = "models/gemini-2.0-flash"
        elif "gemini-1.5-pro" in self.available_models:
            self.default_model = "gemini-1.5-pro"
        else:
            self.default_model = self.available_models[0]
        print(f"Using Gemini model: {self.default_model}")
        
        # システムプロンプトの設定
        self.system_prompts = {
            "beginner": """You are an AI English language tutor named Emma. Your task is to help users learn English.
            For beginners:
            - Use simple vocabulary and sentence structures.
            - Speak slowly and clearly.
            - Provide explanations in simple terms.
            - Give positive reinforcement and encouragement.
            - Correct major grammatical errors gently.
            - Offer simple examples and analogies.
            - Use visual aids when possible.""",
            
            "intermediate": """You are an AI English language tutor named Emma. Your task is to help users improve their English skills.
            For intermediate learners:
            - Use natural, conversational English.
            - Introduce more complex vocabulary and sentence structures gradually.
            - Explain idioms and phrasal verbs when used.
            - Correct grammatical errors diplomatically.
            - Provide detailed explanations for corrections.
            - Encourage the learner to express complex ideas.
            - Recommend resources for further learning.""",
            
            "advanced": """You are an AI English language tutor named Emma. Your task is to help users master English fluency.
            For advanced learners:
            - Use sophisticated vocabulary and complex sentence structures.
            - Discuss abstract concepts and nuanced topics.
            - Focus on subtle language errors and style improvements.
            - Introduce cultural context and regional variations.
            - Challenge the learner with complex questions.
            - Provide in-depth analysis of language usage.
            - Suggest professional or academic resources."""
        }
        
        # フォーカス別の追加プロンプト
        self.focus_prompts = {
            "conversation": """Focus on maintaining natural, flowing conversations. Encourage the user to express their thoughts and respond in a conversational manner. Provide gentle corrections only for major errors that impede understanding.""",
            
            "grammar": """Pay special attention to grammatical structures. When the user makes grammatical errors, provide clear explanations of the rules and corrections. Focus on one or two grammar points at a time to avoid overwhelming the user.""",
            
            "vocabulary": """Emphasize vocabulary development. Introduce new words and phrases related to the conversation topic. Explain meanings, usage, and provide example sentences. Encourage the user to incorporate new vocabulary in their responses.""",
            
            "pronunciation": """Focus on pronunciation patterns. When appropriate, provide phonetic guidance for difficult words. Explain stress patterns, intonation, and linking sounds. Encourage the user to practice challenging sounds."""
        }
        
    def _create_prompt_for_session(self, session: ChatSession, user_message: str) -> str:
        """セッションに基づいてプロンプトを作成する"""
        # セッションのレベルとフォーカスに基づいてプロンプトを作成
        level = session.level if session.level in self.system_prompts else "intermediate"
        focus = session.focus if session.focus in self.focus_prompts else "conversation"
        
        system_prompt = f"{self.system_prompts[level]}\n\n{self.focus_prompts[focus]}"
        
        # 過去の会話履歴を含める
        conversation_history = []
        for msg in session.messages:
            role = "user" if msg.role == "user" else "assistant"
            conversation_history.append(f"{role.upper()}: {msg.content}")
        
        # 最新のユーザーメッセージを追加
        conversation_history.append(f"USER: {user_message}")
        
        # 完全なプロンプトを作成
        prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{chr(10).join(conversation_history)}

Now, respond to the user as Emma the English tutor:
"""
        
        return prompt
    
    async def generate_response(self, session: ChatSession, user_message: str) -> str:
        """ユーザーメッセージに対する応答を生成する"""
        
        # セッション用のプロンプトを作成
        prompt = self._create_prompt_for_session(session, user_message)
        
        # 温度設定（レベルによって調整）
        temperature = 0.7 if session.level == "beginner" else 0.5 if session.level == "intermediate" else 0.3
        
        # Geminiモデルを初期化
        model = genai.GenerativeModel(
            model_name=self.default_model,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        
        # 応答を生成
        response = model.generate_content(prompt)
        
        # 応答テキストを返す
        return response.text
    
    def generate_title(self, first_message: str) -> str:
        """最初のメッセージからセッションタイトルを生成する"""
        try:
            # 最新のモデルを使用
            model = genai.GenerativeModel(self.default_model)
            prompt = f"Generate a short, concise title (3-5 words) for an English learning conversation that starts with this message: '{first_message}'. Return ONLY the title without quotes or explanation."
            
            response = model.generate_content(prompt)
            title = response.text.strip()
            
            # タイトルが長すぎる場合は切り詰める
            if len(title) > 50:
                title = title[:47] + "..."
                
            return title
        except Exception as e:
            print(f"Error generating title: {e}")
            # エラーが発生した場合はメッセージの先頭を使用
            if first_message and len(first_message) > 5:
                return first_message[:20] + "..." if len(first_message) > 20 else first_message
            return "New English Conversation"
