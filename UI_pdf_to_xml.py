import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
from app.utils.pdf_to_xml import PDFtoXMLSchemaTool

# Page config
st.set_page_config(
    page_title="PDF to XML Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Teal/Turquoise themed UI matching Streamlit Cloud
st.markdown("""
<style>
    /* Beautiful teal color scheme */
    :root {
        --primary-teal: #5fa9a6;
        --dark-teal: #4a8885;
        --light-teal: #7bc4c1;
        --accent-red: #e76f6f;
        --bg-teal: #5fa9a6;
        --text-white: #ffffff;
        --text-light: #f0f8f8;
        --border-light: rgba(255, 255, 255, 0.2);
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global teal background */
    .stApp {
        background: linear-gradient(135deg, #5fa9a6 0%, #4a8885 100%);
        color: var(--text-white);
    }
    
    /* Header section */
    .header-container {
        text-align: center;
        padding: 3rem 1rem 2.5rem;
        margin-bottom: 2rem;
    }
    
    .badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
        color: var(--text-white);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: var(--text-white);
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .title-icon {
        display: inline-block;
        margin-right: 1rem;
        vertical-align: middle;
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: var(--text-light);
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.7;
    }
    
    /* Content cards - subtle translucent panels */
    .content-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid var(--border-light);
        border-radius: 14px;
        padding: 1.5rem;
        height: 100%;
        backdrop-filter: blur(4px);
        margin-bottom: 1.25rem;
    }
    
    /* Section titles */
    h3 {
        color: #333 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #f8f9fa;
        border: 2px dashed var(--border-light);
        border-radius: 12px;
        padding: 2.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-teal);
        background: rgba(95, 169, 166, 0.05);
    }
    
    [data-testid="stFileUploader"] label {
        color: #666 !important;
    }
    
    /* Buttons - Red accent for primary */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--accent-red) 0%, #d55e5e 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(231, 111, 111, 0.3);
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(231, 111, 111, 0.4);
        background: linear-gradient(135deg, #ef8080 0%, var(--accent-red) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Center button container */
    .btn-center {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    /* Download button - Teal */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--primary-teal) 0%, var(--dark-teal) 100%);
        box-shadow: 0 4px 16px rgba(95, 169, 166, 0.3);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, var(--light-teal) 0%, var(--primary-teal) 100%);
        box-shadow: 0 6px 24px rgba(95, 169, 166, 0.4);
    }
    
    /* Code block */
    .stCodeBlock {
        background: #f8f9fa !important;
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .stCodeBlock pre {
        background: transparent !important;
        color: #333 !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4caf50;
        border-radius: 8px;
        color: #2e7d32 !important;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid #f44336;
        border-radius: 8px;
        color: #c62828 !important;
    }
    
    .stInfo {
        background: rgba(95, 169, 166, 0.1);
        border: 1px solid var(--primary-teal);
        border-radius: 8px;
        color: var(--dark-teal) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--primary-teal) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Images */
    img {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-teal) !important;
    }
    
    /* Divider */
    hr {
        border-color: #e0e0e0 !important;
        margin: 2rem 0 !important;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: var(--text-light);
        font-size: 0.9rem;
        padding: 2rem 0 1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="badge">FREE AI TOOL</div>
    <div class="main-title">
        <span class="title-icon">📄</span>PDF TO XML
    </div>
    <div class="subtitle">
        Effortlessly convert PDFs into structured XML format with AI-powered precision. Ensure data 
        accuracy, maintain formatting, and simplify document processing in seconds.
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY environment variable not set. Please configure it before running.")
    st.stop()

# Initialize session state
if "xml_content" not in st.session_state:
    st.session_state.xml_content = None
if "xml_path" not in st.session_state:
    st.session_state.xml_path = None

# Main content - simple hero-style uploader and side-by-side preview/output

uploaded_file = st.file_uploader(
    "Browse files",
    type=["pdf"],
    help="Select a PDF document to convert to XML",
    label_visibility="visible"
)

# Centered primary action
btn_col = st.columns([1, 1, 1])
with btn_col[1]:
    generate = st.button("🚀 Generate XML", use_container_width=True, disabled=not uploaded_file)

if uploaded_file and generate:
    with st.spinner("🔄 Converting PDF to XML..."):
        try:
            # Save uploaded file
            temp_dir = tempfile.gettempdir()
            save_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Convert to XML
            tool = PDFtoXMLSchemaTool(api_key=api_key)
            xml_output_path = tool.forward(save_path)
            
            if os.path.exists(xml_output_path):
                with open(xml_output_path, "r", encoding="utf-8") as xml_file:
                    st.session_state.xml_content = xml_file.read()
                    st.session_state.xml_path = xml_output_path
                st.success("✅ XML generated successfully!")
            else:
                st.error(f"❌ Conversion failed: {xml_output_path}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Two columns: preview and output
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 🖼️ PDF Preview")
    if uploaded_file:
        try:
            temp_dir = tempfile.gettempdir()
            save_path = os.path.join(temp_dir, uploaded_file.name)
            
            if not os.path.exists(save_path):
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            doc = fitz.open(save_path)
            first_page = doc[0]
            pix = first_page.get_pixmap(dpi=150)
            img_path = save_path.replace(".pdf", "_preview.png")
            pix.save(img_path)
            
            st.image(img_path, use_container_width=True)
        except Exception as e:
            st.info(f"ℹ️ Preview unavailable: {str(e)}")
    else:
        st.info("Upload a PDF to see a preview here.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### 📋 XML Output")
    
    if st.session_state.xml_content:
        # Display XML
        st.code(st.session_state.xml_content, language="xml", line_numbers=True)
        
        # Download button
        st.download_button(
            label="⬇️ Download XML",
            data=st.session_state.xml_content,
            file_name=os.path.basename(st.session_state.xml_path),
            mime="application/xml",
            use_container_width=True
        )
        
        # Stats
        lines = st.session_state.xml_content.count('\\n') + 1
        size_kb = len(st.session_state.xml_content.encode('utf-8')) / 1024
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        col_a.metric("Lines", f"{lines:,}")
        col_b.metric("Size", f"{size_kb:.1f} KB")
        
    else:
        st.info("👆 Upload a PDF and click Generate to see the XML output here.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer-text">Powered by Groq AI • Built with Streamlit</div>', unsafe_allow_html=True)
