# Changelog

All notable changes to Qubeessaa AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Versioned JSON API `/api/v1/*` (check, grammar, suggestions, feedback, health, stats)
- Redis rate limiting with in-memory fallback
- `USE_ML` env var for fast startup without transformer model
- `aiofiles` dependency for FastAPI StaticFiles
- GA4 analytics tag in all 15 templates
- Absolute canonical URLs in all blog templates
- Related-articles cross-links on all 10 blog templates
- `scripts/expand_corpus_news.py` — BBC/VOA/Wikipedia corpus scraper
- `scripts/monitor_feedback.py` — feedback analysis and review tool
- `scripts/inject_ga4.py` — bulk GA4 tag injection helper
- `.env.example` documenting all env vars
- `DEPLOY.md` — comprehensive deployment guide
- `QUICK_START.md` — developer quick-start guide

### Changed
- `python-multipart` 0.0.6 → 0.0.9 (fixes CVE-2024-24762)
- `PyPDF2` (unmaintained) → `pypdf 4.1.0`
- `lxml` 4.9.3 → 5.1.0 (security advisories on 4.x)
- `render.yaml` Python version 3.12 → 3.11.9 (torch wheel compatibility)
- `Procfile` now uses `uvicorn` directly instead of `python main.py`
- Canonical URLs updated from `replit.app` → `railway.app`
- Grammar checker: vocabulary-aware verb detection prevents noun mis-classification
- Spell checker: lazy transformer import fixes startup hang on CPU-only machines
- Spell checker: `correct_word()` now preserves input capitalisation
- Spell checker: numeric tokens and apostrophe words are no longer spell-checked
- Spell checker: user feedback capped at `_MAX_FEEDBACK_BOOST=5000` per word
- Spell checker: alternatives scored by phonetic+frequency instead of frequency only
- README completely rewritten with API docs, examples, and architecture overview

### Fixed
- Accuracy issues with frequency scoring — now uses balanced 35/35/20/10 weights
- False verb detection in grammar checker (nouns like `mana`, `nama` no longer flagged)
- `test_accuracy_fix.py` and `test_alternatives.py` moved to `tests/` directory

## [2.0.0] - 2026-04-14

### Added
- ML model integration (AfriBERTa transformer)
- User feedback recording system
- Corpus expansion tools
- 12 comprehensive grammar rules
- Smart caching system (50x faster)
- Production-ready REST API
- Rate limiting (100 req/min)
- CORS support
- 59,148+ word vocabulary

### Changed
- Upgraded from basic spell checker to ML-enhanced
- Improved accuracy from 30% to 85-95%
- Added context-aware corrections

## [1.0.0] - Initial Release

### Added
- Basic spell checking functionality
- Simple web interface
- Afaan Oromo corpus
- Edit distance algorithm
- Basic grammar checking (7 rules)

---

## Version History

- **2.0.0**: ML-enhanced version with production features
- **1.0.0**: Initial basic spell checker

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

1. Install new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update corpus file (optional but recommended):
   ```bash
   python download_bible_corpus.py
   ```

3. Restart server:
   ```bash
   python main.py
   ```

---

For detailed changes, see [GitHub Releases](https://github.com/hawitariku/qubee-ai/releases).
