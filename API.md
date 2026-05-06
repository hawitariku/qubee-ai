# Qubee AI API Documentation

Complete API reference for Qubee AI spell and grammar checker.

## Base URL

```
http://localhost:8082
```

## Authentication

Currently no authentication required. Rate limited to 100 requests per minute per IP.

---

## Endpoints

### 1. Web Interface

#### `GET /`

Returns the web interface HTML page.

**Response**: HTML page

---

### 2. Spell Check

#### `POST /check`

Check and correct spelling in text.

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| text | string | Yes | Text to check (max 10,000 chars) |

**Example Request**:
```bash
curl -X POST http://localhost:8082/check \
  -d "text=Ani bishan dhuguu fedh"
```

**Example Response** (HTML):
Returns HTML page with corrections displayed.

**Errors**:
- `400`: Text too long (>10,000 characters)
- `429`: Rate limit exceeded
- `500`: Internal server error

---

### 3. Word Suggestions

#### `POST /suggestions`

Get spelling suggestions for a single word.

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "word": "fedh"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8082/suggestions \
  -H "Content-Type: application/json" \
  -d '{"word":"fedh"}'
```

**Example Response**:
```json
{
  "suggestions": ["fedha", "fedhe", "fedhee"]
}
```

**Errors**:
- `400`: Word too long (>100 characters)
- `429`: Rate limit exceeded

---

### 4. Grammar Check

#### `POST /check_grammar`

Check grammar in text.

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "text": "ani bishaan dhuga"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8082/check_grammar \
  -H "Content-Type: application/json" \
  -d '{"text":"ani bishaan dhuga"}'
```

**Example Response**:
```json
{
  "issues": [
    {
      "type": "capitalization",
      "severity": "warning",
      "message": "First word should be capitalized",
      "suggestion": "Ani",
      "position": 0,
      "word": "ani"
    },
    {
      "type": "missing_punctuation",
      "severity": "warning",
      "message": "Sentence should end with period",
      "suggestion": ".",
      "position": 2,
      "word": "dhuga"
    }
  ]
}
```

**Issue Severities**:
- `error`: Critical grammar error
- `warning`: Recommended fix
- `info`: Suggestion for improvement

**Errors**:
- `400`: Text too long (>10,000 characters)
- `429`: Rate limit exceeded

---

### 5. File Upload

#### `POST /upload`

Upload and check a text file.

**Content-Type**: `multipart/form-data`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes | Text file (max 1MB) |

**Example Request**:
```bash
curl -X POST http://localhost:8082/upload \
  -F "file=@document.txt"
```

**Response**: HTML page with corrections

**Errors**:
- `400`: File too large (>1MB)
- `429`: Rate limit exceeded
- `500`: File processing error

---

### 6. Auto-complete Suggestions

#### `POST /api/suggest`

Get word suggestions for auto-complete.

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "word": "bish"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8082/api/suggest \
  -H "Content-Type: application/json" \
  -d '{"word":"bish"}'
```

**Example Response**:
```json
{
  "suggestions": ["bishaan", "bishaan", "bishaanii"]
}
```

---

### 7. Record Feedback

#### `POST /record_feedback`

Record user feedback on corrections.

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "original_word": "fedh",
  "corrected_word": "fedha",
  "accepted": true
}
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| original_word | string | Yes | Original misspelled word |
| corrected_word | string | Yes | Suggested correction |
| accepted | boolean | Yes | Whether user accepted correction |

**Example Request**:
```bash
curl -X POST http://localhost:8082/record_feedback \
  -H "Content-Type: application/json" \
  -d '{"original_word":"fedh","corrected_word":"fedha","accepted":true}'
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

**Errors**:
- `400`: Missing parameters

---

### 8. Statistics

#### `GET /stats`

Get system statistics.

**Example Request**:
```bash
curl http://localhost:8082/stats
```

**Example Response**:
```json
{
  "vocabulary_size": 59148,
  "bigrams": 325974,
  "trigrams": 481348,
  "ml_enabled": true,
  "cache": {
    "hits": 1523,
    "misses": 342,
    "hit_rate": 0.817
  },
  "user_feedback_count": 45
}
```

---

## Rate Limiting

- **Limit**: 100 requests per minute per IP address
- **Response**: `429 Too Many Requests` when exceeded
- **Headers**: No rate limit headers currently provided

---

## Error Responses

All errors return JSON with this format:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid input)
- `429`: Too Many Requests (rate limit)
- `500`: Internal Server Error

---

## Code Examples

### Python

```python
import requests

# Spell check
response = requests.post('http://localhost:8082/check',
                        data={'text': 'Ani bishaan dhuguu fedh'})
print(response.text)

# Get suggestions
response = requests.post('http://localhost:8082/suggestions',
                        json={'word': 'fedh'})
print(response.json())

# Grammar check
response = requests.post('http://localhost:8082/check_grammar',
                        json={'text': 'ani bishaan dhuga'})
print(response.json())

# Get statistics
response = requests.get('http://localhost:8082/stats')
print(response.json())
```

### JavaScript

```javascript
// Spell check
fetch('http://localhost:8082/check', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'text=Ani bishaan dhuguu fedh'
})
.then(response => response.text())
.then(html => console.log(html));

// Get suggestions
fetch('http://localhost:8082/suggestions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({word: 'fedh'})
})
.then(response => response.json())
.then(data => console.log(data.suggestions));

// Grammar check
fetch('http://localhost:8082/check_grammar', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'ani bishaan dhuga'})
})
.then(response => response.json())
.then(data => console.log(data.issues));
```

### cURL

```bash
# Spell check
curl -X POST http://localhost:8082/check \
  -d "text=Ani bishaan dhuguu fedh"

# Get suggestions
curl -X POST http://localhost:8082/suggestions \
  -H "Content-Type: application/json" \
  -d '{"word":"fedh"}'

# Grammar check
curl -X POST http://localhost:8082/check_grammar \
  -H "Content-Type: application/json" \
  -d '{"text":"ani bishaan dhuga"}'

# Statistics
curl http://localhost:8082/stats
```

---

## CORS

CORS is enabled for all origins (`*`). Suitable for development but should be restricted in production.

---

## Logging

All requests are logged to `spell_checker.log` with timestamps and details.

---

## Future API Changes

Planned additions:
- Authentication with API keys
- Batch processing endpoint
- WebSocket for real-time checking
- Language detection
- Translation endpoints

---

For questions or issues, please open a GitHub issue.
