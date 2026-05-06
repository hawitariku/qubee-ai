"""
Download additional Afaan Oromo texts from Wikipedia to expand corpus
Focuses on news, literature, culture, and general knowledge
"""

import requests
import re
from pathlib import Path
import time

# Afaan Oromo Wikipedia articles to download
WIKI_ARTICLES = [
    # Culture & History
    "Oromoo",
    "Sirna_Gadaa",
    "Aadaa_Oromoo",
    "Seenaa_Oromoo",
    
    # Geography
    "Oromiyaa",
    "Finfinnee",
    "Itoophiyaa",
    
    # Language & Literature
    "Afaan_Oromoo",
    "Qubee_Afaan_Oromoo",
    
    # Science & Education
    "Barumsa",
    "Saayinsii",
    "Teeknooloojii",
    
    # Religion
    "Amantii",
    "Kiristaanummaa",
    " Islaama",
    
    # Modern topics
    "Fayyaa",
    "Diinagdee",
    "Siyaasa",
]

def download_wikipedia_article(title):
    """Download a single Wikipedia article in Afaan Oromo"""
    # Afaan Oromo Wikipedia API endpoint
    url = f"https://om.wikipedia.org/api/rest_v1/page/html/{title}"
    
    headers = {
        'User-Agent': 'AfaanOromoCorpusBuilder/1.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract text from HTML
        html_text = response.text
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Split into sentences (approximate)
        sentences = re.split(r'[.!?]+', text)
        
        # Filter meaningful sentences
        meaningful = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences with Oromo characteristics
            if len(sentence) > 20:
                # Check if it has common Oromo words
                oromo_indicators = [' akka ', ' jedhe', ' inni ', ' isheen ', ' gara ', 
                                   ' fi ', ' kana', ' sana', ' Waaqa', ' Oromoo',
                                   ' ta\'e', ' taate', ' jira', ' dha']
                
                has_oromo = any(indicator in sentence.lower() for indicator in oromo_indicators)
                
                if has_oromo or len(sentence) > 40:
                    meaningful.append(sentence + '.')
        
        return '\n'.join(meaningful)
        
    except Exception as e:
        print(f"  ✗ Failed to download '{title}': {e}")
        return ""

def main():
    print("=" * 70)
    print("📚 Afaan Oromo Corpus Expander - Wikipedia Articles")
    print("=" * 70)
    print()
    print("Downloading additional articles from om.wikipedia.org")
    print()
    
    all_text = []
    successful = 0
    
    for i, title in enumerate(WIKI_ARTICLES, 1):
        print(f"[{i}/{len(WIKI_ARTICLES)}] Downloading: {title}")
        text = download_wikipedia_article(title)
        
        if text:
            all_text.append(text)
            successful += 1
            print(f"  ✓ Got {len(text)} characters")
        else:
            print(f"  ✗ Skipped")
        
        # Be polite to the server
        time.sleep(1)
    
    print(f"\n✅ Successfully downloaded {successful}/{len(WIKI_ARTICLES)} articles")
    
    if all_text:
        # Combine all texts
        combined = '\n\n'.join(all_text)
        
        # Save to file
        output_file = Path("oromo_wikipedia_expansion.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined)
        
        print(f"\n💾 Saved to: {output_file}")
        print(f"📊 Total text: {len(combined):,} characters")
        
        # Count words
        words = set(re.findall(r"[a-z']+", combined.lower()))
        print(f"🔤 Unique words: {len(words):,}")
        
        # Option to merge with main corpus
        print("\n🔄 Would you like to merge with main corpus?")
        print("   This will improve spell checking accuracy!")
        
        merge = input("   Type 'yes' to merge (or press Enter to skip): ").strip().lower()
        
        if merge == 'yes':
            corpus_file = Path("oromo_corpus.txt")
            if corpus_file.exists():
                with open(corpus_file, 'r', encoding='utf-8') as f:
                    original = f.read()
                
                # Create backup
                backup = corpus_file.with_suffix('.txt.bak2')
                corpus_file.rename(backup)
                print(f"  ✓ Backup created: {backup}")
                
                # Merge
                merged = original + "\n\n" + combined
                with open(corpus_file, 'w', encoding='utf-8') as f:
                    f.write(merged)
                
                print(f"  ✓ Merged successfully!")
                print(f"  📊 New corpus size: {len(merged):,} characters")
            else:
                print("  ✗ Main corpus file not found!")
        
        print("\n" + "=" * 70)
        print("✨ DONE!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Restart your web server to load new corpus")
        print("2. Test with various sentences")
        
    else:
        print("\n❌ No text was downloaded. Check your internet connection.")

if __name__ == "__main__":
    main()
