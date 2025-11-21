# Mini-AI-Agent-Groq-
This project acts like a mini AI legal agent.   It reads the *Universal Credit Act 2025* PDF, breaks it into sections, summarizes them using Groq, performs rule checks, and finally produces a clean JSON report
This project works like a mini AI legal assistant. It reads the PDF, breaks it into meaningful sections, summarizes them, runs a few rule checks, and finally creates a clean JSON report This project reads the Universal Credit Act 2025 PDF, breaks it into sections, summarizes it, checks important rules, and finally creates a clean JSON report.
Features

* PDF extraction (PyMuPDF)
* Section splitting (regex)
* Abstractive summary using Groq
* Extraction of legislative sections (definitions, obligations, etc.)
* 6 rule checks
* Output: outputs/report.json
Install & Run

1. Clone / prepare repo

Put PDF at: data/ukpga_20250022_en.pdf
2. Create a Virtual Environment

Run in terminal: python -m venv venv
3. Activate environment:

Mac / Linux: source venv/bin/activate
Windows: venv\Scripts\activate ###4. Install Dependencies pip install -r requirements.txt
5 Run the Script

python main.py
6 Output Location

After running successfully, the final JSON report will be created at:
outputs/report.json
