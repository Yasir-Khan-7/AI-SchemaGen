import os
from backend.core.pdf_to_xml import PDFToXMLConverter

# Example: standalone CLI usage (optional)
if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        exit(1)
    
    converter = PDFToXMLConverter(api_key=api_key)
    
    # Replace with your PDF path
    pdf_path = "sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found")
        exit(1)
    
    print(f"Converting {pdf_path} to XML...")
    result = converter.convert(pdf_path)
    
    if result["success"]:
        xml_path = result["xml_path"]
        print(f"✓ Success! XML saved to: {xml_path}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")

