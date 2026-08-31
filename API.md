# Qubeessaa AI — API Reference

**Base URL:** `https://qubeessaa-ai.up.railway.app`

All endpoints are rate-limited to **100 requests per minute per IP**.  
Rate limiting uses Redis when `REDIS_URL` is set, in-memory otherwise.

Interactive docs (Swagger UI): `/api/docs`

---

## Versioned JSON API — `/api/v1/*`

These are the recommended endpoints for programmatic use.

---

### POST `/api/v1/check`

Spell-check a piece of text. Returns the corrected text, a diff of every
changed word, confidence scores, and alternative suggestions.

**Request body**

```json
{ "text": "Ani bishan dhuguu fedh" }
```

| Field | Type | Required | Max length |
|-------|------|----------|------------|
| `text` | string | yes | 10,000 chars |

**Response**

```json
{
  "original":  "Ani bishan dhuguu fedh",
  "corrected": "Ani bishaan dhuguu fedha",
  "corrections": [
    {
      "original":     "bishan",
      "corrected":    "bishaan",
      "position":     1,
      "confidence":   68,
      "alternatives": ["bishaan", "isaan", "shan"]
    },
    {
      "original":     "fedh",
      "corrected":    "fedha",
      "position":     3,
      "confidence":   71,
      "alternatives": ["fedha", "fedhe"]
    }
  ],
  "total_changes": 2
}
```

| Field | Description |
|-------|-------------|
| `original` | Input text unchanged |
| `corrected` | Full text after all corrections applied |
| `corrections` | Array of changed words (empty if no changes) |
| `corrections[].original` | The original (misspelled) word including any trailing punctuation |
| `corrections[].corrected` | The corrected word |
| `corrections[].position` | Zero-based word index in the original sentence |
| `corrections[].confidence` | Score 0–100. Higher = more certain. Conservative by design |
| `corrections[].alternatives` | Up to 5 alternative corrections sorted by phonetic+frequency score |
| `total_changes` | Number of words corrected |

---

### POST `/api/v1/grammar`

Check grammar of a piece of text. Returns a list of issues with severity
levels and bilingual (Afaan Oromo + English) messages.

**Request body**

```json
{ "text": "ani bishaan dhuga" }
```

**Response**

```json
{
  "issues": [
    {
      "type":       "capitalization",
      "severity":   "warning",
      "message":    "Jechi jalqabaa qubbaa guddaan jalqabuu qaba (First word should be capitalized)",
      "suggestion": "Ani",
      "position":   0,
      "word":       "ani"
    },
    {
      "type":       "missing_punctuation",
      "severity":   "warning",
      "message":    "Jumlaan tuqaa (.) dhaan xumuramuu qaba (Sentence should end with period)",
      "suggestion": ".",
      "position":   2,
      "word":       "dhuga"
    }
  ]
}
```

**Issue types**

| type | severity | Description |
|------|----------|-------------|
| `capitalization` | warning | First word not capitalised |
| `missing_punctuation` | warning / error | No terminal punctuation; error if a question word is present |
| `subject_verb_agreement` | error | Verb ending doesn't match the subject pronoun |
| `tense_inconsistency` | warning | Mixed tenses in one sentence |
| `word_order` | warning | Verb not at end of sentence (SOV rule) |
| `question_mark_missing` | error | Sentence has a question word but no `?` |
| `question_word_position` | info | Question word appears late in the sentence |
| `incomplete_preposition` | error | Preposition is the last word |
| `conjunction_position` | warning / error | Conjunction at start or end of sentence |
| `conjunction_usage` | warning | Conjunction has nothing on one side |
| `repetitive_word` | warning | Same word appears twice in a row |
| `excessive_vowel` | error | Word contains 3+ consecutive identical vowels |
| `missing_verb` | info | `gara` used with no following movement verb |
| `case_marking` | info | `-tti` suffix doesn't follow a noun |

---

### POST `/api/v1/suggestions`

Get the top-N spelling suggestions for a single word without correcting full
text. Useful for autocomplete and inline spell-check widgets.

**Request body**

