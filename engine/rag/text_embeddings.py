import math
import re
import numpy as np
from typing import List, Dict, Any

try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

class SimpleVectorStore:
    def __init__(self):
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.vectors: List[Dict[str, float]] = []
        self.is_indexed = False

    @staticmethod
    def _vectorize(text: str) -> Dict[str, float]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        counts: Dict[str, float] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0.0) + 1.0
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {key: value / norm for key, value in counts.items()}

    def build_index(self, documents: List[str], metadata: List[Dict[str, Any]]) -> None:
        self.documents = documents
        self.metadata = metadata
        if len(documents) == 0:
            return
            
        self.vectors = [self._vectorize(document) for document in documents]
        self.is_indexed = True

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.is_indexed or len(self.documents) == 0:
            return []
            
        query_vec = self._vectorize(query)
        sims = np.array([
            sum(query_vec.get(key, 0.0) * value for key, value in vector.items())
            for vector in self.vectors
        ])
        
        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if sims[idx] > 0.0:
                meta = self.metadata[idx].copy()
                meta["similarity_score"] = float(sims[idx])
                results.append(meta)
                
        return results
