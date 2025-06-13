#!/usr/bin/env python3
"""
RAG POC Main Application
Command-line interface for document processing and vector search
"""

import argparse
import sys
from pathlib import Path
from typing import List
import os

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_poc import RAGPipeline


def setup_argparser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="RAG POC - Document Processing and Vector Search System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build index from documents (CPU mode - default)
  python main.py build -f document1.pdf document2.pptx -o data/output/html

  # Build index with MPS acceleration (macOS only)
  python main.py build -f document1.pdf --device mps

  # Build index with macOS native OCR (best for scanned PDFs/images)
  python main.py build -f document1.pdf --device macos

  # Search in existing index
  python main.py search -q "machine learning concepts" -k 3

  # Add new documents to existing index
  python main.py add -f new_document.docx

  # Test Azure OpenAI connection
  python main.py test-connection
        """
    )
    
    # Add global device argument
    parser.add_argument('--device', choices=['cpu', 'mps', 'macos'], default='cpu',
                       help='Device to use for processing: cpu (default), mps (macOS GPU), or macos (macOS native OCR)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build vector index from documents')
    build_parser.add_argument('-f', '--files', nargs='+', required=True,
                             help='Document files to process')
    build_parser.add_argument('-o', '--output-html-dir', 
                             help='Directory to save HTML files (default: data/output/html)')
    build_parser.add_argument('--index-path',
                             help='Path to save index (default: data/output/faiss_index)')
    build_parser.add_argument('--chunk-size', type=int, default=1000,
                             help='Text chunk size (default: 1000)')
    build_parser.add_argument('--chunk-overlap', type=int, default=200,
                             help='Text chunk overlap (default: 200)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search in vector index')
    search_parser.add_argument('-q', '--query', required=True,
                              help='Search query')
    search_parser.add_argument('-k', '--top-k', type=int, default=5,
                              help='Number of results to return (default: 5)')
    search_parser.add_argument('--index-path',
                              help='Path to load index from (default: data/output/faiss_index)')
    search_parser.add_argument('--show-scores', action='store_true',
                              help='Show similarity scores')
    search_parser.add_argument('--score-threshold', type=float,
                              help='Minimum similarity score threshold')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add documents to existing index')
    add_parser.add_argument('-f', '--files', nargs='+', required=True,
                           help='Document files to add')
    add_parser.add_argument('-o', '--output-html-dir',
                           help='Directory to save HTML files')
    add_parser.add_argument('--index-path',
                           help='Path to existing index (default: data/output/faiss_index)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show index information')
    info_parser.add_argument('--index-path',
                            help='Path to index (default: data/output/faiss_index)')
    
    # Test connection command
    subparsers.add_parser('test-connection', help='Test Azure OpenAI connection')
    
    return parser


def handle_build_command(args) -> None:
    """Handle build command"""
    print("Building vector index...")
    
    # Initialize RAG pipeline
    pipeline = RAGPipeline(
        index_path=args.index_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        device=args.device
    )
    
    # Validate files
    valid_files, invalid_files = pipeline.validate_files(args.files)
    
    if invalid_files:
        print("Invalid files found:")
        for invalid_file in invalid_files:
            print(f"  - {invalid_file}")
        print()
    
    if not valid_files:
        print("No valid files to process!")
        return
    
    print(f"Processing {len(valid_files)} valid files:")
    for file in valid_files:
        print(f"  - {file}")
    print()
    
    try:
        # Build index
        pipeline.build_vector_index(
            file_paths=valid_files,
            output_html_dir=args.output_html_dir
        )
        
        # Show index info
        info = pipeline.get_index_info()
        print(f"Index built successfully!")
        print(f"  - Documents: {info['document_count']}")
        print(f"  - Index path: {info['index_path']}")
        
    except Exception as e:
        print(f"Error building index: {str(e)}")
        sys.exit(1)


def handle_search_command(args) -> None:
    """Handle search command"""
    print(f"Searching for: '{args.query}'")
    
    # Initialize RAG pipeline (no need for document converter in search)
    pipeline = RAGPipeline(index_path=args.index_path, device=args.device, init_document_converter=False)
    
    try:
        # Load existing index
        pipeline.load_existing_index()
        
        # Perform search
        if args.show_scores:
            results = pipeline.search_documents(
                query=args.query,
                k=args.top_k,
                return_scores=True
            )
        else:
            results = pipeline.search_documents(
                query=args.query,
                k=args.top_k,
                score_threshold=args.score_threshold,
                return_scores=False
            )
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            if args.show_scores:
                doc, score = result
                print(f"Result {i} (Score: {score:.4f}):")
            else:
                doc = result
                print(f"Result {i}:")
            
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Chunk: {doc.metadata.get('chunk_id', 'Unknown')} / {doc.metadata.get('total_chunks', 'Unknown')}")
            print(f"Content: {doc.page_content[:300]}...")
            if len(doc.page_content) > 300:
                print("[Content truncated]")
            print("-" * 80)
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        sys.exit(1)


def handle_add_command(args) -> None:
    """Handle add command"""
    print("Adding documents to existing index...")
    
    # Initialize RAG pipeline
    pipeline = RAGPipeline(index_path=args.index_path, device=args.device)
    
    # Load existing index
    try:
        pipeline.load_existing_index()
    except Exception as e:
        print(f"Error loading existing index: {str(e)}")
        print("Make sure to build an index first using the 'build' command.")
        sys.exit(1)
    
    # Validate files
    valid_files, invalid_files = pipeline.validate_files(args.files)
    
    if invalid_files:
        print("Invalid files found:")
        for invalid_file in invalid_files:
            print(f"  - {invalid_file}")
        print()
    
    if not valid_files:
        print("No valid files to add!")
        return
    
    print(f"Adding {len(valid_files)} valid files:")
    for file in valid_files:
        print(f"  - {file}")
    print()
    
    try:
        # Add documents
        pipeline.add_documents_to_index(
            file_paths=valid_files,
            output_html_dir=args.output_html_dir
        )
        
        # Show updated index info
        info = pipeline.get_index_info()
        print(f"Documents added successfully!")
        print(f"  - Total documents: {info['document_count']}")
        
    except Exception as e:
        print(f"Error adding documents: {str(e)}")
        sys.exit(1)


def handle_info_command(args) -> None:
    """Handle info command"""
    # Initialize RAG pipeline
    pipeline = RAGPipeline(index_path=args.index_path, device=args.device)
    
    try:
        # Try to load index
        pipeline.load_existing_index()
        info = pipeline.get_index_info()
        
        print("Index Information:")
        print(f"  - Status: {info['status']}")
        print(f"  - Documents: {info['document_count']}")
        print(f"  - Embedding dimension: {info['embedding_dimension']}")
        print(f"  - Index path: {info['index_path']}")
        
    except Exception as e:
        print(f"No index found at specified path: {str(e)}")


def handle_test_connection_command() -> None:
    """Handle test connection command"""
    print("Testing Azure OpenAI connection...")
    
    try:
        # Initialize RAG pipeline
        pipeline = RAGPipeline()
        
        # Test connection
        if pipeline.test_connection():
            print("✓ Connection successful!")
            print(f"  - Embedding dimension: {pipeline.embedding_manager.get_embedding_dimension()}")
        else:
            print("✗ Connection failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")
        print("\nPlease check your Azure OpenAI configuration:")
        print("  - AZURE_OPENAI_API_KEY")
        print("  - AZURE_OPENAI_ENDPOINT") 
        print("  - AZURE_OPENAI_DEPLOYMENT_NAME")
        sys.exit(1)


def main():
    """Main application entry point"""
    parser = setup_argparser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("Warning: .env file not found. Please create one based on .env.example")
        print()
    
    try:
        if args.command == 'build':
            handle_build_command(args)
        elif args.command == 'search':
            handle_search_command(args)
        elif args.command == 'add':
            handle_add_command(args)
        elif args.command == 'info':
            handle_info_command(args)
        elif args.command == 'test-connection':
            handle_test_connection_command()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()