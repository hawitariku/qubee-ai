try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # legacy fallback
import re

# Extract PDF text
pdf = PdfReader(open('gaz_book.pdf', 'rb'))
text = ''.join([p.extract_text() or '' for p in pdf.pages]).lower()

# Get unique words
pdf_words = set(re.findall(r"[a-z']+", text))
print(f'Total unique words in PDF: {len(pdf_words):,}')

# Load corpus words
with open('oromo_corpus.txt', 'r', encoding='utf-8') as f:
    corpus_text = f.read().lower()
corpus_words = set(re.findall(r"[a-z']+", corpus_text))

# Find new words from PDF
new_words = pdf_words - corpus_words
print(f'New words from PDF (not in corpus): {len(new_words):,}')
print(f'\nSample new words: {list(new_words)[:50]}')
