# Qubee AI Architecture

Technical architecture and design documentation for Qubee AI.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web Browser  │  │  Mobile App  │  │  API Client  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   Web Server    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │   Spell   │    │   Grammar   │   │   Corpus    │
    │  Checker  │    │   Checker   │   │  Manager    │
    └─────┬─────┘    └──────┬──────┘   └──────┬──────┘
          │                  │                  │
    ┌─────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │    ML     │    │ Linguistic  │   │  Vocabulary │
    │   Model   │    │    Rules    │   │  Database   │
    └───────────┘    └─────────────┘   └─────────────┘
```

## Core Components

### 1. Web Server (`main.py`)

**Technology**: FastAPI + Uvicorn

**Responsibilities**:
- HTTP request handling
- Route management
- Rate limiting
- CORS configuration
- Error handling
- Logging

**Key Endpoints**:
- `GET /` - Web interface
- `POST /check` - Spell checking
- `POST /suggestions` - Word suggestions
- `POST /check_grammar` - Grammar checking
- `GET /stats` - System statistics

**Rate Limiting**:
- 100 requests per minute per IP
- Sliding window algorithm
- Automatic cleanup of old requests

### 2. Spell Checker (`spell_checker_ml.py`)

**Core Algorithm**:
```python
def correct_word(word):
    1. Check if word exists in vocabulary → return as-is
    2. Generate candidates (edit distance 1-2)
    3. Score candidates:
       - Edit distance (40% weight)
       - Phonetic similarity (30% weight)
       - Frequency (20% weight)
       - Context (10% weight)
    4. Return highest scoring candidate
```

**Features**:
- Edit distance calculation (Levenshtein)
- Phonetic matching for Afaan Oromo
- Context-aware corrections (bigrams/trigrams)
- Caching for performance
- User feedback learning

**Afaan Oromo Specific**:
- Vowel length handling (a/aa, e/ee, i/ii, o/oo, u/uu)
- Digraph recognition (ch, sh, dh, ny, ph, th)
- Ejective consonants (c, q, x)
- Geminate consonants (doubled consonants)

### 3. Grammar Checker (`grammar_checker.py`)

**Rule-Based System**:

```python
class AfaanOromoGrammarChecker:
    - Capitalization
    - Sentence ending punctuation
    - Subject-verb agreement
    - Tense consistency
    - SOV word order
    - Question formation
    - Preposition usage
    - Conjunction placement
    - Repetitive words
    - Vowel length
    - Common patterns
    - Case marking
```

**Linguistic Knowledge**:
- Pronoun-verb agreement patterns
- Verb conjugation rules
- Tense markers
- Question words
- Prepositions and conjunctions
- Case markers

### 4. Corpus Manager (`corpus_expansion.py`)

**Responsibilities**:
- Download text from sources
- Clean and normalize text
- Merge multiple corpora
- Remove duplicates
- Generate statistics
- Validate quality

**Data Sources**:
- Bible texts (ebible.org)
- Wikipedia articles
- News websites
- Academic papers

### 5. ML Model Integration

**Model**: AfriBERTa (BERT for African languages)

**Usage**:
- Masked language modeling
- Context-aware suggestions
- Semantic similarity
- Fallback to statistical methods

**Performance**:
- First load: ~10-30 seconds
- Inference: ~0.5-2 seconds per sentence
- Cached: <0.05 seconds

## Data Flow

### Spell Checking Request

```
1. User submits text
   ↓
2. FastAPI receives POST /check
   ↓
3. Rate limiter checks request count
   ↓
4. Input validation (length, format)
   ↓
5. Spell checker processes text
   ├─ Tokenize into words
   ├─ Check each word
   ├─ Generate corrections
   └─ Apply context rules
   ↓
6. Grammar checker analyzes
   ├─ Parse sentence structure
   ├─ Apply grammar rules
   └─ Generate suggestions
   ↓
7. Format response
   ↓
8. Return HTML/JSON to user
```

### Correction Algorithm

```
Input: "bishan"

1. Vocabulary Lookup
   ├─ "bishan" not found
   └─ Generate candidates

2. Candidate Generation
   ├─ Edit distance 1: bishaan, bishan, bisaan
   ├─ Edit distance 2: bishaan, bishaani, ...
   └─ Filter: keep only words in vocabulary

3. Scoring
   For each candidate:
   ├─ Edit distance score (40%)
   │  └─ Levenshtein distance
   ├─ Phonetic score (30%)
   │  └─ Sound similarity
   ├─ Frequency score (20%)
   │  └─ Corpus frequency
   └─ Context score (10%)
      └─ Bigram/trigram probability

4. Selection
   └─ Return highest scoring: "bishaan"
