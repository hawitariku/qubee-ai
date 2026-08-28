# Qubeessaa AI — Deployment Guide

Complete instructions for deploying to Railway, adding Redis rate-limiting,
submitting to Google Search Console, and running the corpus expansion script.

---

## 1. Deploy to Railway

### Prerequisites
- Railway account at [railway.app](https://railway.app)
- Git repository pushed to GitHub/GitLab
- Railway CLI (optional but useful): `npm install -g @railway/cli`

### Steps

```bash
# 1. Commit all changes
git add .
git commit -m "feat: improved accuracy, versioned API, Redis rate limiter, GA4"

# 2. Push to your main branch
git push origin main
```

Then in the Railway dashboard:
1. **New Project → Deploy from GitHub repo** — select your repo
2. Railway auto-detects the `Procfile` (`web: python main.py`)
3. Set the following **Environment Variables** in Railway's Variables tab:

| Variable | Value | Notes |
|---|---|---|
| `PORT` | (set automatically by Railway) | Do not override |
| `PYTHON_VERSION` | `3.12.0` | Matches render.yaml |
| `REDIS_URL` | (set after adding Redis plugin) | See section 2 |

4. Click **Deploy** — Railway builds the Docker image and starts the app
5. Your app URL will be something like `https://qubeessaa-ai.up.railway.app`

### Verify deployment

```bash
# Health check
curl https://qubeessaa-ai.up.railway.app/health

# Expected response:
# {"status":"healthy","vocabulary_size":25483,"ml_enabled":false,...}
```

---

## 2. Add Redis for Distributed Rate Limiting

The app uses Redis for rate limiting when `REDIS_URL` is set. Without it, it
falls back to in-memory rate limiting (resets on restart, not shared across
workers). Adding Redis takes 2 minutes on Railway.

### Steps in Railway dashboard

1. Open your project → click **+ New** → **Database** → **Add Redis**
2. Railway provisions a Redis instance and automatically injects `REDIS_URL`
   into your service's environment variables
3. **Redeploy** your service (Railway may do this automatically)

### Verify Redis is active

```bash
curl https://qubeessaa-ai.up.railway.app/api/v1/health
# Look for: "rate_limiter": "redis"
```

If you see `"rate_limiter": "in-memory"`, the `REDIS_URL` env var is not
reaching the app — check Railway's variable scoping.

---

## 3. Replace the GA4 Placeholder ID

All 15 HTML templates have been injected with the GA4 tag using the
placeholder ID `G-XXXXXXXXXX`. Replace it with your real Measurement ID.

### Get your Measurement ID

1. Go to [analytics.google.com](https://analytics.google.com)
2. Admin → Data Streams → your web stream
3. Copy the **Measurement ID** (format: `G-ABCDE12345`)

### Apply it to all templates

```bash
# From the project root — replaces placeholder in all 15 templates at once
python -c "
import os, glob
files = glob.glob('templates/*.html')
for path in files:
    content = open(path, encoding='utf-8').read()
    updated = content.replace('G-XXXXXXXXXX', 'G-ABCDE12345')  # your real ID
    open(path, 'w', encoding='utf-8').write(updated)
    print('Updated:', path)
"
```

Or re-run the injection script with your ID edited in:

```bash
# Edit scripts/inject_ga4.py: change GA4_ID = "G-XXXXXXXXXX"
# to your real ID, then run:
python scripts/inject_ga4.py
```

---

## 4. Submit to Google Search Console

This gets all 10 blog articles indexed by Google.

1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. **Add property** → URL prefix → enter `https://qubeessaa-ai.up.railway.app`
3. Verify ownership (easiest method: HTML tag — paste the meta tag into
   `templates/index.html` inside `<head>`)
4. Once verified, go to **Sitemaps** → enter `sitemap.xml` → Submit
5. Google will crawl and index all 15 pages within a few days

---

## 5. Expand the Corpus (Run Once After Deploy)

The corpus expansion script scrapes BBC Afaan Oromo, VOA Afaan Oromo, and
Oromo Wikipedia to grow the vocabulary beyond the Bible-only baseline.

```bash
# Dry run first — see how many paragraphs each source has
python scripts/expand_corpus_news.py --all --dry-run --limit 50

# Real run with backup
python scripts/expand_corpus_news.py --all --backup --limit 100

# After expansion, restart the app so it reloads the corpus
# On Railway: redeploy from the dashboard, or:
railway up
```

Note: BBC/VOA may occasionally block automated requests. If you get 0
paragraphs from a source, try `--limit 20` and increase gradually.

---

## 6. Monitor User Feedback

After real users interact with the spell checker, review accepted/rejected
corrections to spot wrong suggestions and find words to promote.

```bash
# Basic report
python scripts/monitor_feedback.py

# Full report with top 20 entries and history
python scripts/monitor_feedback.py --top 20 --history

# Save report to file
python scripts/monitor_feedback.py --export feedback_report.txt
```

### Acting on the report

- **Promote suggestions section**: words accepted 5+ times with no rejects
  → add them to `self.common_words` in `spell_checker_ml.py` with freq `7000+`
- **Anomalies section**: corrections with >30% reject rate
  → investigate; may need to add to the `_non_verbs` set in `grammar_checker.py`
  or adjust scoring weights

---

## 7. API Reference (v1)

All endpoints are rate-limited (100 req/min per IP). JSON in, JSON out.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/check` | Spell-check text, returns corrections |
| POST | `/api/v1/grammar` | Grammar check, returns issues list |
| POST | `/api/v1/suggestions` | Top-N spelling suggestions for a word |
| POST | `/api/v1/feedback` | Submit accept/reject for a correction |
| GET | `/api/v1/health` | Liveness probe (vocab size, ML flag, rate limiter) |
| GET | `/api/v1/stats` | Internal metrics |

Interactive docs: `https://qubeessaa-ai.up.railway.app/api/docs`

### Example: spell-check via curl

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
    {"original": "bishan", "corrected": "bishaan", "confidence": 82, "alternatives": [...]},
    {"original": "fedh",   "corrected": "fedha",   "confidence": 79, "alternatives": [...]}
  ],
  "total_changes": 2
}
```

---

## 8. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (no ML model — fast startup)
USE_ML=false python main.py
# Server starts at http://localhost:8080

# Run with ML model (slow first start — downloads ~500MB)
python main.py

# Run tests
python tests/test_spell_checker.py
```

---

## Port Reference

| Context | Port | How set |
|---------|------|---------|
| Railway / Render | Dynamic | `$PORT` env var injected by platform |
| Docker (local) | 8080 | `PORT=8080` in docker-compose.yml |
| Local dev | 8080 | Default in `main.py` |
| HuggingFace Spaces | 7860 | Override with `PORT=7860` env var |

The app reads `os.environ.get("PORT", 8080)` so it works on all platforms
without code changes.
