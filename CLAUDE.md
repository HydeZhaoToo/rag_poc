# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
```bash
# Install dependencies (uses uv package manager)
uv sync
uv sync --extra full  # Include optional dependencies like docling

# Add new dependencies
uv add <package-name>
```

### Core Application Commands
```bash
# Test Azure OpenAI connection
python main.py test-connection

# Build vector index from documents
python main.py build -f <file1> <file2> -o <output_dir>
python main.py build -f "data/input/document.pdf" --chunk-size 300 --chunk-overlap 50

# Search in vector index
python main.py search -q "your query" -k 5
python main.py search -q "query" --show-scores --score-threshold 0.8

# Add documents to existing index
python main.py add -f <new_files>

# Show index information
python main.py info
```

### Development Testing
```bash
# Test Azure OpenAI connection without full pipeline
python test_connection.py

# Run example usage demonstration
python example_usage.py
```

## Architecture Overview

This is a **RAG (Retrieval-Augmented Generation) system** with modular pipeline architecture:

```
Documents → Document Processing → Text Splitting → Embedding → Vector Storage → Retrieval
```

### Core Components

1. **RAGPipeline** (`src/rag_poc/rag_pipeline.py`)
   - Main orchestrator using Facade pattern
   - Integrates all subsystems into unified interface
   - Handles end-to-end document processing and search

2. **Document Processing** (`src/rag_poc/document_processing/`)
   - `DocumentToHTMLConverter`: Uses Docling for multi-format conversion with OCR
   - `SimplePDFConverter`: Fallback PyPDF2-based PDF text extraction
   - `HTMLDocumentSplitter`: LangChain HTML splitter using h1-h6 headers for semantic chunking

3. **Embedding Management** (`src/rag_poc/embedding/`)
   - `AzureOpenAIEmbeddingManager`: Handles text-embedding-ada-002 model (1536 dimensions)
   - Batch processing and connection testing

4. **Vector Storage** (`src/rag_poc/vectorstore/`)
   - `FAISSVectorStore`: Persistent FAISS-based similarity search
   - Index management, incremental updates, score-based filtering

### Configuration Requirements

The system requires Azure OpenAI configuration in `.env`:
```env
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_DEPLOYMENT_NAME=text-embedding-ada-002
CHUNK_SIZE=300
CHUNK_OVERLAP=50
```

### Supported Document Formats

- **Text Documents**: PDF, DOCX, DOC, PPTX, PPT, HTML
- **Images**: PNG, JPG, JPEG (with OCR via Docling)
- **Processing**: Converts all formats to HTML before chunking

### Data Flow Architecture

1. **Input**: Multi-format documents placed in `data/input/`
2. **Conversion**: Docling converts to HTML with macOS vision OCR
3. **Splitting**: HTML headers (h1-h6) define semantic chunk boundaries
4. **Embedding**: Azure OpenAI generates vectors for each chunk
5. **Storage**: FAISS indexes vectors in `data/output/faiss_index`
6. **Retrieval**: Query embeddings match against stored vectors

### Development Patterns

- **Error Handling**: Comprehensive validation and graceful degradation
- **Batch Processing**: Efficient handling of multiple documents
- **Incremental Updates**: Add documents to existing indexes without rebuilding
- **Configuration-Driven**: Behavior controlled via environment variables
- **Fallback Strategies**: SimplePDFConverter when Docling fails

### Testing Strategy

Always test Azure OpenAI connectivity before building indexes:
```bash
python main.py test-connection
```

Use the provided test document for validation:
```bash
python main.py build -f "data/input/AI辅助软件交付成熟度模型白皮书.pdf"
python main.py search -q "L2级 Prompt驱动实践"
```