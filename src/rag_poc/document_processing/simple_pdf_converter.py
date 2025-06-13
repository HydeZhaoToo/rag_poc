"""
Simple PDF converter using PyPDF2 for text extraction without OCR
"""

import os
from pathlib import Path
from typing import Optional, List
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class SimplePDFConverter:
    """Simple PDF to text converter without OCR"""
    
    def __init__(self):
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")
        self.supported_formats = ['.pdf']
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a PDF file to HTML
        
        Args:
            file_path: Path to the input PDF file
            output_dir: Output directory (optional, defaults to same dir as input)
            
        Returns:
            Path to the generated HTML file
        """
        input_path = Path(file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        if input_path.suffix.lower() != '.pdf':
            raise ValueError(f"Only PDF files are supported, got: {file_path}")
        
        # Set output directory
        if output_dir is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract text from PDF
        text_content = self._extract_text_from_pdf(input_path)
        
        # Convert to simple HTML
        html_content = self._text_to_html(text_content, input_path.stem)
        
        # Save HTML file
        output_file = output_dir / f"{input_path.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyPDF2"""
        text_content = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content += f"\n\n=== Page {page_num + 1} ===\n\n"
                        text_content += page_text
                        
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
        
        return text_content
    
    def _text_to_html(self, text: str, title: str) -> str:
        """Convert text to simple HTML with basic structure"""
        
        # Split text into sections based on page breaks
        sections = text.split("=== Page")
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<meta charset='utf-8'>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>"
        ]
        
        for i, section in enumerate(sections):
            if section.strip():
                if i == 0:
                    # First section (before any page break)
                    if section.strip():
                        html_parts.append(f"<div class='content'>{self._format_paragraphs(section.strip())}</div>")
                else:
                    # Page sections
                    page_content = section.split("===")[1] if "===" in section else section
                    if page_content.strip():
                        page_num = section.split("===")[0].strip() if "===" in section else f"Page {i}"
                        html_parts.append(f"<h2>{page_num}</h2>")
                        html_parts.append(f"<div class='page-content'>{self._format_paragraphs(page_content.strip())}</div>")
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _format_paragraphs(self, text: str) -> str:
        """Format text into HTML paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        html_paragraphs = []
        
        for para in paragraphs:
            # Clean up line breaks within paragraphs
            clean_para = ' '.join(line.strip() for line in para.split('\n') if line.strip())
            if clean_para:
                html_paragraphs.append(f"<p>{clean_para}</p>")
        
        return "\n".join(html_paragraphs)
    
    def convert_batch(self, file_paths: List[str], output_dir: Optional[str] = None) -> List[str]:
        """
        Convert multiple PDF files to HTML
        
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
    
    def convert_to_html(self, file_path: str) -> str:
        """
        Convert PDF file to HTML content (without saving to file)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            HTML content as string
        """
        if not self.is_supported_format(file_path):
            raise ValueError(f"File format not supported: {file_path}")
        
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Extract text from PDF
        text_content = self._extract_text_from_pdf(pdf_path)
        
        # Convert to HTML
        html_content = self._text_to_html(text_content, pdf_path.stem)
        
        return html_content