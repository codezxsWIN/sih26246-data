import json
import sqlite3
import requests
import hashlib
import time
from collections import OrderedDict
from typing import Dict, Any, List, Optional
from engine.config import settings
from engine.db.connection import get_db_connection
from engine.db.repositories import GapRepository, ForecastRepository, PolicyRepository
from engine.rag.text_embeddings import SimpleVectorStore

class LRUCache:
    """Simple in-memory LRU cache with TTL for chat queries."""
    def __init__(self, maxsize: int = 256, ttl: int = 1800):
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache = OrderedDict()

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:16]

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        k = self._key(query)
        if k in self._cache:
            entry = self._cache[k]
            if time.time() - entry["ts"] < self.ttl:
                self._cache.move_to_end(k)
                return entry["value"]
            else:
                del self._cache[k]
        return None

    def put(self, query: str, value: Dict[str, Any]) -> None:
        k = self._key(query)
        self._cache[k] = {"value": value, "ts": time.time()}
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)

_copilot_cache = LRUCache(maxsize=256, ttl=1800)

class PolicyCopilot:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_db_connection()
        self.gap_repo = GapRepository(self.conn)
        self.forecast_repo = ForecastRepository(self.conn)
        self.policy_repo = PolicyRepository(self.conn)
        self.vector_store = SimpleVectorStore()
        self._initialize_vector_store()

    def _initialize_vector_store(self) -> None:
        interventions = self.policy_repo.get_interventions(limit=200)
        docs = [f"{i['trigger_rule_id']} {i['recommended_intervention']} for {i['target_occupation']} in {i['target_state']}" for i in interventions]
        self.vector_store.build_index(docs, interventions)

    def answer_chat_query(self, query_text: str) -> Dict[str, Any]:
        cached_result = _copilot_cache.get(query_text)
        if cached_result:
            result = dict(cached_result)
            result["cached"] = True
            return result

        result = self.answer_policy_query(query_text)
        result["cached"] = False
        _copilot_cache.put(query_text, result)
        return result

    def answer_policy_query(self, query_text: str) -> Dict[str, Any]:
        # 1. Fetch relevant database metrics
        gaps = self.gap_repo.get_gaps(limit=10)
        interventions = self.policy_repo.get_interventions(limit=5)
        
        # 2. Search vector store for relevant context
        relevant_docs = self.vector_store.search(query_text, top_k=3)

        # 3. Build verified grounding context
        top_critical = [g for g in gaps if g["shortage_risk_category"] == "Critical Shortage"]
        
        context_str = "VERIFIED LABOUR ENGINE DATABASE FACTS:\n"
        if top_critical:
            context_str += f"- Top Critical Shortage Role: {top_critical[0]['entity_name']} in {top_critical[0]['geography_name']} (Demand Score: {top_critical[0]['demand_score']}, Gap Score: {top_critical[0]['gap_score']})\n"
        
        if interventions:
            context_str += f"- Recommended Intervention: {interventions[0]['recommended_intervention']} (Priority: {interventions[0]['priority_level']}, Est Cost: {interventions[0]['cost_impact_estimate']})\n"

        # 4. Attempt Ollama Qwen2.5 1.5B Generation with strict guardrail prompt
        answer_text = ""
        used_llm = False
        try:
            prompt = (
                f"System: You are the LMI Engine Policy Assistant — a chatbot embedded in the "
                f"AI-Powered Labour Market Intelligence Engine for the Ministry of Skill Development.\n"
                f"STRICT RULES:\n"
                f"1. ONLY answer questions about labour market demand, supply, gap analysis, shortage risks, "
                f"policies (PMKVY, NAPS, DGT ITI), portal navigation, job seeker advice, or employer hiring.\n"
                f"2. For questions outside these topics, refuse politely.\n"
                f"3. Keep answers concise (3-5 sentences).\n\n"
                f"Verified Database Context:\n{context_str}\n\n"
                f"User Question: {query_text}\nAnswer:"
            )
            resp = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": settings.OLLAMA_LLM_MODEL, "prompt": prompt, "stream": False},
                timeout=3
            )
            if resp.status_code == 200:
                answer_text = resp.json().get("response", "")
                used_llm = True
        except Exception:
            used_llm = False

        # Fallback deterministic answer if Ollama is not running locally
        if not answer_text:
            answer_text = (
                f"**Policy Executive Summary:**\n"
                f"Based on real-time data from the Labour Intelligence Engine:\n\n"
                f"1. **Shortage Assessment**: High demand recorded for **{gaps[0]['entity_name']}** in **{gaps[0]['geography_name']}** with a Demand Score of **{gaps[0]['demand_score']}** and a Shortage Risk category of **{gaps[0]['shortage_risk_category']}**.\n"
                f"2. **Strategic Policy Intervention**: Recommend expanding PMKVY/DGT ITI capacity and launching targeted NAPS/NATS apprenticeship drives.\n"
                f"3. **Estimated Budgetary Requirement**: {interventions[0]['cost_impact_estimate'] if interventions else '₹4.5 Cr State Budget Allocation'}."
            )

        return {
            "query": query_text,
            "answer": answer_text,
            "used_llm": used_llm,
            "grounding_facts": [
                {
                    "entity": gaps[0]['entity_name'] if gaps else "Software Developer",
                    "geography": gaps[0]['geography_name'] if gaps else "All India",
                    "demand_score": gaps[0]['demand_score'] if gaps else 75.0,
                    "shortage_risk": gaps[0]['shortage_risk_category'] if gaps else "Critical Shortage"
                }
            ],
            "relevant_interventions": relevant_docs
        }

