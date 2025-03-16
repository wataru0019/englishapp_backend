from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging

# Import AI service (to be implemented)
# from app.services.ai_service import get_ai_response

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Schema for chat message request
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
# Schema for chat message response
class ChatMessageResponse(BaseModel):
    message: str
    session_id: str
    timestamp: str
    
# Schema for session creation request
class SessionRequest(BaseModel):
    level: str = "intermediate"
    focus: str = "conversation"
    
# Schema for session response
class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    level: str
    focus: str

# In-memory session storage (replace with database in production)
active_sessions = {}

@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_ai(request: ChatMessageRequest):
    try:
        # Get or create session ID
        session_id = request.session_id
        if not session_id or session_id not in active_sessions:
            session_id = str(uuid.uuid4())
            active_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "level": "intermediate",
                "focus": "conversation"
            }
        
        # Store user message
        active_sessions[session_id]["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # TODO: Call actual AI service
        # For now, return a mock response
        # response_text = await get_ai_response(request.message, session_id)
        
        # Mock response based on keywords
        message = request.message.lower()
        if "introduce" in message:
            response_text = "Hello! I'm your English learning assistant. I'm here to help you practice your English conversation skills, correct your grammar, and provide feedback on your language usage. What would you like to practice today?"
        elif "grammar" in message:
            response_text = "I'd be happy to help with your grammar! Try writing a few sentences, and I'll provide corrections and explanations for any errors I find."
        elif "interview" in message:
            response_text = "Preparing for an interview is a great way to practice English! What kind of position are you interviewing for? I can help you with common interview questions and phrases specific to your industry."
        elif "topic" in message or "discuss" in message:
            response_text = "I'd love to discuss a topic with you! Here are some suggestions: current events, technology, travel, culture, food, sports, movies, or books. What topic interests you the most?"
        elif "daily" in message or "conversation" in message:
            response_text = "Let's practice some daily conversation! Imagine we're meeting at a coffee shop. How would you greet me and start a conversation?"
        else:
            response_text = f"Thank you for your message! I understand you said: \"{request.message}\". How can I help you improve your English skills today? We could practice conversation, work on grammar, or discuss any topic you're interested in."
        
        # Store AI response
        active_sessions[session_id]["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatMessageResponse(
            message=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    try:
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        active_sessions[session_id] = {
            "created_at": created_at,
            "messages": [],
            "level": request.level,
            "focus": request.focus
        }
        
        return SessionResponse(
            session_id=session_id,
            created_at=created_at,
            level=request.level,
            focus=request.focus
        )
    
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/topics")
async def get_conversation_topics(category: Optional[str] = None, count: int = 5):
    """Get suggested conversation topics for practice"""
    
    # Sample topics organized by category
    all_topics = {
        "daily_life": [
            "Describe your daily routine",
            "What do you usually eat for breakfast?",
            "How do you commute to work or school?",
            "What are your hobbies and interests?",
            "Describe your hometown or neighborhood"
        ],
        "travel": [
            "Where was your last vacation?",
            "What's your dream travel destination?",
            "Do you prefer beach holidays or city breaks?",
            "What's the most interesting place you've visited?",
            "How do you prepare for international travel?"
        ],
        "technology": [
            "How has technology changed your life?",
            "What social media platforms do you use?",
            "Do you think AI will change how we work?",
            "What new technology are you excited about?",
            "How do you balance screen time and other activities?"
        ],
        "culture": [
            "What's a cultural tradition in your country?",
            "Tell me about a festival you enjoy",
            "What type of music do you listen to?",
            "Have you read any good books lately?",
            "What movies or TV shows do you recommend?"
        ],
        "career": [
            "What do you do for work?",
            "Where do you see yourself in five years?",
            "What skills are important in your field?",
            "How do you handle work-life balance?",
            "Describe your ideal job or workplace"
        ]
    }
    
    # Filter by category if provided
    if category and category in all_topics:
        selected_topics = all_topics[category][:count]
    else:
        # Mix topics from different categories
        selected_topics = []
        categories = list(all_topics.keys())
        for i in range(min(count, 15)):
            cat = categories[i % len(categories)]
            topic_index = i // len(categories)
            if topic_index < len(all_topics[cat]):
                selected_topics.append(all_topics[cat][topic_index])
            if len(selected_topics) >= count:
                break
    
    return {"topics": selected_topics}

@router.get("/grammar/examples")
async def get_grammar_examples(level: str = "intermediate"):
    """Get example sentences for grammar practice"""
    
    examples = {
        "beginner": [
            "I ___ (go) to the store yesterday.",
            "She ___ (work) at the hospital.",
            "They ___ (not/like) spicy food.",
            "He ___ (study) English for two years.",
            "___ (be) you a student?"
        ],
        "intermediate": [
            "If I ___ (have) more time, I would travel more.",
            "She ___ (work) here since 2018.",
            "By the time I arrived, they ___ (leave) already.",
            "I wish I ___ (can) speak five languages.",
            "He asked me what I ___ (do) the next weekend."
        ],
        "advanced": [
            "Had I ___ (know) about the change, I would have adjusted my plans.",
            "Not only ___ (be) he late, but he also forgot the documents.",
            "Seldom ___ (have) I seen such a beautiful sunset.",
            "Should you ___ (need) any assistance, please don't hesitate to ask.",
            "The documentary, which ___ (feature) interviews with survivors, ___ (premiere) next month."
        ]
    }
    
    return {"examples": examples.get(level, examples["intermediate"])}
