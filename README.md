# PDF to XML (AI-powered Streamlit app)

A simple, one-page Streamlit experience: upload a PDF, preview it, and instantly download AI-generated XML that preserves the document structure. Uses Groq for fast LLM-powered extraction and PyMuPDF for robust PDF text handling.

## Features
- **One-step convert**: Upload PDF, auto-generate XML, preview and download.
- **Structure aware**: Titles, headings, paragraphs, lists, and inline symbols preserved where possible.
- **Modern UI**: Clean teal theme with prominent red CTAs, side-by-side preview/output.
- **Resilient XML cleaning**: Basic validation and sanitization to keep XML well-formed.
- **Environment-based secrets**: `GROQ_API_KEY` loaded via `.env` (not committed).

## Stack
- **Frontend/UI**: Streamlit
- **AI/LLM**: Groq chat completions API
- **PDF parsing**: PyMuPDF (`fitz`)
- **HTTP**: `requests`
- **Config**: `.env` for `GROQ_API_KEY`

## How it works
1. User uploads a PDF via Streamlit file uploader.
2. PDF text is extracted per page with PyMuPDF.
3. Each page (chunked if needed) is sent to Groq to generate structured XML.
4. XML fragments are concatenated, lightly validated/cleaned, and written to disk.
5. Streamlit displays a side-by-side PDF preview and XML output with a download button.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # create and set GROQ_API_KEY
```

## Run locally
```bash
source .venv/bin/activate
set -a && source .env && set +a
streamlit run UI_pdf_to_xml.py --server.port 8501
```
Then open http://localhost:8501.

## Environment
- `GROQ_API_KEY` (required)

## Notes on AI usage
- The app calls Groq chat completions to transform page text into XML with hierarchical tags (headings, paragraphs, lists).
- Simple validation guards against malformed XML; if validation fails after retries, content is wrapped safely.
- Keep PDFs text-based for best results; heavy scanned PDFs may need OCR first.

## Security
- Do **not** commit `.env` or any secrets.
- `.gitignore` already excludes common secret paths.

## Project layout
- `UI_pdf_to_xml.py` — Streamlit UI + flow.
- `app/utils/pdf_to_xml.py` — PDF → XML conversion logic (Groq + PyMuPDF + cleaning).
- `app/styles/theme.css` — extra styling (if used).
- `requirements.txt` — dependencies.

## Troubleshooting
- If Groq errors: confirm `GROQ_API_KEY` is set and valid.
- If XML is empty/fallback: ensure PDF has extractable text; scanned docs may need OCR.
- If port in use: change `--server.port` flag when running Streamlit.
