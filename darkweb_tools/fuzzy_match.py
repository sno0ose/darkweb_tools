#!/usr/bin/env python3
"""
fuzzy_match.py
Match discovered strings (emails, names) against an employee roster using fuzzy matching.
USAGE:
  python3 fuzzy_match.py --roster employees.csv --discovered discoveries.txt --output matches.csv
Requires: rapidfuzz (recommended) -> pip3 install rapidfuzz
Falls back to simple substring matching if rapidfuzz is unavailable.
"""

import argparse, csv, sys
from pathlib import Path

try:
    from rapidfuzz import process, fuzz
    HAVE_RAPIDFUZZ = True
except Exception:
    HAVE_RAPIDFUZZ = False

def load_roster(path):
    roster = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Expect fields: name, email (best effort)
            roster.append({"name": r.get("name","").strip(), "email": r.get("email","").strip()})
    return roster

def load_discovered(path):
    with open(path, encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

def simple_match(item, roster):
    results = []
    low = item.lower()
    for idx, r in enumerate(roster):
        score = 100 if (low == r.get("email","").lower()) else (50 if low in r.get("name","").lower() else 0)
        results.append((idx, r, score))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:5]

def rapidfuzz_match(item, roster):
    choices = [r.get("name","") + " <" + r.get("email","") + ">" for r in roster]
    match = process.extract(item, choices, scorer=fuzz.token_sort_ratio, limit=5)
    # returns list of tuples (choice, score, index)
    # convert back to roster entries
    results = []
    for choice, score, idx in match:
        results.append((idx, roster[idx], int(score)))
    return results

def main():
    parser = argparse.ArgumentParser(description="Fuzzy-match discoveries to an employee roster")
    parser.add_argument("--roster", required=True, help="CSV roster with headers at least 'name' and 'email'")
    parser.add_argument("--discovered", required=True, help="File with discovered strings (one per line)")
    parser.add_argument("--output", required=True, help="Output CSV of matches")
    args = parser.parse_args()

    roster = load_roster(args.roster)
    discovered = load_discovered(args.discovered)

    with open(args.output, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(["discovered", "match_name", "match_email", "score", "roster_index"])
        for item in discovered:
            if HAVE_RAPIDFUZZ:
                matches = rapidfuzz_match(item, roster)
            else:
                matches = simple_match(item, roster)
            for idx, r, score in matches:
                writer.writerow([item, r.get("name",""), r.get("email",""), score, idx])

    print(f"[+] Matching complete. Output -> {args.output}")
    if not HAVE_RAPIDFUZZ:
        print("[!] rapidfuzz not installed; used simple substring matching. For better results: pip3 install rapidfuzz")

