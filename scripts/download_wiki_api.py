"""
Download Afaan Oromo text using Wikipedia API (more reliable).

Uses the official MediaWiki API with proper headers and rate limiting.
"""

import requests
import time
from pathlib import Path

def get_wikipedia_article(title, lang='om'):
    """Fetch article content from Wikipedia API"""
    print(f"📥 Fetching: {title}")
    
    url = f"https://{lang}.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'extracts',
        'exintro': False,  # Get full article
        'explaintext': True,  # Plain text format
        'redirects': True
    }
    
    headers = {
        'User-Agent': 'AfaanOromoSpellChecker/1.0 (hawitariku628@gmail.com)'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        pages = data['query']['pages']
        
        # Get the first (and only) page
        page_id = list(pages.keys())[0]
        
        if page_id == '-1':
            print(f"  ✗ Article not found")
            return ""
        
        extract = pages[page_id].get('extract', '')
        
        if extract:
            # Clean up the text
            lines = [line.strip() for line in extract.split('\n') if line.strip()]
            # Filter meaningful sentences
            filtered = [line for line in lines if len(line) > 30]
            
            result = '\n'.join(filtered)
            print(f"  ✓ Extracted {len(result)} characters ({len(filtered)} paragraphs)")
            return result
        else:
            print(f"  ✗ No content found")
            return ""
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return ""

def main():
    print("=" * 60)
    print("🌐 Afaan Oromo Wikipedia API Corpus Expander")
    print("=" * 60)
    print()
    print("Downloading articles via Wikipedia API...")
    print()
    
    # List of articles to fetch
    articles = [
        "Afaan Oromoo",
        "Oromoo", 
        "Itoophiyaa",
        "Finfinnee",
        "Barnoota",
        "Seenaa Oromoo",
        "Aadaa Oromoo",
        "Gadaa",
    ]
    
    all_text = []
    successful = 0
    
    for i, title in enumerate(articles):
        text = get_wikipedia_article(title)
        if text:
            all_text.append(text)
            successful += 1
        
        # Rate limiting - wait between requests
        if i < len(articles) - 1:
            print("  ⏳ Waiting 6 seconds...")
            time.sleep(6)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Successfully downloaded {successful}/{len(articles)} articles")
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
        
    else:
        print("\n❌ No text was downloaded.")

if __name__ == "__main__":
    main()
