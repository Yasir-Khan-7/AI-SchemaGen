# ============================================================================
# PDF to XML Schema Generator
# Converts PDF documents into structured XML format using AI-powered extraction
# ============================================================================

from smolagents import Tool  # Agent framework for tool definitions
import fitz  # PyMuPDF library for reading PDF files
import groq  # Groq API client for AI-powered content processing
import xml.etree.ElementTree as ET  # XML parsing and validation
import time  # For handling delays and retries
import os  # For environment variable access

# ============================================================================
# CONFIGURATION: Groq API Setup
# ============================================================================
# Retrieve Groq API key from environment variables (for security)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("Set GROQ_API_KEY in your environment before running.")

# Initialize Groq client for AI API calls
client = groq.Client(api_key=api_key)

# ============================================================================
# PDFtoXMLSchemaTool: Main Tool Class
# ============================================================================
# This tool extracts content from PDFs and converts it into structured XML
# format using AI, preserving all text, symbols, and special formatting
class PDFtoXMLSchemaTool(Tool):
    name = "pdf_to_xml_schema"
    description = "Extracts full content from a PDF and generates a structured XML schema without omitting text, symbols, or special formatting."
    inputs = {"pdf_path": {"type": "string", "description": "Path to the PDF document."}}
    output_type = "string"

    # ========================================================================
    # Method: wrap_in_xml()
    # ========================================================================
    # Fallback method: wraps raw content in XML CDATA section when structured
    # XML generation fails. This ensures no content is lost.
    # CDATA prevents XML special characters (&, <, >) from causing parse errors
    def wrap_in_xml(self, content: str) -> str:
        return f"<fallback>\n<![CDATA[\n{content}\n]]>\n</fallback>"

    # ========================================================================
    # Method: chunk_text()
    # ========================================================================
    # Splits large text into manageable chunks (default 4096 bytes) for API
    # processing. Splits by lines to maintain paragraph structure.
    # This prevents hitting API token limits on large documents.
    # ========================================================================
    # Method: chunk_text()
    # ========================================================================
    # Splits large text into manageable chunks (default 4096 bytes) for API
    # processing. Splits by lines to maintain paragraph structure.
    # This prevents hitting API token limits on large documents.
    def chunk_text(self, text: str, chunk_size: int = 4096) -> list:
        """ Splits text into chunks while preserving structure, including symbols and formatting. """
        sentences = text.split("\n")  # Split by newlines to preserve structure
        chunks, current_chunk = [], ""

        for sentence in sentences:
            # Add sentence to current chunk if it fits within chunk_size
            if len(current_chunk.encode('utf-8')) + len(sentence.encode('utf-8')) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                # Chunk is full, save it and start a new one
                chunks.append(current_chunk.strip())
                current_chunk = sentence + "\n"

        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    # ========================================================================
    # Method: is_content_missing()
    # ========================================================================
    # Quality check: ensures extracted XML retains at least 98% of original
    # content. Returns True if content loss is detected.
    # ========================================================================
    # Method: is_content_missing()
    # ========================================================================
    # Quality check: ensures extracted XML retains at least 98% of original
    # content. Returns True if content loss is detected.
    def is_content_missing(self, original: str, extracted: str) -> bool:
        """ Ensures extracted XML retains at least 98% of the original content. """
        return (len(extracted.encode('utf-8')) / len(original.encode('utf-8'))) < 0.98 if original else False

    # ========================================================================
    # Method: clean_xml_output()
    # ========================================================================
    # Removes common formatting artifacts from AI-generated XML, such as
    # markdown code blocks (```xml) that shouldn't be in XML output
    # ========================================================================
    # Method: clean_xml_output()
    # ========================================================================
    # Removes common formatting artifacts from AI-generated XML, such as
    # markdown code blocks (```xml) that shouldn't be in XML output
    def clean_xml_output(self, xml_string: str) -> str:
        """ Cleans unwanted comments or misplaced formatting hints from XML output. """
        return xml_string.replace("```xml", "").replace("```", "").strip()

    # ========================================================================
    # Method: generate_xml()
    # ========================================================================
    # Core method: calls Groq AI to convert PDF text into structured XML.
    # Implements retry logic (up to 5 attempts) for reliability.
    # Falls back to CDATA wrapping if structured XML generation fails.
    # - Splits large text into chunks
    # - Sends each chunk to AI for XML conversion
    # - Validates output (checks XML syntax and content retention)
    def generate_xml(self, page_text: str, retries: int = 5) -> str:
        """ Calls Groq AI to generate structured XML while handling chunking and retries. """
        for attempt in range(retries):
            try:
                text_chunks = self.chunk_text(page_text)  # Split text into manageable chunks
                full_xml = ""

                # Process each chunk through the AI
                for chunk in text_chunks:
                    response = client.chat.completions.create(
                        model="qwen-2.5-32b",  # AI model for content processing
                        messages=[
                            # System instruction: tells AI to preserve everything
                            {"role": "system", "content": (
                                "Extract structured content while preserving all text, symbols, emojis, and special formatting. "
                                "Ensure XML hierarchy includes headers, paragraphs, and tables with correct alignment. "
                                "Do not omit any content or modify text formatting."
                            )},
                            # User message: the actual PDF text chunk to convert
                            {"role": "user", "content": chunk}
                        ]
                    )
                    # Extract and clean XML from AI response
                    xml_part = self.clean_xml_output(response.choices[0].message.content.strip())
                    full_xml += xml_part + "\n"
                
                # Validate: is XML well-formed and no content lost?
                if self.is_valid_xml(full_xml) and not self.is_content_missing(page_text, full_xml):
                    return full_xml
            except Exception as e:
                print(f"Error generating XML (attempt {attempt + 1}): {e}")
                time.sleep(3)  # Wait before retry to avoid rate limiting

        # All retries failed, return content wrapped in CDATA as fallback
        return self.wrap_in_xml(page_text)

    # ========================================================================
    # Method: is_valid_xml()
    # ========================================================================
    # Validates that generated XML is well-formed and parseable.
    # Wraps content in temporary root element for parsing.
    # ========================================================================
    # Method: is_valid_xml()
    # ========================================================================
    # Validates that generated XML is well-formed and parseable.
    # Wraps content in temporary root element for parsing.
    def is_valid_xml(self, xml_string: str) -> bool:
        """ Validates XML structure. """
        try:
            # Wrap in <root> tags to ensure valid XML document structure
            ET.fromstring(f"<root>{xml_string}</root>")
            return True
        except ET.ParseError:
            # XML parsing failed - structure is invalid
            return False

    # ========================================================================
    # Method: forward()
    # ========================================================================
    # Main processing method: orchestrates PDF reading and XML conversion
    # Steps:
    # 1. Open PDF file using PyMuPDF
    # 2. Create output XML file
    # 3. Extract text from each page
    # 4. Convert each page to XML
    # 5. Write all pages to XML file
    def forward(self, pdf_path: str) -> str:
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            # Generate output XML filename by replacing .pdf extension with .xml
            xml_file_path = pdf_path.replace(".pdf", ".xml")

            # Create and write to XML file
            with open(xml_file_path, "w", encoding="utf-8") as xml_file:
                # Write XML document header
                xml_file.write("<document>\n")
                
                # Process each page in the PDF
                for page_num, page in enumerate(doc, start=1):
                    # Extract text from page, preserving ligatures (fi, fl, etc.)
                    page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES).strip()
                    
                    # Skip empty pages
                    if not page_text:
                        continue
                    
                    # Convert page text to XML using AI
                    xml_schema = self.generate_xml(page_text)
                    # Write page wrapped with page number attribute
                    xml_file.write(f"<page number='{page_num}'>\n{xml_schema}\n</page>\n")
                
                # Close XML document
                xml_file.write("</document>")
            
            # Return success message with output path
            return f"XML schema saved to {xml_file_path}"
        except Exception as e:
            # Return error message if processing fails
            return f"Error processing PDF: {str(e)}"

# ============================================================================
# TOOL INITIALIZATION
# ============================================================================
# Create a global instance of the PDF to XML tool
pdf_to_xml_tool = PDFtoXMLSchemaTool()

# ============================================================================
# MAIN EXECUTION
# ============================================================================
# Run the tool when script is executed directly
if __name__ == "__main__":
    pdf_path = "sample.pdf"  # Replace with actual PDF path
    xml_schema = pdf_to_xml_tool.forward(pdf_path)
    print(xml_schema)

