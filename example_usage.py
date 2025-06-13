#!/usr/bin/env python3
"""
Example usage of the RAG POC system
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_poc import RAGPipeline


def example_usage():
    """Demonstrate basic usage of the RAG system"""
    
    print("RAG POC Example Usage")
    print("=" * 50)
    
    # Initialize the RAG pipeline
    print("1. Initializing RAG pipeline...")
    pipeline = RAGPipeline(
        index_path="data/output/example_index",
        chunk_size=800,
        chunk_overlap=100
    )
    
    # Test connection
    print("2. Testing Azure OpenAI connection...")
    if not pipeline.test_connection():
        print("❌ Connection failed! Please check your .env configuration.")
        return
    print("✅ Connection successful!")
    
    # Example document files (replace with your actual files)
    example_files = [
        "data/input/example_document.pdf",  # Replace with actual file
        # "data/input/presentation.pptx",   # Add more files as needed
        # "data/input/report.docx",
    ]
    
    # Check if example files exist
    existing_files = [f for f in example_files if Path(f).exists()]
    
    if not existing_files:
        print("3. No example files found. Please add some documents to data/input/")
        print("   Supported formats: PDF, DOCX, PPTX, HTML, images")
        print("   Example files should be placed in:")
        for file in example_files:
            print(f"   - {file}")
        return
    
    print(f"3. Found {len(existing_files)} example files:")
    for file in existing_files:
        print(f"   - {file}")
    
    try:
        # Build vector index
        print("4. Building vector index...")
        pipeline.build_vector_index(
            file_paths=existing_files,
            output_html_dir="data/output/html"
        )
        
        # Show index info
        info = pipeline.get_index_info()
        print(f"✅ Index built successfully!")
        print(f"   - Documents indexed: {info['document_count']}")
        
        # Example searches
        example_queries = [
            "What is machine learning?",
            "How does artificial intelligence work?", 
            "Explain the main concepts",
            "What are the key findings?"
        ]
        
        print("5. Performing example searches...")
        for query in example_queries:
            print(f"\n🔍 Query: '{query}'")
            
            results = pipeline.search_documents(
                query=query,
                k=3,
                return_scores=True
            )
            
            if results:
                for i, (doc, score) in enumerate(results, 1):
                    print(f"   Result {i} (Score: {score:.3f}):")
                    print(f"   Source: {Path(doc.metadata.get('source', 'Unknown')).name}")
                    print(f"   Content: {doc.page_content[:150]}...")
                    print()
            else:
                print("   No results found.")
        
        print("✅ Example completed successfully!")
        print("\nNext steps:")
        print("- Add your own documents to data/input/")
        print("- Use main.py for command-line interface")
        print("- Customize the pipeline for your specific needs")
        
    except Exception as e:
        print(f"❌ Error during example: {str(e)}")
        return


if __name__ == "__main__":
    example_usage()