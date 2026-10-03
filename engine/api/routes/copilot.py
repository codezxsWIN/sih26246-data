from pydantic import BaseModel
from fastapi import APIRouter, Request
from engine.db import get_db_connection
from engine.rag import PolicyCopilot

router = APIRouter(prefix="/api/copilot", tags=["AI Policy Copilot"])

class QueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""

@router.post("/query")
def ask_copilot(req: QueryRequest):
    conn = get_db_connection()
    copilot = PolicyCopilot(conn)
    result = copilot.answer_policy_query(req.query)
    return {"status": "success", "result": result}

@router.post("/chat")
def chatbot_query(req: ChatRequest, request: Request):
    from engine.api.middleware.rate_limit import chatbot_limiter
    from engine.rag.topic_guard import is_on_topic
    from engine.rag.nav_helper import get_nav_hints

    # 1. Rate limit check
    chatbot_limiter.check(request)

    # 2. Topic guard check
    allowed, reason = is_on_topic(req.message)
    if not allowed:
        return {
            "status": "blocked",
            "answer": "I can only assist with labour market intelligence, job market data, policies, and portal navigation. Please ask something related to the LMI Engine.",
            "nav_hints": [],
            "used_llm": False,
            "cached": False
        }

    # 3. Check cache / query LLM/fallback
    conn = get_db_connection()
    copilot = PolicyCopilot(conn)
    result = copilot.answer_chat_query(req.message)

    # 4. Nav hints
    nav_hints = get_nav_hints(req.message)

    return {
        "status": "success",
        "answer": result["answer"],
        "used_llm": result.get("used_llm", False),
        "grounding_facts": result.get("grounding_facts", []),
        "nav_hints": nav_hints,
        "cached": result.get("cached", False)
    }

