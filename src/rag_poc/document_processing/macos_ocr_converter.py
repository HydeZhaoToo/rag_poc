"""
macOS native OCR document converter using Docling with OcrMacOptions
Utilizes Apple's Vision framework through docling's OcrMacOptions integration
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions
    from docling.datamodel.base_models import DocInputType
    DOCLING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Docling not available: {e}")
    DOCLING_AVAILABLE = False

# Try to import OcrMacOptions, but fall back to EasyOcrOptions if not available
try:
    from docling.models.ocr_mac_model import OcrMacOptions
    OCRMAC_AVAILABLE = True
except ImportError:
    print("⚠️  OcrMacOptions not available, using EasyOcrOptions with macOS optimization")
    OCRMAC_AVAILABLE = False

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class MacOSOCRConverter:
    """Convert documents using Docling with macOS Vision framework OCR"""
    
    def __init__(self, force_full_page_ocr: bool = True, lang: List[str] = None):
        """Initialize macOS OCR converter with Docling and OcrMacOptions
        
        Args:
            force_full_page_ocr: Whether to force OCR on entire page (default: True)
            lang: Languages for OCR (default: ['en-US', 'zh-Hans', 'zh-Hant'])
        """
        self.supported_formats = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
            '.html', '.htm', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'
        ]
        
        # Check if running on macOS
        if sys.platform != 'darwin':
            raise RuntimeError("macOS OCR converter only works on macOS")
        
        if not DOCLING_AVAILABLE:
            raise RuntimeError("Docling not available. Please install docling.")
            
        # Note: OcrMacOptions may not be available in all docling installations
        # We'll use EasyOcrOptions as fallback with macOS optimization
        
        # Set default languages (prioritize English and Chinese)
        self.lang = lang or ['en-US', 'zh-Hans', 'zh-Hant', 'fr-FR', 'de-DE', 'es-ES']
        self.force_full_page_ocr = force_full_page_ocr
        
        # Initialize Docling converter with macOS OCR options
        self.converter = self._initialize_converter()
        
        print(f"✅ macOS OCR converter initialized with Docling")
        print(f"   Force full page OCR: {self.force_full_page_ocr}")
        print(f"   Languages: {self.lang}")
    
    def _initialize_converter(self) -> DocumentConverter:
        """Initialize DocumentConverter with macOS OCR options"""
        try:
            # Try to use OcrMacOptions if available, otherwise use EasyOcrOptions
            if OCRMAC_AVAILABLE:
                print("🍎 Using OcrMacOptions with Apple Vision framework")
                ocr_options = OcrMacOptions(
                    force_full_page_ocr=self.force_full_page_ocr,
                    lang=self.lang
                )
            else:
                print("🔄 Using EasyOcrOptions with macOS optimization")
                # Use EasyOCR but optimize for macOS by not using GPU (more stable)
                ocr_lang = ['en', 'ch_sim']  # EasyOCR language codes (English + Simplified Chinese)
                ocr_options = EasyOcrOptions(
                    lang=ocr_lang,
                    use_gpu=False,  # Use CPU for stability on macOS
                    download_enabled=True
                )
            
            # Configure pipeline options
            pipeline_options = PipelineOptions(
                do_ocr=True,
                do_table_structure=True,
                ocr_options=ocr_options
            )
            
            # Initialize converter with pipeline options
            converter = DocumentConverter(
                pipeline_options=pipeline_options
            )
            
            print("✅ Docling DocumentConverter with macOS OCR initialized")
            return converter
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize macOS OCR converter: {e}")
    
    def _fallback_extract_pdf_text(self, pdf_path: str) -> Optional[str]:
        """Fallback: Try to extract text directly from PDF using PyPDF2"""
        if not PyPDF2:
            return None
        
        try:
            print("🔄 Attempting PyPDF2 fallback extraction...")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                all_text = []
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text().strip()
                    if text:
                        all_text.append(f"<h2>Page {page_num}</h2>\n<div class='page-content'><p>{text}</p></div>")
                
                if all_text:
                    extracted_text = "\n".join(all_text)
                    # Check if we got meaningful text (not just symbols/gibberish)
                    if len(extracted_text.replace('<', '').replace('>', '').replace('h2', '').replace('div', '').replace('p', '').replace('/', '').strip()) > 100:
                        print("✅ PyPDF2 fallback extraction successful")
                        return extracted_text
                
        except Exception as e:
            print(f"⚠️  PyPDF2 fallback extraction failed: {e}")
        
        return None
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a single file to HTML using macOS OCR via Docling
        
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
        
        print(f"Converting {input_path.name} using Docling with macOS OCR...")
        
        extracted_content = None
        
        # Try Docling with macOS OCR first
        try:
            print("🔄 Using Docling with macOS Vision OCR...")
            result = self.converter.convert(input_path)
            extracted_content = result.document.export_to_html()
            print("✅ Docling macOS OCR conversion successful")
            
        except Exception as e:
            print(f"⚠️  Docling macOS OCR conversion failed: {str(e)}")
            
            # Fallback to PyPDF2 for PDFs only
            if input_path.suffix.lower() == '.pdf':
                extracted_content = self._fallback_extract_pdf_text(str(input_path))
        
        if extracted_content is None:
            raise RuntimeError(f"All conversion methods failed for {file_path}")
        
        # Generate complete HTML document if needed
        if not extracted_content.strip().startswith('<!DOCTYPE html>'):
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
        else:
            html_content = extracted_content
        
        # Save HTML file
        output_file = output_dir / f"{input_path.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ macOS OCR conversion completed: {output_file}")
        return str(output_file)
    
    def convert_batch(self, file_paths: List[str], output_dir: Optional[str] = None) -> List[str]:
        """
        Convert multiple files to HTML using macOS OCR via Docling
        
        Args:
            file_paths: List of input file paths
            output_dir: Output directory
            
        Returns:
            List of generated HTML file paths
        """
        html_files = []
        
        print(f"Starting Docling macOS OCR batch conversion of {len(file_paths)} files...")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                print(f"\n[{i}/{len(file_paths)}] Processing: {Path(file_path).name}")
                html_file = self.convert_file(file_path, output_dir)
                html_files.append(html_file)
            except Exception as e:
                print(f"❌ Error converting {file_path}: {str(e)}")
                continue
        
        print(f"\n✅ Docling macOS OCR batch conversion completed: {len(html_files)}/{len(file_paths)} files successful")
        return html_files
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        import subprocess
        
        try:
            version_result = subprocess.run(['sw_vers', '-productVersion'], 
                                          capture_output=True, text=True, check=True)
            macos_version = version_result.stdout.strip()
        except Exception:
            macos_version = "Unknown"
        
        info = {
            "platform": sys.platform,
            "macos_version": macos_version,
            "docling_available": DOCLING_AVAILABLE,
            "ocrmac_available": OCRMAC_AVAILABLE,
            "pypdf2_available": PyPDF2 is not None,
            "converter_initialized": hasattr(self, 'converter') and self.converter is not None,
            "force_full_page_ocr": self.force_full_page_ocr,
            "supported_formats": self.supported_formats,
            "languages": self.lang,
            "ocr_method": f"Docling with {'OcrMacOptions' if OCRMAC_AVAILABLE else 'EasyOcrOptions'} on macOS"
        }
        
        if DOCLING_AVAILABLE:
            try:
                import docling
                info["docling_version"] = getattr(docling, '__version__', 'unknown')
            except:
                info["docling_version"] = 'unknown'
        
        return info
    
    def convert_to_html(self, file_path: str) -> str:
        """
        Convert document to HTML content (without saving to file)
        
        Args:
            file_path: Path to input document
            
        Returns:
            HTML content as string
        """
        if not self.is_supported_format(file_path):
            raise ValueError(f"File format not supported: {file_path}")
        
        input_path = Path(file_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            # Convert using Docling
            conv_result = self.converter.convert(input_path)
            html_content = conv_result.document.export_to_html()
            print(f"✅ Docling macOS OCR conversion successful: {file_path}")
            return html_content
            
        except Exception as e:
            print(f"⚠️  Docling conversion failed for {file_path}: {str(e)}")
            
            # Try fallback for PDFs
            if input_path.suffix.lower() == '.pdf' and PyPDF2:
                try:
                    fallback_text = self._fallback_extract_pdf_text(str(input_path))
                    if fallback_text:
                        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{input_path.stem}</title>
    <meta charset='utf-8'>
</head>
<body>
    <h1>{input_path.stem}</h1>
    <div class='content'>
        {''.join(f'<p>{para}</p>' for para in fallback_text.split('\n\n') if para.strip())}
    </div>
</body>
</html>"""
                        print(f"✅ PyPDF2 fallback conversion successful: {file_path}")
                        return html_content
                except Exception as fallback_e:
                    print(f"❌ PyPDF2 fallback also failed: {str(fallback_e)}")
            
            raise Exception(f"All conversion methods failed for {file_path}: {str(e)}")