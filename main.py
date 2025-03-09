from smolagents import Tool
import fitz  # PyMuPDF
import groq  # Import Groq client
import xml.etree.ElementTree as ET
import time

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
                        model="qwen-2.5-32b",
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
            
            return f"XML schema saved to {xml_file_path}"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

# Initialize the tool
pdf_to_xml_tool = PDFtoXMLSchemaTool()

# Example usage
pdf_path = "CATL_ESS_ModbusTCP_Communication_Protocol_Between_BMS_and_BSC_removed.pdf"  # Replace with actual PDF path
xml_schema = pdf_to_xml_tool.forward(pdf_path)
print(xml_schema)


