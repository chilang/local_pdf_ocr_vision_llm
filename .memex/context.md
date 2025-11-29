# Local PDF OCR Vision LLM Project

## Project Overview
A Streamlit-based PDF OCR application that uses Qwen3-VL vision models running locally on Apple Silicon via MLX for text extraction from PDF documents.

## Technology Stack
- **Frontend:** Streamlit 1.51.0
- **ML Framework:** MLX (Apple Silicon optimized)
- **Vision Models:** Qwen3-VL (2B, 8B, 32B variants)
- **PDF Processing:** pdf2image, poppler
- **Dependencies:** PyTorch + torchvision (required for model processor only)

## Critical Dependencies

### PyTorch Requirement
**IMPORTANT:** Even though MLX handles inference, PyTorch and torchvision are REQUIRED for the model processor.

```bash
uv pip install torch torchvision
```

**Why:** The `mlx-vlm` library uses HuggingFace's `transformers` library for preprocessing, which includes `AutoVideoProcessor` that depends on PyTorch. The actual model inference runs on MLX, but preprocessing requires PyTorch components.

**Error if missing:**
```
AutoVideoProcessor requires the PyTorch library but it was not found in your environment.
```

### System Dependencies
- **poppler:** Required for pdf2image
  ```bash
  brew install poppler
  ```

## Model Information

### Qwen3-VL MLX Models
Available from mlx-community on HuggingFace:
- `mlx-community/Qwen3-VL-2B-Instruct-4bit` (~0.7GB)
- `mlx-community/Qwen3-VL-2B-Instruct-8bit` (~1.5GB)
- `mlx-community/Qwen3-VL-8B-Instruct-4bit` (~2.5GB)
- `mlx-community/Qwen3-VL-8B-Instruct-8bit` (~5GB)
- `mlx-community/Qwen3-VL-32B-Instruct-4bit` (~10GB)

**Collection:** https://huggingface.co/collections/mlx-community/qwen3-vl

### Model Versions
- **Qwen2-VL:** Older generation, well-supported
- **Qwen2.5-VL:** Had MLX support issues (GitHub issue #192)
- **Qwen3-VL:** Latest generation, fully supported in MLX ✅

## Code Patterns

### Import Pattern
```python
# Rename mlx_vlm.load to avoid conflicts
from mlx_vlm import load as mlx_load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
```

### Function Naming
- Use `load_vision_model()` instead of `load_model()` to avoid conflicts with `mlx_vlm.load`
- Avoid generic names that might conflict with imported functions

### MLX VLM Generate Function
**CRITICAL:** The `generate()` function parameter order is:
```python
generate(model, processor, prompt, image, **kwargs)
```

**NOT:** `generate(model, processor, image, prompt, **kwargs)`

**Return Type:** Returns a `GenerationResult` object with attributes:
- `.text` - The generated text (string)
- `.prompt_tokens` - Number of prompt tokens
- `.generation_tokens` - Number of generated tokens
- `.generation_tps` - Tokens per second
- `.peak_memory` - Peak memory usage

**Always extract text:** `output_text = result.text`

### Streamlit Session State Pattern
**IMPORTANT:** For UI elements that trigger reruns (toggles, checkboxes), store data in session state to persist across reruns.

**Example:**
```python
# Store OCR output in session state
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

### Streamlit Caching
**AVOID:** Using `@st.cache_resource` with functions that call Streamlit UI elements (progress bars, spinners, etc.)

**Reason:** Causes `CacheReplayClosureError` when Streamlit tries to replay cached UI elements that reference layout blocks created outside the function.

**Solution:** Either:
1. Remove caching decorator
2. Use `with st.spinner()` outside the cached function
3. Pass UI callbacks with underscore prefix: `_progress_callback` (tells Streamlit not to hash it)

### Deprecated Streamlit APIs
- Replace `use_container_width=True` with `width="stretch"`
- Replace `use_container_width=False` with `width="content"`

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

## Development Workflow

### Environment Setup
```bash
cd <project_directory>
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Running the App
```bash
# Start on specific port
streamlit run app.py --server.port 9000

# Or use the startup script
./start.sh
```

### Terminal Management
- **Terminal 1:** Streamlit server (keep running)
- **Terminal 2:** Shell operations and testing

### Testing Models
```bash
python test_model.py mlx-community/Qwen3-VL-2B-Instruct-4bit
```

## Troubleshooting

### Browser Cache Issues
If encountering persistent Streamlit errors after code changes:
1. Open app in **incognito/private browser window**
2. Or clear browser cache for localhost
3. Use a different port number

**Symptom:** Error messages referencing old function names or decorators that no longer exist in code.

**Cause:** Browser caching old Streamlit session state.

### Cache Clearing
```bash
# Clear Python bytecode
find . -name "*.pyc" -o -name "*.pyo" | grep -v ".venv" | xargs rm -f

# Clear Streamlit cache
streamlit cache clear
rm -rf ~/.streamlit

# Programmatic cache clear
python -c "import streamlit as st; st.cache_data.clear(); st.cache_resource.clear()"
```

### Model Loading Issues
If model fails to load:
1. Verify PyTorch is installed: `python -c "import torch; print(torch.__version__)"`
2. Check poppler is installed: `which pdftoppm`
3. Ensure sufficient disk space for model download
4. Check HuggingFace cache: `~/.cache/huggingface/`

### Common Errors

#### "Invalid binary data format: GenerationResult"
**Cause:** Trying to use `GenerationResult` object directly instead of extracting text.
**Fix:** Use `result.text` to extract the string.

#### "The image <prompt> must be a valid URL or existing file"
**Cause:** Parameters to `generate()` are in wrong order (image and prompt swapped).
**Fix:** Ensure order is `generate(model, processor, prompt, image, ...)`

## File Structure
```
local_pdf_ocr_vision_llm/
├── .gitignore            # Git ignore patterns
├── README.md             # Project documentation
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
├── start.sh              # Startup script
└── .venv/                # Virtual environment (not in git)
```

## Git Workflow
- Only commit essential files: app.py, requirements.txt, start.sh, README.md, .gitignore, .memex/
- Exclude: .venv/, __pycache__/, tasks.json, backup files, test files
- Use descriptive commit messages with bullet points for features
- .memex/ folder contains project rules and should be version controlled

## Performance Notes
- Models run efficiently on Apple Silicon via MLX
- PyTorch dependency doesn't impact inference performance
- Only preprocessing uses PyTorch; inference is pure MLX
- First model load downloads weights (one-time, cached locally)

## References
- MLX VLM GitHub: https://github.com/Blaizzy/mlx-vlm
- Qwen3-VL MLX Collection: https://huggingface.co/collections/mlx-community/qwen3-vl
- PyTorch requirement issue: https://github.com/Blaizzy/mlx-vlm/issues/137