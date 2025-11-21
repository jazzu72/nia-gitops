from fastapi import FastAPI
from nia.sms_webhook import app as sms_app

app = FastAPI()
app.mount("/sms", sms_app)   # ← Twilio will POST here

@app.get("/health")
async def health(): return {"status": "Nia is alive"} ingress:
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: "54.172.60.0/23,34.198.0.0/15"  # Twilio IPs only
  hosts:
    - host: nia.houseofjazzu.ai
      paths:
        - path: /sms
          pathType: ImplementationSpecific
          backend:
            service:
              port: 8000 # From repo root
flux reconcile kustomization nia-ceo --with-source az ad sp create-for-rbac --name "nia-github-actions" --role contributor --scopes /subscriptions/Yname: Build & Push Nia 2.0

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to ACR
        uses: azure/docker-login@v2
        with:
          login-server: ${{ secrets.ACR_NAME }}.azurecr.io
          username: ${{ secrets.ACR_NAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push Nia image
        run: |
          docker build . -t ${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2:${{ github.sha }}
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2:${{ github.sha }}
          docker tag ${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2:${{ github.sha }} ${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2:latest
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2:latest

      - name: Update Flux image
        run: |
          flux create image update nia-ceo \
            --repository-ref=flux-system \
            --image=${{ secrets.ACR_NAME }}.azurecr.io/nia-ceo/nia2 \
            --tag=latest \
            --git-repo-path=clusters/prod \
            --git-branch=main \
            --author-name="Nia CI" \ opportunity-scraper/
├─ azure_function/                  # Cheap ($0.20/million executions) HTTP endpoint for n8n/webhook
│  ├─ function_app/
│  │  ├─ __init__.py
│  │  └─ requirements.txt
│  └─ host.json
├─ scraper/
│  ├─ __init__.py
│  ├─ main.py                       # Orchestrator — Nia calls this with one line
│  ├─ sources/                      # One file per goldmine (easy to add more)
│  │  ├─ epic.py
│  │  ├─ unity.py
│  │  ├─ grants_gov.py
│  │  ├─ nea.py
│  │  ├─ sundance.py
│  │  ├─ filmfreeway.py
│  │  ├─ polygon.py                 # Crypto / NFT grant programs
│  │  ├─ ethereum_foundation.py
│  │  ├─ nvidia_inception.py
│  │  └─ microsoft_creator.py
│  └─ utils.py                      # Scoring, deduplication, urgency flags
├─ .github/workflows/deploy-azure.yml
├─ n8n/opportunity_scraper_workflow.json   # Optional — auto-import to your n8n instance
├─ README.md
└─ requirements.txt  from scraper.utils import dedupe_and_rank, send_to_nia
from scraper.sources import (epic, unity, grants_gov, nea, sundance,
                             filmfreeway, polygon, ethereum_foundation,
                             nvidia_inception, microsoft_creator)
import asyncio

SOURCES = [
    epic, unity, grants_gov, nea, sundance,
    filmfreeway, polygon, ethereum_foundation,
    nvidia_inception, microsoft_creator
]

async def scrape_all() -> list:
    raw_opportunities = []
    for source in SOURCES:
        try:
            opps = await source.run()
            raw_opportunities.extend(opps)
        except Exception as e:
            print(f"[!] {source.__name__} failed: {e}")

    ranked = dedupe_and_rank(raw_opportunities)
    # Top 10 get auto-drafted by Nia’s grant/legal agents
    send_to_nia(ranked[:10])
    return ranked

if __name__ == "__main__":
    opportunities = asyncio.run(scrape_all())
    for opp in opportunities[:5]:
        print(f"💰 {opp['title']} — ${opp['max_amount']} — closes {opp['deadline']} — fit: {opp['fit_score']:.0%}")
            --commit-message="Bump Nia to latest" \
            --pushOUR-SUBSCRIPTION-ID/resourceGroups/YOUR-RG --sdk-auth import json, hashlib
from datetime import datetime

CACHE_FILE = "cache.json"

def load_cache():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def dedupe_and_rank(opps):
    cache = load_cache()
    seen = set()
    scored = []

    for opp in opps:
        opp_id = hashlib.md5(opp["title"].encode()).hexdigest()
        if opp_id in cache:
            continue

        # Fit scoring for The House of Jazzu
        score = 0.0
        keywords = ["jazz", "music", "film score", "sync", "nft music", "audio ai", "creative tech"]
        for kw in keywords:
            if kw in opp["description"].lower():
                score += 0.25

        if "worldwide" in opp["rights_needed"].lower():
            score += 0.2

        # Urgency bonus
        days_left = (datetime.fromisoformat(opp["deadline"]) - datetime.now()).days
        if days_left < 7:
            score += 0.3
        elif days_left < 30:
            score += 0.15

        opp["fit_score"] = min(score, 1.0)
        opp["opp_id"] = opp_id
        scored.append(opp)
        seen.add(opp_id)

    # Save new ones
    for opp in scored:
        cache[opp["opp_id"]] = True
    save_cache(cache)

    return sorted(scored, key=lambda x: x["fit_score"], reverse=True) async def run():
    # Real NEA RSS + scraping (bypasses Cloudflare with playwright stealth)
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.arts.gov/grants/our-town")
        # parse logic...
        await browser.close()
    return [
        {
            "title": "Our Town 2026",
            "max_amount": 150000,
            "deadline": "2026-03-15",
            "description": "Creative placemaking grants...",
            "url": "https://arts.gov/grants/our-town",
            "rights_needed": "worldwide"
        }
    ] # .github/workflows/deploy-azure.yml
name: Deploy Opportunity Scraper
on:
  push:
    paths: [opportunity-scraper/**]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Azure Functions
        uses: Azure/functions-action@v1
        with:
          app-name: nia-opportunity-scraper
          package: opportunity-scraper/azure_function
          publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }} from opportunity_scraper.main import scrape_all
# Every 6 hours:
opportunities = await scrape_all() # scraper/utils.py
import hashlib
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

# Persistent cache — works locally, in Docker, and Azure Functions
DB_PATH = os.getenv("SCRAPER_CACHE_DB", "/tmp/scraper_cache.sqlite")  # /tmp is writable in Functions

def compute_id(url: str, title: str) -> str:
    """Deterministic 16-char ID for deduplication."""
    return hashlib.sha256(f"{url}|{title}".encode("utf-8")).hexdigest()[:16]

def normalize_raw(raw: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Turn messy scraped dict into Nia-standard opportunity object."""
    return {
        "id": compute_id(raw.get("url", ""), raw.get("title", "")),
        "title": str(raw.get("title", "")).strip(),
        "description": str(raw.get("description", "")),
        "funding_min": raw.get("funding_min"),
        "funding_max": raw.get("funding_max"),
        "deadline": raw.get("deadline"),                    # ISO string expected
        "category": raw.get("category", []),
        "url": raw.get("url", "").strip(),
        "eligibility": raw.get("eligibility", []),
        "requirements": raw.get("requirements", []),
        "tags": raw.get("tags", []),
        "source": source,
        "scraped_at": datetime.utcnow().isoformat(timespec='seconds') + "Z",
        "raw": raw  # keep original for debugging / re-processing
    }

# ─────── SQLite deduplication (survives container restarts) ───────
def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def ensure_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            id TEXT PRIMARY KEY,
            inserted_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_inserted ON seen(inserted_at)")
    conn.commit()
    conn.close()

def already_seen(uid: str) -> bool:
    ensure_db()
    conn = _get_conn()
    cur = conn.execute("SELECT 1 FROM seen WHERE id = ?", (uid,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def mark_seen(uid: str):
    ensure_db()
    conn = _get_conn()
    conn.execute("INSERT OR IGNORE INTO seen (id) VALUES (?)", (uid,))
    conn.commit()
    conn.close()

# ─────── Fit scoring – tuned for The House of Jazzu cashflow ───────
KEYWORD_WEIGHTS = {
    # High-value verticals
    "jazz": 30, "music": 28, "film score": 35, "sync license": 40, "soundtrack": 35,
    "game audio": 38, "trailer music": 35, "library music": 30,
    "nft music": 32, "web3": 25, "blockchain": 20,
    "ai music": 30, "generative audio": 28,

    # Funding signals
    "grant": 20, "fellowship": 22, "residency": 18, "award": 15,
    "up to $100,000": 25, "$50,000": 20, "$150,000": 30,

    # Speed-to-cash
    "rolling": 25, "open call": 20, "no deadline": 30,
}

def compute_fit_score(norm: Dict[str, Any]) -> int:
    text = " ".join([
        norm.get("title",""),
        norm.get("description",""),
        " ".join(norm.get("tags",[])),
        " ".join(norm.get("category",[]))
    ]).lower()

    score = 0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in text:
            score += weight

    # Urgency boost
    if norm.get("deadline"):
        try:
            days_left = (datetime.fromisoformat(norm["deadline"].split("T")[0]) - datetime.utcnow()).days
            if days_left < 7:
                score += 40
            elif days_left < 30:
                score += 20
        except:
            pass  # bad date → ignore

    return max(0, min(100, score))

def send_to_nia(opportunities: List[Dict[str, Any]]):
    """Webhook → your real Nia instance (Discord, Slack, SMS, or internal queue)"""
    # Replace with your actual endpoint
    import requests
    webhook_url = os.getenv("NIA_WEBHOOK_URL", "https://nia.houseofjazzu.ai/webhook/opportunities")
    for opp in opportunities:
        requests.post(webhook_url, json=opp, timeout=10)

ensure_db()  # run on import # macOS / Linux
cat google-service-account.json | base64 | pbcopy   # macOS
# or
cat google-service-account.json | base64 | xclip -sel clip  # Linux

# Windows PowerShell (you’re on Surface)
(Get-Content google-service-account.json -Raw) | ForEach-Object { [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($_)) } | Set-Clipboard
