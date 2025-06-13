# RAG 验证程序 - AI辅助软件交付文档处理系统

这是一个基于 LangChain 和 FAISS 的 RAG (Retrieval-Augmented Generation) 验证程序，专门用于处理和搜索软件交付相关文档。本项目实现了完整的文档处理和向量搜索系统，支持多种文档格式和处理模式，特别针对中文文档进行了优化。

## 🎯 核心特性

- 🔄 **多模式文档处理**：支持 CPU、MPS 和 macOS 原生 OCR 三种处理模式
- 📄 **多格式支持**：PDF、PPT、DOC 等格式转换为 HTML
- 🍎 **macOS 优化**：使用 macOS Vision 框架进行原生 OCR 处理
- 🔍 **智能分割**：基于 HTML 结构的语义分割
- 🧠 **向量搜索**：基于 FAISS 的高效相似度搜索
- 🌐 **Azure 集成**：使用 Azure OpenAI 进行文本向量化
- 🔧 **智能后备**：多层后备机制确保处理稳定性
- 🎭 **中文优化**：特别针对中文文档识别和处理进行优化

## 🏗️ 系统架构

```
多种文档格式 (PDF/DOCX/PPTX/图片)
    ↓
三种处理模式选择:
├── CPU: Enhanced Docling → HTML
├── MPS: Docling MPS 加速 → HTML  
└── macOS: 原生 Vision OCR → HTML
    ↓
LangChain HTML 智能分割 (语义块切割)
    ↓
Azure OpenAI 向量化 (text-embedding-ada-002, 1536维)
    ↓
FAISS 向量数据库 (相似度搜索和文档召回)
```

### 🔄 多模式架构

```
RAG_POC/
├── src/rag_poc/
│   ├── rag_pipeline.py                 # 主管道（设备切换逻辑）
│   ├── document_processing/            # 文档处理模块
│   │   ├── enhanced_docling_converter.py     # CPU模式：增强版Docling
│   │   ├── macos_ocr_converter.py            # macOS模式：原生OCR
│   │   ├── docling_mps_converter.py          # MPS模式：GPU加速
│   │   └── simple_pdf_converter.py           # 后备方案：简单PDF
│   ├── text_splitting/                # 文本分割模块
│   │   ├── html_splitter.py           # HTML智能分割
│   │   └── text_processor.py          # 文本预处理
│   └── vector_store/                  # 向量存储模块
│       ├── faiss_store.py             # FAISS数据库
│       └── embedding_manager.py       # 向量化管理
└── tools/                             # 辅助工具
    ├── verify_macos_ocr.py           # OCR验证工具
    ├── test_all_modes.py             # 全模式测试
    └── configure_pip_mirrors.py      # 镜像配置工具
```

## 🚀 快速开始

### 环境要求

- **操作系统**：macOS (推荐 Intel x86_64)
- **Python**：3.8+
- **包管理器**：uv (推荐) 或 pip
- **Azure OpenAI**：API 访问权限

### 方法一：使用 uv（推荐）

**uv 优势**：
- ⚡ **极速安装**：比 pip 快 10-100 倍
- 🔒 **依赖锁定**：自动生成 `uv.lock` 确保环境一致性
- 🐍 **Python 管理**：自动管理 Python 版本
- 📦 **虚拟环境**：自动创建和管理虚拟环境

```bash
# 1. 安装 uv（如果还没有安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone <项目地址>
cd RAG_POC

# 3. 使用 uv 安装依赖（自动创建虚拟环境）
uv sync

# 4. 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或使用 uv run 直接运行命令（推荐）
uv run python main.py test-connection
```

### 方法二：传统 pip 安装

```bash
# 1. 克隆项目
git clone <项目地址>
cd RAG_POC

# 2. 配置国内镜像源（加速下载）
python configure_pip_mirrors.py config tsinghua

# 3. 安装依赖
python configure_pip_mirrors.py install tsinghua
```

### 方法三：手动 pip 安装

```bash
# 1. 配置 pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 2. 安装 PyTorch (Intel Mac 专用)
pip install torch==2.2.2 torchvision==0.17.2

# 3. 安装项目依赖
pip install -e .
```

### 环境配置

```bash
# 1. 复制环境模板
cp .env.example .env

# 2. 编辑 .env 文件配置 Azure OpenAI
# 3. 测试连接
python main.py test-connection
```

## ⚙️ 配置说明

### Azure OpenAI 配置

创建 `.env` 文件并配置您的 Azure OpenAI 设置：

```env
# Azure OpenAI 配置
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# 可选：自定义分块参数
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
VECTOR_DIMENSION=1536
```

## 📖 使用指南

### 基本用法

#### 1. 测试连接
```bash
# 使用 uv（推荐）
uv run python main.py test-connection

# 或激活虚拟环境后使用
python main.py test-connection
```

#### 2. 文档处理和索引构建

```bash
# macOS OCR 模式（推荐中文文档）
uv run python main.py --device macos build -f data/input/document.pdf

# CPU 模式（使用 Docling）
uv run python main.py --device cpu build -f data/input/document.pdf

# MPS 加速模式
uv run python main.py --device mps build -f data/input/document.pdf
```

#### 3. 向量搜索

```bash
# 基本搜索
uv run python main.py --device macos search -q "L2级 Prompt驱动实践" -k 3

# 带评分的搜索
uv run python main.py --device cpu search -q "AI辅助软件交付" -k 5 --show-scores
```

#### 4. 特定项目测试

```bash
# 处理AI软件交付白皮书并搜索
uv run python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf
uv run python main.py --device macos search -q "L2级 Prompt驱动实践" -k 3
```

### 三种处理模式详解

#### 🍎 macOS 原生 OCR 模式

**特点**：
- 使用 macOS Vision 框架
- 最佳中文识别效果
- 无需网络下载模型
- 速度快，准确度高

**适用场景**：
- 中文文档处理
- 网络环境受限
- 需要快速处理

**使用方法**：
```bash
python main.py --device macos build -f document.pdf
```

#### 🖥️ CPU 模式（Enhanced Docling）

**特点**：
- 使用增强版 Docling 转换器
- 广泛格式支持
- SSL 证书处理
- 智能后备机制

**适用场景**：
- 多格式文档处理
- 生产环境部署
- 需要最佳兼容性

**使用方法**：
```bash
python main.py --device cpu build -f document.pdf
```

#### ⚡ MPS 加速模式

**特点**：
- 使用 Metal Performance Shaders
- GPU 加速处理
- 适合大批量文档

**适用场景**：
- 大量文档处理
- 需要 GPU 加速
- M1/M2 Mac 设备

**使用方法**：
```bash
python main.py --device mps build -f document.pdf
```

### Python API 使用

```python
from rag_poc import RAGPipeline

# 初始化不同设备模式的管道
pipeline = RAGPipeline(
    device="macos",  # 或 "cpu", "mps"
    index_path="data/output/faiss_index",
    chunk_size=1000,
    chunk_overlap=200
)

# 测试连接
if pipeline.test_connection():
    print("Azure OpenAI 连接成功!")

# 构建向量索引
pipeline.build_vector_index([
    "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
])

# 搜索文档
results = pipeline.search_documents("L2级 Prompt驱动实践", k=3)
for doc in results:
    print(f"来源: {doc.metadata['source']}")
    print(f"内容: {doc.page_content[:200]}...")
    print()
```

## 📊 性能对比

| 处理模式 | 处理质量 | 速度 | 中文支持 | 网络要求 | 适用场景 |
|----------|----------|------|----------|----------|----------|
| **macOS OCR** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 无 | 中文文档 |
| **CPU (Docling)** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 首次需要 | 多格式文档 |
| **MPS 加速** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 首次需要 | 大量文档 |

### 推荐配置

- **中文文档优先**：`--device macos`
- **生产环境**：`--device cpu`
- **大批量处理**：`--device mps`
- **网络受限**：`--device macos`

## 🔧 高级功能

### 1. 批量文档处理

```bash
# 处理目录下所有 PDF 文件
for file in data/input/*.pdf; do
    python main.py --device macos build -f "$file"
done
```

### 2. OCR 效果验证

```bash
# 验证 macOS OCR 提取效果
python verify_macos_ocr.py

# 比较不同处理方式
python test_all_modes.py
```

### 3. 镜像源管理

```bash
# 测试镜像源速度
python configure_pip_mirrors.py test

# 切换镜像源
python configure_pip_mirrors.py config aliyun
```

## 📚 技术栈

### 核心依赖

- **LangChain**: 文档处理和文本分割
- **FAISS**: 向量相似度搜索
- **Docling**: 多格式文档转换
- **Azure OpenAI**: 文本向量化
- **PyTorch**: 深度学习框架支持

### 系统集成

- **macOS Vision**: 原生 OCR 处理
- **PyPDF2**: PDF 文本提取后备
- **BeautifulSoup**: HTML 处理
- **NumPy**: 数值计算

## 📋 支持的文档格式

