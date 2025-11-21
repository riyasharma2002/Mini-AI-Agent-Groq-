# Universal Credit Act 2025 — Mini AI Agent (Groq)

This project extracts, summarizes, and analyses the `Universal Credit Act 2025` PDF and produces a structured JSON report.

## Features
- PDF extraction (PyMuPDF)
- Section splitting (regex)
- Abstractive summary using Groq (optional)
- Extraction of legislative sections (definitions, obligations, etc.)
- 6 rule checks
- Output: `outputs/report.json`

## Install & Run

### 1. Clone / prepare repo
Put PDF at: `data/ukpga_20250022_en.pdf`

### 2. Create virtualenv and install
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
