# Local PDF OCR Vision LLM

A Streamlit-based PDF OCR application that uses Qwen3-VL vision models running locally on Apple Silicon via MLX for text extraction from PDF documents.

## Features

- 📄 PDF to text extraction using vision models
- 🖼️ Page-by-page navigation
- 📝 Markdown rendering support
- 💾 Download extracted text
- 🚀 Optimized for Apple Silicon with MLX
- 🎯 Multiple model sizes available (2B, 8B, 32B)

## Requirements

- macOS with Apple Silicon
- Python 3.11+
- Homebrew (for poppler installation)

## Installation

1. Install system dependencies:
```bash
brew install poppler
```

2. Create virtual environment and install Python dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Usage

Start the application:
```bash
./start.sh
```

Or manually:
```bash
streamlit run app.py --server.port 9000
```

Then:
1. Upload a PDF file
2. Select a model from the sidebar
3. Click "Load Model" (first time only)
4. Navigate through pages
5. Click "Extract Text" to perform OCR
6. Toggle markdown rendering if desired
7. Download the extracted text

## Available Models

- Qwen3-VL-2B-Instruct-4bit (~0.7GB)
- Qwen3-VL-2B-Instruct-8bit (~1.5GB)
- Qwen3-VL-8B-Instruct-4bit (~2.5GB)
- Qwen3-VL-8B-Instruct-8bit (~5GB)
- Qwen3-VL-32B-Instruct-4bit (~10GB)

Models are downloaded automatically on first use and cached locally.

## Technology Stack

- **Frontend:** Streamlit
- **ML Framework:** MLX (Apple Silicon optimized)
- **Vision Models:** Qwen3-VL (mlx-community)
- **PDF Processing:** pdf2image, poppler
- **Dependencies:** PyTorch + torchvision (required for model processor)

## License

MIT
