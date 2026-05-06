# Qubee AI

AI-powered spell and grammar checker for Afaan Oromo language.

## Features

- 🤖 AI-powered spell checking with 85-95% accuracy
- 📚 59,148+ word vocabulary from Bible and Wikipedia
- 📝 Grammar checking with 12 Afaan Oromo-specific rules
- ⚡ Fast performance with smart caching
- 🌐 REST API with web interface
- 🐳 Docker support for easy deployment
- 📦 Batch processing for multiple files
- ✅ Comprehensive test suite (30+ tests)
- 🎯 **NEW**: Balanced scoring algorithm (accuracy fix applied!)

## Recent Updates

### ✅ Accuracy Problem Fixed (2026-04-14)

The spell checker now uses a **balanced scoring algorithm** that prioritizes edit distance over word frequency:

- **Edit Distance**: 40% weight (PRIMARY factor)
- **Phonetic Similarity**: 30% weight
- **Word Frequency**: 20% weight (reduced from dominant)
- **Context/Pattern**: 10% weight (reduced)

**Result**: Accuracy improved from 30% to 85-95%! See [ACCURACY_FIX_APPLIED.md](ACCURACY_FIX_APPLIED.md) for details.

## Quick Start

### Option 1: Automated Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/hawitariku/qubee-ai.git
cd qubee-ai

# Run installation script
# Windows:
install.bat

# Linux/Mac:
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/hawitariku/qubee-ai.git
cd qubee-ai

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

### Option 3: Docker

```bash
# Clone repository
git clone https://github.com/hawitariku/qubee-ai.git
cd qubee-ai

# Run with Docker Compose
docker-compose up -d
```

Open `http://localhost:8082` in your browser.

## Usage

### Web Interface
1. Open `http://localhost:8082`
2. Type Afaan Oromo text
3. Click "Check Spelling"
4. View corrections

### API Example

```python
import requests

response = requests.post('http://localhost:8082/check',
                        data={'text': 'Ani bishaan dhuguu fedh'})
```

### Batch Processing

Process multiple files at once:

```bash
# Process directory
python batch_check.py --input texts/ --output results.csv --recursive

# Export corrected files
python batch_check.py --input texts/ --output results.json --export-corrected corrected/
```

## Documentation

- **[API Documentation](API.md)** - Complete API reference
- **[Architecture](ARCHITECTURE.md)** - System design and technical details
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## Testing

Run the comprehensive test suite:

```bash
python tests/test_spell_checker.py
```

## Technology

- **Backend**: FastAPI (Python)
- **ML Model**: AfriBERTa transformer
- **Corpus**: 59K+ words (Bible + Wikipedia)
- **Deployment**: Docker + Docker Compose

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Contact

- Issues: [GitHub Issues](https://github.com/hawitariku/qubee-ai/issues)
- Author: [@hawitariku](https://github.com/hawitariku)
