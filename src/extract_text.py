
import fitz
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        text = page.get_text("text")
        text = text.replace('\r', '\n')
        pages.append(text)
    return "\n\n".join(pages)

def clean_text(raw):
    t = re.sub(r'\n{3,}', '\n\n', raw)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'https?://\S+', '', t)
    lines = [ln.strip() for ln in t.splitlines()]
    lines = [ln for ln in lines if ln != ""]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r'Universal Credit Act\s+2025\s+CHAPTER\s+22',
                     'Universal Credit Act 2025 (CHAPTER 22)', cleaned, flags=re.I)
    return cleaned

def write_clean_text(pdf_path, out_path):
    raw = extract_text_from_pdf(pdf_path)
    cleaned = clean_text(raw)
    Path(out_path).write_text(cleaned, encoding='utf-8')
    return out_path

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Extract and clean PDF text")
    p.add_argument("pdf", help="Path to PDF file")
    p.add_argument("--out", default="data/ukpga_clean.txt", help="Output cleaned text file")
    args = p.parse_args()
    outfile = write_clean_text(args.pdf, args.out)
    print(f"Wrote cleaned text to {outfile}")
