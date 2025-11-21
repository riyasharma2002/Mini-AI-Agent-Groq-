
import json
import re
from pathlib import Path

def split_by_numeric_headings(text):
    header_re = re.compile(r'^\d+\s+[A-Z][^\n]+', re.M)
    matches = list(header_re.finditer(text))
    sections = {}
    if matches:
        for i, m in enumerate(matches):
            start = m.start()
            title = m.group().strip()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections[title] = body
        return sections
    # fallback
    sections["full_text"] = text
    return sections

def save_sections(sections, out_file):
    Path(out_file).write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding='utf-8')

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("clean_text", help="Path to cleaned text file")
    p.add_argument("--out", default="data/sections.json", help="Output JSON file")
    args = p.parse_args()
    text = Path(args.clean_text).read_text(encoding='utf-8')
    sections = split_by_numeric_headings(text)
    save_sections(sections, args.out)
    print(f"Wrote {len(sections)} sections to {args.out}")
