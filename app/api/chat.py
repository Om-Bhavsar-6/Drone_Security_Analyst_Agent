from fastapi import APIRouter
from app.models.query import ChatRequest, ChatResponse
from app.agent.assistant import security_assistant

router = APIRouter(tags=["Security Analyst Agent"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_analyst(payload: ChatRequest):
    """
    Conversational Security Analyst Agent.
    Interprets user operational queries, selects appropriate forensic tools,
    inspects cross-frame events, and answers contextual security questions.
    """
    return security_assistant.process_query(payload)

@router.post("/chat-bonus", response_model=ChatResponse)
def chat_bonus_alias(payload: ChatRequest):
    """Backwards-compatible endpoint for FlytBase bonus requirement."""
    return security_assistant.process_query(payload)
