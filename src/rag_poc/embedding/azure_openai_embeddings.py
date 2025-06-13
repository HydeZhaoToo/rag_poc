"""
Azure OpenAI embeddings configuration and utilities
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain.schema import Document

# Load environment variables
load_dotenv()


class AzureOpenAIEmbeddingManager:
    """Manage Azure OpenAI embeddings for text vectorization"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 azure_endpoint: Optional[str] = None,
                 api_version: Optional[str] = None,
                 deployment_name: Optional[str] = None):
        """
        Initialize Azure OpenAI embeddings
        
        Args:
            api_key: Azure OpenAI API key
            azure_endpoint: Azure OpenAI endpoint URL
            api_version: API version
            deployment_name: Deployment name for the embedding model
        """
        # Use provided values or get from environment
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "text-embedding-ada-002")
        
        if not all([self.api_key, self.azure_endpoint, self.deployment_name]):
            raise ValueError(
                "Missing required Azure OpenAI configuration. Please set:\n"
                "- AZURE_OPENAI_API_KEY\n"
                "- AZURE_OPENAI_ENDPOINT\n"
                "- AZURE_OPENAI_DEPLOYMENT_NAME"
            )
        
        # Initialize Azure OpenAI embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=self.deployment_name,
            openai_api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
        )
        
        # Embedding dimension for text-embedding-ada-002
        self.embedding_dimension = int(os.getenv("VECTOR_DIMENSION", "1536"))
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
    
    def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """
        Generate embeddings for LangChain documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of embedding vectors
        """
        texts = [doc.page_content for doc in documents]
        return self.embed_documents(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.embedding_dimension
    
    def test_connection(self) -> bool:
        """
        Test the connection to Azure OpenAI
        
        Returns:
            True if connection is successful
        """
        try:
            # Test with a simple text
            test_embedding = self.embed_text("test connection")
            return len(test_embedding) == self.embedding_dimension
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False