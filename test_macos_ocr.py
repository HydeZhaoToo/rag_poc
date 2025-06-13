#!/usr/bin/env python3
"""
Test script to compare macOS OCR with other document processing methods
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_poc.document_processing.macos_ocr_converter import MacOSOCRConverter
from rag_poc.document_processing.simple_pdf_converter import SimplePDFConverter

def test_macos_ocr():
    """Test macOS OCR functionality"""
    
    print("🧪 Testing macOS OCR Converter...")
    
    try:
        # Initialize converters
        macos_converter = MacOSOCRConverter()
        simple_converter = SimplePDFConverter()
        
        # Test file
        test_file = "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
        
        print(f"\n📄 Test file: {test_file}")
        
        # Get system info
        info = macos_converter.get_system_info()
        print(f"\n🖥️  System Information:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
        
        # Test file format support
        print(f"\n✅ Supported formats: {macos_converter.supported_formats}")
        print(f"📋 File format supported: {macos_converter.is_supported_format(test_file)}")
        
        # Compare with simple converter
        print(f"\n🔄 Converting with SimplePDFConverter...")
        simple_output = simple_converter.convert_file(test_file, "data/output/test_simple")
        print(f"✅ Simple converter output: {simple_output}")
        
        print(f"\n🍎 Converting with macOS OCR...")
        macos_output = macos_converter.convert_file(test_file, "data/output/test_macos")
        print(f"✅ macOS OCR output: {macos_output}")
        
        # Compare file sizes
        simple_path = Path(simple_output)
        macos_path = Path(macos_output)
        
        if simple_path.exists() and macos_path.exists():
            simple_size = simple_path.stat().st_size
            macos_size = macos_path.stat().st_size
            
            print(f"\n📊 File Size Comparison:")
            print(f"  - Simple PDF: {simple_size:,} bytes")
            print(f"  - macOS OCR: {macos_size:,} bytes")
            print(f"  - Ratio: {macos_size/simple_size:.2f}x")
        
        print(f"\n✅ macOS OCR test completed successfully!")
        
    except Exception as e:
        print(f"❌ macOS OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_macos_ocr()