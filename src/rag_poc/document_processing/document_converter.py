"""
Document converter using Docling to convert various formats to HTML
"""

import os
from pathlib import Path
from typing import Optional, List
from docling.document_converter import DocumentConverter


class DocumentToHTMLConverter:
    """Convert documents (PPT, PDF, DOC, etc.) to HTML using Docling"""
    
    def __init__(self):
        self.converter = DocumentConverter()
        self.supported_formats = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
            '.html', '.htm', '.png', '.jpg', '.jpeg'
        ]
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a single file to HTML
        
        Args:
            file_path: Path to the input file
            output_dir: Output directory (optional, defaults to same dir as input)
            
        Returns:
            Path to the generated HTML file
        """
        input_path = Path(file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        # Set output directory
        if output_dir is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert document
        result = self.converter.convert(input_path)
        
        # Generate HTML content
        html_content = result.document.export_to_html()
        
        # Save HTML file
        output_file = output_dir / f"{input_path.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def convert_batch(self, file_paths: List[str], output_dir: Optional[str] = None) -> List[str]:
        """
        Convert multiple files to HTML
        
        Args:
            file_paths: List of input file paths
            output_dir: Output directory
            
        Returns:
            List of generated HTML file paths
        """
        html_files = []
        
        for file_path in file_paths:
            try:
                html_file = self.convert_file(file_path, output_dir)
                html_files.append(html_file)
                print(f"Converted: {file_path} -> {html_file}")
            except Exception as e:
                print(f"Error converting {file_path}: {str(e)}")
                continue
        
        return html_files
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats