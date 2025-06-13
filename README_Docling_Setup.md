# Docling 配置指南 - macOS Intel x86_64

本指南帮助您在 macOS Intel x86_64 环境下正确配置 Docling。

## 🎯 快速安装

### 方法一：使用配置脚本（推荐）

```bash
# 1. 配置国内镜像源（提高下载速度）
python configure_pip_mirrors.py config tsinghua

# 2. 安装 Docling 和依赖
python configure_pip_mirrors.py install tsinghua
```

### 方法二：手动安装

```bash
# 1. 配置 pip 使用清华镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 2. 安装 PyTorch (Intel Mac 专用版本)
pip install torch==2.2.2 torchvision==0.17.2

# 3. 安装 Docling
pip install docling

# 4. 安装其他依赖
pip install langchain langchain-community langchain-openai faiss-cpu python-dotenv openai tiktoken beautifulsoup4 lxml numpy pypdf2 pandas
```

## 🔧 配置选项

### 国内镜像源选择

```bash
# 测试镜像源速度
python configure_pip_mirrors.py test

# 使用不同镜像源
python configure_pip_mirrors.py config tsinghua   # 清华大学（推荐）
python configure_pip_mirrors.py config aliyun     # 阿里云
python configure_pip_mirrors.py config ustc       # 中科大
python configure_pip_mirrors.py config douban     # 豆瓣
```

## 🚀 使用方式

### 1. CPU 模式（使用 Docling）
```bash
# 构建索引
python main.py --device cpu build -f document.pdf

# 搜索
python main.py --device cpu search -q "搜索内容" -k 3
```

### 2. macOS 原生 OCR 模式
```bash
# 构建索引（最佳中文支持）
python main.py --device macos build -f document.pdf

# 搜索
python main.py --device macos search -q "搜索内容" -k 3
```

### 3. MPS 加速模式（如果需要）
```bash
# 构建索引
python main.py --device mps build -f document.pdf
```

## 📊 性能对比

| 模式 | 处理质量 | 速度 | 中文支持 | 网络要求 |
|------|----------|------|----------|----------|
| CPU (Docling) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 首次需要 |
| macOS OCR | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 无 |
| MPS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 首次需要 |

**推荐**：
- 🍎 **中文文档**：使用 `--device macos`（最佳中文支持）
- 🔄 **多格式文档**：使用 `--device cpu`（最广泛格式支持）
- ⚡ **大量文档**：使用 `--device mps`（如果需要GPU加速）

## 🛠️ 问题排查

### SSL 证书问题
如果遇到 SSL 证书验证失败：

```bash
# 方案1：设置环境变量
export PYTHONHTTPSVERIFY=0

# 方案2：使用 macOS OCR（无网络要求）
python main.py --device macos build -f document.pdf
```

### 下载慢问题
```bash
# 切换到不同的镜像源
python configure_pip_mirrors.py test
python configure_pip_mirrors.py config aliyun  # 尝试阿里云镜像
```

### PyTorch 版本问题
```bash
# 检查 PyTorch 版本
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# 重新安装正确版本
pip uninstall torch torchvision
pip install torch==2.2.2 torchvision==0.17.2
```

## 🧪 测试安装

```bash
# 测试连接
python main.py test-connection

# 测试文档处理
python main.py --device cpu build -f data/input/AI辅助软件交付成熟度模型白皮书.pdf

# 测试搜索
python main.py --device cpu search -q "L2级 Prompt驱动实践" -k 3
```

## 💡 最佳实践

1. **首次使用**：建议先使用 `--device macos` 测试，无需网络下载
2. **生产环境**：使用 `--device cpu` 获得最佳兼容性
3. **大批量处理**：考虑使用 `--device mps` 加速
4. **网络受限**：优先使用 `--device macos` 避免下载问题

## 📚 更多信息

- [Docling 官方文档](https://docling-project.github.io/docling/)
- [PyTorch 安装指南](https://pytorch.org/get-started/locally/)
- [项目 GitHub](https://github.com/your-project)

---

如有问题，请查看错误信息或提交 Issue。