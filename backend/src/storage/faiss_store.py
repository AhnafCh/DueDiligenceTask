"""FAISS Vector Store Wrapper."""
import logging
import os
import pickle
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import faiss

from src.utils.config import get_settings

logger = logging.getLogger(__name__)


class FAISSStore:
    """
    Wrapper around FAISS index for vector similarity search.
    Supports saving/loading indices and ID mapping.
    """
    
    def __init__(self, index_name: str, dimension: int = 768):
        """
        Initialize FAISS store.
        
        Args:
            index_name: Name of the index (e.g., 'semantic', 'citation')
            dimension: Vector dimension (default 768 for Google embeddings)
        """
        self.settings = get_settings()
        self.index_name = index_name
        self.dimension = dimension
        self.index_dir = Path(self.settings.index_dir)
        self.index_path = self.index_dir / f"{index_name}.index"
        self.mapping_path = self.index_dir / f"{index_name}_mapping.pkl"
        
        # Ensure index directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize index and ID mapping
        self.index = None
        self.id_map: Dict[int, str] = {}  # FAISS integer ID -> String ID (chunk_id)
        self.reverse_id_map: Dict[str, int] = {}  # String ID -> FAISS integer ID
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if self.index_path.exists() and self.mapping_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.mapping_path, 'rb') as f:
                    self.id_map = pickle.load(f)
                    
                # Rebuild reverse map
                self.reverse_id_map = {v: k for k, v in self.id_map.items()}
                
                logger.info(f"Loaded FAISS index '{self.index_name}' with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load index '{self.index_name}': {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        # Using IndexFlatL2 for exact search (can be optimized for large datasets)
        # IDMap allows mapping arbitrary integer IDs, but we manage our own mapping
        # to support string IDs (UUIDs)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = {}
        self.reverse_id_map = {}
        logger.info(f"Created new FAISS index '{self.index_name}'")

    def save(self):
        """Save index and mapping to disk."""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.mapping_path, 'wb') as f:
                pickle.dump(self.id_map, f)
            logger.info(f"Saved FAISS index '{self.index_name}' to disk")
        except Exception as e:
            logger.error(f"Failed to save index '{self.index_name}': {e}")
            raise IOError(f"Failed to save FAISS index: {e}")

    def add_vectors(self, vectors: List[List[float]], ids: List[str]):
        """
        Add vectors to the index.
        
        Args:
            vectors: List of embedding vectors
            ids: List of corresponding string IDs (chunk IDs)
        """
        if len(vectors) != len(ids):
            raise ValueError("Number of vectors and IDs must match")
        
        if not vectors:
            return

        # Convert to numpy array
        vectors_np = np.array(vectors).astype('float32')
        
        # Determine next integer IDs
        start_id = 0
        if self.id_map:
            start_id = max(self.id_map.keys()) + 1
            
        new_ids = list(range(start_id, start_id + len(ids)))
        
        # Add to index
        self.index.add(vectors_np)
        
        # Update mappings
        for int_id, str_id in zip(new_ids, ids):
            self.id_map[int_id] = str_id
            self.reverse_id_map[str_id] = int_id
            
        # Serialize immediately for persistence
        self.save()
        logger.debug(f"Added {len(vectors)} vectors to index '{self.index_name}'")

    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[str], List[float]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            Tuple of (List of IDs, List of distances)
        """
        if self.index.ntotal == 0:
            return [], []
            
        # Convert to numpy array
        query_np = np.array([query_vector]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_np, k)
        
        # Map back to string IDs
        result_ids = []
        result_distances = []
        
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1 and idx in self.id_map:
                result_ids.append(self.id_map[idx])
                result_distances.append(float(dist))
                
        return result_ids, result_distances

    def delete_ids(self, ids: List[str]):
        """
        Delete vectors by their string IDs.
        Note: FAISS IndexFlatL2 doesn't support direct deletion efficiently.
        For simplicity in this phase, we might need to rebuild or use IDSelector if supported.
        Standard FAISS remove_ids requires and IDMap index or specific index types.
        
        Current approach: 
        Rebuilding is safest for FlatL2 without IDMap wrapper, but slow.
        Let's assume we can rebuild for now or implement a soft delete if needed.
        
        Better approach for Phase 2:
        Load vectors, remove target ones, create new index.
        """
        # TODO: Implement robust deletion. 
        # For now, we'll log a warning that deletion requires index rebuild pattern
        # or switching to IndexIDMap.
        logger.warning("Delete operation called on FAISS store. Current implementation pending IndexIDMap upgrade.")
        pass

    def clear(self):
        """Clear the entire index."""
        self._create_new_index()
        self.save()
