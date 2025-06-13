#!/usr/bin/env python3
"""
测试所有文档处理模式的脚本
Test script for all document processing modes
"""

import sys
import os
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试依赖导入"""
    print("🧪 测试依赖导入...")
    
    results = {}
    
    # Test basic imports
    try:
        import torch
        results['pytorch'] = f"✅ PyTorch {torch.__version__}"
    except ImportError as e:
        results['pytorch'] = f"❌ PyTorch 导入失败: {e}"
    
    try:
        import docling
        results['docling'] = "✅ Docling 可用"
    except ImportError as e:
        results['docling'] = f"❌ Docling 导入失败: {e}"
    
    try:
        import PyPDF2
        results['pypdf2'] = "✅ PyPDF2 可用"
    except ImportError as e:
        results['pypdf2'] = f"❌ PyPDF2 导入失败: {e}"
    
    try:
        from rag_poc.document_processing.enhanced_docling_converter import EnhancedDoclingConverter
        results['enhanced_docling'] = "✅ Enhanced Docling 可用"
    except ImportError as e:
        results['enhanced_docling'] = f"❌ Enhanced Docling 导入失败: {e}"
    
    try:
        from rag_poc.document_processing.macos_ocr_converter import MacOSOCRConverter
        results['macos_ocr'] = "✅ macOS OCR 可用"
    except ImportError as e:
        results['macos_ocr'] = f"❌ macOS OCR 导入失败: {e}"
    
    # Print results
    print("\n📋 导入测试结果:")
    for component, status in results.items():
        print(f"  {component:15}: {status}")
    
    return results

def test_converter_initialization():
    """测试转换器初始化"""
    print("\n🔧 测试转换器初始化...")
    
    results = {}
    
    # Test Enhanced Docling
    try:
        from rag_poc.document_processing.enhanced_docling_converter import EnhancedDoclingConverter
        converter = EnhancedDoclingConverter()
        results['enhanced_docling'] = "✅ Enhanced Docling 初始化成功"
    except Exception as e:
        results['enhanced_docling'] = f"❌ Enhanced Docling 初始化失败: {str(e)[:100]}..."
    
    # Test macOS OCR
    try:
        from rag_poc.document_processing.macos_ocr_converter import MacOSOCRConverter
        converter = MacOSOCRConverter()
        results['macos_ocr'] = "✅ macOS OCR 初始化成功"
    except Exception as e:
        results['macos_ocr'] = f"❌ macOS OCR 初始化失败: {str(e)[:100]}..."
    
    # Test Docling MPS
    try:
        from rag_poc.document_processing.docling_mps_converter import DoclingMPSConverter
        converter = DoclingMPSConverter()
        results['docling_mps'] = "✅ Docling MPS 初始化成功"
    except Exception as e:
        results['docling_mps'] = f"❌ Docling MPS 初始化失败: {str(e)[:100]}..."
    
    # Test Document Converter
    try:
        from rag_poc.document_processing.document_converter import DocumentToHTMLConverter
        converter = DocumentToHTMLConverter()
        results['document_converter'] = "✅ Document Converter 初始化成功"
    except Exception as e:
        results['document_converter'] = f"❌ Document Converter 初始化失败: {str(e)[:100]}..."
    
    # Test Simple PDF
    try:
        from rag_poc.document_processing.simple_pdf_converter import SimplePDFConverter
        converter = SimplePDFConverter()
        results['simple_pdf'] = "✅ Simple PDF 初始化成功"
    except Exception as e:
        results['simple_pdf'] = f"❌ Simple PDF 初始化失败: {str(e)[:100]}..."
    
    # Test HTML Splitter
    try:
        from rag_poc.document_processing.html_splitter import HTMLDocumentSplitter
        splitter = HTMLDocumentSplitter(chunk_size=300, chunk_overlap=50)
        results['html_splitter'] = "✅ HTML Splitter 初始化成功"
    except Exception as e:
        results['html_splitter'] = f"❌ HTML Splitter 初始化失败: {str(e)[:100]}..."
    
    print("\n📋 初始化测试结果:")
    for component, status in results.items():
        print(f"  {component:15}: {status}")
    
    return results

def test_document_conversion():
    """测试文档转换"""
    print("\n📄 测试文档转换...")
    
    test_file = "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return {}
    
    results = {}
    
    # Test Simple PDF Converter (最快的方式)
    try:
        from rag_poc.document_processing.simple_pdf_converter import SimplePDFConverter
        
        print(f"\n🔄 测试 Simple PDF 转换...")
        start_time = time.time()
        
        converter = SimplePDFConverter()
        html_content = converter.convert_to_html(test_file)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if html_content and len(html_content) > 100:
            content_size = len(html_content)
            results['simple_pdf'] = f"✅ 转换成功 ({duration:.1f}s, {content_size:,} chars)"
        else:
            results['simple_pdf'] = "❌ 转换内容为空或过短"
            
    except Exception as e:
        results['simple_pdf'] = f"❌ 转换失败: {str(e)[:100]}..."
    
    # Test macOS OCR (不需要网络)
    try:
        from rag_poc.document_processing.macos_ocr_converter import MacOSOCRConverter
        
        print(f"\n🔄 测试 macOS OCR 转换...")
        start_time = time.time()
        
        converter = MacOSOCRConverter()
        html_content = converter.convert_to_html(test_file)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if html_content and len(html_content) > 100:
            content_size = len(html_content)
            results['macos_ocr'] = f"✅ 转换成功 ({duration:.1f}s, {content_size:,} chars)"
        else:
            results['macos_ocr'] = "❌ 转换内容为空或过短"
            
    except Exception as e:
        results['macos_ocr'] = f"❌ 转换失败: {str(e)[:100]}..."
    
    # Test Enhanced Docling (需要网络，可能会失败)
    try:
        from rag_poc.document_processing.enhanced_docling_converter import EnhancedDoclingConverter
        
        print(f"\n🔄 测试 Enhanced Docling 转换...")
        start_time = time.time()
        
        converter = EnhancedDoclingConverter()
        html_content = converter.convert_to_html(test_file)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if html_content and len(html_content) > 100:
            content_size = len(html_content)
            results['enhanced_docling'] = f"✅ 转换成功 ({duration:.1f}s, {content_size:,} chars)"
        else:
            results['enhanced_docling'] = "❌ 转换内容为空或过短"
            
    except Exception as e:
        results['enhanced_docling'] = f"❌ 转换失败: {str(e)[:100]}..."
    
    print("\n📋 转换测试结果:")
    for component, status in results.items():
        print(f"  {component:15}: {status}")
    
    return results

def test_rag_pipeline():
    """测试 RAG 管道"""
    print("\n🔍 测试 RAG 管道初始化...")
    
    results = {}
    
    # Test different device modes
    for device in ['cpu', 'macos']:
        try:
            from rag_poc import RAGPipeline
            
            print(f"\n🔄 测试 {device} 模式...")
            pipeline = RAGPipeline(device=device, init_document_converter=True)
            results[device] = "✅ 初始化成功"
            
        except Exception as e:
            results[device] = f"❌ 初始化失败: {str(e)[:100]}..."
    
    print("\n📋 RAG 管道测试结果:")
    for mode, status in results.items():
        print(f"  {mode:15}: {status}")
    
    return results

def main():
    """主测试函数"""
    print("🚀 RAG POC 全模式测试")
    print("=" * 50)
    
    # 系统信息
    print(f"🖥️  系统信息:")
    print(f"  平台: {sys.platform}")
    print(f"  Python: {sys.version.split()[0]}")
    
    try:
        import platform
        print(f"  架构: {platform.machine()}")
        if sys.platform == 'darwin':
            print(f"  macOS: {platform.mac_ver()[0]}")
    except:
        pass
    
    # 运行测试
    import_results = test_imports()
    init_results = test_converter_initialization()
    conversion_results = test_document_conversion()
    pipeline_results = test_rag_pipeline()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    all_results = {
        "依赖导入": import_results,
        "转换器初始化": init_results,
        "文档转换": conversion_results,
        "RAG管道": pipeline_results
    }
    
    for category, results in all_results.items():
        print(f"\n{category}:")
        for component, status in results.items():
            print(f"  {component:15}: {status}")
    
    # 推荐
    print(f"\n💡 使用建议:")
    
    if 'macos_ocr' in conversion_results and '✅' in conversion_results['macos_ocr']:
        print(f"  🍎 推荐使用 macOS OCR: python main.py --device macos")
    
    if 'simple_pdf' in conversion_results and '✅' in conversion_results['simple_pdf']:
        print(f"  📄 Simple PDF 可用: python main.py --device cpu")
    
    print(f"\n🧪 完整测试命令:")
    print(f"  python main.py test-connection")
    print(f"  python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf")
    print(f"  python main.py --device macos search -q 'L2级 Prompt驱动实践' -k 3")

if __name__ == "__main__":
    main()