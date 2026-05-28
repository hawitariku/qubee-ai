"""
Corpus Expansion Utilities for Afaan Oromo Spell Checker
Provides tools to:
- Download and process Wikipedia articles
- Extract text from various sources
- Merge multiple corpora
- Validate and clean corpus data
- Generate corpus statistics
"""

import requests
import re
from pathlib import Path
from typing import List, Optional
from bs4 import BeautifulSoup
import json
from datetime import datetime


class CorpusExpander:
    """Tools for expanding and managing Afaan Oromo corpus"""
    
    def __init__(self, output_path='oromo_corpus.txt'):
        self.output_path = Path(output_path)
        self.backup_path = Path(f'{output_path}.bak')
    
    def backup_corpus(self):
        """Create backup of current corpus"""
        if self.output_path.exists():
            import shutil
            shutil.copy2(self.output_path, self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
    
    def download_wikipedia_article(self, title: str, language='om') -> Optional[str]:
        """
        Download Afaan Oromo Wikipedia article
        Args:
            title: Article title
            language: Language code (default 'om' for Oromo)
        Returns:
            Extracted text or None
        """
        url = f"https://{language}.wikipedia.org/api/rest_v1/page/html/{title}"
        headers = {
            'User-Agent': 'AfaanOromoSpellChecker/1.0'
        }
        
        try:
            print(f"📥 Downloading: {title}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text() for p in paragraphs if p.get_text().strip()])
            
            # Clean text
            text = self.clean_text(text)
            
            if text.strip():
                print(f"✅ Downloaded {len(text)} characters")
                return text
            else:
                print(f"⚠️ No text extracted")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading {title}: {e}")
            return None
    
    def download_multiple_articles(self, titles: List[str]) -> int:
        """Download multiple Wikipedia articles"""
        total_chars = 0
        
        for title in titles:
            text = self.download_wikipedia_article(title)
            if text:
                total_chars += len(text)
                self.append_to_corpus(text, source=f"Wikipedia: {title}")
        
        return total_chars
    
    def extract_text_from_url(self, url: str) -> Optional[str]:
        """Extract text from any URL"""
        try:
            headers = {
                'User-Agent': 'AfaanOromoSpellChecker/1.0'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            return self.clean_text(text)
            
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Afaan Oromo letters and punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\'\"-]', ' ', text)
        
        # Remove numbers (optional - keep for modern vocabulary)
        # text = re.sub(r'\d+', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def append_to_corpus(self, text: str, source: str = ""):
        """Append text to corpus file"""
        with open(self.output_path, 'a', encoding='utf-8') as f:
            if source:
                f.write(f"\n# Source: {source} - {datetime.now().isoformat()}\n")
            f.write(text + "\n")
        
        print(f"📝 Appended {len(text)} characters to corpus")
    
    def merge_corpus_files(self, file_paths: List[str], output_path: str = None):
        """Merge multiple corpus files"""
        if output_path is None:
            output_path = self.output_path
        
        total_lines = 0
        total_chars = 0
        
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    print(f"⚠️ File not found: {file_path}")
                    continue
                
                with open(path, 'r', encoding='utf-8') as in_f:
                    content = in_f.read()
                    out_f.write(content + "\n")
                    
                    lines = content.count('\n')
                    total_lines += lines
                    total_chars += len(content)
                    
                    print(f"✅ Merged {file_path}: {lines} lines, {len(content)} chars")
        
        print(f"\n📊 Total merged: {total_lines} lines, {total_chars} characters")
    
    def validate_corpus(self, file_path: str = None) -> dict:
        """Validate corpus and generate statistics"""
        if file_path is None:
            file_path = self.output_path
        
        path = Path(file_path)
        if not path.exists():
            return {'error': 'File not found'}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic statistics
        lines = content.split('\n')
        words = re.findall(r"[a-z']+", content.lower())
        unique_words = set(words)
        characters = len(content)
        
        # Word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        
        # Average word length
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        stats = {
            'file': str(path),
            'total_lines': len(lines),
            'total_words': len(words),
            'unique_words': len(unique_words),
            'total_characters': characters,
            'avg_word_length': round(avg_word_length, 2),
            'top_words': top_words,
            'timestamp': datetime.now().isoformat()
        }
        
        return stats
    
    def remove_duplicates(self, file_path: str = None) -> int:
        """Remove duplicate lines from corpus"""
        if file_path is None:
            file_path = self.output_path
        
        path = Path(file_path)
        if not path.exists():
            return 0
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lines = []
        duplicates_removed = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_lines.append(line)
            else:
                duplicates_removed += 1
        
        # Write back
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(unique_lines)
        
        print(f"✅ Removed {duplicates_removed} duplicate lines")
        return duplicates_removed
    
    def generate_corpus_report(self, file_path: str = None) -> str:
        """Generate detailed corpus report"""
        stats = self.validate_corpus(file_path)
        
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        report = f"""
{'='*60}
📊 AFaan Oromo Corpus Report
{'='*60}

📁 File: {stats['file']}
📅 Generated: {stats['timestamp']}

📈 Statistics:
  • Total Lines: {stats['total_lines']:,}
  • Total Words: {stats['total_words']:,}
  • Unique Words: {stats['unique_words']:,}
  • Total Characters: {stats['total_characters']:,}
  • Average Word Length: {stats['avg_word_length']} characters

🔝 Top 20 Most Frequent Words:
"""
        
        for i, (word, freq) in enumerate(stats['top_words'][:20], 1):
            report += f"  {i:2d}. {word:<20} {freq:>6,} times\n"
        
        report += f"\n{'='*60}\n"
        
        return report
    
    def get_expansion_suggestions(self) -> List[str]:
        """Suggest topics for corpus expansion"""
        return [
            # General topics
            "Itoophiyaa",
            "Oromiyaa",
            "Finfinnee",
            "Afaan_Oromoo",
            "Gadaa",
            
            # History and culture
            "Seenaa_Oromoo",
            "Aadaa_Oromoo",
            "Siinqee",
            
            # Geography
            "Gaara",
            "Laga_Awaash",
            "Haroo_Bishooftuu",
            
            # Science and education
            "Saayinsii",
            "Barumsa",
            "Yuunivarsiitii",
            
            # Health
            "Fayyaa",
            "Yaala",
            "Qoricha",
            
            # Technology
            "Teeknooloojii",
            "Kompiitara",
            "Intarneetii",
            
            # Religion
            "Amantii",
            "Kiristaanummaa",
            "Islamii",
            
            # Sports
            "Kubbaa_Miilaa",
            "Atileetiksii",
            
            # Politics
            "Siyaasa",
            "Mootummaa",
            "Dimokraasii",
        ]


def main():
    """Interactive corpus expansion"""
    expander = CorpusExpander()
    
    print("\n" + "="*60)
    print("📚 Afaan Oromo Corpus Expansion Tool")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Download Wikipedia articles")
        print("2. Validate current corpus")
        print("3. Remove duplicates")
        print("4. Generate corpus report")
        print("5. Get expansion suggestions")
        print("6. Merge corpus files")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            # Download suggested articles
            suggestions = expander.get_expansion_suggestions()
            print(f"\n📝 Suggested articles ({len(suggestions)} total):")
            for i, title in enumerate(suggestions[:10], 1):
                print(f"  {i}. {title}")
            
            titles_input = input("\nEnter titles to download (comma-separated, or 'all'): ").strip()
            
            if titles_input.lower() == 'all':
                titles = suggestions
            else:
                titles = [t.strip() for t in titles_input.split(',')]
            
            expander.backup_corpus()
            total_chars = expander.download_multiple_articles(titles)
            print(f"\n✅ Downloaded {total_chars} characters total")
        
        elif choice == '2':
            stats = expander.validate_corpus()
            print(f"\n📊 Corpus Statistics:")
            print(f"  • Words: {stats.get('total_words', 0):,}")
            print(f"  • Unique: {stats.get('unique_words', 0):,}")
            print(f"  • Characters: {stats.get('total_characters', 0):,}")
        
        elif choice == '3':
            expander.backup_corpus()
            removed = expander.remove_duplicates()
            print(f"✅ Removed {removed} duplicates")
        
        elif choice == '4':
            report = expander.generate_corpus_report()
            print(report)
        
        elif choice == '5':
            suggestions = expander.get_expansion_suggestions()
            print("\n📝 Expansion Suggestions:")
            for i, title in enumerate(suggestions, 1):
                print(f"  {i:2d}. {title}")
        
        elif choice == '6':
            files_input = input("Enter file paths (comma-separated): ").strip()
            files = [f.strip() for f in files_input.split(',')]
            expander.backup_corpus()
            expander.merge_corpus_files(files)
        
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
