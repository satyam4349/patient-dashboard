from typing import List, Optional
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = None
        self.is_available = False
        self._initialize_embedding_model()

    def _initialize_embedding_model(self):
        """Safely initialize the embedding model with fallback options."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.is_available = True
            logger.info("Embedding model initialized successfully")
        except ImportError as e:
            logger.warning(f"Could not initialize embedding model: {e}")
            logger.warning("System will fall back to non-embedding mode")
            self.is_available = False
        except Exception as e:
            logger.error(f"Unexpected error initializing embedding model: {e}")
            self.is_available = False

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Safely get embedding for text with fallback."""
        if not self.is_available or not self.model:
            return None
        
        try:
            embedding = self.model.encode([text], convert_to_numpy=True)[0]
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def find_similar_entries(self, 
                           query_embedding: np.ndarray, 
                           entry_embeddings: List[np.ndarray], 
                           top_k: int = 3) -> List[int]:
        """Find indices of most similar entries."""
        if not entry_embeddings:
            return []
        
        try:
            similarities = [
                self.compute_similarity(query_embedding, entry_embedding)
                for entry_embedding in entry_embeddings
            ]
            return sorted(
                range(len(similarities)), 
                key=lambda i: similarities[i], 
                reverse=True
            )[:top_k]
        except Exception as e:
            logger.error(f"Error finding similar entries: {e}")
            return list(range(min(top_k, len(entry_embeddings))))
