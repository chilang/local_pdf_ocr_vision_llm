# Local PDF OCR Vision LLM Project

## Project Overview
A Streamlit-based PDF OCR application that uses Qwen3-VL vision models running locally on Apple Silicon via MLX for text extraction from PDF documents.

## Technology Stack
- **Frontend:** Streamlit 1.51.0
- **ML Framework:** MLX (Apple Silicon optimized)
- **Vision Models:** Qwen3-VL (2B, 8B, 32B variants)
- **PDF Processing:** pdf2image, poppler
- **Dependencies:** PyTorch + torchvision (required for model processor only)

## Setup

### System Dependencies
```bash
brew install poppler  # Required for pdf2image
```

### Python Environment
```bash
cd <project_directory>
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Important:** PyTorch and torchvision are required dependencies even though MLX handles inference. The `mlx-vlm` library uses HuggingFace's `transformers` for preprocessing, which depends on PyTorch components. Actual model inference runs on MLX.

### Running the App
```bash
./start.sh
# Or manually: streamlit run app.py --server.port 9000
```

## Available Models

From mlx-community on HuggingFace:
- `mlx-community/Qwen3-VL-2B-Instruct-4bit` (~0.7GB)
- `mlx-community/Qwen3-VL-2B-Instruct-8bit` (~1.5GB)
- `mlx-community/Qwen3-VL-8B-Instruct-4bit` (~2.5GB)
- `mlx-community/Qwen3-VL-8B-Instruct-8bit` (~5GB)
- `mlx-community/Qwen3-VL-32B-Instruct-4bit` (~10GB)

**Collection:** https://huggingface.co/collections/mlx-community/qwen3-vl

Models are downloaded automatically on first use and cached locally in `~/.cache/huggingface/`

## Code Patterns

### Import Pattern
```python
# Rename mlx_vlm.load to avoid conflicts
from mlx_vlm import load as mlx_load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
```

### MLX VLM Generate Function
**Parameter order:**
```python
generate(model, processor, prompt, image, **kwargs)
```

**Return type:** `GenerationResult` object with attributes:
- `.text` - The generated text (string)
- `.prompt_tokens` - Number of prompt tokens
- `.generation_tokens` - Number of generated tokens
- `.generation_tps` - Tokens per second
- `.peak_memory` - Peak memory usage

**Always extract text:** `output_text = result.text`

### Streamlit Session State Pattern
For UI elements that trigger reruns (toggles, checkboxes), store data in session state to persist across reruns.

**Example:**
```python
# Store OCR output in session state inside button handler
if st.button("Extract Text"):
    result = generate(...)
    st.session_state.output_text = result.text

# Display outside button handler so it persists across reruns
if 'output_text' in st.session_state:
    render_markdown = st.toggle("Render as Markdown", value=False)
    if render_markdown:
        st.markdown(st.session_state.output_text)
    else:
        st.text_area("Output", value=st.session_state.output_text)
```

**Why:** When a toggle changes, Streamlit reruns the script. If output is only displayed inside a button handler, it disappears on rerun.

### Streamlit Selectbox Formatting
To display shortened names while keeping full values:
```python
model_name = st.selectbox(
    "Select Model",
    options=available_models,
    format_func=lambda x: x.split('/')[-1]  # Display only part after slash
)
```

## Default OCR Prompt
```
Extract all text and table from this image. Preserve the layout and formatting as much as possible.

Output pretty formatted markdown
```

This prompt is optimized for:
- Text extraction
- Table detection and formatting
- Layout preservation
- Markdown output for better rendering

## File Structure
```
local_pdf_ocr_vision_llm/
├── .gitignore            # Git ignore patterns
├── .memex/               # Project rules and context
│   └── context.md
├── README.md             # Project documentation
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
├── start.sh              # Startup script
└── .venv/                # Virtual environment (not in git)
```

## Git Workflow
- Commit essential files: app.py, requirements.txt, start.sh, README.md, .gitignore, .memex/
- Exclude: .venv/, __pycache__/, tasks.json, backup files, test files
- Use descriptive commit messages with bullet points for features

## References
- MLX VLM GitHub: https://github.com/Blaizzy/mlx-vlm
- Qwen3-VL MLX Collection: https://huggingface.co/collections/mlx-community/qwen3-vl