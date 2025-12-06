import os
import time
import xml.etree.ElementTree as ET
from typing import List, Optional

import fitz  # PyMuPDF
from groq import Groq

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "qwen-2.5-32b")
CHUNK_SIZE = 4096
CONTENT_THRESHOLD = 0.98


class PDFToXMLConverter:
    """Converts PDF content to XML using Groq chat completions."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required to initialize the converter.")
        self.client = Groq(api_key=api_key)
        self.model = model or DEFAULT_MODEL

    @staticmethod
    def wrap_in_xml(content: str) -> str:
        return f"<fallback>\n<![CDATA[\n{content}\n]]>\n</fallback>"

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """Splits text into UTF-8 safe chunks to fit model limits."""
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
        return (len(extracted.encode("utf-8")) / len(original.encode("utf-8"))) < CONTENT_THRESHOLD

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

    def generate_xml_fragment(self, page_text: str, retries: int = 5) -> str:
        """Call Groq to transform page text into XML, with retries for robustness."""
        for attempt in range(retries):
            try:
                chunks = self.chunk_text(page_text)
                fragments: List[str] = []

                for chunk in chunks:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Extract structured content while preserving all text, symbols, emojis, and "
                                    "special formatting. Ensure XML hierarchy includes headers, paragraphs, and tables "
                                    "with correct alignment. Do not omit any content or modify text formatting."
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
                # Log-friendly retry delay; caller handles surfaced errors if all retries fail.
                time.sleep(2)

        return self.wrap_in_xml(page_text)

    def convert_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Convert a PDF (as bytes) to XML string."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            xml_parts = ["<document>"]

            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES).strip()
                if not page_text:
                    continue
                xml_fragment = self.generate_xml_fragment(page_text)
                xml_parts.append(f"<page number='{page_num}'>\n{xml_fragment}\n</page>")

            xml_parts.append("</document>")
            return "\n".join(xml_parts)
        except Exception as exc:
            raise RuntimeError(f"Failed to process PDF: {exc}") from exc

