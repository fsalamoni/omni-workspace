import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid
import numpy as np

# We lazy load sentence_transformers to avoid huge startup times if memory isn't used
_embedding_model = None

def get_embedding_model(model_name: str):
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model

class Memory(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    session_id: str
    timestamp: str

class AgentDB:
    """Numpy-based vector memory (fallback for Windows without C++ build tools)."""
    
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2", m: int = 16, ef_construction: int = 200):
        self.db_path = db_path
        self.model_name = model_name
        self.dim = 384  # Dimension for all-MiniLM-L6-v2
        
        os.makedirs(self.db_path, exist_ok=True)
        self.meta_path = os.path.join(self.db_path, "memory_meta.json")
        self.vectors_path = os.path.join(self.db_path, "memory_vectors.npy")
        
        # Meta store: list of dicts mapping to int ids
        self.meta_store: Dict[int, Memory] = {}
        self.vectors: List[np.ndarray] = []
        self._next_id = 0
        
        self._load()

    def _load(self):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.meta_store = {int(k): Memory(**v) for k, v in data.items()}
                self._next_id = max(self.meta_store.keys()) + 1 if self.meta_store else 0
                
        if os.path.exists(self.vectors_path):
            self.vectors = list(np.load(self.vectors_path))

    def _save(self):
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v.model_dump() for k, v in self.meta_store.items()}, f)
        if self.vectors:
            np.save(self.vectors_path, np.array(self.vectors))

    async def store(self, text: str, metadata: Dict[str, Any], session_id: str) -> str:
        model = get_embedding_model(self.model_name)
        embedding = model.encode([text])[0]
        
        mem_id = str(uuid.uuid4())
        memory = Memory(
            id=mem_id,
            text=text,
            metadata=metadata,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        idx = self._next_id
        self._next_id += 1
        
        self.vectors.append(embedding)
        self.meta_store[idx] = memory
        
        self._save()
        return mem_id

    async def recall(self, query: str, top_k: int = 5, session_id: Optional[str] = None) -> List[Memory]:
        if len(self.meta_store) == 0 or len(self.vectors) == 0:
            return []
            
        model = get_embedding_model(self.model_name)
        query_emb = model.encode([query])[0]
        
        # Cosine similarity
        A = np.array(self.vectors)
        B = query_emb
        scores = np.dot(A, B) / (np.linalg.norm(A, axis=1) * np.linalg.norm(B))
        
        # Get top K indices
        k = min(top_k * 2, len(self.vectors))
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            memory = self.meta_store.get(int(idx))
            if memory:
                if session_id and memory.session_id != session_id:
                    continue
                results.append(memory)
                if len(results) >= top_k:
                    break
                
        return results

import uuid
