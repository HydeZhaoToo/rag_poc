"""
FAISS vector store implementation for document storage and retrieval
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import faiss
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings


class FAISSVectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self, 
                 embeddings: Embeddings,
                 index_path: Optional[str] = None,
                 embedding_dimension: int = 1536):
        """
        Initialize FAISS vector store
        
        Args:
            embeddings: Embedding model instance
            index_path: Path to save/load FAISS index
            embedding_dimension: Dimension of embedding vectors
        """
        self.embeddings = embeddings
        self.embedding_dimension = embedding_dimension
        self.index_path = index_path or "data/output/faiss_index"
        
        # Initialize FAISS vector store
        self.vectorstore: Optional[FAISS] = None
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
    
    def create_index(self, documents: List[Document]) -> None:
        """
        Create FAISS index from documents
        
        Args:
            documents: List of Document objects to index
        """
        if not documents:
            raise ValueError("No documents provided for indexing")
        
        print(f"Creating FAISS index from {len(documents)} documents...")
        
        # Create FAISS vector store from documents
        self.vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        print("FAISS index created successfully")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing index
        
        Args:
            documents: List of Document objects to add
        """
        if not documents:
            return
        
        if self.vectorstore is None:
            self.create_index(documents)
        else:
            print(f"Adding {len(documents)} documents to existing index...")
            self.vectorstore.add_documents(documents)
            print("Documents added successfully")
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 5,
                         score_threshold: Optional[float] = None) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of similar documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Create or load an index first.")
        
        if score_threshold is not None:
            # Use similarity search with score threshold
            docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            return [doc for doc, score in docs_and_scores if score >= score_threshold]
        else:
            return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_scores(self, 
                                    query: str, 
                                    k: int = 5) -> List[Tuple[Document, float]]:
        """
        Perform similarity search with scores
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Create or load an index first.")
        
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def save_index(self, path: Optional[str] = None) -> None:
        """
        Save FAISS index to disk
        
        Args:
            path: Path to save index (optional, uses default if not provided)
        """
        if self.vectorstore is None:
            raise ValueError("No vector store to save")
        
        save_path = path or self.index_path
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"Saving FAISS index to {save_path}...")
        self.vectorstore.save_local(save_path)
        print("Index saved successfully")
    
    def load_index(self, path: Optional[str] = None) -> None:
        """
        Load FAISS index from disk
        
        Args:
            path: Path to load index from (optional, uses default if not provided)
        """
        load_path = path or self.index_path
        
        # Check for both possible file structures
        if not (os.path.exists(f"{load_path}.faiss") or 
                os.path.exists(os.path.join(load_path, "index.faiss"))):
            raise FileNotFoundError(f"FAISS index not found at {load_path}")
        
        print(f"Loading FAISS index from {load_path}...")
        self.vectorstore = FAISS.load_local(
            load_path, 
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("Index loaded successfully")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the index"""
        if self.vectorstore is None:
            return 0
        return self.vectorstore.index.ntotal
    
    def delete_index(self, path: Optional[str] = None) -> None:
        """
        Delete FAISS index files
        
        Args:
            path: Path to index files (optional, uses default if not provided)
        """
        delete_path = path or self.index_path
        
        # Delete FAISS index files
        for ext in ['.faiss', '.pkl']:
            file_path = f"{delete_path}{ext}"
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
        
        self.vectorstore = None
        print("Index deleted successfully")
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index"""
        if self.vectorstore is None:
            return {"status": "No index loaded", "document_count": 0}
        
        return {
            "status": "Index loaded",
            "document_count": self.get_document_count(),
            "embedding_dimension": self.embedding_dimension,
            "index_path": self.index_path
        }