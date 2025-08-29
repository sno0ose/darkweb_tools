Dark-web OSINT Tooling - Safe, Defensive Scripts
Files included:
 - tor_fetch.py      : Fetch a single URL over Tor (passive read-only) and save raw HTML + metadata
 - extractor.py      : Extract emails, IPs, AWS keys, bitcoin addresses, URLs and phone numbers from raw files
 - fuzzy_match.py    : Fuzzy-match discoveries to an employee roster (CSV)

Usage notes and OPSEC:
 - Run only with explicit authorization and within legal guidance.
 - Run these scripts inside an isolated VM; do not use corporate credentials or systems.
 - Do not interact, post, or transact on illicit sites.
 - tor_fetch.py requires Tor (socks5) running locally; set up Tor before use.
 - extractor.py and fuzzy_match.py are for triage and prioritization; human validation is required.

Example quick workflow:
  python3 tor_fetch.py --url http://exampleonionaddress.onion --outdir ./evidence --name sample1
  python3 extractor.py --input ./evidence/sample1.raw.html --output ./evidence/sample1.iocs.json
  python3 fuzzy_match.py --roster employees.csv --discovered evidence/sample1.iocs.json --output matches.csv

Caveats:
 - These are starter tooling for defensible collection and triage. A production service requires indexing, secure storage, analyst UI, commercial feeds, and legal coverage.
