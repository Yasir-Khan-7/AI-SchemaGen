import os
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core import PDFToXMLConverter

app = FastAPI(title="AI SchemaGen API", version="0.1.0")

allowed_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
origins: List[str] = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_converter: PDFToXMLConverter | None = None


def get_converter() -> PDFToXMLConverter:
    global _converter
    if _converter is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to your environment.")
        model = os.getenv("GROQ_MODEL")
        _converter = PDFToXMLConverter(api_key=api_key, model=model)
    return _converter


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate")
async def generate(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        converter = get_converter()
        xml_content = converter.convert_pdf_bytes(pdf_bytes)
        safe_name = file.filename.rsplit(".", 1)[0] or "output"
        return {"xml": xml_content, "filename": f"{safe_name}.xml"}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

