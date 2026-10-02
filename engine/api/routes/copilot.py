from pydantic import BaseModel
from fastapi import APIRouter
from engine.db import get_db_connection
from engine.rag import PolicyCopilot

router = APIRouter(prefix="/api/copilot", tags=["AI Policy Copilot"])

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def ask_copilot(req: QueryRequest):
    conn = get_db_connection()
    copilot = PolicyCopilot(conn)
    result = copilot.answer_policy_query(req.query)
    return {"status": "success", "result": result}
