"""
Complete RAG pipeline that integrates all components
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from langchain.schema import Document

from .document_processing.docling_mps_converter import DoclingMPSConverter
from .document_processing.document_converter import DocumentToHTMLConverter
from .document_processing.enhanced_docling_converter import EnhancedDoclingConverter
from .document_processing.simple_pdf_converter import SimplePDFConverter
from .document_processing.macos_ocr_converter import MacOSOCRConverter
from .document_processing.html_splitter import HTMLDocumentSplitter
from .embedding.azure_openai_embeddings import AzureOpenAIEmbeddingManager
from .vectorstore.faiss_store import FAISSVectorStore


class RAGPipeline:
    """Complete RAG pipeline for document processing and retrieval"""
    
    def __init__(self, 
                 index_path: Optional[str] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 device: str = "cpu",
                 init_document_converter: bool = True):
        """
        Initialize RAG pipeline
        
        Args:
            index_path: Path to save/load FAISS index
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            device: Device to use ("cpu", "mps", or "macos")
            init_document_converter: Whether to initialize document converter
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.device = device
        
        # Initialize document converter based on device (only if needed)
        if init_document_converter:
            if device == "macos":
                print("🍎 Using macOS native OCR for document processing")
                try:
                    self.document_converter = MacOSOCRConverter()
                except Exception as e:
                    print(f"⚠️  macOS OCR initialization failed, falling back to simple PDF converter: {str(e)}")
                    self.document_converter = SimplePDFConverter()
            elif device == "mps":
                print("🚀 Using MPS acceleration for document processing")
                try:
                    self.document_converter = DoclingMPSConverter(use_mps=True)
                except Exception as e:
                    print(f"⚠️  MPS initialization failed, falling back to simple PDF converter: {str(e)}")
                    self.document_converter = SimplePDFConverter()
            else:
                print("🖥️  Using CPU for document processing with Enhanced Docling")
                try:
                    self.document_converter = EnhancedDoclingConverter(use_ocr=True, lang=['en', 'zh'])
                    print("✅ Enhanced Docling converter initialized successfully")
                except Exception as e:
                    print(f"⚠️  Enhanced Docling initialization failed, trying standard Docling: {str(e)}")
                    try:
                        self.document_converter = DocumentToHTMLConverter()
                        print("✅ Standard Docling DocumentConverter initialized")
                    except Exception as e2:
                        print(f"⚠️  All Docling methods failed, falling back to simple PDF converter: {str(e2)}")
                        print("💡 To fix this, run: ./install_docling_macos_intel.sh")
                        self.document_converter = SimplePDFConverter()
        else:
            self.document_converter = None
            
        self.html_splitter = HTMLDocumentSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_manager = AzureOpenAIEmbeddingManager()
        self.vector_store = FAISSVectorStore(
            embeddings=self.embedding_manager.embeddings,
            index_path=index_path,
            embedding_dimension=self.embedding_manager.get_embedding_dimension()
        )
        
        print("RAG Pipeline initialized successfully")
    
    def process_documents(self, 
                         file_paths: List[str], 
                         output_html_dir: Optional[str] = None) -> List[Document]:
        """
        Process documents from files to vector embeddings
        
        Args:
            file_paths: List of document file paths
            output_html_dir: Directory to save HTML files
            
        Returns:
            List of processed Document objects
        """
        print(f"Processing {len(file_paths)} documents...")
        
        # Step 1: Convert documents to HTML
        print("Step 1: Converting documents to HTML...")
        html_files = self.document_converter.convert_batch(file_paths, output_html_dir)
        
        if not html_files:
            raise ValueError("No documents were successfully converted to HTML")
        
        # Step 2: Split HTML documents into chunks
        print("Step 2: Splitting HTML documents into chunks...")
        all_documents = self.html_splitter.split_multiple_files(html_files)
        
        if not all_documents:
            raise ValueError("No chunks were created from HTML documents")
        
        print(f"Created {len(all_documents)} document chunks")
        return all_documents
    
    def build_vector_index(self, 
                          file_paths: List[str], 
                          output_html_dir: Optional[str] = None,
                          save_index: bool = True) -> None:
        """
        Build vector index from document files
        
        Args:
            file_paths: List of document file paths
            output_html_dir: Directory to save HTML files
            save_index: Whether to save the index to disk
        """
        # Process documents
        documents = self.process_documents(file_paths, output_html_dir)
        
        # Step 3: Create vector index
        print("Step 3: Creating vector index...")
        self.vector_store.create_index(documents)
        
        # Step 4: Save index if requested
        if save_index:
            print("Step 4: Saving vector index...")
            self.vector_store.save_index()
        
        print("Vector index built successfully!")
    
    def add_documents_to_index(self, 
                              file_paths: List[str], 
                              output_html_dir: Optional[str] = None,
                              save_index: bool = True) -> None:
        """
        Add new documents to existing index
        
        Args:
            file_paths: List of document file paths
            output_html_dir: Directory to save HTML files
            save_index: Whether to save the updated index
        """
        # Process new documents
        documents = self.process_documents(file_paths, output_html_dir)
        
        # Add to existing index
        print("Adding documents to existing index...")
        self.vector_store.add_documents(documents)
        
        # Save updated index if requested
        if save_index:
            print("Saving updated index...")
            self.vector_store.save_index()
        
        print("Documents added to index successfully!")
    
    def search_documents(self, 
                        query: str, 
                        k: int = 5,
                        score_threshold: Optional[float] = None,
                        return_scores: bool = False) -> List[Document] | List[Tuple[Document, float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            return_scores: Whether to return scores with documents
            
        Returns:
            List of similar documents or (document, score) tuples
        """
        if return_scores:
            return self.vector_store.similarity_search_with_scores(query, k=k)
        else:
            return self.vector_store.similarity_search(query, k=k, score_threshold=score_threshold)
    
    def load_existing_index(self, index_path: Optional[str] = None) -> None:
        """
        Load existing vector index
        
        Args:
            index_path: Path to load index from
        """
        self.vector_store.load_index(index_path)
        print("Existing index loaded successfully")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats"""
        return ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.html', '.htm', '.png', '.jpg', '.jpeg']
    
    def validate_files(self, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate input files
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Tuple of (valid_files, invalid_files)
        """
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if not path.exists():
                invalid_files.append(f"{file_path} (file not found)")
            elif not self.document_converter.is_supported_format(file_path):
                invalid_files.append(f"{file_path} (unsupported format)")
            else:
                valid_files.append(file_path)
        
        return valid_files, invalid_files
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index"""
        return self.vector_store.get_index_info()
    
    def test_connection(self) -> bool:
        """Test Azure OpenAI connection"""
        return self.embedding_manager.test_connection()