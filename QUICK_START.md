# Qubeessaa AI — Quick Start

Get the app running locally in under 5 minutes.

---

## Prerequisites

- Python 3.11 or 3.12
- Git

---

## 1. Clone and install

```bash
git clone https://github.com/hawitariku/qubeessaa-ai.git
cd qubeessaa-ai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## 2. Configure (optional)

```bash
cp .env.example .env
```

Open `.env` and set:

```
# Skip the 500 MB AfriBERTa model download for fast startup
USE_ML=false

# Leave PORT and REDIS_URL at defaults for local dev
PORT=8080
```

---

## 3. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Open **http://localhost:8080** — type some Afaan Oromo text and hit Check.

> **With ML disabled** startup takes ~6 seconds.  
> **With ML enabled** first startup downloads ~500 MB and takes 2–5 minutes.

---

## 4. Run tests

```bash
python tests/test_spell_checker.py
# Expected: 25 passed, 0 failed
```

---

## 5. Expand the corpus (optional)

The vocabulary comes from the Biblica Afaan Oromo Bible. To add news text:

```bash
# Dry run first
python scripts/expand_corpus_news.py --all --dry-run --limit 20

# Real run
python scripts/expand_corpus_news.py --all --backup --limit 100
```

Then restart the server so it reloads the updated corpus.

---

## 6. Deploy

See [DEPLOY.md](DEPLOY.md) for Railway, Render, and Docker instructions.

---

## Common issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: fastapi` | Run `pip install -r requirements.txt` |
| Server hangs on startup | Set `USE_ML=false` in `.env` |
| Port already in use | Change `PORT=8081` in `.env` |
| `user_feedback.json` not found | Ignored on first run; created automatically |
