"""
Check what Afaan Oromo Bible PDFs are available on ebible.org
and show the correct filenames.
"""

import requests
from bs4 import BeautifulSoup

url = "https://ebible.org/pdf/gaz/"

print("🔍 Checking available PDF files...")
print()

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pdf_files = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            pdf_files.append(link['href'])
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF files:")
        print()
        for pdf in sorted(pdf_files)[:10]:  # Show first 10
            print(f"  📄 {pdf}")
        
        if len(pdf_files) > 10:
            print(f"  ... and {len(pdf_files) - 10} more")
    else:
        print("❌ No PDF files found on this page")
        print("\nMaybe the structure changed. Check manually:")
        print(url)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry opening in browser:")
    print(url)
