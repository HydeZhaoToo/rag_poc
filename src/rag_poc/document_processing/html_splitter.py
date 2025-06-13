"""
HTML document splitter using LangChain's HTML splitter
"""

from typing import List, Optional
from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain.schema import Document
from pathlib import Path


class HTMLDocumentSplitter:
    """Split HTML documents by sections using LangChain's HTML splitter"""
    
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200,
                 headers_to_split_on: Optional[List[tuple]] = None):
        """
        Initialize HTML splitter
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            headers_to_split_on: HTML headers to split on (h1, h2, etc.)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default headers to split on
        if headers_to_split_on is None:
            self.headers_to_split_on = [
                ("h1", "Header 1"),
                ("h2", "Header 2"), 
                ("h3", "Header 3"),
                ("h4", "Header 4"),
                ("h5", "Header 5"),
                ("h6", "Header 6"),
            ]
        else:
            self.headers_to_split_on = headers_to_split_on
        
        # Initialize the HTML splitter
        self.html_splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
    
    def split_html_file(self, html_file_path: str) -> List[Document]:
        """
        Split HTML file into chunks
        
        Args:
            html_file_path: Path to HTML file
            
        Returns:
            List of Document objects
        """
        html_path = Path(html_file_path)
        
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file_path}")
        
        # Read HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Split HTML content
        html_docs = self.html_splitter.split_text(html_content)
        
        # Add metadata to documents
        for i, doc in enumerate(html_docs):
            doc.metadata.update({
                'source': str(html_path),
                'chunk_id': i,
                'total_chunks': len(html_docs)
            })
        
        return html_docs
    
    def split_html_content(self, html_content: str, source_name: str = "unknown") -> List[Document]:
        """
        Split HTML content directly
        
        Args:
            html_content: HTML content string
            source_name: Name of the source document
            
        Returns:
            List of Document objects
        """
        # Split HTML content
        html_docs = self.html_splitter.split_text(html_content)
        
        # Add metadata to documents
        for i, doc in enumerate(html_docs):
            doc.metadata.update({
                'source': source_name,
                'chunk_id': i,
                'total_chunks': len(html_docs)
            })
        
        return html_docs
    
    def split_multiple_files(self, html_file_paths: List[str]) -> List[Document]:
        """
        Split multiple HTML files
        
        Args:
            html_file_paths: List of HTML file paths
            
        Returns:
            List of all Document objects from all files
        """
        all_docs = []
        
        for html_file_path in html_file_paths:
            try:
                docs = self.split_html_file(html_file_path)
                all_docs.extend(docs)
                print(f"Split {html_file_path} into {len(docs)} chunks")
            except Exception as e:
                print(f"Error splitting {html_file_path}: {str(e)}")
                continue
        
        return all_docs