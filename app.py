import streamlit as st
import tempfile
import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import io

# Import MLX VLM
try:
    from mlx_vlm import load as mlx_load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    st.error("MLX VLM not available. Please install mlx-vlm.")

# Page configuration
st.set_page_config(
    page_title="PDF OCR with Local Vision LLM",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 PDF OCR with Local Vision LLM")
st.markdown("Upload a PDF and extract text using a local Qwen3-VL model via MLX")

# Sidebar for model configuration
with st.sidebar:
    st.header("⚙️ Model Configuration")
    
    # Model selection dropdown
    available_models = [
        "mlx-community/Qwen3-VL-2B-Instruct-4bit",
        "mlx-community/Qwen3-VL-2B-Instruct-8bit",
        "mlx-community/Qwen3-VL-8B-Instruct-4bit",
        "mlx-community/Qwen3-VL-8B-Instruct-8bit",
        "mlx-community/Qwen3-VL-32B-Instruct-4bit",
    ]
    
    # Extract provider name from first model
    model_provider = available_models[0].split('/')[0]
    
    model_name = st.selectbox(
        f"Select Model ({model_provider})",
        options=available_models,
        index=0,
        help="Choose an MLX-optimized Qwen3-VL vision model",
        format_func=lambda x: x.split('/')[-1]  # Display only the model name after the slash
    )
    
    # Show model info
    if "2B" in model_name and "4bit" in model_name:
        st.caption("📦 ~0.7GB download")
    elif "2B" in model_name and "8bit" in model_name:
        st.caption("📦 ~1.5GB download")
    elif "8B" in model_name and "4bit" in model_name:
        st.caption("📦 ~2.5GB download")
    elif "8B" in model_name and "8bit" in model_name:
        st.caption("📦 ~5GB download")
    elif "32B" in model_name and "4bit" in model_name:
        st.caption("📦 ~10GB download")
    
    # OCR prompt
    ocr_prompt = st.text_area(
        "OCR Prompt",
        value="Extract all text and table from this image. Preserve the layout and formatting as much as possible.\n\nOutput pretty formatted markdown",
        help="Customize the prompt for OCR extraction"
    )
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This app uses:
    - **Qwen3-VL** vision models
    - **MLX** for Apple Silicon optimization
    - **pdf2image** for PDF conversion
    
    **Note:** PyTorch is required for the model processor but inference runs on MLX.
    """)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
    st.session_state.processor = None
    st.session_state.model_loaded = False
    st.session_state.model_name = None

# Model loading function
def load_vision_model(model_name):
    """Load the MLX vision model"""
    try:
        model, processor = mlx_load(model_name)
        config = load_config(model_name)
        return model, processor, config, None
    except Exception as e:
        return None, None, None, str(e)

# Main content area
# Create expandable left panel
with st.expander("📤 Upload PDF", expanded=True):
    upload_container = st.container()
    
    with upload_container:
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file to extract text from"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_pdf_path = tmp_file.name
            
            try:
                # Convert PDF to images
                with st.spinner("Converting PDF to images..."):
                    images = convert_from_path(tmp_pdf_path, dpi=200)
                
                st.success(f"✅ PDF loaded successfully! Found {len(images)} page(s)")
                
                # Page selection
                if len(images) > 1:
                    page_num = st.selectbox(
                        "Select page to OCR",
                        range(1, len(images) + 1),
                        format_func=lambda x: f"Page {x}"
                    )
                else:
                    page_num = 1
                
                # Display selected page
                selected_image = images[page_num - 1]
                st.image(selected_image, caption=f"Page {page_num}", width="stretch")
                
                # Store in session state
                st.session_state.current_image = selected_image
                st.session_state.page_num = page_num
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
            finally:
                # Clean up temp file
                if os.path.exists(tmp_pdf_path):
                    os.unlink(tmp_pdf_path)

# OCR Results section
st.header("📝 OCR Results")

if 'current_image' in st.session_state:
    # Load model button
    if not st.session_state.model_loaded or st.session_state.model_name != model_name:
        if st.button("🔄 Load Model", type="primary"):
            with st.spinner(f"Loading model: {model_name}..."):
                model, processor, config, error = load_vision_model(model_name)
            
            if error:
                st.error(f"Failed to load model: {error}")
                st.info("Make sure the model is available. You may need to download it first.")
            else:
                st.session_state.model = model
                st.session_state.processor = processor
                st.session_state.config = config
                st.session_state.model_loaded = True
                st.session_state.model_name = model_name
                st.success("✅ Model loaded successfully!")
                st.rerun()
    
    # OCR button
    if st.session_state.model_loaded:
        st.success(f"✅ Model ready: {st.session_state.model_name}")
        
        if st.button("🚀 Extract Text", type="primary"):
            try:
                with st.spinner("Extracting text from image..."):
                    # Prepare the image
                    image = st.session_state.current_image
                    
                    # Create the prompt with image
                    prompt = ocr_prompt
                    
                    # Apply chat template
                    formatted_prompt = apply_chat_template(
                        st.session_state.processor,
                        st.session_state.config,
                        prompt,
                        num_images=1
                    )
                    
                    # Generate OCR output
                    result = generate(
                        st.session_state.model,
                        st.session_state.processor,
                        formatted_prompt,
                        image,
                        max_tokens=2048,
                        temperature=0.1,
                        verbose=False
                    )
                    
                    # Extract text from GenerationResult and store in session state
                    st.session_state.output_text = result.text
                    
            except Exception as e:
                st.error(f"Error during OCR: {str(e)}")
                st.exception(e)
        
        # Display results if available
        if 'output_text' in st.session_state and st.session_state.output_text:
            st.subheader(f"Extracted Text (Page {st.session_state.page_num})")
            
            # Toggle for markdown rendering
            render_markdown = st.toggle("Render as Markdown", value=False)
            
            if render_markdown:
                st.markdown(st.session_state.output_text)
            else:
                st.text_area(
                    "OCR Output",
                    value=st.session_state.output_text,
                    height=400,
                    label_visibility="collapsed"
                )
            
            # Download button
            st.download_button(
                label="📥 Download Text",
                data=st.session_state.output_text,
                file_name=f"ocr_page_{st.session_state.page_num}.txt",
                mime="text/plain"
            )
    else:
        st.info("👆 Click 'Load Model' to start")
else:
    st.info("👈 Upload a PDF file to begin")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Powered by Qwen3-VL and MLX | Running locally on Apple Silicon</small>
</div>
""", unsafe_allow_html=True)
