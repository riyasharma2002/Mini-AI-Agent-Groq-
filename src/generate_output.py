# src/generate_output.py
import subprocess
from pathlib import Path

PDF = "data/ukpga_20250022_en.pdf"
CLEAN = "data/ukpga_clean.txt"
SECTIONS = "data/sections.json"
REPORT = "outputs/report.json"

def run_command(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main(use_groq=False, model=None):
    Path("outputs").mkdir(parents=True, exist_ok=True)

    # 1. extract text
    run_command(["python", "src/extract_text.py", PDF, "--out", CLEAN])

    # 2. extract sections
    run_command(["python", "src/extract_sections.py", CLEAN, "--out", SECTIONS])

    # 3. summarize + rule checks
    cmd = ["python", "src/summarize_and_rules.py", SECTIONS, "--out", REPORT]

    if use_groq:
        cmd.append("--use-groq")
        if model:
            cmd += ["--model", model]

    run_command(cmd)
    print("Pipeline completed. Report:", REPORT)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--use-groq", action="store_true", help="Use Groq summarization")
    p.add_argument("--model", default=None, help="Groq model name")
    args = p.parse_args()

    main(use_groq=args.use_groq, model=args.model)
