
import os
import json
import re
from pathlib import Path

# Try to import Groq client
try:
    from groq import Groq
except Exception:
    Groq = None

def groq_summarize(text, max_bullets=8, model="llama3-70b-8192"):
    """
    Uses the Groq SDK to produce bullets. Requires GROQ_API_KEY in env.
    """
    if Groq is None:
        raise RuntimeError("groq SDK not installed or failed to import.")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Please set GROQ_API_KEY environment variable.")
    client = Groq(api_key=api_key)

    # Build prompt
    system_msg = (
        "You are a helpful assistant specialized in summarizing legal acts. "
        "Produce 5-10 concise bullet points covering: purpose, key definitions, eligibility, obligations, enforcement elements."
    )
    user_msg = f"TEXT:\n\n{text[:20000]}\n\nReturn bullet points, one per line."

    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=800,
        temperature=0.0
    )
    
    content = None
    if hasattr(resp, "choices"):
        
        try:
            content = resp.choices[0].message["content"]
        except Exception:
            try:
                content = resp.choices[0].message_content
            except Exception:
                content = str(resp)
    else:
        content = str(resp)

    # Normalize into bullets
    bullets = [b.strip(" -•\t\n") for b in re.split(r'\n+', content) if b.strip()]
    return bullets[:max_bullets]

def heuristic_summary(sections):
    bullets = []
    for title, body in sections.items():
        first_line = body.splitlines()[0] if body else ""
        candidate = f"{title}: {first_line[:220].strip()}"
        bullets.append(candidate)
        if len(bullets) >= 10:
            break
    if len(bullets) < 5:
        bullets += ["See the Act for details."] * (5 - len(bullets))
    return bullets[:10]

def extract_key_texts(sections):
    categories = {
        "definitions": ["definition", "means", "interpretation", "defined"],
        "obligations": ["must", "exercise", "oblig", "secure"],
        "responsibilities": ["Secretary of State", "Department for Communities", "responsib", "must exercise"],
        "eligibility": ["pre-2026 claimant", "severe conditions", "terminally ill", "entitled", "claimant"],
        "payments": ["standard allowance", "LCWRA element", "ESA IR", "uplift percentage", "relevant CPI"],
        "penalties": ["penalt", "enforce", "offence", "recovery"],
        "record_keeping": ["assessment", "medical", "relevant evidence", "regulation 41", "regulation 43"]
    }
    joined = "\n\n".join(v for v in sections.values()).lower()
    out = {}
    for k, kws in categories.items():
        hits = []
        for kw in kws:
            idx = joined.find(kw.lower())
            if idx != -1:
                start = max(0, joined.rfind('\n', 0, idx))
                end = joined.find('\n', idx+250)
                snippet = joined[start:end].strip()
                hits.append(snippet)
        out[k] = "\n\n".join(hits[:6]) if hits else ""
    return out

def run_rule_checks(sections):
    combined = "\n\n".join(sections.values()).lower()
    checks = []
    rules = [
        ("Act must define key terms", ["definition", "means", "interpretation"]),
        ("Act must specify eligibility criteria", ["pre-2026 claimant", "severe conditions", "terminally ill", "entitled"]),
        ("Act must specify responsibilities of the administering authority", ["secretary of state must", "department for communities", "must exercise the power"]),
        ("Act must include enforcement or penalties", ["penalt", "enforce", "social security administration act 1992"]),
        ("Act must include payment calculation or entitlement structure", ["standard allowance", "relevant cpi percentage", "uplift percentage", "lcwra element"]),
        ("Act must include record-keeping or reporting requirements", ["relevant evidence", "assessment", "medical examination", "regulation 41", "regulation 43"])
    ]
    for rule, phrases in rules:
        evidence = None
        for p in phrases:
            i = combined.find(p)
            if i != -1:
                start = max(0, combined.rfind('\n', 0, i))
                end = combined.find('\n', i+200)
                evidence = combined[start:end].strip()
                break
        if evidence:
            status = "pass"
            confidence = 90
        else:
            status = "partial_pass" if "regulation" in combined else "fail"
            confidence = 65 if status == "partial_pass" else 40
        checks.append({
            "rule": rule,
            "status": status,
            "evidence": evidence or "No clear literal match found; closest scan used.",
            "confidence": confidence
        })
    return checks

def build_report(sections, use_groq=False, groq_model="llama3-70b-8192"):
    joined = "\n\n".join(sections.values())
    if use_groq:
        try:
            bullets = groq_summarize(joined, max_bullets=8, model=groq_model)
        except Exception as e:
            print("Groq summarization failed; falling back to heuristic summary. Error:", e)
            bullets = heuristic_summary(sections)
    else:
        bullets = heuristic_summary(sections)
    keys = extract_key_texts(sections)
    report = {
        "summary": bullets,
        "sections": {
            "definitions": keys["definitions"],
            "obligations": keys["obligations"],
            "responsibilities": keys["responsibilities"],
            "eligibility": keys["eligibility"],
            "payments": keys["payments"],
            "penalties": keys["penalties"],
            "record_keeping": keys["record_keeping"]
        },
        "rule_checks": run_rule_checks(sections)
    }
    return report

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("sections_json", help="JSON file from extract_sections.py")
    p.add_argument("--out", default="outputs/report.json", help="Output JSON file")
    p.add_argument("--use-groq", action="store_true", help="Use Groq for abstractive summarization")
    p.add_argument("--model", default="llama3-70b-8192", help="Groq model to use (default llama3-70b-8192)")
    args = p.parse_args()
    sections = json.loads(Path(args.sections_json).read_text(encoding='utf-8'))
    report = build_report(sections, use_groq=args.use_groq, groq_model=args.model)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote final report to {args.out}")
