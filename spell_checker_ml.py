import re
import collections
import json
import logging
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from grammar_checker import AfaanOromoGrammarChecker

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")

try:
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠️ Transformers not installed. Install with: pip install transformers torch")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLEnhancedSpellChecker:
    """Enhanced spell checker with ML model integration and learning capabilities"""
    
    def __init__(self, corpus_path=None, use_ml=True, model_name="castorini/afriberta_small"):
        self.words_db = collections.Counter()
        self.bigrams = collections.Counter()
        self.trigrams = collections.Counter()
        
        # Learning system: track user corrections
        self.correction_history = []
        self.user_feedback_db = collections.Counter()  # Track accepted corrections
        self.feedback_log_path = Path('user_feedback.json')
        self._load_user_feedback()
        
        # ML Model integration
        self.use_ml = use_ml and HAS_TRANSFORMERS
        self.ml_model = None
        self.ml_tokenizer = None
        
        if self.use_ml:
            try:
                print(f"\n🤖 Loading ML model: {model_name}")
                self.ml_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ml_model = AutoModelForMaskedLM.from_pretrained(model_name)
                self.ml_model.eval()  # Set to evaluation mode
                print("✅ ML model loaded successfully!")
            except Exception as e:
                print(f"⚠️ Failed to load ML model: {e}")
                self.use_ml = False
        
        # Common Afaan Oromo words with high priority
        self.common_words = {
            'afaan': 10000, 'oromoo': 10000, 'inni': 9000, 'isheen': 9000,
            'ani': 9000, 'nuti': 9000, 'isin': 9000, 'isaan': 9000,
            'bishaan': 8000, 'mana': 8000, 'deeme': 8000, 'dhufe': 8000,
            'fedha': 8000, 'jira': 8000, 'barumsa': 8000, 'gabri': 8000,
            'nama': 7000, 'dubartii': 7000, 'ijoollee': 7000, 'hojii': 7000,
            'gaba': 7000, 'magalaa': 7000, 'finfinnee': 7000, 'biyya': 7000,
            'waaqayyo': 7000, 'kitaaba': 7000, 'qulqulluu': 7000, 'guddaa': 7000,
        }
        
        print("Initializing ML-enhanced spell checker...")
        
        # Performance cache
        self.correction_cache = {}  # Cache common corrections
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Grammar checker
        self.grammar_checker = AfaanOromoGrammarChecker()
        
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
            
            if Path(extracted_txt).exists():
                print(f"\n📄 Loading cached PDF extraction: {extracted_txt}")
                self.train_from_file(extracted_txt)
                sources_loaded += 1
            else:
                print(f"\n📄 Extracting text from PDF: gaz_book.pdf")
                pdf_text = self.extract_text_from_pdf('gaz_book.pdf')
                if pdf_text:
                    print(f"   Processing PDF text ({len(pdf_text):,} characters)...")
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
        
        # 5. Backup corpus
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
        print(f"🤖 ML Model: {'Enabled' if self.use_ml else 'Disabled'}")
        print(f"💾 Cache: {len(self.correction_cache)} entries")
        
        # Add common words with high priority
        for word, freq in self.common_words.items():
            if word not in self.words_db or self.words_db[word] < freq:
                self.words_db[word] = freq
        
        # Boost words from user feedback
        self._apply_user_feedback_boosts()
        
        # Optimize vocabulary
        self.optimize_vocabulary(min_frequency=2)
        
        print(f"{'='*60}")

    def _load_user_feedback(self):
        """Load user correction feedback from disk"""
        if self.feedback_log_path.exists():
            try:
                with open(self.feedback_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_feedback_db = collections.Counter(data.get('feedback', {}))
                    self.correction_history = data.get('history', [])
                logger.info(f"Loaded {len(self.user_feedback_db)} user feedback entries")
            except Exception as e:
                logger.error(f"Error loading user feedback: {e}")
                self.user_feedback_db = collections.Counter()
                self.correction_history = []

    def _save_user_feedback(self):
        """Save user correction feedback to disk"""
        try:
            data = {
                'feedback': dict(self.user_feedback_db),
                'history': self.correction_history[-1000:]  # Keep last 1000 entries
            }
            with open(self.feedback_log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.user_feedback_db)} user feedback entries")
        except Exception as e:
            logger.error(f"Error saving user feedback: {e}")

    def _apply_user_feedback_boosts(self):
        """Apply boosts to words based on user feedback"""
        for correction_pair, count in self.user_feedback_db.items():
            # correction_pair format: "original->corrected"
            if '->' in correction_pair:
                _, corrected = correction_pair.split('->', 1)
                # Boost frequency based on user acceptances
                boost = count * 100  # Each acceptance adds 100 to frequency
                self.words_db[corrected] += boost
        logger.info(f"Applied feedback boosts for {len(self.user_feedback_db)} corrections")

    def record_user_feedback(self, original_word: str, corrected_word: str, accepted: bool):
        """Record user feedback on a correction"""
        key = f"{original_word}->{corrected_word}"
        
        if accepted:
            self.user_feedback_db[key] += 1
            # Immediately apply boost
            self.words_db[corrected_word] += 50
        else:
            # User rejected - reduce frequency
            self.words_db[corrected_word] = max(1, self.words_db[corrected_word] - 20)
        
        # Log the feedback
        self.correction_history.append({
            'original': original_word,
            'corrected': corrected_word,
            'accepted': accepted,
            'timestamp': datetime.now().isoformat()
        })
        
        # Save to disk
        self._save_user_feedback()
        logger.info(f"Recorded feedback: {original_word} -> {corrected_word} (accepted={accepted})")

    def train_from_text(self, text):
        """Train the model from text"""
        words = re.findall(r"[a-z']+", text.lower())
        
        # Count word frequencies
        for word in words:
            self.words_db[word] += 1
        
        # Count bigrams
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            self.bigrams[bigram] += 1
        
        # Count trigrams
        for i in range(len(words) - 2):
            trigram = (words[i], words[i+1], words[i+2])
            self.trigrams[trigram] += 1
    
    def optimize_vocabulary(self, min_frequency=2):
        """Remove rare words"""
        before = len(self.words_db)
        self.words_db = {word: count for word, count in self.words_db.items() if count >= min_frequency}
        self.words_db = collections.Counter(self.words_db)
        after = len(self.words_db)
        print(f"   🔧 Optimized vocabulary: {before:,} → {after:,} words (removed {before-after:,} rare words)")

    def train_from_file(self, path):
        """Train from file"""
        print(f"📚 Loading corpus: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().lower()
        self.train_from_text(text)
        print(f"✅ Vocabulary size: {len(self.words_db)} unique words")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF"""
        if not HAS_PDF:
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

    def get_ml_suggestions(self, sentence: str, word_index: int, top_k: 5) -> List[str]:
        """Get suggestions from ML model using masked language modeling"""
        if not self.use_ml or not self.ml_model:
            return []
        
        try:
            words = sentence.split()
            if word_index >= len(words):
                return []
            
            # Replace target word with [MASK]
            masked_words = words.copy()
            original_word = masked_words[word_index]
            masked_words[word_index] = self.ml_tokenizer.mask_token
            
            masked_sentence = ' '.join(masked_words)
            
            # Tokenize and predict
            inputs = self.ml_tokenizer(masked_sentence, return_tensors='pt')
            
            with torch.no_grad():
                outputs = self.ml_model(**inputs)
                predictions = outputs.logits[0, word_index]  # Get predictions for masked token
            
            # Get top-k predictions
            top_indices = torch.topk(predictions, top_k * 3).indices.tolist()  # Get more to filter
            
            suggestions = []
            for idx in top_indices:
                word = self.ml_tokenizer.decode([idx]).strip()
                if word and word != original_word and len(word) > 1:
                    # Check if it's in our vocabulary or similar
                    suggestions.append(word)
                    if len(suggestions) >= top_k:
                        break
            
            return suggestions
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return []

    def _get_edits(self, word):
        """Generate all possible corrections 1 edit away"""
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
        
        # Afaan Oromo specific: vowel lengthening
        vowel_doubles = []
        vowels = 'aeiou'
        for L, R in splits:
            if R and R[0] in vowels:
                vowel_doubles.append(L + R[0] + R)
        
        return set(deletes + transposes + replaces + inserts + digraph_inserts + vowel_doubles)

    def _known(self, words):
        """Returns subset of words that appear in vocabulary"""
        return set(w for w in words if w in self.words_db)
    
    def _similarity_ratio(self, word1, word2):
        """Calculate similarity ratio"""
        if not word1 or not word2:
            return 0.0
        
        base_similarity = SequenceMatcher(None, word1, word2).ratio()
        
        # Vowel length penalty
        vowel_patterns_1 = re.findall(r'([aeiou])\1', word1)
        vowel_patterns_2 = re.findall(r'([aeiou])\1', word2)
        
        if len(vowel_patterns_1) != len(vowel_patterns_2):
            base_similarity *= 0.85
        
        return base_similarity
    
    def _phonetic_similarity(self, word1, word2):
        """Advanced phonetic similarity for Afaan Oromo"""
        if not word1 or not word2:
            return 0.0
        
        word1 = word1.lower()
        word2 = word2.lower()
        
        if word1 == word2:
            return 1.0
        
        score = 0.0
        
        # Afaan Oromo phonetic rules
        ejective_map = {
            'c': ['k', 'ch', 's'],
            'q': ['k', 'c'],
            'x': ['h', 's', 'sh'],
            'ch': ['c', 'sh'],
            'sh': ['x', 'ch'],
        }
        
        geminate_map = {
            'dh': ['d'],
            'd': ['dh'],
            'ny': ['n'],
            'n': ['ny'],
            'ph': ['p'],
            'th': ['t'],
        }
        
        max_len = max(len(word1), len(word2))
        if max_len == 0:
            return 1.0
        
        matches = 0
        i, j = 0, 0
        
        while i < len(word1) and j < len(word2):
            if word1[i] == word2[j]:
                matches += 1
                i += 1
                j += 1
                continue
            
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
            
            if not matched_digraph:
                # VOWEL LENGTH PROTECTION: Penalize vowel length changes more
                if word1[i] in 'aeiou' and word2[j] in 'aeiou':
                    # Check for vowel length difference (aa vs a, ee vs e)
                    if word1[i] == word2[j]:
                        matches += 0.7  # Same vowel, just length difference
                    else:
                        matches += 0.4  # Different vowels (more penalty)
                elif word1[i] not in 'aeiou' and word2[j] not in 'aeiou':
                    matches += 0.3
                
                i += 1
                j += 1
        
        phonetic_score = matches / max_len
        
        # STRONGER LENGTH PENALTY for vowel length differences
        length_diff = abs(len(word1) - len(word2))
        length_penalty = 1.0 - (length_diff * 0.15)  # Increased from 0.1 to 0.15
        length_penalty = max(0.4, length_penalty)  # Lower minimum (was 0.5)
        
        # EXTRA PENALTY: If difference is mainly vowel length
        vowel_diff = 0
        for c1, c2 in zip(word1, word2):
            if c1 in 'aeiou' and c2 in 'aeiou' and c1 != c2:
                vowel_diff += 1
        if vowel_diff > 0:
            length_penalty *= (1.0 - vowel_diff * 0.1)
        
        return phonetic_score * length_penalty

    def _calculate_edit_distance(self, word1, word2):
        """Calculate Levenshtein distance"""
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

    def get_word_suggestions(self, word, top_n=5):
        """Get top N suggestions for a misspelled word with balanced scoring"""
        word_lower = word.lower()
        
        # Check cache first
        cache_key = f"suggest:{word_lower}:{top_n}"
        if cache_key in self.correction_cache:
            self.cache_hits += 1
            return self.correction_cache[cache_key]
        
        self.cache_misses += 1
        
        # If word is correct, return it
        if word_lower in self.words_db:
            return [word_lower]
        
        all_suggestions = []
        
        # Edit distance 1 candidates
        candidates_1 = self._known(self._get_edits(word_lower))
        for cand in candidates_1:
            # Use balanced scoring
            edit_dist = 1
            edit_score = 90  # Edit distance 1
            phonetic_score = self._phonetic_similarity(word_lower, cand) * 100
            freq = self.words_db[cand]
            max_freq = max(self.words_db.values()) if self.words_db else 1
            freq_score = (freq / max_freq) * 100
            
            # Combined score
            score = (
                edit_score * 0.40 +
                phonetic_score * 0.30 +
                freq_score * 0.20 +
                50 * 0.10  # Base pattern score
            )
            all_suggestions.append((cand, score))
        
        # Edit distance 2 candidates (limited)
        if len(candidates_1) < top_n:
            candidates_2 = self._known(e2 for e1 in list(self._get_edits(word_lower))[:100] 
                                      for e2 in self._get_edits(e1))
            for cand in candidates_2:
                # Use balanced scoring
                edit_dist = 2
                edit_score = 70  # Edit distance 2
                phonetic_score = self._phonetic_similarity(word_lower, cand) * 100
                freq = self.words_db[cand]
                max_freq = max(self.words_db.values()) if self.words_db else 1
                freq_score = (freq / max_freq) * 100
                
                # Combined score
                score = (
                    edit_score * 0.40 +
                    phonetic_score * 0.30 +
                    freq_score * 0.20 +
                    40 * 0.10  # Base pattern score
                )
                all_suggestions.append((cand, score))
        
        # ML enhancement: get suggestions from transformer model
        if self.use_ml and len(all_suggestions) < top_n:
            test_sentence = f"Ani {word_lower} jira"  # Simple context
            ml_suggestions = self.get_ml_suggestions(test_sentence, 1, top_n=3)
            for ml_word in ml_suggestions:
                if ml_word not in [s[0] for s in all_suggestions]:
                    # Give ML suggestions a moderate score (assume edit distance 2)
                    edit_score = 70
                    phonetic_score = self._phonetic_similarity(word_lower, ml_word) * 100
                    freq = self.words_db.get(ml_word, 10)
                    max_freq = max(self.words_db.values()) if self.words_db else 1
                    freq_score = (freq / max_freq) * 100
                    
                    score = (
                        edit_score * 0.40 +
                        phonetic_score * 0.30 +
                        freq_score * 0.20 +
                        60 * 0.10  # ML bonus
                    )
                    all_suggestions.append((ml_word, score))
        
        # Sort by score and return top N
        all_suggestions.sort(key=lambda x: x[1], reverse=True)
        suggestions = [s[0] for s in all_suggestions[:top_n]]
        
        # Cache the result
        self.correction_cache[cache_key] = suggestions
        
        return suggestions if suggestions else [word_lower]

    def correct_word(self, word):
        """Corrects a single word using balanced scoring"""
        word_lower = word.lower()
        
        # Check cache
        cache_key = f"correct:{word_lower}"
        if cache_key in self.correction_cache:
            self.cache_hits += 1
            return self.correction_cache[cache_key]
        
        self.cache_misses += 1
        
        if word_lower in self.words_db:
            return word
        
        candidates = self._known(self._get_edits(word_lower))
        
        if not candidates:
            candidates = self._known(e2 for e1 in self._get_edits(word_lower) 
                                    for e2 in self._get_edits(e1))
        
        if not candidates:
            return word
        
        # Use balanced scoring instead of just frequency
        best_score = -1
        best_candidate = word
        
        for candidate in candidates:
            # 1. EDIT DISTANCE SCORE (40% weight)
            edit_dist = self._calculate_edit_distance(word_lower, candidate)
            if edit_dist == 0:
                edit_score = 100
            elif edit_dist == 1:
                edit_score = 90
            elif edit_dist == 2:
                edit_score = 70
            elif edit_dist == 3:
                edit_score = 50
            else:
                edit_score = max(0, 30 - (edit_dist - 3) * 10)
            
            # 2. PHONETIC SIMILARITY (30% weight)
            phonetic_score = self._phonetic_similarity(word_lower, candidate) * 100
            
            # 3. FREQUENCY SCORE (20% weight) - REDUCED!
            freq = self.words_db[candidate]
            max_freq = max(self.words_db.values()) if self.words_db else 1
            freq_score = (freq / max_freq) * 100
            
            # 4. PATTERN MATCHING (10% weight)
            pattern_score = 0
            
            # Afaan Oromo suffix bonus
            oromo_suffixes = ['uu', 'aa', 'ee', 'ii', 'oo', 'aan', 'een', 'iin', 'oon', 'un', 'tti', 'rra', 'ssa']
            if any(candidate.endswith(suffix) for suffix in oromo_suffixes):
                pattern_score += 30
            
            # Vowel length preservation
            if word_lower.count('aa') > 0 and candidate.count('aa') > 0:
                pattern_score += 20
            if word_lower.count('ee') > 0 and candidate.count('ee') > 0:
                pattern_score += 20
            
            # COMBINED SCORE with balanced weights
            total_score = (
                edit_score * 0.40 +      # Edit distance (PRIMARY)
                phonetic_score * 0.30 +  # Phonetic similarity
                freq_score * 0.20 +      # Frequency (REDUCED)
                pattern_score * 0.10     # Pattern matching
            )
            
            if total_score > best_score:
                best_score = total_score
                best_candidate = candidate
        
        # Cache result
        self.correction_cache[cache_key] = best_candidate
        
        return best_candidate

    def correct_sentence_with_context(self, sentence):
        """Correct spelling using context and ML"""
        words = sentence.split()
        corrected_words = []
        corrections_made = []
        
        is_incomplete = self._is_sentence_incomplete(sentence)
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            word_lower = clean_word.lower()
            
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
            
            # ML enhancement: get context-aware suggestions
            if self.use_ml:
                ml_suggestions = self.get_ml_suggestions(sentence, i, top_k=3)
                # Boost candidates that ML also suggests
                for cand in list(candidates):
                    if cand in ml_suggestions:
                        self.words_db[cand] += 200  # Temporary boost
            
            # Use context to select best candidate
            best_candidate = self._select_with_context(
                candidates, word_lower, corrected_words, i, words, i
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(candidates, best_candidate, word_lower)
            
            # SMART CORRECTION LOGIC (Option C - Balanced)
            # Only correct when it makes sense, respect dialects and ambiguity
            
            edit_dist = self._calculate_edit_distance(word_lower, best_candidate)
            phonetic_sim = self._phonetic_similarity(word_lower, best_candidate)
            
            should_correct = False
            
            # Rule 1: OBVIOUS TYPOS - Edit distance 1, high phonetic similarity
            # Example: "affan" → "afaan" (1 char diff, sounds very similar)
            # Example: "fedh" → "fedha" (missing vowel at end)
            if edit_dist == 1 and phonetic_sim >= 0.75 and confidence >= 75:
                should_correct = True
            
            # Rule 2: CLEAR TYPOS - Edit distance 1, good phonetic, high confidence
            # Example: "fedh" → "fedha" (missing vowel)
            elif edit_dist == 1 and phonetic_sim >= 0.75 and confidence >= 85:
                should_correct = True
            
            # Rule 3: CONTEXT HELPS - Lower threshold if context strongly supports
            # Example: "Oromo" in language context → "Oromoo"
            elif edit_dist <= 2 and confidence >= 90 and phonetic_sim >= 0.70:
                should_correct = True
            
            # Rule 4: DON'T CORRECT if word follows STRONG Afaan Oromo patterns
            # and confidence is not very high
            # Examples: "hiin" (double vowel), "hawin" (geminated consonant)
            elif self._follows_oromo_patterns(word_lower) and confidence < 90:
                should_correct = False  # Respect dialect words when not very confident
            
            # Rule 5: DON'T CORRECT if ambiguous (multiple valid interpretations)
            # Example: "mal" could be "maal" or "jal"
            elif len(candidates) > 1 and confidence < 85:
                should_correct = False  # Too ambiguous
            
            # Default: Don't correct if uncertain
            else:
                should_correct = False
            
            if should_correct and best_candidate != word_lower:
                corrected_words.append(best_candidate + punctuation)
                corrections_made.append({
                    'original': word,
                    'corrected': best_candidate + punctuation,
                    'position': i,
                    'confidence': confidence
                })
            else:
                corrected_words.append(word)
        
        corrected_sentence = " ".join(corrected_words)
        return corrected_sentence, corrections_made
    
    def _is_sentence_incomplete(self, sentence):
        """Check if sentence appears incomplete"""
        sentence = sentence.strip()
        
        if not sentence:
            return True
        
        if sentence.endswith(('.', '!', '?', ':', ';')):
            return False
        
        words = sentence.split()
        if words:
            last_word = re.sub(r'[^\w\']', '', words[-1].lower())
            incomplete_endings = ['dh', 'fh', 'mh', 'nh', 'deem', 'dhuf', 'bar', 'ny']
            if any(last_word.endswith(ending) for ending in incomplete_endings):
                return True
        
        if len(words) < 3:
            return True
        
        return False
    
    def _follows_oromo_patterns(self, word):
        """Check if word follows valid Afaan Oromo phonetic patterns
        Returns True if word might be a valid dialect variation"""
        
        if not word or len(word) < 2:
            return False
        
        # Pattern 1: Double vowels (common in Oromo)
        # Examples: hiin, akkaam, gaaraa, bareedaa
        double_vowel = re.search(r'([aeiou])\1', word)
        if double_vowel:
            return True
        
        # Pattern 2: Geminated consonants (dh, ny, ph, th)
        # Examples: hawin, dhugde, nyadhe
        geminate_consonants = ['dh', 'ny', 'ph', 'th', 'ch', 'sh']
        if any(word.find(gc) >= 0 for gc in geminate_consonants):
            return True
        
        # Pattern 3: Valid Oromo suffixes
        # Examples: -uu, -aa, -ee, -tti, -rra, -ssa
        oromo_suffixes = ['uu', 'aa', 'ee', 'ii', 'oo', 'aan', 'een', 'iin', 
                         'oon', 'un', 'tti', 'rra', 'ssa', 'ni', 'tu', 'ra']
        if any(word.endswith(suffix) for suffix in oromo_suffixes):
            return True
        
        # Pattern 4: Ejective consonants (c, q, x)
        # Examples: qulqulluu, ciccittaa, xaxaa
        ejective_consonants = ['c', 'q', 'x']
        if any(word.find(ec) >= 0 for ec in ejective_consonants):
            return True
        
        # Pattern 5: Word length >= 4 and contains multiple vowels
        # Very short words or words with only 1 vowel are more likely typos
        vowels = sum(1 for c in word if c in 'aeiou')
        if len(word) >= 4 and vowels >= 2:
            return True
        
        return False
    
    def _select_with_context(self, candidates, original_word, prev_words, position, all_words=None, current_pos=None):
        """Select best candidate using context"""
        if not candidates:
            return original_word
        
        if len(candidates) == 1:
            return list(candidates)[0]
        
        best_score = -1
        best_candidate = list(candidates)[0]
        
        prev_word = prev_words[-1] if prev_words else None
        if prev_word:
            prev_word = re.sub(r'[^\w\']', '', prev_word).lower()
        
        next_word = None
        if all_words and current_pos is not None and current_pos + 1 < len(all_words):
            next_word = re.sub(r'[^\w\']', '', all_words[current_pos + 1]).lower()

        # Afaan Oromo specific patterns
        oromo_verb_patterns = {
            'ani': ['fedha', 'barra', 'dhuga', 'nyaadha', 'deema', 'jira', 'beeka', 'barbaada', 'jedha', 'kaaa', 'taha'],
            'inni': ['deeme', 'dhufe', 'fedhe', 'bara', 'dhuge', 'nyaate', 'jira', 'beeka', 'jedhe', 'taha'],
            'isheen': ['deemte', 'dhufte', 'fedhte', 'bartee', 'dhugde', 'nyaatte', 'jirti', 'beekti', 'jette', 'tatte'],
            'nuti': ['fedhna', 'barra', 'dhugna', 'nyaanna', 'deemna', 'jirra', 'beekna', 'jedhna', 'taha'],
            'isin': ['fedha', 'barra', 'dhugdu', 'nyaattu', 'deemtu', 'jirtu', 'beektu', 'jettu', 'taha'],
            'isaan': ['fedhu', 'baru', 'dhugu', 'nyaatu', 'deemu', 'jiru', 'beeku', 'jettu', 'tahu'],
        }
        
        oromo_preposition_patterns = {
            'gara': ['mana', 'barumsaa', 'hojii', 'gaba', 'suuqa', 'bakka', 'magalaa', 'garee'],
            'irraa': ['mana', 'barumsaa', 'gaba', 'bakka', 'magalaa', 'fageenya'],
            'itti': ['deeme', 'dhufe', 'kaae', 'kaayye', 'deebie', 'galagge'],
            'waliin': ['deeme', 'dhufe', 'jira', 'hojje', 'bulle', 'turre'],
            'keessa': ['mana', 'gala', 'bakka', 'barumsaa', 'magalaa', 'biyyoo'],
            'biraa': ['dhufe', 'deeme', 'jira', 'kaae', 'argame'],
        }
        
        oromo_adjective_patterns = {
            'nama': ['gaarii', 'balaa', 'guddaa', 'xiqqaa', 'dheeraa', 'gabaabaa'],
            'bishaan': ['qulqulluu', 'hoaa', 'qorraa', 'miaa'],
            'mana': ['guddaa', 'haaraa', 'mooraa', 'balaa'],
        }
        
        # BALANCED SCORING FORMULA (Fixed for accuracy)
        # Weights: Edit distance 40%, Phonetic 30%, Frequency 20%, Context 10%
        
        for candidate in candidates:
            # 1. EDIT DISTANCE SCORE (0-100 points) - HIGHEST WEIGHT (40%)
            edit_dist = self._calculate_edit_distance(original_word, candidate)
            if edit_dist == 0:
                edit_score = 100
            elif edit_dist == 1:
                edit_score = 85
            elif edit_dist == 2:
                edit_score = 60
            elif edit_dist == 3:
                edit_score = 40
            else:
                edit_score = max(0, 20 - (edit_dist - 3) * 10)
            
            # 2. PHONETIC SIMILARITY (0-100 points) - HIGH WEIGHT (30%)
            phonetic_score = self._phonetic_similarity(original_word, candidate) * 100
            
            # 3. FREQUENCY SCORE (0-100 points) - MODERATE WEIGHT (20%)
            freq = self.words_db[candidate]
            max_freq = max(self.words_db.values()) if self.words_db else 1
            freq_score = (freq / max_freq) * 100
            
            # 4. CONTEXT SCORE (0-50 points) - LOW WEIGHT (10%)
            context_score = 0
            
            # Bigram context bonus
            if prev_word:
                bigram = (prev_word, candidate)
                if bigram in self.bigrams:
                    context_score += 15  # Reduced from *5 multiplier
                
                # Verb pattern matching (smaller bonus)
                if prev_word in oromo_verb_patterns:
                    if candidate in oromo_verb_patterns[prev_word]:
                        context_score += 20  # Reduced from 100
                    else:
                        is_verb = any(candidate.endswith(end) for end in ['e', 'a', 'u', 'te', 'na', 'tu'])
                        if not is_verb:
                            context_score -= 5  # Small penalty
                
                # Preposition patterns
                if prev_word in oromo_preposition_patterns:
                    if candidate in oromo_preposition_patterns[prev_word]:
                        context_score += 12  # Reduced from 60
                
                # Adjective patterns
                if prev_word in oromo_adjective_patterns:
                    if candidate in oromo_adjective_patterns[prev_word]:
                        context_score += 10  # Reduced from 50
            
            # Trigram context (smaller bonus)
            if len(prev_words) >= 2:
                word_before_prev = re.sub(r'[^\w\']', '', prev_words[-2]).lower() if len(prev_words) >= 2 else None
                if word_before_prev:
                    trigram = (word_before_prev, prev_word, candidate)
                    if trigram in self.trigrams:
                        context_score += 10  # Reduced from *8 multiplier
            
            # Forward lookahead (smaller bonus)
            if next_word:
                forward_bigram = (candidate, next_word)
                if forward_bigram in self.bigrams:
                    context_score += 8  # Reduced from *6 multiplier
            
            # Suffix bonus (reduced)
            oromo_suffixes = ['uu', 'aa', 'ee', 'ii', 'oo', 'aan', 'een', 'iin', 'oon', 'un', 'tti', 'rra', 'ssa']
            if any(candidate.endswith(suffix) for suffix in oromo_suffixes):
                context_score += 5  # Reduced from *1.3 multiplier
            
            # SOV word order (reduced)
            if prev_word in ['barumsaa', 'mana', 'gaba', 'hojii', 'bishaan', 'nyaata', 'kitaba', 'finfinnee']:
                common_verbs = ['deeme', 'dhufe', 'fedha', 'jira', 'bara', 'dhuga', 'nyaata', 'bine', 'qaba']
                if candidate in common_verbs:
                    context_score += 10  # Reduced from 70
            
            # COMBINED SCORE with proper weights
            total_score = (
                edit_score * 0.40 +      # Edit distance (most important)
                phonetic_score * 0.30 +  # Phonetic similarity
                freq_score * 0.20 +      # Word frequency (reduced from dominant)
                context_score * 0.10     # Context (reduced)
            )

            if total_score > best_score:
                best_score = total_score
                best_candidate = candidate
        
        return best_candidate
    
    def _calculate_confidence(self, candidates, best_candidate, original_word):
        """Calculate confidence score (0-100%) - CONSERVATIVE"""
        if not candidates:
            return 0
        
        # 1. Edit distance is most important for confidence
        edit_dist = self._calculate_edit_distance(original_word, best_candidate)
        if edit_dist == 0:
            edit_confidence = 100
        elif edit_dist == 1:
            edit_confidence = 80
        elif edit_dist == 2:
            edit_confidence = 60
        elif edit_dist == 3:
            edit_confidence = 40
        else:
            edit_confidence = max(0, 30 - (edit_dist - 3) * 10)
        
        # 2. Phonetic similarity
        phonetic = self._phonetic_similarity(original_word, best_candidate)
        phonetic_confidence = int(phonetic * 100)
        
        # 3. Frequency ratio (less weight)
        freq_scores = {cand: self.words_db[cand] for cand in candidates}
        max_freq = max(freq_scores.values()) if freq_scores else 1
        best_freq = freq_scores.get(best_candidate, 0)
        freq_confidence = int((best_freq / max_freq) * 50) if max_freq > 0 else 0
        
        # CONSERVATIVE: Weight edit distance and phonetic more
        total_confidence = min(100, int(
            edit_confidence * 0.50 +        # Edit distance (50%)
            phonetic_confidence * 0.35 +    # Phonetic (35%)
            freq_confidence * 0.15          # Frequency (15%)
        ))
        
        # PENALTY: If original word is very different from candidate
        len_diff = abs(len(original_word) - len(best_candidate))
        if len_diff >= 3:
            total_confidence = max(0, total_confidence - 20)
        elif len_diff >= 2:
            total_confidence = max(0, total_confidence - 10)
        
        return total_confidence

    def ai_correct_sentence(self, sentence):
        """Main correction method - backward compatible"""
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
        """Comprehensive grammar checking using advanced grammar checker"""
        return self.grammar_checker.check_grammar(sentence)
    
    def get_cache_stats(self):
        """Get cache performance statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cache_size': len(self.correction_cache)
        }
