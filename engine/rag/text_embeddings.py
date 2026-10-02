import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

class SimpleVectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.is_indexed = False

    def build_index(self, documents: List[str], metadata: List[Dict[str, Any]]) -> None:
        self.documents = documents
        self.metadata = metadata
        if len(documents) == 0:
            return
            
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        self.is_indexed = True

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.is_indexed or len(self.documents) == 0:
            return []
            
        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        
        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if sims[idx] > 0.0:
                meta = self.metadata[idx].copy()
                meta["similarity_score"] = float(sims[idx])
                results.append(meta)
                
        return results
