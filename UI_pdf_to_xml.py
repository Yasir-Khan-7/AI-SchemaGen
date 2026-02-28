import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
from app.utils.pdf_to_xml import PDFtoXMLSchemaTool

st.set_page_config(
    page_title="PDF to XML Converter | AI-SchemaGen",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: rgba(255, 255, 255, 0.03);
        --bg-card-hover: rgba(255, 255, 255, 0.06);
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-accent: rgba(99, 102, 241, 0.3);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-violet: #8b5cf6;
        --accent-indigo: #6366f1;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --gradient-primary: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
        --gradient-accent: linear-gradient(135deg, #06b6d4, #8b5cf6);
        --gradient-bg: linear-gradient(180deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%);
        --glass: rgba(255, 255, 255, 0.02);
        --glass-border: rgba(255, 255, 255, 0.05);
        --shadow-glow: 0 0 60px rgba(99, 102, 241, 0.08);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    * {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }

    .stApp {
        background: var(--gradient-bg);
        color: var(--text-primary);
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* ── Animated background orbs ── */
    .bg-orbs {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .bg-orbs .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.15;
        animation: float 20s ease-in-out infinite;
    }
    .bg-orbs .orb-1 {
        width: 600px; height: 600px;
        background: var(--accent-violet);
        top: -200px; right: -100px;
        animation-delay: 0s;
    }
    .bg-orbs .orb-2 {
        width: 500px; height: 500px;
        background: var(--accent-cyan);
        bottom: -150px; left: -100px;
        animation-delay: -7s;
    }
    .bg-orbs .orb-3 {
        width: 300px; height: 300px;
        background: var(--accent-indigo);
        top: 40%; left: 50%;
        animation-delay: -14s;
    }
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -20px) scale(1.05); }
        66% { transform: translate(-20px, 15px) scale(0.95); }
    }

    /* ── Top nav bar ── */
    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .nav-logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .nav-logo-icon {
        width: 36px; height: 36px;
        background: var(--gradient-primary);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
    }
    .nav-logo-text {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }
    .nav-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #a5b4fc !important;
        letter-spacing: 0.04em;
    }
    .nav-badge-dot {
        width: 6px; height: 6px;
        background: var(--accent-emerald);
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ── Hero section ── */
    .hero {
        text-align: center;
        padding: 3rem 1rem 2rem;
        position: relative;
    }
    .hero-overline {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 1rem;
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #a5b4fc !important;
        margin-bottom: 1.5rem;
        letter-spacing: 0.03em;
    }
    .hero h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.03em;
        margin: 0 0 1rem !important;
        color: var(--text-primary) !important;
    }
    .hero h1 .gradient-text {
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        max-width: 580px;
        margin: 0 auto 2rem;
        font-size: 1.1rem;
        color: var(--text-secondary) !important;
        line-height: 1.7;
        font-weight: 400;
    }

    /* ── Feature pills ── */
    .feature-pills {
        display: flex;
        justify-content: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 2.5rem;
    }
    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.45rem 0.9rem;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 100px;
        font-size: 0.82rem;
        color: var(--text-secondary) !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .feature-pill:hover {
        border-color: var(--border-accent);
        background: rgba(99, 102, 241, 0.05);
    }
    .feature-pill-icon {
        font-size: 0.9rem;
    }

    /* ── Glass card (upload / output containers) ── */
    .glass-card {
        background: var(--glass);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.8rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: var(--border-accent);
        box-shadow: var(--shadow-glow);
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1.2rem;
    }
    .card-icon {
        width: 32px; height: 32px;
        background: var(--gradient-primary);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em;
    }
    .card-subtitle {
        font-size: 0.78rem;
        color: var(--text-muted) !important;
    }

    /* ── Upload area ── */
    .upload-zone {
        border: 2px dashed rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: rgba(99, 102, 241, 0.03);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
    }
    .upload-zone:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(99, 102, 241, 0.06);
    }
    .upload-icon-wrapper {
        width: 64px; height: 64px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.2rem;
        font-size: 1.5rem;
    }
    .upload-text {
        font-size: 0.95rem;
        color: var(--text-secondary) !important;
        margin-bottom: 0.4rem;
    }
    .upload-text strong {
        color: #a5b4fc !important;
    }
    .upload-hint {
        font-size: 0.78rem;
        color: var(--text-muted) !important;
    }

    /* ── File uploader overrides ── */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploaderFileList"],
    [data-testid="stFileUploader"] svg {
        display: none !important;
    }
    [data-testid="stFileUploader"] button {
        background: var(--gradient-primary) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4) !important;
    }
    [data-testid="stFileUploaderDeleteBtn"] {
        display: none !important;
    }

    /* ── Processing state ── */
    .processing-card {
        text-align: center;
        padding: 2rem;
    }
    .processing-spinner {
        display: inline-block;
        width: 48px; height: 48px;
        border: 3px solid rgba(99, 102, 241, 0.15);
        border-top-color: var(--accent-indigo);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-bottom: 1rem;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* ── Buttons ── */
    .stButton > button {
        width: 100%;
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        padding: 0.85rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25) !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    .stDownloadButton > button {
        background: var(--gradient-primary) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4) !important;
    }

    /* ── Code block (XML output) ── */
    .stCodeBlock {
        background: var(--bg-secondary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-subtle) !important;
        max-height: 550px;
        overflow-y: auto;
    }
    .stCodeBlock pre {
        background: transparent !important;
        color: #e2e8f0 !important;
        font-size: 0.85rem !important;
        line-height: 1.65 !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    }
    .stCodeBlock code {
        font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    }

    /* ── Status messages ── */
    .stSuccess {
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 12px !important;
        color: #6ee7b7 !important;
    }
    .stError {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
    }
    .stInfo {
        background: rgba(99, 102, 241, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        color: #a5b4fc !important;
    }
    .stWarning {
        background: rgba(245, 158, 11, 0.08) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: 12px !important;
        color: #fcd34d !important;
    }

    /* ── Spinner override ── */
    .stSpinner > div {
        border-top-color: var(--accent-indigo) !important;
    }
    [data-testid="stStatusWidget"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
    }

    /* ── Image preview ── */
    img {
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }

    /* ── Stats row ── */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin-top: 1.2rem;
    }
    .stat-item {
        flex: 1;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #a5b4fc !important;
    }
    .stat-label {
        font-size: 0.72rem;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.15rem;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 2.5rem 0 1rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-subtle);
    }
    .footer-text {
        font-size: 0.82rem;
        color: var(--text-muted) !important;
    }
    .footer-text a {
        color: #a5b4fc !important;
        text-decoration: none;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    /* ── Horizontal rule ── */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 2rem 0 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--border-subtle);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #a5b4fc !important;
        border-bottom: 2px solid var(--accent-indigo) !important;
    }

    /* ── Column gap fix ── */
    [data-testid="stHorizontalBlock"] {
        gap: 1.5rem;
    }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .hero h1 {
            font-size: 2.2rem !important;
        }
        .feature-pills {
            gap: 0.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Background orbs
st.markdown("""
<div class="bg-orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)

# Navigation bar
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">
        <div class="nav-logo-icon">⚡</div>
        <span class="nav-logo-text">AI-SchemaGen</span>
    </div>
    <div class="nav-badge">
        <span class="nav-badge-dot"></span>
        Powered by Llama 4 Maverick
    </div>
</div>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">
    <div class="hero-overline">✦ Free AI-Powered Tool</div>
    <h1>Convert PDF to<br><span class="gradient-text">Structured XML</span></h1>
    <p class="hero-subtitle">
        Transform your PDF documents into clean, well-structured XML with AI precision.
        Preserves formatting, maintains data accuracy, and delivers results in seconds.
    </p>
    <div class="feature-pills">
        <span class="feature-pill"><span class="feature-pill-icon">🧠</span> AI-Powered</span>
        <span class="feature-pill"><span class="feature-pill-icon">⚡</span> Fast Processing</span>
        <span class="feature-pill"><span class="feature-pill-icon">🎯</span> High Accuracy</span>
        <span class="feature-pill"><span class="feature-pill-icon">📐</span> Semantic Tags</span>
        <span class="feature-pill"><span class="feature-pill-icon">🔒</span> Secure</span>
    </div>
</div>
""", unsafe_allow_html=True)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY environment variable not set. Please configure it before running.")
    st.stop()

if "xml_content" not in st.session_state:
    st.session_state.xml_content = None
if "xml_path" not in st.session_state:
    st.session_state.xml_path = None

# Upload area
st.markdown("""
<div class="upload-zone">
    <div class="upload-icon-wrapper">📄</div>
    <p class="upload-text"><strong>Click below</strong> to upload your PDF</p>
    <p class="upload-hint">Supports PDF files up to 200MB</p>
</div>
""", unsafe_allow_html=True)

upload_cols = st.columns([1, 2, 1])
with upload_cols[1]:
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

if uploaded_file:
    with st.spinner("Analyzing document and generating XML..."):
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

# Results section
if uploaded_file:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon">📄</div>
                <div>
                    <div class="card-title">PDF Preview</div>
                    <div class="card-subtitle">First page of your document</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

            page_count = len(doc)
            file_size_kb = round(os.path.getsize(save_path) / 1024, 1)
            st.markdown(f"""
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-value">{page_count}</div>
                    <div class="stat-label">Pages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{file_size_kb} KB</div>
                    <div class="stat-label">File Size</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            doc.close()
        except Exception:
            st.empty()

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon">📋</div>
                <div>
                    <div class="card-title">XML Output</div>
                    <div class="card-subtitle">AI-generated structured markup</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.xml_content:
            st.code(st.session_state.xml_content, language="xml", line_numbers=True)

            xml_size_kb = round(len(st.session_state.xml_content.encode("utf-8")) / 1024, 1)
            tag_count = st.session_state.xml_content.count("<")
            st.markdown(f"""
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-value">{xml_size_kb} KB</div>
                    <div class="stat-label">XML Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{tag_count}</div>
                    <div class="stat-label">Tags</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="Download XML File",
                data=st.session_state.xml_content,
                file_name=os.path.basename(st.session_state.xml_path),
                mime="application/xml",
                use_container_width=True
            )
        else:
            st.info("Processing your document... XML output will appear here once complete.")

st.markdown("""
<div class="footer">
    <p class="footer-text">
        Built with AI-SchemaGen &middot; Powered by Groq &middot; Made with Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
