#!/usr/bin/env python3
"""
验证 macOS OCR 内容提取效果的工具
Tool to verify macOS OCR content extraction effectiveness
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def analyze_html_content(html_file_path: str) -> Dict:
    """分析 HTML 文件内容"""
    
    if not os.path.exists(html_file_path):
        return {"error": f"文件不存在: {html_file_path}"}
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本统计
        stats = {
            "file_size": os.path.getsize(html_file_path),
            "total_characters": len(content),
            "total_lines": len(content.split('\n')),
        }
        
        # 提取页面内容
        pages = re.findall(r'<h2>Page (\d+)</h2>\s*<div class=\'page-content\'><p>(.*?)</p></div>', content, re.DOTALL)
        
        stats["total_pages"] = len(pages)
        stats["pages_with_content"] = 0
        stats["pages_content"] = []
        
        # 分析每页内容
        for page_num, page_content in pages:
            if page_content.strip():
                stats["pages_with_content"] += 1
                stats["pages_content"].append({
                    "page": int(page_num),
                    "character_count": len(page_content),
                    "word_count": len(page_content.split()),
                    "preview": page_content[:200] + ("..." if len(page_content) > 200 else "")
                })
        
        # 检测中文内容
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
        stats["chinese_characters"] = len(chinese_chars)
        stats["has_chinese"] = len(chinese_chars) > 0
        
        # 检测英文内容
        english_words = re.findall(r'\b[a-zA-Z]+\b', content)
        stats["english_words"] = len(english_words)
        stats["has_english"] = len(english_words) > 0
        
        # 检测特定关键词（基于您的测试文档）
        keywords = [
            "AI辅助软件交付成熟度模型",
            "L2级 Prompt驱动实践",
            "Docling",
            "成熟度",
            "人工智能",
            "软件交付",
            "RAG",
            "向量化"
        ]
        
        found_keywords = []
        for keyword in keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        stats["found_keywords"] = found_keywords
        stats["keyword_coverage"] = len(found_keywords) / len(keywords) if keywords else 0
        
        return stats
        
    except Exception as e:
        return {"error": f"读取文件出错: {str(e)}"}

def compare_extraction_methods(pdf_path: str) -> Dict:
    """比较不同提取方法的效果"""
    
    results = {}
    
    # 测试 macOS OCR
    print("🍎 测试 macOS OCR 提取...")
    try:
        from rag_poc.document_processing.macos_ocr_converter import MacOSOCRConverter
        
        converter = MacOSOCRConverter()
        output_file = converter.convert_file(pdf_path, "data/output/comparison_macos")
        
        if os.path.exists(output_file):
            results["macos_ocr"] = analyze_html_content(output_file)
            results["macos_ocr"]["output_file"] = output_file
        
    except Exception as e:
        results["macos_ocr"] = {"error": str(e)}
    
    # 测试 SimplePDF
    print("📄 测试 Simple PDF 提取...")
    try:
        from rag_poc.document_processing.simple_pdf_converter import SimplePDFConverter
        
        converter = SimplePDFConverter()
        output_file = converter.convert_file(pdf_path, "data/output/comparison_simple")
        
        if os.path.exists(output_file):
            results["simple_pdf"] = analyze_html_content(output_file)
            results["simple_pdf"]["output_file"] = output_file
        
    except Exception as e:
        results["simple_pdf"] = {"error": str(e)}
    
    return results

def extract_and_display_content(html_file_path: str, num_pages: int = 3):
    """提取并显示 HTML 文件的具体内容"""
    
    print(f"\n📖 显示文件内容: {Path(html_file_path).name}")
    print("=" * 80)
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取页面内容
        pages = re.findall(r'<h2>Page (\d+)</h2>\s*<div class=\'page-content\'><p>(.*?)</p></div>', content, re.DOTALL)
        
        for i, (page_num, page_content) in enumerate(pages[:num_pages]):
            print(f"\n📄 第 {page_num} 页内容:")
            print("-" * 50)
            
            # 清理 HTML 内容并显示
            clean_content = page_content.strip()
            if clean_content:
                # 显示前500字符
                display_content = clean_content[:500]
                if len(clean_content) > 500:
                    display_content += "\n... [内容已截断]"
                
                print(display_content)
            else:
                print("⚠️  此页无文本内容")
        
        if len(pages) > num_pages:
            print(f"\n... 还有 {len(pages) - num_pages} 页内容未显示")
            
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")

def search_content_in_html(html_file_path: str, search_terms: List[str]):
    """在 HTML 文件中搜索特定内容"""
    
    print(f"\n🔍 在 {Path(html_file_path).name} 中搜索内容...")
    print("=" * 80)
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for term in search_terms:
            print(f"\n🎯 搜索: '{term}'")
            
            # 查找所有匹配
            matches = []
            for match in re.finditer(re.escape(term), content, re.IGNORECASE):
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                matches.append(context)
            
            if matches:
                print(f"✅ 找到 {len(matches)} 个匹配:")
                for i, context in enumerate(matches[:3], 1):  # 只显示前3个
                    print(f"  [{i}] ...{context}...")
                if len(matches) > 3:
                    print(f"  ... 还有 {len(matches) - 3} 个匹配")
            else:
                print("❌ 未找到匹配内容")
                
    except Exception as e:
        print(f"❌ 搜索出错: {e}")

def main():
    """主验证函数"""
    
    print("🔍 macOS OCR 内容提取验证工具")
    print("=" * 60)
    
    # 默认测试文件
    test_pdf = "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
    test_html = "data/output/test_macos/AI辅助软件交付成熟度模型白皮书.html"
    
    # 检查文件是否存在
    if not os.path.exists(test_pdf):
        print(f"❌ 测试 PDF 文件不存在: {test_pdf}")
        return
    
    # 1. 分析现有的 HTML 文件（如果存在）
    if os.path.exists(test_html):
        print("📊 分析现有的 macOS OCR 提取结果...")
        stats = analyze_html_content(test_html)
        
        if "error" not in stats:
            print(f"\n📈 提取统计:")
            print(f"  文件大小: {stats['file_size']:,} 字节")
            print(f"  总字符数: {stats['total_characters']:,}")
            print(f"  总页数: {stats['total_pages']}")
            print(f"  有内容页数: {stats['pages_with_content']}")
            print(f"  中文字符数: {stats['chinese_characters']:,}")
            print(f"  英文单词数: {stats['english_words']:,}")
            print(f"  关键词覆盖: {stats['keyword_coverage']:.1%} ({len(stats['found_keywords'])}/{len(['AI辅助软件交付成熟度模型', 'L2级 Prompt驱动实践', 'Docling', '成熟度', '人工智能', '软件交付', 'RAG', '向量化'])})")
            
            if stats['found_keywords']:
                print(f"  找到关键词: {', '.join(stats['found_keywords'])}")
        else:
            print(f"❌ {stats['error']}")
        
        # 显示具体内容
        extract_and_display_content(test_html, num_pages=2)
        
        # 搜索特定内容
        search_terms = [
            "L2级 Prompt驱动实践",
            "AI辅助软件交付成熟度模型",
            "成熟度模型",
            "Docling",
            "向量化"
        ]
        search_content_in_html(test_html, search_terms)
    
    else:
        print(f"⚠️  macOS OCR 结果文件不存在: {test_html}")
        print("💡 请先运行: python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf")
    
    # 2. 比较不同提取方法
    print(f"\n" + "=" * 60)
    print("🔄 比较不同提取方法的效果...")
    
    comparison = compare_extraction_methods(test_pdf)
    
    print(f"\n📊 提取方法对比:")
    print("-" * 60)
    
    for method, result in comparison.items():
        method_name = "macOS OCR" if method == "macos_ocr" else "Simple PDF"
        print(f"\n{method_name}:")
        
        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            print(f"  ✅ 文件大小: {result['file_size']:,} 字节")
            print(f"  📝 总字符数: {result['total_characters']:,}")
            print(f"  📄 页数: {result['total_pages']}")
            print(f"  🇨🇳 中文字符: {result['chinese_characters']:,}")
            print(f"  🇺🇸 英文单词: {result['english_words']:,}")
            print(f"  🎯 关键词覆盖: {result['keyword_coverage']:.1%}")
    
    # 3. 使用建议
    print(f"\n" + "=" * 60)
    print("💡 使用建议:")
    
    if "macos_ocr" in comparison and "error" not in comparison["macos_ocr"]:
        macos_stats = comparison["macos_ocr"]
        if macos_stats["chinese_characters"] > 0 and macos_stats["keyword_coverage"] > 0.5:
            print("✅ macOS OCR 提取效果良好，推荐使用")
            print("   命令: python main.py --device macos build -f your_document.pdf")
        else:
            print("⚠️  macOS OCR 提取效果一般，可能需要检查文档质量")
    
    print(f"\n📖 查看完整提取内容:")
    for method, result in comparison.items():
        if "output_file" in result:
            print(f"  {method}: {result['output_file']}")

if __name__ == "__main__":
    main()