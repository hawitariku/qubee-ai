"""
Qubeessaa AI — Afaan Oromo Spell & Grammar Checker
FastAPI application with:
  - Versioned JSON API  (/api/v1/*)
  - Redis rate-limiting with in-memory fallback
  - Input sanitisation on all endpoints
  - Port driven by PORT env var (default 8080)
"""

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from spell_checker_ml import MLEnhancedSpellChecker
import logging
import re
import os
import time
from datetime import datetime
from functools import wraps
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Qubeessaa AI — Afaan Oromo Spell Checker",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename="spell_checker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiting — Redis with in-memory fallback
# ---------------------------------------------------------------------------

RATE_LIMIT = 100       # max requests per window
RATE_LIMIT_WINDOW = 60  # seconds

# Try to connect to Redis; fall back to a plain dict if unavailable.
_redis_client = None
_request_counts: dict = {}   # in-memory fallback storage

try:
    import redis as _redis_lib
    _redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    _redis_client = _redis_lib.from_url(_redis_url, socket_connect_timeout=1)
    _redis_client.ping()
    logger.info(f"Redis rate-limiter connected at {_redis_url}")
except Exception:
    logger.warning("Redis unavailable — using in-memory rate limiter (single-process only).")
    _redis_client = None


def _check_rate_limit(client_ip: str) -> bool:
    """
    Returns True if the request is allowed, False if the limit is exceeded.
    Uses Redis sliding-window when available, in-memory list otherwise.
    """
    if _redis_client:
        key = f"rl:{client_ip}"
        pipe = _redis_client.pipeline()
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, RATE_LIMIT_WINDOW * 2)
        results = pipe.execute()
        count = results[2]
        return count <= RATE_LIMIT
    else:
        now = time.time()
        if client_ip not in _request_counts:
            _request_counts[client_ip] = []
        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip]
            if now - t < RATE_LIMIT_WINDOW
        ]
        if len(_request_counts[client_ip]) >= RATE_LIMIT:
            return False
        _request_counts[client_ip].append(now)
        return True


def rate_limit(f):
    """Decorator — applies rate limiting to any async route handler."""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or args[0]
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
            )
        return await f(*args, **kwargs)
    return wrapper

# ---------------------------------------------------------------------------
# Jinja2 template renderer (cache disabled for hot-reload compatibility)
# ---------------------------------------------------------------------------

_jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)


def render(request: Request, template_name: str, context: dict) -> HTMLResponse:
    tmpl = _jinja_env.get_template(template_name)
    return HTMLResponse(content=tmpl.render(request=request, **context))

# ---------------------------------------------------------------------------
# Input sanitisation helpers
# ---------------------------------------------------------------------------

# Allowed characters in a single Oromo word submitted via the feedback endpoint.
_WORD_RE = re.compile(r"^[a-zA-Z\'\-]{1,60}$")


def _sanitise_word(value: str) -> str:
    """
    Strip whitespace and validate that the value looks like an Oromo word.
    Raises HTTPException(400) if the value fails validation.
    """
    value = value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="Empty word provided.")
    if not _WORD_RE.match(value):
        raise HTTPException(
            status_code=400,
            detail="Invalid characters in word. Only letters, apostrophes, and hyphens are allowed.",
        )
    return value.lower()


def _sanitise_text(value: str, max_len: int = 10_000) -> str:
    """Strip and validate free-form text input."""
    value = value.strip()
    if len(value) > max_len:
        raise HTTPException(
            status_code=400,
            detail=f"Text too long. Maximum {max_len:,} characters allowed.",
        )
    return value

# ---------------------------------------------------------------------------
# Spell-checker initialisation
# ---------------------------------------------------------------------------

# Spell-checker initialisation
# ---------------------------------------------------------------------------

_use_ml = os.environ.get("USE_ML", "true").lower() not in ("false", "0", "no")
print(f"🔄 Initialising Spell Checker (ML={'enabled' if _use_ml else 'disabled'})…")
checker = MLEnhancedSpellChecker(corpus_path="oromo_corpus.txt", use_ml=_use_ml)
print("✅ Spell checker ready!")

