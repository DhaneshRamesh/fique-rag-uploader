# fique-rag-uploader — Scraper & Uploader (Content → Azure Blob)

This repository contains the **scraper and uploader pipeline** used to collect Fique’s blog and knowledge content, convert it to JSONL, and push it into Azure Blob Storage for downstream ingestion by the FiqueBot backend (RAG ingestion pipeline). This repo is intentionally separate from the backend to enforce a clean ETL boundary and separation of concerns.

---

## 📌 PTRI (Problem → Tech → Result → Impact)

**Problem:**  
Fique’s blog and knowledge content are published across pages and need regular scraping, normalization, and ingestion so the chatbot can answer up-to-date site & support queries.

**Tech:**  
- Python (scraper scripts)  
- JSONL output for chunked documents  
- Azure Blob Storage (incoming container)  
- Bash automation scripts (push_jsonl.sh)  
- GitHub Actions for scheduled runs / deployment

**Result:**  
Automated scraper that produces `fique_articles.jsonl` and uploads content to Azure Blob, enabling the backend ingestion pipeline to consume fresh content for vectorisation and retrieval.

**Impact:**  
Keeps the chatbot knowledge base current with the latest blog posts and FAQs, improving answer relevance and reducing stale responses for end users.

---

## 🔎 Repo Contents (key files)

- `.github/workflows/upload.yml` — GH Action to run scraper on schedule and upload results.  
- `scraper_fique.py` — main scraper that crawls Fique blog pages and serializes content to JSON / JSONL.  
- `fique_articles.json` — snapshot / sample JSON output (for local dev).  
- `fique_articles.jsonl` — newline-delimited JSON produced by the scraper (consumed by uploader).  
- `push_jsonl.sh` — shell script to upload `jsonl` to Azure Blob (uses `az` CLI or `curl` with SAS).  
- `upload_blob.py` — Python uploader utility to push files to Azure Blob Storage (used by scripts or GH Actions).  
- `requirements.txt` — python dependencies for scraping & upload.

---

## 🔌 How it fits with FiqueBot

1. Scraper runs on schedule (daily/weekly) or on-demand and writes `fique_articles.jsonl`.  
2. The uploader pushes the JSONL file to Azure Blob Storage `incoming/` container.  
3. Event Grid (or backend polling) detects the new blob and triggers the backend ingestion endpoint (`/ingest`) to process, generate embeddings, and update the vector store.  
4. FiqueBot backend uses the updated vector store to answer queries referencing the latest blog content.

Related repos:
- Backend: `fiquebot-backend` — retrieval + ingestion.  
- Frontend: `fiquebot-frontend` — adapted AOAI UI.

---

## ⚙️ Quickstart — Local dev

1. Clone the repo
```bash
git clone https://github.com/DhaneshRamesh/fique-rag-uploader.git
cd fique-rag-uploader
```

2. Create virtual env and install
```bash
python -m venv .venv
source .venv/bin/activate       # mac/linux
.venv\Scripts\activate          # windows
pip install -r requirements.txt
```

3. Run the scraper locally (example)
```bash
python scraper_fique.py --output=fique_articles.jsonl
# or if script supports a site param:
python scraper_fique.py --site https://fique.example.com --output=fique_articles.jsonl
```

4. Upload produced JSONL to Azure Blob (example)
```bash
# Using Python uploader
python upload_blob.py --file=fique_articles.jsonl --container=incoming --account-name=$STORAGE_ACCOUNT_NAME --sas-token=$SAS

# OR using az cli (if you have SAS/credentials)
az storage blob upload --account-name $STORAGE_ACCOUNT_NAME --container-name incoming --name fique_articles.jsonl --file fique_articles.jsonl --auth-mode key
```

---

## 🔐 Configuration / Environment Variables

Create a `.env` or use GitHub Actions secrets — **never commit secrets**.

```
# Storage
STORAGE_ACCOUNT_NAME=
STORAGE_ACCOUNT_KEY=        # or use SAS token in uploader
BLOB_CONTAINER_INCOMING=incoming

# Scraper
SCRAPER_USER_AGENT="FiqueBot-Scraper/1.0"
SCRAPER_RATE_LIMIT=1        # seconds between requests

# Optional (if using upload script with SAS)
SAS_TOKEN=
```

---

## 🕒 Automation (GitHub Actions)

This repo includes a GitHub Actions workflow (`.github/workflows/upload.yml`) that runs the scraper daily and uploads results to Azure Blob.

**Triggers:**
- `push` to `main`
- Manual trigger (`workflow_dispatch`)
- Scheduled run daily at **02:00 UTC**

**Jobs performed:**
1. Checkout repo  
2. Setup Python + dependencies + Playwright browsers  
3. Run scraper (`scraper_fique.py`)  
4. Upload generated JSONL to Azure Blob Storage (`upload_blob.py`)  
5. Push updated JSONL file back to repo for version control (`push_jsonl.sh`)

**Secrets used:**
- `AZURE_CONN_STR` → Azure Storage connection string  
- `GH_PAT` → GitHub Personal Access Token (for pushing updated JSONL)

This ensures the chatbot backend always has **fresh content** from the Fique blog without manual intervention.

---

## ✅ Best practices & verification

- **Rate-limit scraping** and respect robots.txt to avoid IP blocking.  
- **Normalize content** (strip scripts, extract article title/date/body) to create clean chunks for embedding.  
- **Add metadata** in each JSONL entry (url, published_date, title) so the backend can show citations.  
- **Test uploads** by verifying the blob appears in the `incoming/` container and triggers the backend ingestion (check backend `/health` or ingestion logs).  
- **Logging**: ensure scraper logs which pages were fetched and any failures; keep `fique_articles.jsonl` versioned for debugging.

---

## 📄 Sample JSONL entry (one line per document)
```json
{
  "id": "article-2025-08-01-01",
  "url": "https://fique.example.com/blog/how-to-use-x",
  "title": "How to use X",
  "published_date": "2025-08-01",
  "content": "Full article text here...",
  "source": "fique_blog",
  "language": "en"
}
```

---

## 🧾 Commit & changelog suggestions

- `feat(scraper): add initial scraper for Fique blog and jsonl output`  
- `chore(ci): add GitHub Actions schedule to run scraper`  
- `feat(uploader): add upload_blob.py and push_jsonl.sh for blob upload`

Add a short `docs/CHANGES.md` summarizing schedules and major parser changes so the backend team can track content updates.

---

## ✅ Resume / GitHub blurb (1–2 lines)
**Fique content scraper & uploader:** automated scraping and Azure Blob upload pipeline that keeps the chatbot knowledge base fresh by pushing newline-delimited JSON content for ingestion into the RAG pipeline.
