"""
Improved Spell Checker with Better Accuracy
Fixes:
- Better scoring balance
- Stronger edit distance weighting
- More flexible context matching
- Improved phonetic similarity
"""

import re
import collections
from difflib import SequenceMatcher


class ImprovedSpellChecker:
    """Enhanced accuracy spell checker"""
    
    def __init__(self, words_db, bigrams, trigrams):
        self.words_db = words_db
        self.bigrams = bigrams
        self.trigrams = trigrams
        
        # Expanded verb patterns with more variations
        self.verb_patterns = {
            'ani': {
                'present': ['fedha', 'barra', 'dhuga', 'nyaadha', 'deema', 'jira', 'beeka', 'barbaada', 'jedha', 'kaaa', 'taha', 'hojjedha', 'barra', 'dhugha'],
                'past': ['fedhe', 'barre', 'dhuge', 'nyaadhe', 'deeme', 'jire', 'beeke', 'barbaade', 'jedhe', 'kaae', 'tahe', 'hojjedhe'],
            },
            'inni': {
                'present': ['fedha', 'bara', 'dhuga', 'nyaata', 'deema', 'jira', 'beeka', 'barbaada', 'jedha', 'taha', 'hojjeta'],
                'past': ['deeme', 'dhufe', 'fedhe', 'bara', 'dhuge', 'nyaate', 'jira', 'beeka', 'jedhe', 'taha', 'nyaaate', 'hojjete'],
            },
            'isheen': {
                'present': ['fedha', 'barra', 'dhugdi', 'nyaatti', 'deemti', 'jirti', 'beekti', 'jetti', 'tatti', 'hojjetti'],
                'past': ['deemte', 'dhufte', 'fedhte', 'bartee', 'dhugde', 'nyaatte', 'jirti', 'beekti', 'jette', 'tatte', 'hojjette'],
            },
        }
        
    def _get_edits(self, word):
        """Generate edit distance 1 candidates"""
        letters = "abcdefghijklmnopqrstuvwxyz'"
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        
        # Afaan Oromo digraphs
        digraphs = ["ch", "sh", "dh", "ny", "ph", "th"]
        digraph_inserts = []
        for L, R in splits:
            for digraph in digraphs:
                digraph_inserts.append(L + digraph + R)
        
        # Vowel lengthening
        vowel_doubles = []
        vowels = 'aeiou'
        for L, R in splits:
            if R and R[0] in vowels:
                vowel_doubles.append(L + R[0] + R)
        
        return set(deletes + transposes + replaces + inserts + digraph_inserts + vowel_doubles)
    
    def _known(self, words):
        """Filter to known words"""
        return set(w for w in words if w in self.words_db)
    
    def _phonetic_similarity(self, word1, word2):
        """Improved phonetic similarity"""
        if word1 == word2:
            return 1.0
        
        # Base similarity
        base = SequenceMatcher(None, word1, word2).ratio()
        
        # Length penalty
        len_diff = abs(len(word1) - len(word2))
        len_penalty = max(0.5, 1.0 - (len_diff * 0.15))
        
        # Vowel length check (important in Oromo)
        v1 = re.findall(r'([aeiou])\1', word1)
        v2 = re.findall(r'([aeiou])\1', word2)
        if len(v1) != len(v2):
            base *= 0.9
        
        return base * len_penalty
    
    def _edit_distance(self, word1, word2):
        """Calculate Levenshtein distance"""
        if len(word1) < len(word2):
            return self._edit_distance(word2, word1)
        
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
    
    def score_candidate(self, candidate, original_word, prev_word=None, next_word=None):
        """
        Improved scoring with better balance
        Returns: (score, confidence)
        """
        edit_dist = self._edit_distance(original_word, candidate)
        phonetic = self._phonetic_similarity(original_word, candidate)
        freq = self.words_db[candidate]
        
        # IMPROVED SCORING: Edit distance is PRIMARY (most important)
        # This fixes the 70% accuracy issue
        
        # 1. Edit distance score (0-100 points) - HIGHEST WEIGHT
        # Closer words get much higher scores
        if edit_dist == 0:
            edit_score = 100
        elif edit_dist == 1:
            edit_score = 85  # One edit = still very likely
        elif edit_dist == 2:
            edit_score = 60  # Two edits = possible
        else:
            edit_score = max(0, 40 - (edit_dist - 2) * 15)
        
        # 2. Phonetic similarity (0-100 points) - HIGH WEIGHT
        phonetic_score = phonetic * 100
        
        # 3. Frequency score (0-100 points) - MODERATE WEIGHT
        # Normalize frequency to prevent domination
        max_freq = max(self.words_db.values()) if self.words_db else 1
        freq_score = (freq / max_freq) * 100
        
        # 4. Context bonus (0-50 points)
        context_score = 0
        
        if prev_word:
            # Check verb patterns
            for subject, tenses in self.verb_patterns.items():
                if prev_word == subject:
                    all_verbs = tenses.get('present', []) + tenses.get('past', [])
                    if candidate in all_verbs:
                        context_score += 50  # Strong match
                        break
                    elif any(candidate.endswith(v[:-1]) for v in all_verbs if len(v) > 3):
                        context_score += 25  # Partial match
            
            # Bigram frequency
            bigram = (prev_word, candidate)
            if bigram in self.bigrams:
                context_score += min(30, self.bigrams[bigram] / 10)
        
        # COMBINED SCORE with proper weights
        # Edit distance: 40%, Phonetic: 30%, Frequency: 20%, Context: 10%
        total_score = (
            edit_score * 0.40 +      # Edit distance (most important)
            phonetic_score * 0.30 +  # Phonetic similarity
            freq_score * 0.20 +      # Word frequency
            context_score * 0.10     # Context
        )
        
        # Confidence calculation (0-100%)
        confidence = min(100, int(
            edit_score * 0.50 +      # Edit distance dominates confidence
            phonetic_score * 0.30 +  # Phonetic matters
            freq_score * 0.20        # Frequency matters less
        ))
        
        return total_score, confidence
    
    def correct_word_with_accuracy(self, word, prev_word=None, next_word=None):
        """
        Accurate word correction
        Returns: (corrected_word, confidence, was_corrected)
        """
        word_lower = word.lower()
        
        # If word exists in vocabulary, it's correct
        if word_lower in self.words_db:
            return word_lower, 100, False
        
        # Get candidates at edit distance 1
        candidates = self._known(self._get_edits(word_lower))
        
        # If no candidates at distance 1, try distance 2
        if not candidates:
            edits_1 = list(self._get_edits(word_lower))[:150]  # Limit for performance
            candidates = self._known(e2 for e1 in edits_1 for e2 in self._get_edits(e1))
        
        if not candidates:
            return word_lower, 0, False  # No correction possible
        
        # Score all candidates
        scored_candidates = []
        for candidate in candidates:
            score, confidence = self.score_candidate(
                candidate, word_lower, prev_word, next_word
            )
            scored_candidates.append((candidate, score, confidence))
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Get best candidate
        best_candidate, best_score, best_confidence = scored_candidates[0]
        
        # Only correct if confidence is reasonable
        if best_confidence >= 60:  # Lowered from 70 to catch more corrections
            return best_candidate, best_confidence, True
        else:
            return word_lower, best_confidence, False  # Keep original
    
    def correct_sentence_accurate(self, sentence):
        """Accurate sentence correction with context"""
        words = sentence.split()
        corrected_words = []
        corrections_made = []
        
        for i, word in enumerate(words):
            # Clean word
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            # Get context
            prev_word = None
            next_word = None
            if i > 0:
                prev_word = re.sub(r'[^\w\']', '', words[i-1]).lower()
            if i < len(words) - 1:
                next_word = re.sub(r'[^\w\']', '', words[i+1]).lower()
            
            # Correct word
            word_lower = clean_word.lower()
            corrected, confidence, was_corrected = self.correct_word_with_accuracy(
                word_lower, prev_word, next_word
            )
            
            if was_corrected:
                corrected_words.append(corrected + punctuation)
                corrections_made.append({
                    'original': word,
                    'corrected': corrected + punctuation,
                    'position': i,
                    'confidence': confidence
                })
            else:
                corrected_words.append(word)
        
        return " ".join(corrected_words), corrections_made


