"""
Download Afaan Oromo text from Wikipedia to expand the corpus.

This script:
1. Fetches articles from om.wikipedia.org
2. Extracts clean text content
3. Appends to oromo_corpus.txt
4. Shows progress and statistics
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time

# Afaan Oromo Wikipedia articles to download
WIKIPEDIA_ARTICLES = [
    "https://om.wikipedia.org/wiki/Afaan_Oromoo",
    "https://om.wikipedia.org/wiki/Oromoo",
    "https://om.wikipedia.org/wiki/Itoophiyaa",
    "https://om.wikipedia.org/wiki/Finfinnee",
    "https://om.wikipedia.org/wiki/Barnoota",
]

def download_article(url):
    """Download and extract text from a Wikipedia article"""
    print(f"\n📥 Downloading: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            print("  ✗ Could not find content")
            return ""
        
        # Get all paragraphs
        paragraphs = content_div.find_all('p')
        
        text_lines = []
        for p in paragraphs:
            # Remove references like [1], [2]
            text = p.get_text()
            text = re.sub(r'\[\d+\]', '', text)
            
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Filter: keep sentences with Oromo characteristics
            if len(text) > 30 and any(word in text.lower() for word in 
                                     [' akka ', ' jedhe ', ' inni ', ' isheen ', 
                                      ' dha ', ' ni ', ' kan ', ' fi ']):
                text_lines.append(text)
        
        extracted = '\n'.join(text_lines)
        print(f"  ✓ Extracted {len(extracted)} characters ({len(text_lines)} sentences)")
        
        return extracted
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return ""

def main():
    print("=" * 60)
    print("🌐 Afaan Oromo Wikipedia Corpus Expander")
    print("=" * 60)
    print()
    print("Downloading articles from om.wikipedia.org...")
    print()
    
    all_text = []
    successful = 0
    
    for url in WIKIPEDIA_ARTICLES:
        text = download_article(url)
        if text:
            all_text.append(text)
            successful += 1
        
        # Wait to respect Wikipedia's rate limits
        time.sleep(5)

    print(f"\n{'=' * 60}")
    print(f"✅ Successfully downloaded {successful}/{len(WIKIPEDIA_ARTICLES)} articles")
    print(f"{'=' * 60}")
    
    if all_text:
        combined = '\n\n'.join(all_text)
        
        # Append to existing corpus
        corpus_file = Path("oromo_corpus.txt")
        
        # Read existing content
        if corpus_file.exists():
            with open(corpus_file, 'r', encoding='utf-8') as f:
                existing = f.read()
            merged = existing + "\n\n" + combined
        else:
            merged = combined
        
        # Save merged corpus
        with open(corpus_file, 'w', encoding='utf-8') as f:
            f.write(merged)
        
        print(f"\n💾 Updated: {corpus_file}")
        print(f"📊 Total size: {len(merged):,} characters")
        print(f"📈 Added: {len(combined):,} new characters")
        
        # Count approximate words
        words = len(merged.split())
        print(f"🔤 Approximate words: {words:,}")
        
        print("\n" + "=" * 60)
        print("✨ DONE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart your web server:")
        print("   C:\\Python312\\python.exe main.py")
        print("2. Test with expanded vocabulary!")
        print("\nExample test sentence:")
        print("  'Afaan Oromoo kuusaa jechoota bal'aa qaba'")
        
    else:
        print("\n❌ No text was downloaded. Check your internet connection.")

if __name__ == "__main__":
    main()
