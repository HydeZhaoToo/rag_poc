#!/usr/bin/env python3
"""
Test MPS acceleration for macOS
"""

import sys
from pathlib import Path
import torch

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mps_availability():
    """Test MPS availability and basic functionality"""
    print("=== macOS MPS 测试 ===")
    print()
    
    # Check PyTorch version
    print(f"PyTorch version: {torch.__version__}")
    
    # Check MPS availability
    mps_available = torch.backends.mps.is_available()
    print(f"MPS available: {mps_available}")
    
    if mps_available:
        print("✅ MPS 加速器可用!")
        
        # Test basic MPS operations
        try:
            # Create tensor on MPS device
            device = torch.device("mps")
            x = torch.randn(1000, 1000, device=device)
            y = torch.randn(1000, 1000, device=device)
            
            # Perform computation on MPS
            result = torch.matmul(x, y)
            
            print(f"✅ MPS 计算测试成功! 结果形状: {result.shape}")
            print(f"✅ 设备: {result.device}")
            
            # Memory info
            if hasattr(torch.mps, 'current_allocated_memory'):
                memory_mb = torch.mps.current_allocated_memory() / 1024 / 1024
                print(f"✅ 当前MPS内存使用: {memory_mb:.2f} MB")
            
        except Exception as e:
            print(f"❌ MPS 计算测试失败: {str(e)}")
            
    else:
        print("❌ MPS 不可用")
        print("可能的原因:")
        print("- 不是 Apple Silicon Mac (M1/M2/M3)")
        print("- macOS 版本过低 (需要 macOS 12.3+)")
        print("- PyTorch 版本不支持 MPS")
    
    print()

def test_docling_mps():
    """Test Docling with MPS acceleration"""
    print("=== Docling MPS 集成测试 ===")
    print()
    
    try:
        from rag_poc.document_processing.docling_mps_converter import DoclingMPSConverter
        
        # Initialize converter
        converter = DoclingMPSConverter(use_mps=True)
        
        # Print system info
        system_info = converter.get_system_info()
        print("系统信息:")
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        
        print()
        print("✅ Docling MPS 转换器初始化成功!")
        
        # Test with a file if available
        test_file = "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
        if Path(test_file).exists():
            print(f"发现测试文件: {test_file}")
            print("可以运行完整测试:")
            print(f"  python main.py build -f \"{test_file}\" --chunk-size 300")
        else:
            print("未找到测试文件，请添加PDF文件到 data/input/ 目录")
            
    except Exception as e:
        print(f"❌ Docling MPS 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_pipeline_mps():
    """Test complete RAG pipeline with MPS"""
    print("=== RAG Pipeline MPS 测试 ===")
    print()
    
    try:
        from rag_poc import RAGPipeline
        
        # Initialize pipeline (this will show MPS status)
        pipeline = RAGPipeline(chunk_size=300, chunk_overlap=50)
        
        # Get system info from document converter
        if hasattr(pipeline.document_converter, 'get_system_info'):
            system_info = pipeline.document_converter.get_system_info()
            print("Pipeline 系统信息:")
            for key, value in system_info.items():
                print(f"  {key}: {value}")
        
        print("✅ RAG Pipeline MPS 集成成功!")
        
    except Exception as e:
        print(f"❌ RAG Pipeline MPS 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mps_availability()
    print()
    test_docling_mps() 
    print()
    test_pipeline_mps()