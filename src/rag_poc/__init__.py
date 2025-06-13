"""
RAG POC - Document Processing and Vector Search System
"""

from .rag_pipeline import RAGPipeline
from .document_processing.document_converter import DocumentToHTMLConverter
from .document_processing.html_splitter import HTMLDocumentSplitter
from .embedding.azure_openai_embeddings import AzureOpenAIEmbeddingManager
from .vectorstore.faiss_store import FAISSVectorStore

__version__ = "0.1.0"
__all__ = [
    "RAGPipeline",
    "DocumentToHTMLConverter", 
    "HTMLDocumentSplitter",
    "AzureOpenAIEmbeddingManager",
    "FAISSVectorStore"
]