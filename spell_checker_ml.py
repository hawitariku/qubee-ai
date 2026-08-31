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
    # pypdf is the maintained successor to the unmaintained PyPDF2 package.
    # Both expose the same PdfReader API used below.
    try:
        from pypdf import PdfReader as _PdfReader
    except ImportError:
        from PyPDF2 import PdfReader as _PdfReader  # legacy fallback
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# transformers/torch are imported lazily inside __init__ only when use_ml=True.
# Top-level import is intentionally omitted — it causes multi-minute hangs on
# CPU-only machines where PyTorch must initialise its CUDA/MPS subsystems.
HAS_TRANSFORMERS = False  # updated to True inside __init__ if import succeeds

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
        
        # ML Model integration — lazy import to avoid startup hang on CPU-only machines
        self.use_ml = False
        self.ml_model = None
        self.ml_tokenizer = None
        self._torch = None  # set when ML loads successfully

        if use_ml:
            try:
                from transformers import AutoTokenizer, AutoModelForMaskedLM
                import torch as _torch
                print(f"\n🤖 Loading ML model: {model_name}")
                self.ml_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ml_model = AutoModelForMaskedLM.from_pretrained(model_name)
                self.ml_model.eval()
                self.use_ml = True
                # Make torch available to get_ml_suggestions
                self._torch = _torch
                print("✅ ML model loaded successfully!")
            except ImportError:
                print("⚠️ transformers/torch not installed — running without ML model.")
                self.use_ml = False
            except Exception as e:
                print(f"⚠️ Failed to load ML model: {e}")
                self.use_ml = False
        
        # Common Afaan Oromo words with high priority
        self.common_words = {
            'afaan': 10000, 'oromoo': 10000, 'inni': 9500, 'isheen': 9500,
            'ani': 9500, 'nuti': 9500, 'isin': 9500, 'isaan': 9500,
            # Core pronouns get extra-high freq so corpus variants don't beat them
            'ati': 9500,
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
        
        # Optimize vocabulary - remove rare words (likely typos)
        self.optimize_vocabulary(min_frequency=5)

        # Wire the final vocabulary into the grammar checker so verb detection
        # can cross-reference it and avoid mis-classifying nouns as verbs.
        self.grammar_checker.set_vocabulary(self.words_db)

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

    # Maximum frequency boost a single word can accumulate from user feedback.
    # Prevents runaway boosts from repeated or accidental accepts.
    _MAX_FEEDBACK_BOOST = 5000

    def _apply_user_feedback_boosts(self):
        """Apply boosts to words based on user feedback"""
        for correction_pair, count in self.user_feedback_db.items():
            # correction_pair format: "original->corrected"
            if '->' in correction_pair:
                _, corrected = correction_pair.split('->', 1)
                # Boost frequency based on user acceptances, capped per word
                boost = min(count * 100, self._MAX_FEEDBACK_BOOST)
                self.words_db[corrected] += boost
        logger.info(f"Applied feedback boosts for {len(self.user_feedback_db)} corrections")

    def record_user_feedback(self, original_word: str, corrected_word: str, accepted: bool):
        """Record user feedback on a correction"""
        key = f"{original_word}->{corrected_word}"

        if accepted:
            self.user_feedback_db[key] += 1
            # Immediate boost, capped so a single word can't exceed MAX_FEEDBACK_BOOST
            current_boost = self.user_feedback_db[key] * 50
            if current_boost <= self._MAX_FEEDBACK_BOOST:
                self.words_db[corrected_word] += 50
            else:
                logger.warning(
                    f"Feedback boost cap reached for '{corrected_word}' "
                    f"(accepted {self.user_feedback_db[key]} times). No further boost applied."
                )
        else:
            # User rejected — reduce frequency, but never below 1
            self.words_db[corrected_word] = max(1, self.words_db[corrected_word] - 20)

        # Log the feedback event
        self.correction_history.append({
            'original': original_word,
            'corrected': corrected_word,
            'accepted': accepted,
            'timestamp': datetime.now().isoformat()
        })

        # Flag high-volume corrections for manual review (> 20 accepts or > 10 rejects)
        total_accepts = self.user_feedback_db.get(key, 0)
        reject_key = f"rejected:{key}"
        total_rejects = self.user_feedback_db.get(reject_key, 0)
        if accepted and total_accepts == 20:
            logger.info(f"REVIEW CANDIDATE (high accepts): '{original_word}' → '{corrected_word}' accepted {total_accepts}x")
        if not accepted:
            self.user_feedback_db[reject_key] = self.user_feedback_db.get(reject_key, 0) + 1
            if self.user_feedback_db[reject_key] == 10:
                logger.warning(f"REVIEW CANDIDATE (frequent rejects): '{original_word}' → '{corrected_word}' rejected {self.user_feedback_db[reject_key]}x")

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
        """Extract text from PDF using pypdf (or PyPDF2 as legacy fallback)."""
        if not HAS_PDF:
            return ""
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = _PdfReader(f)
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
            
            with self._torch.no_grad():
                outputs = self.ml_model(**inputs)
                predictions = outputs.logits[0, word_index]  # Get predictions for masked token
            
            # Get top-k predictions
            top_indices = self._torch.topk(predictions, top_k * 3).indices.tolist()  # Get more to filter
            
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

    def get_alternatives_by_frequency(self, word, top_n=5):
        """Get top N alternatives sorted by FREQUENCY ONLY (for user suggestions)"""
        word_lower = word.lower()
        
        # If word is correct, return empty
        if word_lower in self.words_db:
            return []
        
        all_candidates = []
        
        # Get edit distance 1 and 2 candidates
        edits1 = self._get_edits(word_lower)
        candidates1 = self._known(edits1)
        
        edits2 = set(e2 for e1 in edits1 for e2 in self._get_edits(e1))
        candidates2 = self._known(edits2)
        
        all_candidates = candidates1.union(candidates2)
        
        if not all_candidates:
            return []
        
        # FILTER: Remove fragments and invalid words
        valid_candidates = []
        for cand in all_candidates:
            # Skip very short words (likely fragments)
            if len(cand) < 4:  # Increased from 3 to 4
                continue
            
            # Skip words that are just single letters repeated (aa, kk, etc.)
            if len(set(cand)) == 1:
                continue
            
            # Skip words with only 2 unique characters (kaa, kka, etc.)
            if len(set(cand)) <= 2:
                continue
            
            # Must have at least one vowel
            if not any(v in cand for v in 'aeiou'):
                continue
            
            # Must have at least one consonant
            consonants = set('bcdfghjklmnpqrstvwxyz')
            if not any(c in cand for c in consonants):
                continue
            
            # Must have reasonable frequency (at least 50 occurrences for quality)
            if self.words_db[cand] < 50:
                continue
            
            # Skip words that are mostly repeated characters (kaaa, ammm, etc.)
            char_counts = {}
            for c in cand:
                char_counts[c] = char_counts.get(c, 0) + 1
            max_repeat = max(char_counts.values())
            if max_repeat > len(cand) * 0.6:  # More than 60% is one character
                continue
            
            valid_candidates.append(cand)
        
        # Sort by a BALANCED score: 60% phonetic similarity + 40% normalised frequency.
        # This prevents high-frequency but phonetically-irrelevant words (e.g. Biblical
        # proper nouns) from crowding out more accurate suggestions.
        max_freq = max((self.words_db[c] for c in valid_candidates), default=1)

        def _alt_score(cand: str) -> float:
            phonetic = self._phonetic_similarity(word_lower, cand)
            freq_norm = self.words_db[cand] / max_freq
            return phonetic * 0.60 + freq_norm * 0.40

        sorted_candidates = sorted(valid_candidates, key=_alt_score, reverse=True)

        return sorted_candidates[:top_n]

    def correct_word(self, word):
        """Corrects a single word using balanced scoring.
        Preserves the capitalisation pattern of the input word.
        """
        word_lower = word.lower()
        is_capitalised = word and word[0].isupper()
        
        # Check cache
        cache_key = f"correct:{word_lower}"
        if cache_key in self.correction_cache:
            self.cache_hits += 1
            return self.correction_cache[cache_key]
        
        self.cache_misses += 1
        
        if word_lower in self.words_db:
            return word
        
        # IMPROVED: Collect ALL candidates (edit distance 1 AND 2) and score them all
        all_candidates = set()
        
        # Edit distance 1 candidates
        edits1 = self._get_edits(word_lower)
        candidates1 = self._known(edits1)
        all_candidates.update(candidates1)
        
        # Edit distance 2 candidates (always check, don't skip!)
        edits2 = set(e2 for e1 in edits1 for e2 in self._get_edits(e1))
        candidates2 = self._known(edits2)
        all_candidates.update(candidates2)
        
        if not all_candidates:
            return word
        
        # Score ALL candidates and pick the best
        scored_candidates = []
        
        for candidate in all_candidates:
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
            
            # 3. FREQUENCY SCORE (20% weight)
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
            
            # Geminate consonant bonus (kk, tt, pp, etc.)
            geminate_pairs = ['kk', 'tt', 'pp', 'bb', 'dd', 'ff', 'gg', 'll', 'mm', 'nn', 'rr', 'ss']
            for gem in geminate_pairs:
                if gem in candidate:
                    pattern_score += 15
            
            # COMBINED SCORE with balanced weights
            # Prioritize phonetic similarity and edit distance over frequency
            total_score = (
                edit_score * 0.35 +      # Edit distance
                phonetic_score * 0.35 +  # Phonetic similarity (INCREASED)
                freq_score * 0.20 +      # Frequency
                pattern_score * 0.10     # Pattern matching
            )
            
            scored_candidates.append((candidate, total_score, edit_dist, freq))
        
        # Sort by score (highest first), then by frequency as tiebreaker
        scored_candidates.sort(key=lambda x: (x[1], x[3]), reverse=True)
        
        # Get the best candidate
        best_candidate = scored_candidates[0][0] if scored_candidates else word_lower

        # Restore original capitalisation
        if is_capitalised and best_candidate:
            best_candidate = best_candidate.capitalize()

        # Cache result
        self.correction_cache[cache_key] = best_candidate

        return best_candidate

    def correct_sentence_with_context(self, sentence):
        """Correct spelling using balanced scoring (simplified approach)"""
        words = sentence.split()
        corrected_words = []
        corrections_made = []
        
        for i, word in enumerate(words):
            # Separate punctuation from word
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            word_lower = clean_word.lower()

            # Skip purely numeric tokens — numbers don't need spell checking
            if clean_word.isdigit():
                corrected_words.append(word)
                continue

            # Preserve words containing apostrophes if they look like valid
            # Afaan Oromo glottal-stop forms (e.g. ba'ee, ta'uu, dha'uu).
            # If the base form (before apostrophe) is recognisable, keep as-is.
            if "'" in clean_word:
                parts = clean_word.lower().split("'")
                if all(len(p) >= 1 for p in parts):
                    corrected_words.append(word)
                    continue

            # If word is in vocabulary, keep it as-is
            if word_lower in self.words_db:
                corrected_words.append(word)
                continue
            
            # Use the balanced scoring from correct_word()
            corrected = self.correct_word(word_lower)

            # Preserve original capitalization
            if clean_word[0].isupper():
                corrected = corrected.capitalize()

            # Add punctuation back
            corrected_with_punct = corrected + punctuation

            # Track correction if word changed
            if corrected != word_lower:
                # Compute real confidence using edit distance + phonetic + frequency.
                # Gather the same candidate set correct_word() used so the confidence
                # calculation has meaningful comparisons rather than just the winner.
                _edits1 = self._get_edits(word_lower)
                _cands = self._known(_edits1)
                if not _cands:
                    _edits2 = set(e2 for e1 in list(_edits1)[:50] for e2 in self._get_edits(e1))
                    _cands = self._known(_edits2)
                confidence = self._calculate_confidence(
                    _cands if _cands else {corrected.lower()},
                    corrected.lower(),
                    word_lower
                )
                corrected_words.append(corrected_with_punct)
                corrections_made.append({
                    'original': word,
                    'corrected': corrected_with_punct,
                    'position': i,
                    'confidence': confidence,
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

    def correct_sentence(self, sentence):
        """Alias for ai_correct_sentence — used by tests and external callers."""
        return self.ai_correct_sentence(sentence)
    
    def get_detailed_corrections(self, sentence):
        """Get detailed correction information with alternative suggestions"""
        corrected, corrections = self.correct_sentence_with_context(sentence)
        
        # Add alternative suggestions for each correction (sorted by FREQUENCY)
        for correction in corrections:
            original_word = correction['original'].lower().strip('.,!?;:')
            corrected_word = correction['corrected'].lower().strip('.,!?;:')
            if original_word:
                # Get top 6 alternatives sorted by FREQUENCY (we'll remove the chosen one)
                alternatives = self.get_alternatives_by_frequency(original_word, top_n=6)
                # Remove the chosen correction from alternatives
                if corrected_word in alternatives:
                    alternatives.remove(corrected_word)
                correction['alternatives'] = alternatives[:5]  # Top 5 after removing chosen
        
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
