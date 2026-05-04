# Qubee AI

**AI-powered language assistant for Afaan Oromo** - Intelligent spell checking, grammar validation, and context-aware corrections using transformer models and linguistic rules.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 What is Qubee AI?

Qubee AI is a production-ready spell and grammar checker specifically designed for the Afaan Oromo language. It combines machine learning (AfriBERTa transformer) with linguistic expertise to provide accurate, context-aware corrections that understand Afaan Oromo's unique grammar patterns.

## ✨ Key Features

- 🤖 **AI-Powered Corrections** - Hybrid ML + statistical approach for 85-95% accuracy
- 📚 **Rich Vocabulary** - 59,148+ words from Bible and Wikipedia sources
- 🎯 **Context-Aware** - Understands pronoun-verb agreement, SOV word order, and tense consistency
- ⚡ **Fast Performance** - Smart caching delivers 50x faster repeated queries
- 📝 **Grammar Checking** - 12 comprehensive grammar rules for Afaan Oromo
- 🔄 **Learning System** - Improves from user feedback over time
- 🌐 **REST API** - Production-ready endpoints with rate limiting and CORS
- 🎨 **Web Interface** - Clean, intuitive UI for instant corrections

## 🔤 Language-Specific Intelligence

Qubee AI understands Afaan Oromo's unique features:
- Vowel length distinctions (a vs aa, e vs ee)
- Digraphs (ch, sh, dh, ny, ph, th)
- Ejective consonants (c, q, x)
- Geminate consonants (yy, tt, etc.)
- SOV (Subject-Object-Verb) word order
- Pronoun-verb agreement patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/hawitariku/qubee-ai.git
cd qubee-ai

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:8082
```

## 📖 Usage Examples

### Web Interface

1. Open `http://localhost:8082` in your browser
2. Type or paste Afaan Oromo text in the text area
3. Click "Check Spelling" button
4. View corrections and grammar suggestions

### API Usage

```python
import requests

# Check spelling
response = requests.post('http://localhost:8082/check',
                        data={'text': 'Ani bishaan dhuguu fedh'})

# Get word suggestions
response = requests.post('http://localhost:8082/suggestions',
                        json={'word': 'fedh'})

# Check grammar
response = requests.post('http://localhost:8082/check_grammar',
                        json={'text': 'Ani bishaan dhuguu fedha'})
```

## 🧪 Test Sentences

Try these examples to see Qubee AI in action:

| Input | Expected Output | Tests |
|-------|----------------|-------|
| `Ani bishan dhuguu fedh` | `ani bishaan dhuguu fedha` | Vowel length, capitalization, verb ending |
| `Isheen mana deeme` | `isheen mana deemte` | Pronoun-verb agreement |
| `Waaqayo nagaa kenna` | `Waaqayyo nagaa kenna` | Geminate consonant |
| `Inni gara mana barumsaa deeme` | `inni gara mana barumsaa deeme` | Correct sentence recognition |

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **ML Model**: AfriBERTa transformer
- **NLP**: Custom linguistic rules + statistical methods
- **Frontend**: HTML/Jinja2 templates
- **Corpus**: 59K+ words (Bible + Wikipedia)

## 📊 Performance Metrics

- **Accuracy**: 85-95% on common words
- **Speed**: <0.05s for cached queries, 2-5s for new queries
- **Vocabulary**: 59,148 unique words
- **N-grams**: 325,974 bigrams + 481,348 trigrams
- **Grammar Rules**: 12 comprehensive checks

## 📁 Project Structure

```
qubee-ai/
├── main.py                          # FastAPI web server
├── grammar_checker.py               # Grammar checking engine
├── spell_checker_ml.py              # ML-enhanced spell checker
├── corpus_expansion.py              # Corpus management tools
├── oromo_corpus.txt                 # Main vocabulary database
├── templates/                       # HTML templates
│   └── index.html                   # Web interface
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🔧 Configuration

### Server Settings

Edit `main.py` to configure:
- Port number (default: 8082)
- Rate limiting (default: 100 requests/minute)
- CORS settings
- Logging level

### Corpus Expansion

To expand the vocabulary:

```bash
# Download more Wikipedia articles
python corpus_expansion.py

# Download Bible texts
python download_bible_corpus.py
```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/check` | POST | Spell check text |
| `/suggestions` | POST | Get word suggestions |
| `/check_grammar` | POST | Grammar checking |
| `/upload` | POST | Upload file for checking |
| `/record_feedback` | POST | Record user feedback |
| `/stats` | GET | System statistics |

## 💡 Use Cases

- ✍️ Writing assistance for Afaan Oromo content
- 📖 Educational tools for language learners
- 📰 Content editing for news and publications
- 🔬 NLP research on low-resource languages
- 🌍 Language preservation and standardization

## 🌟 Why "Qubee"?

"Qubee" (ቁቤ) means "alphabet" or "writing system" in Afaan Oromo. Qubee AI honors the Qubee Latin script adopted in 1991, which revolutionized Oromo literacy and cultural expression.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Expand the Corpus**: Add more Afaan Oromo text sources
2. **Improve Accuracy**: Refine the scoring algorithm
3. **Add Features**: Implement new functionality
4. **Fix Bugs**: Report and fix issues
5. **Documentation**: Improve guides and examples

### Development Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR_USERNAME/qubee-ai.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git commit -am "Add your feature"

# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request
```

## 📝 Known Issues

- **70% false correction rate** in some cases (see `ACCURACY_PROBLEM_SUMMARY.md`)
- Frequency scoring can dominate edit distance
- Context bonuses may override correct suggestions

See `ACCURACY_FIX_GUIDE.md` for solutions.

## 🗺️ Roadmap

### Short-term (1-2 weeks)
- [ ] Fix accuracy issues with balanced scoring
- [ ] Add BK-tree for faster edit distance
- [ ] Implement Redis caching
- [ ] Create browser extension prototype

### Medium-term (1-2 months)
- [ ] Build mobile app (React Native)
- [ ] Add voice input (speech-to-text)
- [ ] Implement translation features
- [ ] Create VS Code extension

### Long-term (3-6 months)
- [ ] Community platform for corpus contributions
- [ ] Multi-dialect support
- [ ] Advanced NLP (summarization, paraphrasing)
- [ ] Enterprise deployment options

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Sources**: [ebible.org](https://ebible.org) and [Afaan Oromo Wikipedia](https://om.wikipedia.org)
- **ML Model**: AfriBERTa transformer
- **Community**: Oromo language speakers and contributors

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/hawitariku/qubee-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hawitariku/qubee-ai/discussions)
- **Author**: [@hawitariku](https://github.com/hawitariku)

## ⭐ Star History

If you find Qubee AI useful, please consider giving it a star! ⭐

---

**Built with ❤️ for the Afaan Oromo community**
