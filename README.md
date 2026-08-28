# Qubeessaa AI — Afaan Oromo Spell & Grammar Checker

A free, AI-assisted spell checker and grammar checker for **Afaan Oromo** (Oromiffa),
the language of the Oromo people, written in the **Qubee** Latin alphabet.

**Live app:** https://qubeessaa-ai.up.railway.app

---

## Features

- **Spell checking** — 25,000+ post-pruning vocabulary (59,000+ raw tokens) built from the Biblica Afaan Oromo Bible and Wikipedia
- **Grammar checking** — 12 rule-based checks covering SOV word order, subject-verb agreement, tense consistency, punctuation, and more
- **Afaan Oromo-aware corrections** — phonetic similarity scoring for vowel length (`bishan→bishaan`), digraphs (`dh`, `ny`, `ch`, `sh`), and ejective consonants (`q`, `x`, `c`)
- **Context-aware suggestions** — bigram/trigram scoring + optional AfriBERTa transformer (ML) for masked-language suggestions
- **User feedback loop** — accept/reject corrections; preferences persist and influence future suggestions
- **File upload** — drag-and-drop `.txt` file checking (up to 1 MB)
- **REST API** — versioned JSON API (`/api/v1/*`) for programmatic access
- **Educational blog** — 10 articles on Afaan Oromo language, grammar, history, and culture
- **Redis rate limiting** — 100 requests/minute per IP with graceful in-memory fallback

---

## Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/hawitariku/qubeessaa-ai.git
cd qubeessaa-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
cp .env.example .env
# Edit .env — set USE_ML=false for fast startup without the transformer model

# 5. Run
python main.py
# → http://localhost:8080
```

> **Tip:** Set `USE_ML=false` in `.env` to skip the ~500 MB AfriBERTa download.
> The statistical spell checker is fully functional without it.

---

## API Reference

All endpoints are rate-limited (100 req/min per IP). Versioned JSON API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/check` | Spell-check text — returns corrected text + per-word diffs |
| `POST` | `/api/v1/grammar` | Grammar check — returns list of issues with severity |
| `POST` | `/api/v1/suggestions` | Top-N spelling suggestions for a single word |
| `POST` | `/api/v1/feedback` | Submit accept/reject for a correction |
| `GET`  | `/api/v1/health` | Liveness probe (vocab size, ML flag, rate limiter type) |
| `GET`  | `/api/v1/stats` | Internal metrics (vocab, n-grams, cache, feedback count) |

Interactive docs: https://qubeessaa-ai.up.railway.app/api/docs

### Example

```bash
curl -X POST https://qubeessaa-ai.up.railway.app/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"text": "Ani bishan dhuguu fedh"}'
```

```json
{
  "original": "Ani bishan dhuguu fedh",
  "corrected": "Ani bishaan dhuguu fedha",
  "corrections": [
    {
      "original": "bishan",
      "corrected": "bishaan",
      "confidence": 82,
      "alternatives": ["bishaan", "isaan", "shan"]
    },
    {
      "original": "fedh",
      "corrected": "fedha",
      "confidence": 79,
      "alternatives": ["fedha", "fedhe"]
    }
  ],
  "total_changes": 2
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port the server listens on (injected automatically by Railway/Render) |
| `REDIS_URL` | *(unset)* | Redis connection string for distributed rate limiting; falls back to in-memory if unset |
| `USE_ML` | `true` | Set to `false` to skip loading the AfriBERTa transformer model |

Copy `.env.example` to `.env` to configure locally.

---

## Project Structure

```
qubeessaa-ai/
├── main.py                   # FastAPI app — all HTTP routes
├── spell_checker_ml.py       # Core spell checker (statistical + optional ML)
├── grammar_checker.py        # Rule-based grammar checker (12 checks)
├── oromo_corpus.txt          # Primary corpus (Biblica Afaan Oromo Bible, CC BY-SA)
├── requirements.txt          # Pinned Python dependencies
├── Procfile                  # Heroku/Railway start command
├── render.yaml               # Render.com service configuration
├── Dockerfile                # Container image (port 8080)
├── docker-compose.yml        # Local Docker Compose setup
├── .env.example              # Environment variable template
├── templates/                # Jinja2 HTML templates (15 pages)
├── static/                   # Static files (ads.txt)
├── scripts/
│   ├── expand_corpus_news.py # Scrape BBC/VOA/Wikipedia for corpus expansion
│   ├── monitor_feedback.py   # Analyse user_feedback.json
│   ├── inject_ga4.py         # Inject GA4 tag into all templates
│   └── corpus_expansion.py   # Interactive corpus management tool
└── tests/
    └── test_spell_checker.py # 25-test suite (accuracy, grammar, edge cases, perf)
```

---

## How the Spell Checker Works

Every misspelled word goes through a four-factor scoring pipeline:

| Factor | Weight | What it measures |
|--------|--------|-----------------|
| Edit distance | 35% | Levenshtein distance from the input word |
| Phonetic similarity | 35% | Custom Oromo-aware matcher: ejectives, digraphs, vowel length |
| Word frequency | 20% | Corpus occurrence count |
| Pattern / context | 10% | Bigrams, trigrams, verb-pronoun patterns, SOV word order |

Afaan Oromo-specific extensions to standard edit generation:
- **Vowel doubling** — inserts doubled vowel at vowel positions (`a→aa`, `e→ee`, etc.) because vowel length is phonemic in Oromo
- **Digraph insertion** — inserts `dh`, `ny`, `ch`, `sh`, `ph`, `th` as atomic units

---

## Expanding the Corpus

The vocabulary is built primarily from the Biblica® Open New Oromo Contemporary Version™ Bible
(CC BY-SA 4.0). To add news and Wikipedia text:

```bash
# Dry run first — see what would be added
python scripts/expand_corpus_news.py --all --dry-run --limit 50

# Real run with automatic backup
python scripts/expand_corpus_news.py --all --backup --limit 100
```

Sources: BBC Afaan Oromo, VOA Afaan Oromo, Oromo Wikipedia.

---

## Running Tests

```bash
python tests/test_spell_checker.py
# Runs 25 tests: accuracy, grammar, edge cases, performance, vocabulary
# Expected: 25 passed, 0 failed
```

---

## Deployment

See [DEPLOY.md](DEPLOY.md) for full instructions covering:
- Railway (recommended — one-click deploy)
- Render.com
- Docker (local or self-hosted)
- Redis setup for distributed rate limiting
- Google Search Console sitemap submission
- Replacing the GA4 placeholder ID

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI 0.104 + Uvicorn |
| Templating | Jinja2 |
| Spell checker | Custom statistical engine (Python) |
| ML model | AfriBERTa (`castorini/afriberta_small`) — optional |
| Rate limiting | Redis (in-memory fallback) |
| Corpus | Biblica Afaan Oromo Bible + Wikipedia |
| Deployment | Railway / Render / Docker |

---

## License

MIT — see [LICENSE](LICENSE).

The primary corpus (`oromo_corpus.txt`) is the Biblica® Open New Oromo Contemporary Version™,
licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Scripture taken from the Holy Bible, New Oromo Contemporary Version® © 2022 Biblica, Inc.®

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Pull requests welcome — especially for:
- Corpus expansion (more diverse Afaan Oromo text sources)
- Grammar rule improvements
- Dialect vocabulary (Borana, Harar, Wollega)
