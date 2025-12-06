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

# Teal/Turquoise themed UI
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

    /* Header block */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .badge {
        display: inline-block;
        color: #c0e7e5;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.4rem 0 0.9rem;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .subtitle {
        max-width: 760px;
        margin: 0 auto 1.8rem;
        font-size: 1.05rem;
        color: #e8f4f3;
        line-height: 1.7;
    }

    /* Content cards - subtle translucent panels */
    .content-card {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        height: auto;
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
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        transition: none;
        display: flex;
        justify-content: center;
        margin-top: 1.25rem;
    }
    [data-testid="stFileUploader"] section {
        width: auto !important;
        min-width: 260px;
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
    }
    /* Hide default texts and drag/drop hints; show only the button */
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploaderFileList"],
    [data-testid="stFileUploader"] svg,
    [data-testid="stFileUploader"] div:nth-child(2) {
        display: none !important;
    }
    /* Style the native button */
    [data-testid="stFileUploader"] button {
        visibility: visible !important;
        display: inline-block !important;
        background: linear-gradient(135deg, #e65858 0%, #d94747 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem 2.2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 10px 26px rgba(0,0,0,0.18) !important;
        margin-left: 3rem;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.16) !important;
        border-color: rgba(0,0,0,0.12) !important;
    }
    [data-testid="stFileUploader"] button:active {
        transform: translateY(0);
    }
    [data-testid="stFileUploaderDeleteBtn"] {
        display: none !important;
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
        background: linear-gradient(135deg, #e65858 0%, #d94747 100%);
        box-shadow: 0 8px 20px rgba(226, 88, 88, 0.35);
        color: #ffffff !important;
        border: none !important;
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

center_cols = st.columns([1, 1, 1])
with center_cols[1]:
    uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        label_visibility="collapsed"
    )

# Auto-generate when file is uploaded
if uploaded_file:
    with st.spinner("Converting PDF to XML..."):
        try:
            temp_dir = tempfile.gettempdir()
            save_path = os.path.join(temp_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            tool = PDFtoXMLSchemaTool(api_key=api_key)
            xml_output_path = tool.forward(save_path)

            if os.path.exists(xml_output_path):
                with open(xml_output_path, "r", encoding="utf-8") as xml_file:
                    st.session_state.xml_content = xml_file.read()
                    st.session_state.xml_path = xml_output_path
            else:
                st.session_state.xml_content = None
                st.session_state.xml_path = None
        except Exception:
            st.session_state.xml_content = None
            st.session_state.xml_path = None

# Two columns: preview and output
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    # PDF preview
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
            st.empty()

with col2:
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
        
    else:
        st.empty()

# Remove footer entirely