- **PDF** (.pdf) - 主要测试格式
- **Microsoft Word** (.docx, .doc)
- **Microsoft PowerPoint** (.pptx, .ppt)
- **HTML** (.html, .htm)
- **图片** (.png, .jpg, .jpeg) - 使用 OCR

## 🔍 核心组件

### 1. 智能文档处理

- **多层次后备机制**：
  ```
  Docling OCR → Simple PDF → macOS OCR
  ```

- **HTML 语义分割**：
  - 基于 HTML 标签结构
  - 保持语义完整性
  - 智能重叠处理

### 2. 向量化优化

- **Azure OpenAI text-embedding-ada-002**
- **1536 维向量空间**
- **批量处理优化**

### 3. FAISS 向量搜索

- **高效索引**：基于 FAISS 的相似度搜索
- **元数据管理**：支持源文档追踪
- **相似度阈值**：可配置的搜索精度

## 🚀 示例工作流

1. **准备文档**：将文档放入 `data/input/`
2. **配置环境**：设置 Azure OpenAI 凭据
3. **构建索引**：`python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf`
4. **搜索测试**：`python main.py --device macos search -q "L2级 Prompt驱动实践" -k 3`
5. **验证结果**：`python verify_macos_ocr.py`

## 🛠️ 开发和测试

### 测试套件

```bash
# 运行完整测试
python test_all_modes.py

# 验证 OCR 效果
python verify_macos_ocr.py

# 测试连接
python main.py test-connection
```

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=$(pwd)/src
python main.py --device macos build -f document.pdf --verbose
```

## 🐛 问题排查

### 常见问题

#### 1. SSL 证书验证失败

```bash
# 解决方案1：使用 macOS OCR（无网络要求）
python main.py --device macos build -f document.pdf

# 解决方案2：设置环境变量
export PYTHONHTTPSVERIFY=0
```

#### 2. PyTorch 版本问题

```bash
# 检查版本
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# 重新安装
pip uninstall torch torchvision
pip install torch==2.2.2 torchvision==0.17.2
```

#### 3. FAISS 索引未找到

```bash
# 重新构建索引
python main.py --device macos build -f document.pdf --rebuild
```

#### 4. 下载速度慢

```bash
# 测试并切换镜像源
python configure_pip_mirrors.py test
python configure_pip_mirrors.py config aliyun
```

#### 5. Azure OpenAI 连接问题

- 检查 `.env` 文件配置
- 验证 API 密钥和端点
- 确认部署名称正确
- 测试网络连接

### 错误代码

- **ERR_001**：Azure OpenAI 连接失败
- **ERR_002**：文档转换失败
- **ERR_003**：FAISS 索引构建失败
- **ERR_004**：向量化处理失败

### 调试技巧

```bash
# 详细错误信息
python -v main.py build -f your_document.pdf

# 检查系统环境
python test_all_modes.py

# 验证 OCR 输出
python verify_macos_ocr.py
```

## 📈 项目演进

### 版本历史

- **v1.0**: 基础 RAG 功能实现
- **v1.1**: 增加 macOS OCR 支持
- **v1.2**: 多设备处理模式
- **v1.3**: 增强错误处理和后备机制
- **v1.4**: 完善中文支持和镜像配置

### 当前成果

✅ **已完成**：
- 完整的多模式文档处理系统
- 稳定的 macOS OCR 集成
- 智能后备和错误处理
- 中文文档优化支持
- 完善的工具和验证套件

📊 **测试验证**：
- 成功处理《AI辅助软件交付成熟度模型白皮书》
- macOS OCR 中文识别准确率 >95%
- 向量搜索"L2级 Prompt驱动实践"精确匹配
- 33个文档块成功建立索引


## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 打开 Pull Request

## 📞 支持和联系

- **Issues**: 在 GitHub 上提交问题
- **文档**: 查看项目 README 和代码注释
- **示例**: 参考 `verify_macos_ocr.py` 和 `test_all_modes.py`

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**注意**: 本项目专门针对 AI 辅助软件交付成熟度模型相关文档进行了优化，特别是中文文档的处理。系统已经过实际测试，能够有效处理和搜索相关技术文档。

🎉 **开始使用**: 
```bash
# 使用 uv（推荐）
uv run python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf
uv run python main.py --device macos search -q "L2级 Prompt驱动实践" -k 3

# 或激活虚拟环境后使用
source .venv/bin/activate
python main.py --device macos build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf
python main.py --device macos search -q "L2级 Prompt驱动实践" -k 3
```