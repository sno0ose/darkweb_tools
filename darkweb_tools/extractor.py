#!/usr/bin/env python3
"""
extractor.py
Extract IOCs (emails, IPs, keys, bitcoin addresses, URLs, phone numbers) from raw text/HTML files.

USAGE:
  python3 extractor.py --input evidence/sample.raw.html --output evidence/sample.iocs.json

Output: JSON with lists of findings and basic counts.
NOTE: This is an automated triage tool. Human validation required for context and confidence scoring.
"""

import argparse, re, json
from pathlib import Path

EMAIL_RE = re.compile(rb"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I)
IP_RE = re.compile(rb"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b")
AWS_KEY_RE = re.compile(rb"AKIA[0-9A-Z]{16}")
BTC_RE = re.compile(rb"\\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\\b")
URL_RE = re.compile(rb"https?://[\\w\\-\\./?%&=:#]+", re.I)
PHONE_RE = re.compile(rb"(?:\\+\\d{1,3}[\\s-]?)?(?:\\(\\d+\\)[\\s-]?|\\d{2,4}[\\s-])?\\d{3,4}[\\s-]?\\d{3,4}")

def unique_sorted(items):
    s = set(items)
    return sorted(s)

def extract_bytes(b: bytes):
    findings = {}
    findings["emails"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in EMAIL_RE.findall(b)])
    findings["ips"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in IP_RE.findall(b)])
    findings["aws_keys"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in AWS_KEY_RE.findall(b)])
    findings["bitcoin_addrs"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in BTC_RE.findall(b)])
    findings["urls"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in URL_RE.findall(b)])
    findings["phones"] = unique_sorted([m.decode("utf-8", errors="ignore") for m in PHONE_RE.findall(b)])
    return findings

def main():
    parser = argparse.ArgumentParser(description="Extract IOCs from raw HTML/text files.")
    parser.add_argument("--input", required=True, help="Input file (raw HTML/text)")
    parser.add_argument("--output", required=True, help="Output JSON file for extracted IOCs")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"Input not found: {p}")

    content = p.read_bytes()
    findings = extract_bytes(content)
    # Basic counts
    summary = {k: len(v) for k, v in findings.items()}
    out = {
        "input_file": str(p.resolve()),
        "timestamp_utc": __import__('time').strftime("%Y-%m-%dT%H:%M:%SZ", __import__('time').gmtime()),
        "summary": summary,
        "findings": findings
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[+] Extraction complete. Summary: {summary}")
    print(f"[+] Results written to {args.output}")

if __name__ == "__main__":
    main()
