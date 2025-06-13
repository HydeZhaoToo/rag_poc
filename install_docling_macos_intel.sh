#!/bin/bash

# Docling installation script for macOS Intel x86_64
# 针对 macOS Intel x86_64 机器的 Docling 安装脚本

echo "🍎 Docling Installation for macOS Intel x86_64"
echo "================================================"

# Check system architecture
ARCH=$(uname -m)
echo "🔍 System Architecture: $ARCH"

if [[ "$ARCH" != "x86_64" ]]; then
    echo "⚠️  Warning: This script is optimized for Intel x86_64 Macs"
    echo "   Your system shows: $ARCH"
    echo "   You may need different PyTorch versions"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python Version: $PYTHON_VERSION"

# Configure pip to use Chinese mirrors for faster downloads
echo ""
echo "🚀 Configuring pip to use Chinese mirrors..."

# Create pip config directory if not exists
mkdir -p ~/.pip

# Configure pip to use Tsinghua mirror (fastest for most regions)
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

echo "✅ Pip configured to use Tsinghua mirror"

# Alternative mirrors (uncomment to use different mirror)
# echo "Alternative mirrors available:"
# echo "  - 阿里云: https://mirrors.aliyun.com/pypi/simple/"
# echo "  - 中国科技大学: https://pypi.mirrors.ustc.edu.cn/simple/"
# echo "  - 豆瓣: https://pypi.douban.com/simple/"
# echo "  - 百度: https://mirror.baidu.com/pypi/simple/"

echo ""
echo "📦 Installing Docling with macOS Intel x86_64 optimizations..."

# Install specific PyTorch version for Intel Macs first
echo "Installing PyTorch 2.2.2 for Intel x86_64..."
pip3 install torch==2.2.2 torchvision==0.17.2 --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install Docling
echo "Installing Docling..."
pip3 install docling --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Install additional dependencies
echo "Installing additional dependencies..."
pip3 install --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    langchain \
    langchain-community \
    langchain-openai \
    faiss-cpu \
    python-dotenv \
    openai \
    tiktoken \
    beautifulsoup4 \
    lxml \
    numpy \
    pypdf2 \
    pandas

echo ""
echo "🔧 Checking installation..."

# Test imports
python3 -c "
import torch
print(f'✅ PyTorch version: {torch.__version__}')
print(f'✅ PyTorch device: {torch.device(\"cpu\")}')

try:
    import docling
    print(f'✅ Docling imported successfully')
    print(f'✅ Docling version: {docling.__version__}')
except ImportError as e:
    print(f'❌ Docling import failed: {e}')

try:
    from docling.document_converter import DocumentConverter
    print('✅ DocumentConverter imported successfully')
except ImportError as e:
    print(f'❌ DocumentConverter import failed: {e}')
"

echo ""
echo "🎯 Installation Summary:"
echo "   - PyTorch 2.2.2 (Intel x86_64 optimized)"
echo "   - Docling (latest version)"
echo "   - All RAG POC dependencies"
echo "   - Using Tsinghua mirror for faster downloads"

echo ""
echo "✅ Installation complete!"
echo ""
echo "💡 Usage Tips:"
echo "   - Use '--device cpu' for regular CPU processing"
echo "   - Use '--device macos' for native macOS OCR"
echo "   - Docling will now be used instead of SimplePDF for better quality"
echo ""
echo "🧪 Test your installation:"
echo "   python main.py test-connection"
echo "   python main.py --device cpu build -f your_document.pdf"