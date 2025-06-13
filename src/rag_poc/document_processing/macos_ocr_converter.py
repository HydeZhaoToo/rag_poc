"""
macOS native OCR document converter using Vision framework
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import json
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class MacOSOCRConverter:
    """Convert documents using macOS native OCR capabilities"""
    
    def __init__(self):
        """Initialize macOS OCR converter"""
        self.supported_formats = [
            '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'
        ]
        
        # Check if running on macOS
        if sys.platform != 'darwin':
            raise RuntimeError("macOS OCR converter only works on macOS")
        
        # Check macOS version (Vision framework requires macOS 10.13+)
        try:
            version_result = subprocess.run(['sw_vers', '-productVersion'], 
                                          capture_output=True, text=True, check=True)
            version = version_result.stdout.strip()
            major_version = int(version.split('.')[0])
            minor_version = int(version.split('.')[1]) if len(version.split('.')) > 1 else 0
            
            if major_version < 10 or (major_version == 10 and minor_version < 13):
                raise RuntimeError("macOS OCR requires macOS 10.13 or later")
                
            print(f"✅ macOS {version} detected - Vision framework available")
            
        except Exception as e:
            raise RuntimeError(f"Failed to check macOS version: {e}")
    
    def _create_swift_ocr_script(self) -> str:
        """Create Swift script for OCR processing"""
        swift_script = '''
import Foundation
import Vision
import CoreImage
import ImageIO

func performOCR(on imagePath: String) -> String? {
    guard let url = URL(string: "file://" + imagePath),
          let cgImageSource = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(cgImageSource, 0, nil) else {
        print("Error: Could not load image from path: \\(imagePath)")
        return nil
    }
    
    let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    let request = VNRecognizeTextRequest()
    
    // Configure for better accuracy
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    
    // Support multiple languages including Chinese
    request.recognitionLanguages = ["en-US", "zh-Hans", "zh-Hant"]
    
    var recognizedText = ""
    
    do {
        try requestHandler.perform([request])
        
        guard let observations = request.results else {
            print("No text recognition results")
            return nil
        }
        
        for observation in observations {
            guard let topCandidate = observation.topCandidates(1).first else { continue }
            recognizedText += topCandidate.string + "\\n"
        }
        
    } catch {
        print("Error performing OCR: \\(error)")
        return nil
    }
    
    return recognizedText.isEmpty ? nil : recognizedText
}

// Main execution
guard CommandLine.arguments.count >= 2 else {
    print("Usage: swift script.swift <image_path>")
    exit(1)
}

let imagePath = CommandLine.arguments[1]

if let text = performOCR(on: imagePath) {
    print(text)
} else {
    print("No text found in image")
    exit(1)
}
'''
        return swift_script
    
    def _try_extract_pdf_text(self, pdf_path: str) -> Optional[str]:
        """Try to extract text directly from PDF before using OCR"""
        if not PyPDF2:
            return None
        
        try:
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
                        print("✅ Successfully extracted text directly from PDF")
                        return extracted_text
                
        except Exception as e:
            print(f"⚠️  Direct PDF text extraction failed: {e}")
        
        return None

    def _pdf_to_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """Convert PDF pages to images using sips (macOS built-in tool)"""
        pdf_path_obj = Path(pdf_path)
        output_dir_obj = Path(output_dir)
        output_dir_obj.mkdir(parents=True, exist_ok=True)
        
        image_files = []
        
        try:
            # Get number of pages using mdls
            result = subprocess.run(['mdls', '-name', 'kMDItemNumberOfPages', pdf_path], 
                                  capture_output=True, text=True, check=True)
            
            # Parse the output to get page count
            page_count = 1
            if 'kMDItemNumberOfPages' in result.stdout:
                try:
                    page_count = int(result.stdout.split('=')[1].strip())
                except:
                    page_count = 1
            
            print(f"Converting PDF with {page_count} pages to images...")
            
            # Convert each page to PNG using sips
            for page_num in range(1, page_count + 1):
                output_file = output_dir_obj / f"{pdf_path_obj.stem}_page_{page_num:03d}.png"
                
                # Use sips to convert PDF page to PNG
                cmd = [
                    'sips', '-s', 'format', 'png',
                    '-s', 'dpiWidth', '300',
                    '-s', 'dpiHeight', '300',
                    pdf_path,
                    '--out', str(output_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and output_file.exists():
                    image_files.append(str(output_file))
                    print(f"✅ Page {page_num} converted: {output_file.name}")
                else:
                    print(f"⚠️  Failed to convert page {page_num}")
            
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
        
        return image_files
    
    def _ocr_image(self, image_path: str) -> str:
        """Perform OCR on a single image using macOS Vision framework"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
            f.write(self._create_swift_ocr_script())
            script_path = f.name
        
        try:
            # Run Swift script for OCR
            result = subprocess.run(['swift', script_path, image_path], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"OCR failed for {image_path}: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            print(f"OCR timeout for {image_path}")
            return ""
        except Exception as e:
            print(f"OCR error for {image_path}: {e}")
            return ""
        finally:
            # Clean up script file
            try:
                os.unlink(script_path)
            except:
                pass
    
    def convert_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert a single file to HTML using macOS OCR
        
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
        
        print(f"Converting {input_path.name} using macOS OCR...")
        
        # Handle different file types
        if input_path.suffix.lower() == '.pdf':
            # First try direct text extraction from PDF
            extracted_text = self._try_extract_pdf_text(str(input_path))
            
            if not extracted_text:
                print("⚠️  Direct text extraction failed, falling back to OCR...")
                # Fall back to OCR if direct extraction failed
                with tempfile.TemporaryDirectory() as temp_dir:
                    image_files = self._pdf_to_images(str(input_path), temp_dir)
                    
                    if not image_files:
                        raise RuntimeError("Failed to convert PDF to images")
                    
                    # OCR each page
                    all_text = []
                    for i, image_file in enumerate(image_files, 1):
                        print(f"Processing page {i}/{len(image_files)}...")
                        text = self._ocr_image(image_file)
                        if text:
                            all_text.append(f"<h2>Page {i}</h2>\n<div class='page-content'><p>{text}</p></div>")
                    
                    extracted_text = "\n".join(all_text)
        else:
            # Direct OCR for image files
            extracted_text = self._ocr_image(str(input_path))
            if extracted_text:
                extracted_text = f"<div class='content'><p>{extracted_text}</p></div>"
        
        if not extracted_text:
            raise RuntimeError("No text could be extracted from the document")
        
        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>{input_path.stem}</title>
<meta charset='utf-8'>
</head>
<body>
<h1>{input_path.stem}</h1>
{extracted_text}
</body>
</html>"""
        
        # Save HTML file
        output_file = output_dir / f"{input_path.stem}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ macOS OCR conversion completed: {output_file}")
        return str(output_file)
    
    def convert_batch(self, file_paths: List[str], output_dir: Optional[str] = None) -> List[str]:
        """
        Convert multiple files to HTML using macOS OCR
        
        Args:
            file_paths: List of input file paths
            output_dir: Output directory
            
        Returns:
            List of generated HTML file paths
        """
        html_files = []
        
        print(f"Starting macOS OCR batch conversion of {len(file_paths)} files...")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                print(f"\n[{i}/{len(file_paths)}] Processing: {Path(file_path).name}")
                html_file = self.convert_file(file_path, output_dir)
                html_files.append(html_file)
            except Exception as e:
                print(f"❌ Error converting {file_path}: {str(e)}")
                continue
        
        print(f"\n✅ macOS OCR batch conversion completed: {len(html_files)}/{len(file_paths)} files successful")
        return html_files
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        try:
            version_result = subprocess.run(['sw_vers', '-productVersion'], 
                                          capture_output=True, text=True, check=True)
            macos_version = version_result.stdout.strip()
            
            swift_result = subprocess.run(['swift', '--version'], 
                                        capture_output=True, text=True, check=True)
            swift_version = swift_result.stdout.split('\n')[0]
            
        except Exception:
            macos_version = "Unknown"
            swift_version = "Unknown"
        
        return {
            "platform": sys.platform,
            "macos_version": macos_version,
            "swift_version": swift_version,
            "supported_formats": self.supported_formats,
            "ocr_method": "macOS Vision Framework"
        }