# Islamic Knowledge Harvester v2
User Manual

STEP 1 — Extract Project

unzip islamic_knowledge_harvester_v2.zip
cd islamic_knowledge_harvester_v2

STEP 2 — Create Python Environment

python -m venv venv
source venv/bin/activate

STEP 3 — Install Dependencies

pip install httpx
pip install pytesseract
pip install pillow
pip install beautifulsoup4
pip install requests
pip install playwright
pip install sentence-transformers

Install OCR engine

sudo apt install tesseract-ocr

STEP 4 — Install Playwright Browser

playwright install

STEP 5 — Start LM Studio

Load model:

qwen2.5-9b-instruct

Enable API server

http://localhost:1234

STEP 6 — Run Poster Harvester

python scripts/harvest_poster.py

STEP 7 — Provide URL

Paste Facebook or Instagram post URL

STEP 8 — Verify Dataset

data/wisdom_db.json

STEP 9 — Run Full Autonomous Mode

python scripts/run_autonomous_agent.py
