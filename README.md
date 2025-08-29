Darkweb Tools — README

Important — read first
These tools are provided for defensive, passive OSINT collection and triage only. Do not use them to interact with, post to, or transact on illicit marketplaces or forums. Always obtain written authorization from the client/owner of any target before running these tools. Run every collection activity in an isolated VM, follow your legal and privacy policies, and consult counsel if unsure.

⸻

What’s in this package
	•	tor_fetch.py — Passive Tor fetcher: downloads a single URL over Tor (SOCKS5) and saves raw HTML/text plus metadata (timestamp, sha256, headers).
	•	extractor.py — IOC extractor: parses a raw HTML/text file and extracts common IOCs (emails, IPs, AWS keys, Bitcoin addresses, URLs, phone numbers) into JSON.
	•	fuzzy_match.py — Fuzzy matcher: attempts to map discovered strings (names / emails) to entries in an employee roster CSV; uses rapidfuzz if available.
	•	README.txt — This file (plain text version).
	•	darkweb_tools.zip — packaged archive (if downloaded).

⸻

Pre-requisites & OPSEC
	1.	Authorization: Written ROE / client authorization that explicitly permits this work. Keep it on file.
	2.	Isolated environment: Use a dedicated, up-to-date VM (no corporate credentials, no personal accounts). Snapshot before use.
	3.	Tor: Run a Tor daemon locally on the collector VM (default SOCKS5 127.0.0.1:9050).
	•	On Debian/Ubuntu: sudo apt install tor then sudo systemctl start tor
	4.	Python 3.8+ and common utilities: pip3 install requests[socks] rapidfuzz (rapidfuzz optional).
	5.	No interaction: Never log in, post, or buy. Collect passively only.
	6.	Evidence storage: Use encrypted storage for raw captures and results. Maintain chain-of-custody metadata (who, when, why).

⸻

Installation (quick)
# on your isolated VM
sudo apt update && sudo apt install -y tor python3-pip
pip3 install requests[socks] rapidfuzz
# unpack the zip (if needed)
unzip darkweb_tools.zip -d ~/darkweb_tools
cd ~/darkweb_tools
chmod +x *.py

Usage examples

Start Tor (ensure Tor daemon is running before fetching):
sudo systemctl start tor
sudo systemctl status tor

Passive fetch an .onion page (tor_fetch)
python3 tor_fetch.py --url http://exampleonionaddress.onion/ --outdir ./evidence --name sample1
Output:
	•	./evidence/sample1.raw.html — raw bytes saved
	•	./evidence/sample1.meta.json — metadata (timestamp, status_code, headers, sha256)

Extract IOCs (extractor)
python3 fuzzy_match.py --roster employees.csv --discovered discovered.txt --output matches.csv
Output (JSON):
	•	summary — counts of each IOC type
	•	findings — arrays: emails, ips, aws_keys, bitcoin_addrs, urls, phones

Fuzzy-match discoveries to an employee roster (fuzzy_match)
Prepare a roster CSV employees.csv with header: name,email (example below). Prepare a discovered.txt with one discovery string per line (or transform extracted emails into a simple file).
python3 fuzzy_match.py --roster employees.csv --discovered discovered.txt --output matches.csv

Output:
	•	matches.csv — rows of discovered item → matched roster name/email → score

employees.csv example
name,email
Jane Doe,jane.doe@example.com
Brad Smith,brad.smith@example.com

discovered.txt example
jane.doe@example.com
john.d@example.net

How the flow typically works (recommended)
	1.	tor_fetch.py to capture raw content (passive).
	2.	extractor.py to produce structured IOCs.
	3.	Deduplicate & normalize IOCs into a master discoveries.txt.
	4.	fuzzy_match.py to correlate with employee roster.
	5.	Human analyst reviews hits, inspects raw captures, performs enrichment (WHOIS, crt.sh, HIBP, VirusTotal), assigns confidence and severity.
	6.	High confidence/high severity items → escalate per ROE (phone + secure email + evidence package).
⸻
Evidence handling & naming convention
	•	Use clear artifact naming: YYYYMMDDTHHMMSS_target_tool.ext (e.g., 20250801T153000_sample1.raw.html).
	•	Keep a manifest JSON with: collector_id, url, timestamp_utc, sha256, handler, notes.
	•	Store evidence in an encrypted store and keep logs of access for chain-of-custody.
⸻
Output interpretation & confidence
	•	Emails: may be test or fake — validate against corporate roster and HIBP (HaveIBeenPwned).
	•	IP addresses: may be proxies or infrastructure; enrich with whois/geo and correlation to known malicious IP lists.
	•	Keys & hashes: treat as high priority; verify their format and potential service (e.g., AKIA pattern is AWS-like but could be false).
	•	Bitcoin addresses: useful for extortion cases; do not attempt blockchain de-anonymization without legal/LE involvement.

Always annotate each finding with a confidence (High/Medium/Low) and the basis for that confidence.
⸻
Integration & automation tips
	•	Run tor_fetch.py on collector hosts and push raw captures to an indexing pipeline (Elasticsearch/OpenSearch) for search and triage.
	•	Use extractor.py as a post-ingest extractor job to produce JSON IOCs for ingestion into your triage system or ticketing tool.
	•	Use fuzzy_match.py to create an initial prioritized list; human validation required.
	•	Automate enrichment (WHOIS, crt.sh, HIBP, VT) using separate scripts and store enrichment results in the evidence manifest.
⸻
Troubleshooting
	•	Tor connection errors: ensure Tor is running (systemctl status tor), check 127.0.0.1:9050, increase request timeout.
	•	Requests failing with SSL errors: many onion sites are plain HTTP; ensure requests uses socks5h:// and avoids SSL hostname checks for .onion if necessary — but do not suppress validation for clearnet.
	•	Rapidfuzz missing: if rapidfuzz not installed, fuzzy_match.py falls back to basic substring matching but results are lower quality. Install with pip3 install rapidfuzz.
	•	Permission errors writing files: check outdir permissions; run from an isolated directory.
⸻
Security & legal reminders (cannot be overstated)
	•	Authorization is mandatory. Keep the client’s signed ROE and scope.
	•	Do not interact. No replies, no downloads beyond the captured page, no posting, no purchases. Interaction risks legal exposure and OPSEC compromise.
	•	Use isolation. Run in a VM with no bridge to corp environment; snapshot before and after.
	•	Handle PII carefully. Coordinate with client HR/legal on handling employee PII.
	•	Escalation & takedown must be coordinated and documented.
⸻
Extending the toolkit

This is starter tooling intended for defensive triage. For a production service you’ll want:
	•	Collector orchestration (scheduler, retries, rotation), secure index (Elasticsearch + encrypted S3), analyst UI, enrichment pipelines, commercial feed integrations (DarkOwl, Flashpoint), and takedown/legal workflows.
	•	Additional scripts to convert findings into STIX/TAXII, SIEM ingestion formats, and automated email/phone alerts for high-severity cases.

Example quick workflow (all together)
# start tor (on collector VM)
sudo systemctl start tor

# fetch a page over tor
python3 tor_fetch.py --url "http://exampleonionaddress.onion/" --outdir ./evidence --name sample1

# extract IOCs
python3 extractor.py --input ./evidence/sample1.raw.html --output ./evidence/sample1.iocs.json

# create a simple discoveries.txt (e.g., emails) for matching
jq -r '.findings.emails[]' ./evidence/sample1.iocs.json > discoveries.txt

# fuzzy-match to roster
python3 fuzzy_match.py --roster employees.csv --discovered discoveries.txt --output ./evidence/matches.csv
