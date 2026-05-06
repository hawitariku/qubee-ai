"""
Download complete Afaan Oromo Bible text from eBible.org
This downloads the Guji Oromo Bible (Kitaaba Woyyuu) in plain text format
and adds it to the corpus for better spell checking.
"""

import requests
import zipfile
import re
from pathlib import Path

# URL for the plain text Bible (readaloud format - easy to parse)
BIBLE_ZIP_URL = "https://ebible.org/Scripture-DL/text/gax_readaloud.zip"

def download_bible_zip():
    """Download the Bible text ZIP file"""
    print("📥 Downloading Afaan Oromo Bible text...")
    print("   Source: eBible.org (Guji Oromo - Kitaaba Woyyuu)")
    print("   Size: ~1-2 MB")
    print()
    
    try:
        response = requests.get(BIBLE_ZIP_URL, timeout=60)
        response.raise_for_status()
        
        # Save ZIP file
        zip_path = Path("gax_readaloud.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def extract_and_clean(zip_path):
    """Extract text files and clean the content"""
    print("\n📂 Extracting Bible texts...")
    
    extract_dir = Path("bible_text_temp")
    extract_dir.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            print(f"✅ Extracted {len(zip_ref.namelist())} files")
        
        # Read all text files
        all_text = []
        text_files = list(extract_dir.glob("*.txt")) + list(extract_dir.rglob("*.txt"))
        
        print(f"\n📖 Processing {len(text_files)} text files...")
        
        for txt_file in sorted(text_files):
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Clean the text
            cleaned = clean_bible_text(content)
            if cleaned:
                all_text.append(cleaned)
                print(f"  ✓ {txt_file.name} ({len(cleaned)} chars)")
        
        return '\n\n'.join(all_text)
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return ""

def clean_bible_text(text):
    """Clean Bible text - keep meaningful sentences"""
    # Split into lines
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip very short lines (likely headers/numbers)
        if len(line) < 15:
            continue
        
        # Keep lines that have Oromo patterns
        # Common Oromo words: akka, jedhe, inni, isheen, gara, fi, kana, sana
        oromo_patterns = [' akka ', ' jedhe', ' inni ', ' isheen ', ' gara ', 
                         ' fi ', ' kana', ' sana', ' Waaqa', ' Waaqayyo',
                         ' Yesuus', ' Kristos', ' Rabbi', ' isa', ' isaani']
        
        has_oromo = any(pattern in line for pattern in oromo_patterns)
        
        if has_oromo or len(line) > 30:  # Keep longer lines too
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def merge_with_corpus(bible_text):
    """Merge Bible text with existing corpus"""
    corpus_file = Path("oromo_corpus.txt")
    
    if corpus_file.exists():
        print("\n🔄 Merging with existing corpus...")
        with open(corpus_file, 'r', encoding='utf-8') as f:
            original = f.read()
        
        # Create backup
        backup = corpus_file.with_suffix('.txt.bak')
        corpus_file.rename(backup)
        print(f"  ✓ Backup created: {backup}")
        
        # Merge: Bible text first, then original
        merged = bible_text + "\n\n" + original
        
        with open(corpus_file, 'w', encoding='utf-8') as f:
            f.write(merged)
        
        print(f"  ✓ Merged successfully!")
        return len(merged)
    else:
        # Create new corpus
        print("\n📝 Creating new corpus file...")
        with open(corpus_file, 'w', encoding='utf-8') as f:
            f.write(bible_text)
        return len(bible_text)

def main():
    print("=" * 70)
    print("📖 Afaan Oromo Bible Corpus Downloader - COMPLETE EDITION")
    print("=" * 70)
    print()
    print("This will download the COMPLETE Guji Oromo Bible (Kitaaba Woyyuu)")
    print("and add it to your spell checker corpus.")
    print()
    
    # Step 1: Download
    zip_path = download_bible_zip()
    if not zip_path:
        print("\n❌ Cannot proceed without download. Check internet connection.")
        return
    
    # Step 2: Extract and clean
    bible_text = extract_and_clean(zip_path)
    
    if not bible_text:
        print("\n❌ No text extracted from Bible files.")
        return
    
    print(f"\n📊 Total Bible text: {len(bible_text):,} characters")
    
    # Step 3: Save standalone Bible file
    bible_file = Path("oromo_bible_complete.txt")
    with open(bible_file, 'w', encoding='utf-8') as f:
        f.write(bible_text)
    print(f"💾 Saved standalone Bible: {bible_file}")
    
    # Step 4: Merge with corpus
    new_size = merge_with_corpus(bible_text)
    print(f"📊 New corpus size: {new_size:,} characters")
    
    # Step 5: Count words
    words = set(re.findall(r"[a-z']+", bible_text.lower()))
    print(f"🔤 New vocabulary: {len(words):,} unique words")
    
    print("\n" + "=" * 70)
    print("✨ SUCCESS! Bible corpus added!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart your web server:")
    print("   C:\\Python312\\python.exe main.py")
    print("2. Test with Bible verses!")
    print("\nExample test sentences:")
    print("  'Waaqi jalqaba ol-gubba'aa fi lafa dade'")
    print("  'Yesuus Kristos fayyisaa dha'")
    print("  'Worra Waaqa jaalatu ka akka fedha isaa waamameef'")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
