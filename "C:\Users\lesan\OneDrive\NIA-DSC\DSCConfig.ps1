# 1. Create the full folder structure
$repo = "Nia-TheHouseOfJazzu"
New-Item -ItemType Directory -Path $repo -Force
Set-Location $repo

git init
git branch -M main

# Core structure
@"
.nia/
  memory/
  agents/
  tools/
  workflows/
  logs/
config/
contracts/
  templates/
grants/
procurement/
publishing/
infra/
docs/
scripts/
"@ -split "`n" | ForEach-Object { if ($_.Trim()) { New-Item $_ -ItemType Directory -Force } }
# ==== README.md ====
@"
# Nia – Autonomous AI CEO of The House of Jazzu

Nia is a fully autonomous cloud-native executive intelligence that runs every aspect of a creative media company (music publishing, film scoring, NFTs, grants, procurement, legal, finance) with zero daily human input after setup.

## Current Status (November 2025)
- Persistent memory: Live
- Contract, Grant, Procurement, Publishing agents: Fully autonomous
- Running on Claude 4 + Grok 4 + LangGraph
- Financial rails: Stripe Connect + Mercury API


Run the entire script above → you now have a complete, professional, push-ready GitHub repo with:
## Quick Start (PowerShell)
```powershell
./scripts/Install-Nia.ps1
# 2. Create all files with exact content
