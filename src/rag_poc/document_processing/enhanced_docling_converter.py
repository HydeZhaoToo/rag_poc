"""
Enhanced Docling converter with SSL and network issue handling for macOS Intel x86_64
优化的 Docling 转换器，针对 macOS Intel x86_64 处理 SSL 和网络问题
"""

import os
import ssl
import sys
from pathlib import Path
from typing import Optional, List
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Configure SSL to handle certificate issues
try:
    # Disable SSL certificate verification for model downloads
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
except Exception:
    pass

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions
    DOCLING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Docling not available: {e}")
    DOCLING_AVAILABLE = False

# Fallback to PyPDF2 if Docling fails
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class EnhancedDoclingConverter:
    """Enhanced Docling converter with fallback mechanisms"""
    
    def __init__(self, use_ocr: bool = True, lang: List[str] = None):
        """
        Initialize enhanced Docling converter
        
        Args:
            use_ocr: Whether to use OCR (may require network)
            lang: Languages for OCR (default: ['en', 'zh'])
        """
        self.use_ocr = use_ocr
        self.lang = lang or ['en', 'zh']
        self.supported_formats = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
            '.html', '.htm', '.png', '.jpg', '.jpeg'
        ]
        
        # Configure environment for network issues
        self._configure_environment()
        
        # Initialize converter with retry mechanism
        self.converter = self._initialize_converter()
        
        print(f"✅ Enhanced Docling converter initialized")
        print(f"   OCR enabled: {self.use_ocr}")
        print(f"   Languages: {self.lang}")
    
    def _configure_environment(self):
        """Configure environment variables for network issues"""
        
        # Set proxy environment if needed (uncomment if behind proxy)
        # os.environ['http_proxy'] = 'your-proxy-here'
        # os.environ['https_proxy'] = 'your-proxy-here'
        
        # Disable SSL verification for model downloads
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        # Set user agent to avoid blocking
        os.environ['USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        
        print("🔧 Environment configured for network issues")
    
    def _initialize_converter(self) -> Optional[DocumentConverter]:
        """Initialize DocumentConverter with error handling"""
        
        if not DOCLING_AVAILABLE:
            print("❌ Docling not available, will use fallback methods")
            return None
        
        try:
            print("🔄 Initializing Docling DocumentConverter...")
            
            if self.use_ocr:
                # Configure OCR options (remove unsupported parameters)
                ocr_options = EasyOcrOptions(
                    lang=self.lang,
                    use_gpu=False,  # Use CPU for stability on Intel Macs
                    download_enabled=True
                )
                
                # Create pipeline options
                pipeline_options = PipelineOptions(
                    do_ocr=True,
                    do_table_structure=True,
                    ocr_options=ocr_options
                )
                
                converter = DocumentConverter(pipeline_options=pipeline_options)
            else:
                # No OCR, faster processing
                converter = DocumentConverter()
            
            print("✅ DocumentConverter initialized successfully")
            return converter
            
        except Exception as e:
            print(f"⚠️  DocumentConverter initialization failed: {str(e)}")
            
            # Try without OCR as fallback
            if self.use_ocr:
                print("🔄 Retrying without OCR...")
                try:
                    converter = DocumentConverter()
                    print("✅ DocumentConverter initialized without OCR")
                    self.use_ocr = False
                    return converter
                except Exception as e2:
                    print(f"❌ Complete DocumentConverter failure: {str(e2)}")
            
            return None
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Fallback: Extract text using PyPDF2"""
        
        if not PYPDF2_AVAILABLE:
            raise RuntimeError("Neither Docling nor PyPDF2 available")
        
        print("🔄 Using PyPDF2 fallback for text extraction...")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text().strip()
                    if text:
                        text_content.append(f"<h2>Page {page_num}</h2>\n<div class='page-content'><p>{text}</p></div>")
                
                if text_content:
                    return "\n".join(text_content)
                else:
                    raise RuntimeError("No text extracted from PDF")
                    
        except Exception as e:
            raise RuntimeError(f"PyPDF2 extraction failed: {e}")
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a single file to HTML
        
        Args:
            file_path: Path to the input file
            output_dir: Output directory (optional)
            
        Returns:
            Path to the generated HTML file
        """
        input_path = Path(file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        if not self.is_supported_format(file_path):
            raise ValueError(f"Unsupported file format: {input_path.suffix}")
        
        # Set output directory
        if output_dir is None:
            output_dir = input_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting {input_path.name} with Enhanced Docling...")
        
        extracted_content = None
        
        # Try Docling first
        if self.converter is not None:
            try:
                print("🔄 Using Docling DocumentConverter...")
                result = self.converter.convert(input_path)
                extracted_content = result.document.export_to_html()
                print("✅ Docling conversion successful")
                
            except Exception as e:
                print(f"⚠️  Docling conversion failed: {str(e)}")
                if "SSL" in str(e) or "certificate" in str(e):
                    print("💡 This appears to be an SSL/certificate issue")
        
        # Fallback to PyPDF2 for PDFs
        if extracted_content is None and input_path.suffix.lower() == '.pdf':
            try:
                print("🔄 Falling back to PyPDF2...")
                extracted_content = self._extract_with_pypdf2(str(input_path))
                print("✅ PyPDF2 extraction successful")
                
            except Exception as e:
                print(f"❌ PyPDF2 extraction also failed: {str(e)}")
        
        if extracted_content is None:
            raise RuntimeError(f"All conversion methods failed for {file_path}")
        
        # Generate complete HTML document
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>{input_path.stem}</title>
<meta charset='utf-8'>
</head>
<body>
<h1>{input_path.stem}</h1>
{extracted_content}
</body>
</html>"""
        
        # Save HTML file
        output_file = output_dir / f"{input_path.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Conversion completed: {output_file}")
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
        
        print(f"Starting Enhanced Docling batch conversion of {len(file_paths)} files...")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                print(f"\n[{i}/{len(file_paths)}] Processing: {Path(file_path).name}")
                html_file = self.convert_file(file_path, output_dir)
                html_files.append(html_file)
            except Exception as e:
                print(f"❌ Error converting {file_path}: {str(e)}")
                continue
        
        print(f"\n✅ Enhanced Docling batch conversion completed: {len(html_files)}/{len(file_paths)} files successful")
        return html_files
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        info = {
            "platform": sys.platform,
            "docling_available": DOCLING_AVAILABLE,
            "pypdf2_available": PYPDF2_AVAILABLE,
            "converter_initialized": self.converter is not None,
            "ocr_enabled": self.use_ocr,
            "supported_formats": self.supported_formats,
            "languages": self.lang
        }
        
        if DOCLING_AVAILABLE:
            try:
                import docling
                info["docling_version"] = getattr(docling, '__version__', 'unknown')
            except:
                info["docling_version"] = 'unknown'
        
        return info