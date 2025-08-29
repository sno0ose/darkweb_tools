#!/usr/bin/env python3
"""
tor_fetch.py
Safely fetch a single URL over Tor (SOCKS5) and save raw content + metadata.
USAGE (dry-run recommended):
  python3 tor_fetch.py --url http://exampleonionaddress.onion --outdir ./evidence --name sample
REQUIREMENTS:
  - tor daemon running locally (default SOCKS5 127.0.0.1:9050)
  - pip install requests[socks]
IMPORTANT:
  - ONLY run against targets you are authorized to access.
  - DO NOT interact with marketplaces or perform transactions.
  - Run in an isolated VM; do not reuse corporate credentials.
"""

import argparse, os, hashlib, json, time
from pathlib import Path
try:
    import requests
except Exception as e:
    raise SystemExit("Missing dependency 'requests[socks]'. Install with: pip3 install requests[socks]") from e

def sha256_bytes(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Fetch a URL over Tor (passive fetch only) and save raw HTML + metadata.")
    parser.add_argument("--url", required=True, help="URL to fetch (e.g., http://xxxxx.onion/)")
    parser.add_argument("--outdir", default="./evidence", help="Directory to write outputs")
    parser.add_argument("--name", default=None, help="Optional base name for files (defaults to timestamp)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout seconds")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base_name = args.name or time.strftime("%Y%m%dT%H%M%SZ")
    raw_path = outdir / f"{base_name}.raw.html"
    meta_path = outdir / f"{base_name}.meta.json"

    # Configure Tor SOCKS5 proxy (assumes Tor running locally)
    socks_proxy = "socks5h://127.0.0.1:9050"
    session = requests.Session()
    session.proxies.update({"http": socks_proxy, "https": socks_proxy})

    headers = {
        "User-Agent": "osint-collector/1.0 (+https://example.org)"
    }

    print(f"[+] Fetching {args.url} via Tor SOCKS5 proxy {socks_proxy} (timeout={args.timeout}) - PASSIVE ONLY")
    try:
        r = session.get(args.url, headers=headers, timeout=args.timeout)
        content = r.content
        text = r.text
        status = r.status_code
        sha = sha256_bytes(content)
        with open(raw_path, "wb") as f:
            f.write(content)
        meta = {
            "url": args.url,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status_code": status,
            "content_size_bytes": len(content),
            "sha256": sha,
            "headers": dict(r.headers),
            "fetch_method": "tor_socks5",
            "proxy": socks_proxy,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print(f"[+] Saved raw content -> {raw_path}")
        print(f"[+] Saved metadata -> {meta_path}")
    except Exception as e:
        print("[!] Fetch failed:", str(e))
        # Save an error meta entry
        meta = {
            "url": args.url,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": str(e)
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
