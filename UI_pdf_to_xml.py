import streamlit as st
from smolagents import Tool
import fitz  # PyMuPDF
import groq  # Import Groq client
import xml.etree.ElementTree as ET
import time
import os
import tempfile
# Streamlit UI
st.set_page_config(page_title="PDF to XML Converter", page_icon="📄", layout="wide")
# Initialize Groq client
client = groq.Client(api_key="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")

class PDFtoXMLSchemaTool(Tool):
    name = "pdf_to_xml_schema"
    description = "Extracts full content from a PDF and generates a structured XML schema without omitting text, symbols, or special formatting."
    inputs = {"pdf_path": {"type": "string", "description": "Path to the PDF document."}}
    output_type = "string"

    def wrap_in_xml(self, content: str) -> str:
        """ Wraps raw content inside XML without modifying it. """
        return f"<fallback>\n<![CDATA[\n{content}\n]]>\n</fallback>"

    def chunk_text(self, text: str, chunk_size: int = 4096) -> list:
        """ Splits text into chunks while preserving structure, including symbols and formatting. """
        sentences = text.split("\n")
        chunks, current_chunk = [], ""

        for sentence in sentences:
            if len(current_chunk.encode('utf-8')) + len(sentence.encode('utf-8')) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def is_content_missing(self, original: str, extracted: str) -> bool:
        """ Ensures extracted XML retains at least 98% of the original content. """
        return (len(extracted.encode('utf-8')) / len(original.encode('utf-8'))) < 0.98 if original else False

    def clean_xml_output(self, xml_string: str) -> str:
        """ Cleans unwanted comments or misplaced formatting hints from XML output. """
        return xml_string.replace("```xml", "").replace("```", "").strip()

    def generate_xml(self, page_text: str, retries: int = 5) -> str:
        """ Calls Groq AI to generate structured XML while handling chunking and retries. """
        for attempt in range(retries):
            try:
                text_chunks = self.chunk_text(page_text)
                full_xml = ""

                for chunk in text_chunks:
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": (
                                "Extract structured content while preserving all text, symbols, emojis, and special formatting. "
                                "Ensure XML hierarchy includes headers, paragraphs, and tables with correct alignment. "
                                "Do not omit any content or modify text formatting."
                            )},
                            {"role": "user", "content": chunk}
                        ]
                    )
                    xml_part = self.clean_xml_output(response.choices[0].message.content.strip())
                    full_xml += xml_part + "\n"
                
                if self.is_valid_xml(full_xml) and not self.is_content_missing(page_text, full_xml):
                    return full_xml
            except Exception as e:
                print(f"Error generating XML (attempt {attempt + 1}): {e}")
                time.sleep(3)

        return self.wrap_in_xml(page_text)

    def is_valid_xml(self, xml_string: str) -> bool:
        """ Validates XML structure. """
        try:
            ET.fromstring(f"<root>{xml_string}</root>")
            return True
        except ET.ParseError:
            return False

    def forward(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            xml_file_path = pdf_path.replace(".pdf", ".xml")

            with open(xml_file_path, "w", encoding="utf-8") as xml_file:
                xml_file.write("<document>\n")
                
                for page_num, page in enumerate(doc, start=1):
                    page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES).strip()
                    if not page_text:
                        continue
                    xml_schema = self.generate_xml(page_text)
                    xml_file.write(f"<page number='{page_num}'>\n{xml_schema}\n</page>\n")
                
                xml_file.write("</document>")
            
            return xml_file_path
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

# Initialize the tool
pdf_to_xml_tool = PDFtoXMLSchemaTool()
st.markdown("""
    <style>
        
            header{
            
            border-bottom: 4px solid red !important;
            }
        .stApp  {
            background: #4ca1af !important;
            font-family: 'Arial', sans-serif;
        }
        h1{
            text-align: center;
            font-weight: 600 !important;
            color: white !important;
            margin:0 !important;
            padding:10px !important;
            }
        h4{
            font-weight: 500 !important;
            text-align: center;
            color: white !important;
               margin:0 !important;
            padding:10px !important;
            }
            h5{
            font-weight: 400 !important;
            text-align: center !important;
            color: white !important;
              margin:0 !important;
            padding:10px !important;
            word-wrap: break-word;  /* Ensure long words wrap */
            white-space: normal;  /* Allow normal wrapping */
            margin:auto !important;
            max-width:800px;
            margin-bottom :20px !important;
            }
       
       [data-testid="stFileUploaderDropzone"]{
            background: #4ca1af !important;
            display: flex;
            max-width: 150px;
            margin:auto !important;
            }
          [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
            }
            section{
            text-align: center !important;
           
            
        }
            [data-testid="stFullScreenFrame"]{
            text-align: center !important;
            display:flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin:auto !important;
            }
           
            pre{
            height: 840px !important;
            }
            [data-testid="stBaseButton-secondary"]
            {
            color: white !important;
            background: linear-gradient(135deg,#e35d5b , #e53935) !important;
            }

            .stFileUploaderFileName {
            color: white !important;
            }
            small{
            color: white !important;}
            [data-testid="stBaseButton-minimal"]{
            color: white !important;
          }
            .stSpinner{
            color: white !important;
           
            }
           .st-ax{
            color : white !important;
            }
            .e1fexwmo1{
            color : darkblue !important;
            }
            
    </style>
""", unsafe_allow_html=True)


st.markdown("""<h4>FREE AI TOOL</h4>""", unsafe_allow_html=True)
st.markdown("""<h1>📄 PDF TO XML</h1>""", unsafe_allow_html=True)
st.markdown("""<h5>Effortlessly convert PDFs into structured XML format with AI-powered precision. 
            Ensure data accuracy, maintain formatting, and simplify document processing in seconds.</h5>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")


if uploaded_file:

    # Use a temporary directory to ensure compatibility across OS
    temp_dir = tempfile.gettempdir()
    save_path = os.path.join(temp_dir, uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)  # Create side-by-side layout

    with col1:
        # 📌 PDF Preview: Display the first page as an image
        try:
            doc = fitz.open(save_path)
            first_page = doc[0]
            pix = first_page.get_pixmap()
            img_path = save_path.replace(".pdf", ".png")
            pix.save(img_path)
            
            st.image(img_path)
        except Exception as e:
            st.error(f"Error generating PDF preview: {e}")

    with col2:
   
            
                with st.spinner("Processing..."):
                    xml_output = pdf_to_xml_tool.forward(save_path)
                    if os.path.exists(xml_output):
                    

                        with open(xml_output, "r", encoding="utf-8") as xml_file:
                            xml_content = xml_file.read()
                            st.code(xml_content, language="xml")  # Show XML preview

                        # Provide download button
                        with open(xml_output, "rb") as xml_file:
                            st.download_button(label="⬇ Download XML", data=xml_file, file_name=os.path.basename(xml_output))
                        # Hide the button after 3 seconds
                    
                    else:
                        st.error("❌ An error occurred during conversion.")