```json
{ "word": "bishan", "top_n": 5 }
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `word` | string | yes | Max 60 chars |
| `top_n` | integer | no | Default 5, max 10 |

**Response**

```json
{
  "word": "bishan",
  "suggestions": ["bishaan", "isaan", "shan", "bishaan", "baasan"]
}
```

Suggestions are ranked by a balanced score of edit distance (40%), phonetic
similarity (30%), and corpus frequency (20%).

---

### POST `/api/v1/feedback`

Record whether a user accepted or rejected a correction. Accepted corrections
boost the corrected word's frequency for future sessions. Rejected corrections
reduce it slightly.

Both word fields are validated — only letters, apostrophes, and hyphens are
accepted (max 60 chars each).

**Request body**

```json
{
  "original_word":  "bishan",
  "corrected_word": "bishaan",
  "accepted":       true
}
```

**Response**

```json
{ "status": "success", "message": "Feedback recorded" }
```

**Feedback accumulation limits**

- Each accepted correction adds +50 to the corrected word's in-memory frequency
- The total boost per word is capped at **5,000** to prevent runaway frequency inflation
- Words accepted 20+ times are flagged in the server log for manual review
- Words rejected 10+ times are also flagged

---

### GET `/api/v1/health`

Liveness / readiness probe. Returns 200 when the app is up and the spell
checker has loaded its vocabulary.

**Response**

```json
{
  "status":           "healthy",
  "vocabulary_size":  25483,
  "ml_enabled":       false,
  "rate_limiter":     "in-memory",
  "timestamp":        "2026-08-31T14:17:37.500000"
}
```

| Field | Description |
|-------|-------------|
| `vocabulary_size` | Number of words in the active vocabulary after pruning |
| `ml_enabled` | Whether the AfriBERTa transformer model is loaded |
| `rate_limiter` | `"redis"` or `"in-memory"` |

---

### GET `/api/v1/stats`

Internal metrics. Useful for monitoring dashboards.

**Response**

```json
{
  "vocabulary_size":    25483,
  "bigrams":            325975,
  "trigrams":           481352,
  "ml_enabled":         false,
  "cache":              { "hits": 142, "misses": 31, "hit_rate": "82.1%", "cache_size": 31 },
  "user_feedback_count": 5,
  "rate_limiter":       "in-memory"
}
```

---

## Legacy Endpoints

These endpoints are kept for backwards compatibility and work the same as their
`/api/v1/` equivalents. They will not be removed but new integrations should
use `/api/v1/*`.

| Method | Legacy path | Equivalent v1 path |
|--------|-------------|-------------------|
| POST | `/suggestions` | `/api/v1/suggestions` |
| POST | `/check_grammar` | `/api/v1/grammar` |
| POST | `/api/suggest` | `/api/v1/suggestions` |
| POST | `/record_feedback` | `/api/v1/feedback` |
| GET | `/health` | `/api/v1/health` |
| GET | `/stats` | `/api/v1/stats` |

The `/check` and `/upload` endpoints are **web-UI only** — they accept
`multipart/form-data` and return HTML, not JSON.

---

## Error Responses

All endpoints return standard HTTP error codes with a JSON body:

```json
{ "detail": "Rate limit exceeded. Please try again later." }
```

| Code | When |
|------|------|
| 400 | Invalid input (word too long, text too long, bad characters) |
| 422 | Missing required field |
| 429 | Rate limit exceeded (100 req/min per IP) |
| 500 | Internal server error |

---

## Code Examples

### Python

```python
import requests

BASE = "https://qubeessaa-ai.up.railway.app"

# Spell-check
resp = requests.post(f"{BASE}/api/v1/check", json={"text": "Ani bishan fedh"})
data = resp.json()
print(data["corrected"])          # "Ani bishaan fedha"
print(data["corrections"][0]["confidence"])  # 68

# Grammar check
resp = requests.post(f"{BASE}/api/v1/grammar", json={"text": "ani bishaan dhuga"})
for issue in resp.json()["issues"]:
    print(issue["severity"], issue["message"])

# Submit feedback
requests.post(f"{BASE}/api/v1/feedback", json={
    "original_word": "bishan",
    "corrected_word": "bishaan",
    "accepted": True
})
```

### JavaScript (fetch)

```javascript
const BASE = "https://qubeessaa-ai.up.railway.app";

const resp = await fetch(`${BASE}/api/v1/check`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Ani bishan dhuguu fedh" })
});
const data = await resp.json();
console.log(data.corrected);           // "Ani bishaan dhuguu fedha"
console.log(data.corrections[0].confidence);  // 68
```

### curl

```bash
# Spell-check
curl -s -X POST https://qubeessaa-ai.up.railway.app/api/v1/check \
  -H "Content-Type: application/json" \
  -d '{"text":"Ani bishan dhuguu fedh"}' | python -m json.tool

# Grammar check
curl -s -X POST https://qubeessaa-ai.up.railway.app/api/v1/grammar \
  -H "Content-Type: application/json" \
  -d '{"text":"ani bishaan dhuga"}' | python -m json.tool

# Health check
curl https://qubeessaa-ai.up.railway.app/api/v1/health
```

---

## Rate Limiting Details

The rate limiter uses a **sliding window** algorithm (100 requests per 60-second
window per client IP).

When **Redis** is available (`REDIS_URL` env var set), limits are enforced using
Redis sorted sets — accurate across restarts and multiple workers.

Without Redis, limits are tracked in a Python dict — accurate within a single
process but resets on restart. Suitable for single-instance deployments.

When the limit is exceeded the response is:

```
HTTP 429 Too Many Requests
{"detail": "Rate limit exceeded. Please try again later."}
```
