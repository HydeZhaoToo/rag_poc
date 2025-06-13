#!/usr/bin/env python3
"""
Simple test script for Azure OpenAI connection without docling
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

load_dotenv()

def test_azure_openai():
    """Test Azure OpenAI connection directly"""
    try:
        from rag_poc.embedding.azure_openai_embeddings import AzureOpenAIEmbeddingManager
        
        print("Testing Azure OpenAI connection...")
        print(f"API Key: {os.getenv('AZURE_OPENAI_API_KEY')[:20]}...")
        print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
        
        # Initialize embedding manager
        embedding_manager = AzureOpenAIEmbeddingManager()
        
        # Test connection
        if embedding_manager.test_connection():
            print("✅ Connection successful!")
            print(f"Embedding dimension: {embedding_manager.get_embedding_dimension()}")
            
            # Test embedding generation
            test_text = "This is a test sentence for embedding."
            embedding = embedding_manager.embed_text(test_text)
            print(f"Generated embedding vector length: {len(embedding)}")
            print("✅ Embedding generation successful!")
            
        else:
            print("❌ Connection failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_azure_openai()