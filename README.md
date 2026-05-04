# Qubee AI

AI-powered spell and grammar checker for Afaan Oromo language.

## Features

- 🤖 AI-powered spell checking with 85-95% accuracy
- 📚 59,148+ word vocabulary from Bible and Wikipedia
- 📝 Grammar checking with 12 Afaan Oromo-specific rules
- ⚡ Fast performance with smart caching
- 🌐 REST API with web interface

## Quick Start

```bash
# Clone repository
git clone https://github.com/hawitariku/qubee-ai.git
cd qubee-ai

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
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

## Technology

- **Backend**: FastAPI (Python)
- **ML Model**: AfriBERTa transformer
- **Corpus**: 59K+ words (Bible + Wikipedia)

## License

MIT License - see [LICENSE](LICENSE) file.

## Contact

- Issues: [GitHub Issues](https://github.com/hawitariku/qubee-ai/issues)
- Author: [@hawitariku](https://github.com/hawitariku)
