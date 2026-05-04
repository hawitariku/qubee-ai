from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from spell_checker_ml import MLEnhancedSpellChecker
import logging
from datetime import datetime
from jinja2 import FileSystemLoader, ChoiceLoader, BaseLoader
import time
from functools import wraps

app = FastAPI(title="Afaan Oromo Spell Checker", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(
    filename='spell_checker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
request_counts = {}
RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def rate_limit(f):
    @wraps(f)
    async def decorator(*args, **kwargs):
        request = kwargs.get('request') or args[0]
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        
        # Remove old requests
        request_counts[client_ip] = [
            t for t in request_counts[client_ip]
            if current_time - t < RATE_LIMIT_WINDOW
        ]
        
        if len(request_counts[client_ip]) >= RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        request_counts[client_ip].append(current_time)
        return await f(*args, **kwargs)
    return decorator

# Initialize templates with disabled cache for compatibility
from starlette.templating import Jinja2Templates as StarletteJinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0  # Disable cache
)

def templates(request: Request, name: str, context: dict):
    template = jinja_env.get_template(name)
    content = template.render(request=request, **context)
    return HTMLResponse(content=content)

# Initialize ML-enhanced spell checker
print("🔄 Initializing ML-Enhanced Spell Checker...")
checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=True)
print("✅ ML-Enhanced spell checker ready!")

@app.get("/", response_class=HTMLResponse)
@rate_limit
async def get_form(request: Request):
    """Show the web interface"""
    return templates(request, "index.html", {
        "original": None,
        "corrected": None
    })

@app.post("/check")
@rate_limit
async def check_spelling(request: Request, text: str = Form(...)):
    """Process spelling correction with detailed feedback"""
    try:
        logger.info(f"Spell check request: {text[:50]}...")
        
        if not text.strip():
            return templates(request, "index.html", {
                "original": text,
                "corrected": None,
                "error": "Please enter some text"
            })
        
        # Validate input length
        if len(text) > 10000:
            return templates(request, "index.html", {
                "original": text,
                "corrected": None,
                "error": "Text too long. Maximum 10,000 characters allowed."
            })
        
        # Get detailed corrections
        result = checker.get_detailed_corrections(text)
        
        # Check grammar
        grammar_issues = checker.check_grammar_basic(text)
        
        logger.info(f"Corrections: {result['total_changes']}, Grammar issues: {len(grammar_issues)}")
        
        return templates(request, "index.html", {
            "original": text,
            "corrected": result['corrected'],
            "corrections": result['corrections'],
            "grammar_issues": grammar_issues,
            "error": None
        })
    except Exception as e:
        logger.error(f"Error in check_spelling: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/suggestions")
@rate_limit
async def get_suggestions(request: Request):
    """Get word suggestions for a misspelled word"""
    try:
        data = await request.json()
        word = data.get('word', '')
        
        if not word.strip():
            return JSONResponse({'suggestions': []})
        
        if len(word) > 100:
            raise HTTPException(status_code=400, detail="Word too long")
        
        suggestions = checker.get_word_suggestions(word.strip(), top_n=5)
        return JSONResponse({'suggestions': suggestions})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check_grammar")
@rate_limit
async def check_grammar(request: Request):
    """Check grammar of a sentence"""
    try:
        data = await request.json()
        text = data.get('text', '')
        
        if not text.strip():
            return JSONResponse({'issues': []})
        
        if len(text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long")
        
        issues = checker.check_grammar_basic(text.strip())
        return JSONResponse({'issues': issues})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_grammar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
@rate_limit
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Process uploaded text file"""
    try:
        logger.info(f"File upload: {file.filename}")
        
        # Validate file size (max 1MB)
        content = await file.read()
        if len(content) > 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum 1MB allowed.")
        
        text = content.decode('utf-8')
        
        result = checker.get_detailed_corrections(text)
        grammar_issues = checker.check_grammar_basic(text)
        
        return templates(request, "index.html", {
            "original": text,
            "corrected": result['corrected'],
            "corrections": result['corrections'],
            "grammar_issues": grammar_issues,
            "error": None
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggest")
async def api_suggest(request: Request):
    """API endpoint for auto-complete/suggestions"""
    data = await request.json()
    word = data.get('word', '')
    
    if not word.strip():
        return JSONResponse({'suggestions': []})
    
    suggestions = checker.get_word_suggestions(word.strip(), top_n=5)
    return JSONResponse({'suggestions': suggestions})

@app.post("/record_feedback")
async def record_feedback(request: Request):
    """Record user feedback on corrections"""
    data = await request.json()
    original_word = data.get('original_word', '')
    corrected_word = data.get('corrected_word', '')
    accepted = data.get('accepted', True)
    
    if not original_word or not corrected_word:
        return JSONResponse({'status': 'error', 'message': 'Missing parameters'})
    
    checker.record_user_feedback(original_word, corrected_word, accepted)
    return JSONResponse({'status': 'success', 'message': 'Feedback recorded'})

@app.get("/stats")
async def get_stats():
    """Get spell checker statistics"""
    vocab_size = len(checker.words_db)
    bigram_count = len(checker.bigrams)
    trigram_count = len(checker.trigrams)
    cache_stats = checker.get_cache_stats()
    
    return JSONResponse({
        'vocabulary_size': vocab_size,
        'bigrams': bigram_count,
        'trigrams': trigram_count,
        'ml_enabled': checker.use_ml,
        'cache': cache_stats,
        'user_feedback_count': len(checker.user_feedback_db)
    })

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Afaan Oromo Spell Checker Web Server...")
    print("📍 Open your browser and go to: http://localhost:8082")
    print("💡 Press Ctrl+C to stop the server\n")
    uvicorn.run(app, host="0.0.0.0", port=8082)
