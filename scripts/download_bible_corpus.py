"""
Download and extract Afaan Oromo Bible texts from ebible.org
to expand the spell checker corpus.

How it works:
1. Downloads PDF files from https://ebible.org/pdf/gaz/
2. Extracts text from each PDF
3. Combines all text into one file
4. Updates oromo_corpus.txt with expanded vocabulary

User workflow:
- Run this script once
- Wait for downloads to complete
- Restart your web server
- Enjoy improved spell checking!
"""

import requests
import re
from pathlib import Path
import PyPDF2
from io import BytesIO

# URL for the complete Afaan Oromo Bible PDF
BIBLE_PDF_URL = "https://ebible.org/pdf/gaz/gaz_book.pdf"

def download_bible_pdf():
    """Download the complete Bible PDF"""
    print("📥 Downloading Afaan Oromo Bible PDF...")
    print("   Source: eBible.org (Afaan Oromoo - Kitaaba Qulqulluu)")
    print(f"   URL: {BIBLE_PDF_URL}")
    print()
    
    try:
        response = requests.get(BIBLE_PDF_URL, timeout=300)
        response.raise_for_status()
        
        # Save PDF file
        pdf_path = Path("gaz_book.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {pdf_path}")
        print(f"   Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extract text from the Bible PDF"""
    print("\n📂 Extracting text from PDF...")
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            print(f"   Total pages: {total_pages}")
            print()
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # Show progress
                if (i + 1) % 50 == 0 or i == 0 or i == total_pages - 1:
                    print(f"   Processing page {i + 1}/{total_pages}...")
            
            return text
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return ""

def clean_text(text):
    """Clean extracted text - keep only Afaan Oromo content"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Keep sentences that look like Afaan Oromo
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        # Filter: should have common Oromo words/patterns
        if len(line) > 20 and (' akka ' in line.lower() or 
                                ' jedhe ' in line.lower() or
                                ' inni ' in line.lower() or
                                ' isheen ' in line.lower() or
                                ' gara ' in line.lower()):
            lines.append(line)
    
    return '\n'.join(lines)

def main():
    print("=" * 60)
    print("📖 Afaan Oromo Bible Corpus Expander - COMPLETE")
    print("=" * 60)
    print()
    print("This will download the COMPLETE Bible PDF and extract text.")
    print("Estimated time: 3-8 minutes (depending on internet)")
    print()
    
    # Check for required library
    try:
        import PyPDF2
    except ImportError:
        print("❌ PyPDF2 not installed!")
        print("Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'PyPDF2'])
        import PyPDF2
    
    print("\n📥 Downloading and extracting texts...\n")
    
    # Step 1: Download PDF
    pdf_path = download_bible_pdf()
    if not pdf_path:
        print("\n❌ Cannot proceed without download. Check internet connection.")
        return
    
    # Step 2: Extract text
    bible_text = extract_text_from_pdf(pdf_path)
    
    if not bible_text:
        print("\n❌ No text was extracted from the PDF.")
        return
    
    # Step 3: Clean the text
    print("\n🧹 Cleaning extracted text...")
    cleaned_text = clean_text(bible_text)
    
    if not cleaned_text:
        print("\n❌ No meaningful text found after cleaning.")
        return
    
    print(f"✅ Successfully extracted Bible text")
    print(f"📊 Total Bible text: {len(cleaned_text):,} characters")
    
    # Save to new corpus file
    output_file = Path("oromo_bible_corpus.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"📊 Total size: {len(cleaned_text):,} characters")
    
    # Option to merge with existing corpus
    print("\n🔄 Updating main corpus...")
    existing_corpus = Path("oromo_corpus.txt")
    
    if existing_corpus.exists():
        with open(existing_corpus, 'r', encoding='utf-8') as f:
            original = f.read()
        
        # Combine (Bible text first, then original)
        merged = cleaned_text + "\n\n" + original
        
        # Backup original
        backup = existing_corpus.with_suffix('.txt.bak')
        existing_corpus.rename(backup)
        print(f"✓ Backed up original to: {backup}")
        
        # Write merged
        with open(existing_corpus, 'w', encoding='utf-8') as f:
            f.write(merged)
        
        print(f"✓ Merged Bible corpus with existing corpus")
        print(f"📊 New total size: {len(merged):,} characters")
    
    # Count words
    words = set(re.findall(r"[a-z']+", cleaned_text.lower()))
    print(f"🔤 New vocabulary: {len(words):,} unique words")
    
    print("\n" + "=" * 60)
    print("✨ DONE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart your web server:")
    print("   C:\\Python312\\python.exe main.py")
    print("2. Test with Bible verses!")
    print("\nExample test sentences:")
    print("  'Waaqayyo jalqaba uume samii fi lafa'")
    print("  'Yesuus Kristos fayyisaa dha'")
    print("  'Ani bishaan jireenyaa siif kenna'")

if __name__ == "__main__":
    main()
