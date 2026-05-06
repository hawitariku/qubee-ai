import re
import collections
from difflib import SequenceMatcher
from pathlib import Path

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")

class AfaanOromoSpellChecker:
    def __init__(self, corpus_path=None):
        self.words_db = collections.Counter()
        self.bigrams = collections.Counter()  # Word pairs for context
        self.trigrams = collections.Counter()  # Word triplets for context
        
        # Common Afaan Oromo words with high priority (to override corpus typos)
        self.common_words = {
            'afaan': 10000, 'oromoo': 10000, 'inni': 9000, 'isheen': 9000,
            'ani': 9000, 'nuti': 9000, 'isin': 9000, 'isaan': 9000,
            'bishaan': 8000, 'mana': 8000, 'deeme': 8000, 'dhufe': 8000,
            'fedha': 8000, 'jira': 8000, 'barumsa': 8000, 'gabri': 8000,
            'nama': 7000, 'dubartii': 7000, 'ijoollee': 7000, 'hojii': 7000,
            'gaba': 7000, 'magalaa': 7000, 'finfinnee': 7000, 'biyya': 7000,
            'waaqayyo': 7000, 'kitaaba': 7000, 'qulqulluu': 7000, 'guddaa': 7000,
        }
        
        print("Initializing advanced spell checker...")
        
        # Train from multiple sources
        sources_loaded = 0
        
        # 1. Main corpus
        if corpus_path:
            self.train_from_file(corpus_path)
            sources_loaded += 1
        else:
            sample_text = "Ani bishaan dhuguu fedha. Inni gara mana deeme. Isheen barattuu dha."
            self.train_from_text(sample_text)
        
        # 2. Extract text from gaz_book.pdf (with caching)
        if Path('gaz_book.pdf').exists() and HAS_PDF:
            extracted_txt = 'gaz_book_extracted.txt'
            
            # Check if cached extraction exists
            if Path(extracted_txt).exists():
                print(f"\n📄 Loading cached PDF extraction: {extracted_txt}")
                self.train_from_file(extracted_txt)
                sources_loaded += 1
            else:
                print(f"\n📄 Extracting text from PDF: gaz_book.pdf")
                pdf_text = self.extract_text_from_pdf('gaz_book.pdf')
                if pdf_text:
                    print(f"   Processing PDF text ({len(pdf_text):,} characters)...")
                    # Cache the extracted text
                    with open(extracted_txt, 'w', encoding='utf-8') as f:
                        f.write(pdf_text)
                    print(f"   💾 Cached to: {extracted_txt}")
                    self.train_from_text(pdf_text)
                    sources_loaded += 1
                    print(f"   ✅ PDF loaded successfully!")
        elif Path('gaz_book.pdf').exists() and not HAS_PDF:
            print(f"\n⚠️ gaz_book.pdf exists but PyPDF2 not installed")
        
        # 3. Bible corpus
        bible_files = ['oromo_bible_corpus.txt', 'oromo_bible_complete.txt']
        for bible_file in bible_files:
            if Path(bible_file).exists():
                print(f"\n📖 Loading Bible corpus: {bible_file}")
                self.train_from_file(bible_file)
                sources_loaded += 1
        
        # 4. Wikipedia expansion
        wiki_files = ['oromo_wikipedia_expansion.txt', 'oromo_wikipedia_corpus.txt']
        for wiki_file in wiki_files:
            if Path(wiki_file).exists():
                print(f"\n📚 Loading Wikipedia corpus: {wiki_file}")
                self.train_from_file(wiki_file)
                sources_loaded += 1
        
        # 5. Backup corpus (original data before Bible merge)
        backup_files = ['oromo_corpus.txt.bak']
        for backup_file in backup_files:
            if Path(backup_file).exists():
                print(f"\n💾 Loading backup corpus: {backup_file}")
                self.train_from_file(backup_file)
                sources_loaded += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Loaded {sources_loaded} corpus sources")
        print(f"📊 Vocabulary: {len(self.words_db):,} unique words")
        print(f"📊 Bigrams: {len(self.bigrams):,}")
        print(f"📊 Trigrams: {len(self.trigrams):,}")
        
        # Add common words with high priority
        for word, freq in self.common_words.items():
            if word not in self.words_db or self.words_db[word] < freq:
                self.words_db[word] = freq
        
        # Optimize vocabulary (remove rare words)
        self.optimize_vocabulary(min_frequency=2)
        
        print(f"{'='*60}")

    def train_from_text(self, text):
        # Afaan Oromo includes ' (hudhaa). We keep letters and the apostrophe.
        words = re.findall(r"[a-z']+", text.lower())
        
        # Count word frequencies
        for word in words:
            self.words_db[word] += 1
        
        # Count bigrams (word pairs)
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            self.bigrams[bigram] += 1
        
        # Count trigrams (word triplets)
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            self.trigrams[trigram] += 1
    
    def optimize_vocabulary(self, min_frequency=2):
        """Remove rare words that appear less than min_frequency times"""
        before = len(self.words_db)
        self.words_db = {word: count for word, count in self.words_db.items() if count >= min_frequency}
        self.words_db = collections.Counter(self.words_db)
        after = len(self.words_db)
        print(f"   🔧 Optimized vocabulary: {before:,} → {after:,} words (removed {before-after:,} rare words)")

    def train_from_file(self, path):
        print(f"📚 Loading corpus: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().lower()
        self.train_from_text(text)
        print(f"✅ Vocabulary size: {len(self.words_db)} unique words")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        if not HAS_PDF:
            print(f"   ⚠️ PyPDF2 not installed")
            return ""
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
            print(f"   ⚠️ PDF extraction error: {e}")
            return ""

    def _get_edits(self, word):
        """Generates all possible corrections 1 edit away - Afaan Oromo optimized"""
        letters = "abcdefghijklmnopqrstuvwxyz'"
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        
        # Afaan Oromo specific: add common digraphs
        digraphs = ["ch", "sh", "dh", "ny", "ph", "th"]
        digraph_inserts = []
        for L, R in splits:
            for digraph in digraphs:
                digraph_inserts.append(L + digraph + R)
        
        # Afaan Oromo specific: vowel lengthening (important in Oromo)
        vowel_doubles = []
        vowels = 'aeiou'
        for L, R in splits:
            if R and R[0] in vowels:
                # Double the vowel (e.g., 'a' -> 'aa')
                vowel_doubles.append(L + R[0] + R)
        
        return set(deletes + transposes + replaces + inserts + digraph_inserts + vowel_doubles)

    def _known(self, words):
        """Returns subset of words that appear in our vocabulary"""
        return set(w for w in words if w in self.words_db)
    
    def _similarity_ratio(self, word1, word2):
        """Calculate similarity ratio between two words using improved algorithm"""
        if not word1 or not word2:
            return 0.0
        
        # Use SequenceMatcher for base similarity
        base_similarity = SequenceMatcher(None, word1, word2).ratio()
        
        # Afaan Oromo specific improvements
        # 1. Vowel length matters in Oromo (aa vs a)
        vowel_patterns_1 = re.findall(r'([aeiou])\1', word1)
        vowel_patterns_2 = re.findall(r'([aeiou])\1', word2)
        
        # Penalize if vowel length differs
        if len(vowel_patterns_1) != len(vowel_patterns_2):
            base_similarity *= 0.85
        
        return base_similarity
    
    def _phonetic_similarity(self, word1, word2):
        """Advanced phonetic similarity for Afaan Oromo"""
        if not word1 or not word2:
            return 0.0
        
        word1 = word1.lower()
        word2 = word2.lower()
        
        # Exact match
        if word1 == word2:
            return 1.0
        
        score = 0.0
        
        # Afaan Oromo phonetic rules:
        # 1. Ejective consonants: c, q, x have special sounds
        ejective_map = {
            'c': ['k', 'ch', 's'],
            'q': ['k', 'c'],
            'x': ['h', 's', 'sh'],
            'ch': ['c', 'sh'],
            'sh': ['x', 'ch'],
        }
        
        # 2. Geminated (doubled) consonants are phonemic
        geminate_map = {
            'dh': ['d'],
            'd': ['dh'],
            'ny': ['n'],
            'n': ['ny'],
            'ph': ['p'],
            'th': ['t'],
        }
        
        # Calculate phonetic distance
        max_len = max(len(word1), len(word2))
        if max_len == 0:
            return 1.0
        
        # Character-by-character phonetic comparison
        matches = 0
        i, j = 0, 0
        
        while i < len(word1) and j < len(word2):
            # Exact match
            if word1[i] == word2[j]:
                matches += 1
                i += 1
                j += 1
                continue
            
            # Check for digraphs (two-character sounds)
            matched_digraph = False
            if i + 1 < len(word1):
                digraph1 = word1[i:i+2]
                if digraph1 in geminate_map and word2[j] in geminate_map[digraph1]:
                    matches += 0.8
                    i += 2
                    j += 1
                    matched_digraph = True
                elif digraph1 in ejective_map and word2[j] in ejective_map[digraph1]:
                    matches += 0.7
                    i += 2
                    j += 1
                    matched_digraph = True
            
            if not matched_digraph and j + 1 < len(word2):
                digraph2 = word2[j:j+2]
                if digraph2 in geminate_map and word1[i] in geminate_map[digraph2]:
                    matches += 0.8
                    i += 1
                    j += 2
                    matched_digraph = True
                elif digraph2 in ejective_map and word1[i] in ejective_map[digraph2]:
                    matches += 0.7
                    i += 1
                    j += 2
                    matched_digraph = True
            
            # Single character substitution
            if not matched_digraph:
                # Vowel similarity
                if word1[i] in 'aeiou' and word2[j] in 'aeiou':
                    matches += 0.5
                # Consonant similarity
                elif word1[i] not in 'aeiou' and word2[j] not in 'aeiou':
                    matches += 0.3
                
                i += 1
                j += 1
        
        # Base phonetic score
        phonetic_score = matches / max_len
        
        # Bonus for same length
        length_diff = abs(len(word1) - len(word2))
        length_penalty = 1.0 - (length_diff * 0.1)
        length_penalty = max(0.5, length_penalty)
        
        return phonetic_score * length_penalty

    def get_word_suggestions(self, word, top_n=5):
        """Get top N suggestions for a misspelled word"""
        word_lower = word.lower()
        
        # If word is correct, return it
        if word_lower in self.words_db:
            return [word_lower]
        
        all_suggestions = []
        
        # Edit distance 1 candidates
        candidates_1 = self._known(self._get_edits(word_lower))
        for cand in candidates_1:
            score = self.words_db[cand] * (1.0 + self._similarity_ratio(word_lower, cand))
            all_suggestions.append((cand, score))
        
        # Edit distance 2 candidates (limited for performance)
        if len(candidates_1) == 0:
            candidates_2 = self._known(e2 for e1 in self._get_edits(word_lower)[:100] 
                                      for e2 in self._get_edits(e1))
            for cand in candidates_2:
                score = self.words_db[cand] * self._similarity_ratio(word_lower, cand)
                all_suggestions.append((cand, score))
        
        # Sort by score and return top N
        all_suggestions.sort(key=lambda x: x[1], reverse=True)
        suggestions = [s[0] for s in all_suggestions[:top_n]]
        
        return suggestions if suggestions else [word_lower]

    def correct_word(self, word):
        """Corrects a single word using edit distance and frequency"""
        word_lower = word.lower()
        
        # If word is already known, return it
        if word_lower in self.words_db:
            return word
        
        # Generate candidates at edit distance 1
        candidates = self._known(self._get_edits(word_lower))
        
        # If no candidates at distance 1, try distance 2
        if not candidates:
            candidates = self._known(e2 for e1 in self._get_edits(word_lower) 
                                    for e2 in self._get_edits(e1))
        
        # If still no candidates, return original
        if not candidates:
            return word
        
        # Return most frequent candidate
        best = max(candidates, key=self.words_db.get)
        return best

    def correct_sentence_with_context(self, sentence):
        """Correct spelling using Afaan Oromo context awareness (bigrams/trigrams)"""
        words = sentence.split()
        corrected_words = []
        corrections_made = []
        
        # Check if sentence appears incomplete (no proper ending)
        is_incomplete = self._is_sentence_incomplete(sentence)
        
        for i, word in enumerate(words):
            # Strip punctuation for checking
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            word_lower = clean_word.lower()
            
            # If word is correct, keep it
            if word_lower in self.words_db:
                corrected_words.append(word)
                continue
            
            # Get candidate corrections
            candidates = self._known(self._get_edits(word_lower))
            if not candidates:
                edits_list = list(self._get_edits(word_lower))[:200]
                candidates = self._known(e2 for e1 in edits_list 
                                        for e2 in self._get_edits(e1))
            
            if not candidates:
                corrected_words.append(word)
                continue
            
            # Use Afaan Oromo context to select best candidate
            best_candidate = self._select_with_context(
                candidates, word_lower, corrected_words, i, words, i
            )
            
            # Only apply correction if confidence is high enough
            confidence = self._calculate_confidence(candidates, best_candidate, word_lower)
            
            # For incomplete sentences, require higher confidence (70%)
            min_confidence = 70 if is_incomplete else 50
            
            if confidence >= min_confidence and best_candidate != word_lower:
                corrected_words.append(best_candidate + punctuation)
                corrections_made.append({
                    'original': word,
                    'corrected': best_candidate + punctuation,
                    'position': i,
                    'confidence': confidence
                })
            else:
                # Keep original word if confidence too low
                corrected_words.append(word)
        
        corrected_sentence = " ".join(corrected_words)
        return corrected_sentence, corrections_made
    
    def _is_sentence_incomplete(self, sentence):
        """Check if sentence appears incomplete"""
        sentence = sentence.strip()
        
        # Incomplete indicators
        if not sentence:
            return True
        
        # Check if ends with proper punctuation
        if sentence.endswith(('.', '!', '?', ':', ';')):
            return False
        
        # Check if last word is a common verb ending (might be incomplete)
        words = sentence.split()
        if words:
            last_word = re.sub(r'[^\w\']', '', words[-1].lower())
            # Common incomplete verb forms
            incomplete_endings = ['dh', 'fh', 'mh', 'nh', 'deem', 'dhuf', 'bar', 'ny']
            if any(last_word.endswith(ending) for ending in incomplete_endings):
                return True
        
        # Short sentences without punctuation are likely incomplete
        if len(words) < 3:
            return True
        
        return False
    
    def _select_with_context(self, candidates, original_word, prev_words, position, all_words=None, current_pos=None):
        """Select best candidate using Afaan Oromo contextual information with lookahead"""
        if not candidates:
            return original_word
        
        # If only one candidate, return it
        if len(candidates) == 1:
            return list(candidates)[0]
        
        best_score = -1
        best_candidate = list(candidates)[0]
        
        # Get previous word context
        prev_word = prev_words[-1] if prev_words else None
        if prev_word:
            prev_word = re.sub(r'[^\w\']', '', prev_word).lower()
        
        # Get next word for lookahead
        next_word = None
        if all_words and current_pos is not None and current_pos + 1 < len(all_words):
            next_word = re.sub(r'[^\w\']', '', all_words[current_pos + 1]).lower()

        # Afaan Oromo specific common patterns
        # Subject pronouns + common verbs (expanded)
        oromo_verb_patterns = {
            'ani': ['fedha', 'barra', 'dhuga', 'nyaadha', 'deema', 'jira', 'beeka', 'barbaada', 'jedha', 'kaaa', 'taha'],
            'inni': ['deeme', 'dhufe', 'fedhe', 'bara', 'dhuge', 'nyaate', 'jira', 'beeka', 'jedhe', 'taha'],
            'isheen': ['deemte', 'dhufte', 'fedhte', 'bartee', 'dhugde', 'nyaatte', 'jirti', 'beekti', 'jette', 'tatte'],
            'nuti': ['fedhna', 'barra', 'dhugna', 'nyaanna', 'deemna', 'jirra', 'beekna', 'jedhna', 'taha'],
            'isin': ['fedha', 'barra', 'dhugdu', 'nyaattu', 'deemtu', 'jirtu', 'beektu', 'jettu', 'taha'],
            'isaan': ['fedhu', 'baru', 'dhugu', 'nyaatu', 'deemu', 'jiru', 'beeku', 'jettu', 'tahu'],
        }
        
        # Common preposition + noun patterns (expanded)
        oromo_preposition_patterns = {
            'gara': ['mana', 'barumsaa', 'hojii', 'gaba', 'suuqa', 'bakka', 'magalaa', 'garee'],
            'irraa': ['mana', 'barumsaa', 'gaba', 'bakka', 'magalaa', 'fageenya'],
            'itti': ['deeme', 'dhufe', 'kaae', 'kaayye', 'deebie', 'galagge'],
            'waliin': ['deeme', 'dhufe', 'jira', 'hojje', 'bulle', 'turre'],
            'keessa': ['mana', 'gala', 'bakka', 'barumsaa', 'magalaa', 'biyyoo'],
            'biraa': ['dhufe', 'deeme', 'jira', 'kaae', 'argame'],
        }
        
        # Common adjective-noun patterns
        oromo_adjective_patterns = {
            'nama': ['gaarii', 'balaa', 'guddaa', 'xiqqaa', 'dheeraa', 'gabaabaa'],
            'bishaan': ['qulqulluu', 'hoaa', 'qorraa', 'miaa'],
            'mana': ['guddaa', 'haaraa', 'mooraa', 'balaa'],
        }
        
        for candidate in candidates:
            score = self.words_db[candidate] * 2  # Base frequency score (doubled)
            
            # Enhanced phonetic similarity (PRIMARY factor)
            phonetic_score = self._phonetic_similarity(original_word, candidate)
            score *= (1.0 + phonetic_score * 1.5)  # Increased from 0.5 to 1.5
            
            # Edit distance penalty (closer = better)
            edit_dist = self._calculate_edit_distance(original_word, candidate)
            edit_penalty = max(0, 100 - edit_dist * 15)
            score += edit_penalty
            
            # Word length similarity bonus
            len_ratio = min(len(original_word), len(candidate)) / max(len(original_word), len(candidate))
            score *= (1.0 + len_ratio * 0.3)
            
            # Bigram context scoring with Afaan Oromo patterns
            if prev_word:
                bigram = (prev_word, candidate)
                if bigram in self.bigrams:
                    score += self.bigrams[bigram] * 5  # Increased from 3 to 5
                
                # Check pronoun + verb agreement
                if prev_word in oromo_verb_patterns:
                    if candidate in oromo_verb_patterns[prev_word]:
                        score += 100  # Increased from 50 to 100
                    else:
                        # Check if it's at least a valid verb form
                        is_verb = any(candidate.endswith(end) for end in ['e', 'a', 'u', 'te', 'na', 'tu'])
                        if is_verb:
                            score -= 10  # Smaller penalty if at least it's a verb
                        else:
                            score -= 40  # Increased from 20 to 40
                
                # Check preposition + noun patterns
                if prev_word in oromo_preposition_patterns:
                    if candidate in oromo_preposition_patterns[prev_word]:
                        score += 60  # Increased from 30 to 60
                
                # Check adjective-noun patterns
                if prev_word in oromo_adjective_patterns:
                    if candidate in oromo_adjective_patterns[prev_word]:
                        score += 50
            
            # Check if this forms a common trigram
            if len(prev_words) >= 2:
                word_before_prev = re.sub(r'[^\w\']', '', prev_words[-2]).lower() if len(prev_words) >= 2 else None
                if word_before_prev:
                    trigram = (word_before_prev, prev_word, candidate)
                    if trigram in self.trigrams:
                        score += self.trigrams[trigram] * 8  # Increased from 5 to 8
            
            # Lookahead: check if candidate + next_word forms common bigram
            if next_word:
                forward_bigram = (candidate, next_word)
                if forward_bigram in self.bigrams:
                    score += self.bigrams[forward_bigram] * 6  # Increased from 4 to 6
            
            # Boost common Oromo word endings
            oromo_suffixes = ['uu', 'aa', 'ee', 'ii', 'oo', 'aan', 'een', 'iin', 'oon', 'un', 'tti', 'rra', 'ssa']
            if any(candidate.endswith(suffix) for suffix in oromo_suffixes):
                score *= 1.3  # Increased from 1.2 to 1.3
            
            # Afaan Oromo SOV word order boost
            if prev_word in ['barumsaa', 'mana', 'gaba', 'hojii', 'bishaan', 'nyaata', 'kitaba', 'finfinnee']:
                common_verbs = ['deeme', 'dhufe', 'fedha', 'jira', 'bara', 'dhuga', 'nyaata', 'bine', 'qaba']
                if candidate in common_verbs:
                    score += 70  # Increased from 40 to 70
            
            # Bonus for words that appear frequently in corpus
            if self.words_db[candidate] > 100:
                score *= 1.2
            elif self.words_db[candidate] > 50:
                score *= 1.1

            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        return best_candidate
    
    def _calculate_edit_distance(self, word1, word2):
        """Calculate Levenshtein distance between two words"""
        if len(word1) < len(word2):
            return self._calculate_edit_distance(word2, word1)
        
        if len(word2) == 0:
            return len(word1)
        
        previous_row = range(len(word2) + 1)
        for i, c1 in enumerate(word1):
            current_row = [i + 1]
            for j, c2 in enumerate(word2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _calculate_confidence(self, candidates, best_candidate, original_word):
        """Calculate confidence score for a correction (0-100%)"""
        if not candidates:
            return 0
        
        # Base confidence from frequency ranking
        freq_scores = {cand: self.words_db[cand] for cand in candidates}
        max_freq = max(freq_scores.values())
        best_freq = freq_scores.get(best_candidate, 0)
        
        # Frequency ratio (0-50 points)
        freq_score = (best_freq / max_freq * 50) if max_freq > 0 else 0
        
        # Phonetic similarity (0-30 points)
        phonetic = self._phonetic_similarity(original_word, best_candidate)
        phonetic_score = phonetic * 30
        
        # Edit distance (0-20 points)
        edit_dist = abs(len(original_word) - len(best_candidate))
        edit_score = max(0, 20 - edit_dist * 5)
        
        total_confidence = min(100, int(freq_score + phonetic_score + edit_score))
        return total_confidence

    def ai_correct_sentence(self, sentence):
        """Main correction method - returns only corrected text for backward compatibility"""
        corrected, _ = self.correct_sentence_with_context(sentence)
        return corrected
    
    def get_detailed_corrections(self, sentence):
        """Get detailed correction information"""
        corrected, corrections = self.correct_sentence_with_context(sentence)
        return {
            'original': sentence,
            'corrected': corrected,
            'corrections': corrections,
            'total_changes': len(corrections)
        }
    
    def check_grammar_basic(self, sentence):
        """Basic grammar checking for Afaan Oromo"""
        issues = []
        words = sentence.split()
        
        if not words:
            return issues
        
        # Rule 1: Sentence should start with capital letter
        if words[0] and words[0][0].islower():
            issues.append({
                'type': 'capitalization',
                'message': 'Jechi jalqabaa qubbaa guddaan jalqabuu qaba (First word should be capitalized)',
                'suggestion': words[0].capitalize(),
                'position': 0
            })
        
        # Rule 2: Check for double vowels (common typo in Oromo)
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-z]', '', word.lower())
            if re.search(r'([aeiou])\1{2,}', clean):  # 3+ same vowels
                issues.append({
                    'type': 'excessive_vowel',
                    'message': f'Vowwwel {word} is too long',
                    'suggestion': re.sub(r'([aeiou])\1+', r'\1\1', clean),
                    'position': i
                })
        
        # Rule 3: Common verb conjugation patterns
        common_endings = ['a', 'e', 'i', 'o', 'u']
        if words:
            last_word = re.sub(r'[^\w\']', '', words[-1]).lower()
            if last_word and last_word[-1] not in common_endings and len(last_word) > 2:
                suggestions = self.get_word_suggestions(last_word, top_n=3)
                if suggestions and suggestions[0] != last_word:
                    issues.append({
                        'type': 'possible_incomplete_verb',
                        'message': f'Tarjimaan xumuramaa hin taane ta\'uu danda\'a (Verb might be incomplete)',
                        'suggestion': suggestions[0],
                        'position': len(words) - 1
                    })
        
        # Rule 4: Check subject-verb agreement
        pronouns = {'ani': '1st', 'inni': '3rd_m', 'isheen': '3rd_f', 'nuti': '1st_pl', 'isin': '2nd_pl', 'isaan': '3rd_pl'}
        if words[0].lower() in pronouns and len(words) > 2:
            subject = words[0].lower()
            verb = re.sub(r'[^\w\']', '', words[-1]).lower()
            
            # Check if verb matches subject
            verb_endings = {
                'ani': ['a', 'n'],
                'inni': ['e'],
                'isheen': ['te', 'tte'],
                'nuti': ['na', 'rra'],
                'isin': ['tu', 'ttu'],
                'isaan': ['u']
            }
            
            if subject in verb_endings:
                valid = any(verb.endswith(end) for end in verb_endings[subject])
                if not valid and len(verb) > 3:
                    issues.append({
                        'type': 'subject_verb_agreement',
                        'message': f'Subject-verb agreement may be incorrect ({subject} → verb)',
                        'position': len(words) - 1
                    })
        
        # Rule 5: Check for repetitive words
        for i in range(len(words) - 1):
            w1 = re.sub(r'[^\w\']', '', words[i].lower())
            w2 = re.sub(r'[^\w\']', '', words[i+1].lower())
            if w1 == w2 and len(w1) > 2:
                issues.append({
                    'type': 'repetitive_word',
                    'message': f'Repetitive word: {words[i]}',
                    'suggestion': words[i],
                    'position': i
                })
        
        # Rule 6: Common question word patterns
        question_words = ['maal', 'eenyu', 'eessa', 'yoom', 'akkam', 'maaliif']
        if any(w.lower() in question_words for w in words):
            if not sentence.rstrip().endswith('?'):
                issues.append({
                    'type': 'missing_question_mark',
                    'message': 'Question should end with ?',
                    'position': len(words) - 1
                })
        
        # Rule 7: Check conjunction usage (fi, yookaan)
        for i, word in enumerate(words):
            if word.lower() in ['fi', 'yookaan']:
                if i == 0 or i == len(words) - 1:
                    issues.append({
                        'type': 'conjunction_placement',
                        'message': f'Conjunction "{word}" should connect two elements',
                        'position': i
                    })
        
        return issues
