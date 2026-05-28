"""
Download science, technology, health, and business articles from Afaan Oromo Wikipedia.

This expands vocabulary into modern professional domains.
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
        'exintro': False,
        'explaintext': True,
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
        page_id = list(pages.keys())[0]
        
        if page_id == '-1':
            print(f"  ✗ Article not found")
            return ""
        
        extract = pages[page_id].get('extract', '')
        
        if extract:
            lines = [line.strip() for line in extract.split('\n') if line.strip()]
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
    print("🔬 Professional Vocabulary Expander")
    print("=" * 60)
    print()
    print("Downloading science, tech, health & business articles...")
    print()
    
    # Diverse professional topics
    articles = [
        # Science & Technology
        "Saayinsii",
        "Teeknooloojii",
        "Kompiitara",
        "Intarneetii",
        
        # Health & Medicine
        "Fayyaa",
        "Hospitaala",
        "Qorichaa",
        
        # Business & Economy
        "Diinagdee",
        "Daldalaa",
        "Hojii",
        
        # Education
        "Yuunivarsiitii",
        "Man_barumsaa",
    ]
    
    all_text = []
    successful = 0
    
    for i, title in enumerate(articles):
        text = get_wikipedia_article(title)
        if text:
            all_text.append(text)
            successful += 1
        
        # Rate limiting
        if i < len(articles) - 1:
            time.sleep(6)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Successfully downloaded {successful}/{len(articles)} articles")
    print(f"{'=' * 60}")
    
    if all_text:
        combined = '\n\n'.join(all_text)
        
        # Append to existing corpus
        corpus_file = Path("oromo_corpus.txt")
        
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