```

## Database Schema

### Vocabulary Database (in-memory dict)

```python
words_db = {
    'bishaan': 5234,  # word: frequency
    'mana': 8921,
    'deeme': 3456,
    ...
}
```

### Bigrams

```python
bigrams = {
    ('ani', 'bishaan'): 45,  # (word1, word2): count
    ('bishaan', 'dhuguu'): 67,
    ...
}
```

### Trigrams

```python
trigrams = {
    ('ani', 'bishaan', 'dhuguu'): 23,  # (w1, w2, w3): count
    ...
}
```

### User Feedback

```json
{
  "fedh->fedha": {
    "accepted": 45,
    "rejected": 3,
    "last_updated": "2026-04-14T10:30:00"
  }
}
```

## Performance Optimizations

### 1. Caching Strategy

```python
cache = {
    'sentence_hash': {
        'corrected': '...',
        'timestamp': ...,
        'hit_count': 5
    }
}
```

**Benefits**:
- 50x faster for repeated queries
- Reduces CPU usage
- Improves user experience

### 2. Lazy Loading

- Corpus loaded on first request
- ML model loaded on demand
- Bigrams/trigrams computed once

### 3. Efficient Data Structures

- Hash tables for O(1) lookup
- Trie for prefix matching (future)
- BK-tree for edit distance (future)

## Security Considerations

### Input Validation

```python
# Length limits
MAX_TEXT_LENGTH = 10_000
MAX_WORD_LENGTH = 100
MAX_FILE_SIZE = 1_048_576  # 1MB

# Sanitization
- Remove control characters
- Validate UTF-8 encoding
- Escape HTML in output
```

### Rate Limiting

```python
RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Per-IP tracking
request_counts = {
    'ip_address': [timestamp1, timestamp2, ...]
}
```

### CORS Configuration

```python
# Development: Allow all origins
allow_origins = ["*"]

# Production: Restrict to specific domains
allow_origins = ["https://qubee-ai.com"]
```

## Scalability

### Current Limitations

- Single-threaded processing
- In-memory storage
- No distributed caching
- No load balancing

### Future Improvements

1. **Horizontal Scaling**
   - Multiple server instances
   - Load balancer (Nginx)
   - Shared Redis cache

2. **Database**
   - PostgreSQL for persistence
   - Redis for caching
   - Elasticsearch for search

3. **Async Processing**
   - Background job queue
   - Celery for long tasks
   - WebSocket for real-time

4. **CDN**
   - Static assets on CDN
   - Edge caching
   - Global distribution

## Deployment Architecture

### Development

```
Local Machine
├─ Python 3.11
├─ FastAPI dev server
└─ SQLite (future)
```

### Production (Recommended)

```
Cloud Provider (AWS/GCP/Azure)
├─ Load Balancer
├─ Application Servers (2+)
│  ├─ Docker containers
│  ├─ Gunicorn + Uvicorn
│  └─ Auto-scaling
├─ Database
│  ├─ PostgreSQL (primary)
│  └─ Redis (cache)
├─ Storage
│  └─ S3/Cloud Storage (corpus)
└─ Monitoring
   ├─ Prometheus
   └─ Grafana
```

## Error Handling

### Error Types

1. **Client Errors (4xx)**
   - 400: Invalid input
   - 429: Rate limit exceeded

2. **Server Errors (5xx)**
   - 500: Internal error
   - 503: Service unavailable

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2026-04-14T10:30:00Z"
}
```

### Logging

```python
# Log levels
- DEBUG: Detailed diagnostic info
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

# Log format
timestamp - level - module - message
```

## Testing Strategy

### Unit Tests
- Individual function testing
- Mock external dependencies
- Edge case coverage

### Integration Tests
- API endpoint testing
- Database interactions
- End-to-end workflows

### Performance Tests
- Load testing (Apache Bench)
- Stress testing
- Memory profiling

## Future Architecture

### Microservices (Long-term)

```
API Gateway
├─ Spell Check Service
├─ Grammar Check Service
├─ Translation Service
├─ User Management Service
└─ Analytics Service
```

### Event-Driven (Long-term)

```
Message Queue (RabbitMQ/Kafka)
├─ Spell check events
├─ User feedback events
├─ Corpus update events
└─ Analytics events
```

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | HTTP server |
| ASGI Server | Uvicorn | Production server |
| ML Framework | Transformers | NLP models |
| ML Model | AfriBERTa | Context understanding |
| Template Engine | Jinja2 | HTML rendering |
| Language | Python 3.11 | Core language |
| Containerization | Docker | Deployment |
| Version Control | Git | Source control |

---

For implementation details, see source code comments and inline documentation.