# ---------------------------------------------------------------------------
# SEO / infrastructure endpoints (no rate-limit needed)
# ---------------------------------------------------------------------------

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return "google.com, pub-4332009994407882, DIRECT, f08c47fec0942fa0"


@app.get("/favicon.ico")
async def favicon():
    """
    Serve an SVG favicon as ICO to stop browser 404 log spam.
    The SVG renders a simple 'Q' lettermark in the brand purple.
    """
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="6" fill="#667eea"/>'
        '<text x="16" y="23" font-family="Arial,sans-serif" font-size="20" '
        'font-weight="bold" fill="white" text-anchor="middle">Q</text>'
        '</svg>'
    )
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return (
        "User-agent: *\nAllow: /\n\n"
        "Sitemap: https://qubeessaa-ai.up.railway.app/sitemap.xml"
    )


@app.get("/sitemap.xml")
async def sitemap_xml():
    base = "https://qubeessaa-ai.up.railway.app"
    pages = [
        ("", "1.0", "weekly"),
        ("/about", "0.8", "monthly"),
        ("/blog", "0.9", "weekly"),
        ("/help", "0.7", "monthly"),
        ("/privacy", "0.5", "monthly"),
        ("/blog/qubee-alphabet-guide", "0.8", "monthly"),
        ("/blog/common-spelling-mistakes", "0.8", "monthly"),
        ("/blog/grammar-basics", "0.8", "monthly"),
        ("/blog/history-of-afaan-oromo", "0.8", "monthly"),
        ("/blog/improve-writing-skills", "0.8", "monthly"),
        ("/blog/afaan-oromo-dialects", "0.8", "monthly"),
        ("/blog/afaan-oromo-proverbs", "0.8", "monthly"),
        ("/blog/punctuation-rules", "0.8", "monthly"),
        ("/blog/gadaa-system-language", "0.8", "monthly"),
        ("/blog/afaan-oromo-numbers", "0.8", "monthly"),
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, priority, freq in pages:
        xml += (
            f"  <url><loc>{base}{path}</loc>"
            f"<priority>{priority}</priority>"
            f"<changefreq>{freq}</changefreq></url>\n"
        )
    xml += "</urlset>"
    return Response(content=xml, media_type="application/xml")

# ---------------------------------------------------------------------------
# Web UI routes (HTML responses)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@rate_limit
async def get_form(request: Request):
    return render(request, "index.html", {"original": None, "corrected": None})


@app.post("/check", response_class=HTMLResponse)
@rate_limit
async def check_spelling(request: Request, text: str = Form(...)):
    try:
        logger.info(f"Spell check request: {text[:60]}…")
        if not text.strip():
            return render(request, "index.html", {
                "original": text, "corrected": None,
                "error": "Please enter some text",
            })
        text = _sanitise_text(text)
        result = checker.get_detailed_corrections(text)
        grammar_issues = checker.check_grammar_basic(text)
        logger.info(
            f"Corrections: {result['total_changes']}, "
            f"Grammar issues: {len(grammar_issues)}"
        )
        return render(request, "index.html", {
            "original": text,
            "corrected": result["corrected"],
            "corrections": result["corrections"],
            "grammar_issues": grammar_issues,
            "error": None,
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in check_spelling: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/upload", response_class=HTMLResponse)
@rate_limit
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        logger.info(f"File upload: {file.filename}")
        content = await file.read()
        if len(content) > 1_048_576:
            raise HTTPException(status_code=400, detail="File too large. Maximum 1 MB allowed.")
        text = content.decode("utf-8")
        result = checker.get_detailed_corrections(text)
        grammar_issues = checker.check_grammar_basic(text)
        return render(request, "index.html", {
            "original": text,
            "corrected": result["corrected"],
            "corrections": result["corrections"],
            "grammar_issues": grammar_issues,
            "error": None,
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in upload_file: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/record_feedback")
@rate_limit
async def record_feedback(request: Request):
    """
    Accept/reject a spelling correction suggestion.
    Both word fields are sanitised before being stored.
    """
    data = await request.json()
    try:
        original_word = _sanitise_word(data.get("original_word", ""))
        corrected_word = _sanitise_word(data.get("corrected_word", ""))
    except HTTPException as exc:
        return JSONResponse({"status": "error", "message": exc.detail}, status_code=exc.status_code)

    accepted = bool(data.get("accepted", True))
    checker.record_user_feedback(original_word, corrected_word, accepted)
    return JSONResponse({"status": "success", "message": "Feedback recorded"})

# ---------------------------------------------------------------------------
# Legacy JSON endpoints (kept for backwards compatibility)
# ---------------------------------------------------------------------------

@app.post("/suggestions")
@rate_limit
async def legacy_suggestions(request: Request):
    data = await request.json()
    word = data.get("word", "").strip()
    if not word:
        return JSONResponse({"suggestions": []})
    if len(word) > 60:
        raise HTTPException(status_code=400, detail="Word too long.")
    suggestions = checker.get_word_suggestions(word, top_n=5)
    return JSONResponse({"suggestions": suggestions})


@app.post("/check_grammar")
@rate_limit
async def legacy_check_grammar(request: Request):
    data = await request.json()
    text = _sanitise_text(data.get("text", ""))
    if not text:
        return JSONResponse({"issues": []})
    issues = checker.check_grammar_basic(text)
    return JSONResponse({"issues": issues})


# /api/suggest kept for autocomplete widgets — now rate-limited
@app.post("/api/suggest")
@rate_limit
async def api_suggest(request: Request):
    data = await request.json()
    word = data.get("word", "").strip()
    if not word:
        return JSONResponse({"suggestions": []})
    suggestions = checker.get_word_suggestions(word, top_n=5)
    return JSONResponse({"suggestions": suggestions})

# ---------------------------------------------------------------------------
# Versioned JSON API  (/api/v1/*)
# ---------------------------------------------------------------------------

@app.post("/api/v1/check")
@rate_limit
async def api_v1_check(request: Request):
    """
    Spell-check a piece of text.

    Request body (JSON):
        { "text": "Ani bishan dhuguu fedh" }

    Response:
        {
          "original": "...",
          "corrected": "...",
          "corrections": [ { "original": "bishan", "corrected": "bishaan",
                              "confidence": 85, "alternatives": [...] }, ... ],
          "total_changes": 2
        }
    """
    data = await request.json()
    text = _sanitise_text(data.get("text", ""))
    if not text:
        raise HTTPException(status_code=400, detail="'text' field is required.")
    result = checker.get_detailed_corrections(text)
    return JSONResponse(result)


@app.post("/api/v1/grammar")
@rate_limit
async def api_v1_grammar(request: Request):
    """
    Grammar-check a piece of text.

    Request body:  { "text": "ani bishaan dhuga" }
    Response:      { "issues": [ { "type": "...", "severity": "...", ... } ] }
    """
    data = await request.json()
    text = _sanitise_text(data.get("text", ""))
    if not text:
        raise HTTPException(status_code=400, detail="'text' field is required.")
    issues = checker.check_grammar_basic(text)
    return JSONResponse({"issues": issues})


@app.post("/api/v1/suggestions")
@rate_limit
async def api_v1_suggestions(request: Request):
    """
    Get spelling suggestions for a single word.

    Request body:  { "word": "bishan", "top_n": 5 }
    Response:      { "word": "bishan", "suggestions": ["bishaan", ...] }
    """
    data = await request.json()
    word = data.get("word", "").strip()
    if not word:
        raise HTTPException(status_code=400, detail="'word' field is required.")
    if len(word) > 60:
        raise HTTPException(status_code=400, detail="Word too long (max 60 chars).")
    top_n = min(int(data.get("top_n", 5)), 10)
    suggestions = checker.get_word_suggestions(word, top_n=top_n)
    return JSONResponse({"word": word, "suggestions": suggestions})


@app.post("/api/v1/feedback")
@rate_limit
async def api_v1_feedback(request: Request):
    """
    Submit accept/reject feedback for a spelling correction.

    Request body:
        { "original_word": "bishan", "corrected_word": "bishaan", "accepted": true }
    """
    data = await request.json()
    try:
        original_word = _sanitise_word(data.get("original_word", ""))
        corrected_word = _sanitise_word(data.get("corrected_word", ""))
    except HTTPException as exc:
        raise exc
    accepted = bool(data.get("accepted", True))
    checker.record_user_feedback(original_word, corrected_word, accepted)
    return JSONResponse({"status": "success", "message": "Feedback recorded"})


@app.get("/api/v1/health")
async def api_v1_health():
    """Liveness / readiness probe."""
    return JSONResponse({
        "status": "healthy",
        "vocabulary_size": len(checker.words_db),
        "ml_enabled": checker.use_ml,
        "rate_limiter": "redis" if _redis_client else "in-memory",
        "timestamp": datetime.now().isoformat(),
    })


@app.get("/api/v1/stats")
async def api_v1_stats():
    """Internal metrics — vocabulary, n-grams, cache, feedback."""
    cache_stats = checker.get_cache_stats()
    return JSONResponse({
        "vocabulary_size": len(checker.words_db),
        "bigrams": len(checker.bigrams),
        "trigrams": len(checker.trigrams),
        "ml_enabled": checker.use_ml,
        "cache": cache_stats,
        "user_feedback_count": len(checker.user_feedback_db),
        "rate_limiter": "redis" if _redis_client else "in-memory",
    })

# ---------------------------------------------------------------------------
# Legacy monitoring endpoints (kept for existing health-check configs)
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "vocabulary_size": len(checker.words_db),
        "ml_enabled": checker.use_ml,
        "timestamp": datetime.now().isoformat(),
    })


@app.get("/stats")
async def get_stats():
    cache_stats = checker.get_cache_stats()
    return JSONResponse({
        "vocabulary_size": len(checker.words_db),
        "bigrams": len(checker.bigrams),
        "trigrams": len(checker.trigrams),
        "ml_enabled": checker.use_ml,
        "cache": cache_stats,
        "user_feedback_count": len(checker.user_feedback_db),
    })

# ---------------------------------------------------------------------------
# Static page routes
# ---------------------------------------------------------------------------

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return render(request, "about.html", {})

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return render(request, "help.html", {})

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return render(request, "privacy.html", {})

@app.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    return render(request, "blog.html", {})

@app.get("/blog/qubee-alphabet-guide", response_class=HTMLResponse)
async def blog_qubee_alphabet(request: Request):
    return render(request, "blog_qubee_alphabet.html", {})

@app.get("/blog/common-spelling-mistakes", response_class=HTMLResponse)
async def blog_spelling_mistakes(request: Request):
    return render(request, "blog_spelling_mistakes.html", {})

@app.get("/blog/grammar-basics", response_class=HTMLResponse)
async def blog_grammar_basics(request: Request):
    return render(request, "blog_grammar_basics.html", {})

@app.get("/blog/history-of-afaan-oromo", response_class=HTMLResponse)
async def blog_history(request: Request):
    return render(request, "blog_history.html", {})

@app.get("/blog/improve-writing-skills", response_class=HTMLResponse)
async def blog_improve_writing(request: Request):
    return render(request, "blog_improve_writing.html", {})

@app.get("/blog/afaan-oromo-dialects", response_class=HTMLResponse)
async def blog_oromo_dialects(request: Request):
    return render(request, "blog_oromo_dialects.html", {})

@app.get("/blog/afaan-oromo-proverbs", response_class=HTMLResponse)
async def blog_oromo_proverbs(request: Request):
    return render(request, "blog_oromo_proverbs.html", {})

@app.get("/blog/punctuation-rules", response_class=HTMLResponse)
async def blog_punctuation(request: Request):
    return render(request, "blog_punctuation.html", {})

@app.get("/blog/gadaa-system-language", response_class=HTMLResponse)
async def blog_gadaa(request: Request):
    return render(request, "blog_gadaa_system.html", {})

@app.get("/blog/afaan-oromo-numbers", response_class=HTMLResponse)
async def blog_numbers(request: Request):
    return render(request, "blog_afaan_oromo_numbers.html", {})

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Starting Qubeessaa AI on port {port}…")
    uvicorn.run(app, host="0.0.0.0", port=port)
