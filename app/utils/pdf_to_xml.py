import os
import time
import xml.etree.ElementTree as ET
from typing import List

import fitz  # PyMuPDF
import groq


class PDFtoXMLSchemaTool:
    """
    Converts PDF content to structured XML via Groq.
    Usage:
        tool = PDFtoXMLSchemaTool(api_key="...")
        xml = tool.forward("/path/to/file.pdf")
    """

    def __init__(self, api_key: str, model: str = "meta-llama/llama-4-maverick-17b-128e-instruct"):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required.")
        self.client = groq.Client(api_key=api_key)
        self.model = model

    @staticmethod
    def wrap_in_xml(content: str) -> str:
        return f"<fallback>\n<![CDATA[\n{content}\n]]>\n</fallback>"

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 4096) -> List[str]:
        sentences = text.split("\n")
        chunks: List[str] = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk.encode("utf-8")) + len(sentence.encode("utf-8")) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def is_content_missing(original: str, extracted: str) -> bool:
        if not original:
            return False
        return (len(extracted.encode("utf-8")) / len(original.encode("utf-8"))) < 0.98

    @staticmethod
    def clean_xml_output(xml_string: str) -> str:
        return xml_string.replace("```xml", "").replace("```", "").strip()

    @staticmethod
    def is_valid_xml(xml_string: str) -> bool:
        try:
            ET.fromstring(f"<root>{xml_string}</root>")
            return True
        except ET.ParseError:
            return False

    def generate_xml(self, page_text: str, retries: int = 5) -> str:
        for attempt in range(retries):
            try:
                fragments = []
                for chunk in self.chunk_text(page_text):
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Extract structured content while preserving all text, symbols, emojis, and special formatting. "
                                    "Ensure XML hierarchy includes headers, paragraphs, and tables with correct alignment. "
                                    "Do not omit any content or modify text formatting."
                                ),
                            },
                            {"role": "user", "content": chunk},
                        ],
                    )
                    fragment = self.clean_xml_output(response.choices[0].message.content.strip())
                    fragments.append(fragment)

                full_xml = "\n".join(fragments)
                if self.is_valid_xml(full_xml) and not self.is_content_missing(page_text, full_xml):
                    return full_xml
            except Exception:
                time.sleep(2)

        return self.wrap_in_xml(page_text)

    def forward(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            xml_file_path = pdf_path.replace(".pdf", ".xml")
            xml_parts = ["<document>"]

            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES).strip()
                if not page_text:
                    continue
                xml_fragment = self.generate_xml(page_text)
                xml_parts.append(f"<page number='{page_num}'>\n{xml_fragment}\n</page>")

            xml_parts.append("</document>")

            with open(xml_file_path, "w", encoding="utf-8") as xml_file:
                xml_file.write("\n".join(xml_parts))

            return xml_file_path
        except Exception as exc:
            return f"Error processing PDF: {exc}"

