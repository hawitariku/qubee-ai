import re
import collections
from difflib import SequenceMatcher
from pathlib import Path

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class AfaanOromoSpellChecker:
    def __init__(self, corpus_path=None):
        self.words_db = collections.Counter()
        self.bigrams = collections.Counter()
        self.trigrams = collections.Counter()
        
        print("Initializing advanced spell checker with ALL corpus sources including PDF...")
        
        sources_loaded = 0
        
        # 1. Main corpus (oromo_corpus.txt - already has Bible merged)
        if corpus_path and Path(corpus_path).exists():
            print(f"\n[1/5] Loading main corpus: {corpus_path}")
            self.train_from_file(corpus_path)
            sources_loaded += 1
        
        # 2. Extract text DIRECTLY from gaz_book.pdf
        if Path('gaz_book.pdf').exists() and HAS_PDF:
            print(f"\n[2/5] Extracting text from PDF: gaz_book.pdf")
            pdf_text = self.extract_text_from_pdf('gaz_book.pdf')
            if pdf_text:
                print(f"   📄 Processing PDF text ({len(pdf_text):,} characters)...")
                self.train_from_text(pdf_text)
                sources_loaded += 1
                print(f"   ✅ PDF loaded successfully!")
        elif Path('gaz_book.pdf').exists() and not HAS_PDF:
            print(f"\n[2/5] ⚠️ gaz_book.pdf exists but PyPDF2 not installed")
            print("   Install with: pip install PyPDF2")
        
        # 3. Standalone Bible corpus (extracted text)
        if Path('oromo_bible_corpus.txt').exists():
            print(f"\n[3/5] Loading Bible corpus: oromo_bible_corpus.txt")
            self.train_from_file('oromo_bible_corpus.txt')
            sources_loaded += 1
        
        # 4. Backup corpus (original before Bible merge - has Wikipedia)
        if Path('oromo_corpus.txt.bak').exists():
            print(f"\n[4/5] Loading backup corpus: oromo_corpus.txt.bak")
            self.train_from_file('oromo_corpus.txt.bak')
            sources_loaded += 1
        
        # 5. Any other .txt files
        other_files = ['oromo_wikipedia_expansion.txt', 'oromo_bible_complete.txt']
        for other_file in other_files:
            if Path(other_file).exists():
                print(f"\n[+] Loading additional corpus: {other_file}")
                self.train_from_file(other_file)
                sources_loaded += 1
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Loaded {sources_loaded} corpus sources")
        print(f"📊 Vocabulary: {len(self.words_db):,} unique words")
        print(f"📊 Bigrams: {len(self.bigrams):,}")
        print(f"📊 Trigrams: {len(self.trigrams):,}")
        print(f"{'='*60}")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.lower()
        except Exception as e:
            print(f"   ⚠️ Could not extract from PDF: {e}")
            return ""