def test_accuracy():
    """Test the improved accuracy"""
    from spell_checker_ml import MLEnhancedSpellChecker
    
    # Load existing spell checker to get vocabulary
    print("Loading vocabulary...")
    checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    # Create improved checker with same vocabulary
    improved = ImprovedSpellChecker(checker.words_db, checker.bigrams, checker.trigrams)
    
    # Test cases
    test_cases = [
        ("Ani bishaan dhuguu fedh", "Ani bishaan dhuguu fedha"),
        ("Inni gara mana deeme", "Inni gara mana deeme"),
        ("Isheen barattuu dha", "Isheen barattuu dha"),
        ("Ani kitaaba bar", "Ani kitaaba bara"),
        ("Inni hojii hojj", "Inni hojii hojjeta"),
    ]
    
    print("\n" + "="*60)
    print("Testing Improved Accuracy")
    print("="*60 + "\n")
    
    correct = 0
    total = len(test_cases)
    
    for input_sentence, expected in test_cases:
        corrected, corrections = improved.correct_sentence_accurate(input_sentence)
        
        is_correct = corrected.lower() == expected.lower()
        if is_correct:
            correct += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        
        print(f"{status}")
        print(f"  Input:    {input_sentence}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {corrected}")
        if corrections:
            print(f"  Changes:  {len(corrections)}")
            for c in corrections:
                print(f"    {c['original']} → {c['corrected']} ({c['confidence']}%)")
        print()
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print("="*60)
    print(f"Accuracy: {correct}/{total} = {accuracy:.1f}%")
    print("="*60)


if __name__ == '__main__':
    test_accuracy()
