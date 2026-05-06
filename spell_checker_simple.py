import re
import collections

class AfaanOromoSpellChecker:
    def __init__(self, corpus_path=None):
        self.words_db = collections.Counter()
        
        print("Initializing spell checker...")
        
        # Train the frequency dictionary from corpus
        if corpus_path:
            self.train_from_file(corpus_path)
        else:
            sample_text = "Ani bishaan dhuguu fedha. Inni gara mana deeme. Isheen barattuu dha."
            self.train_from_text(sample_text)
        
        print(f"✅ Spell checker ready with {len(self.words_db)} words!")

    def train_from_text(self, text):
        # Afaan Oromo includes ' (hudhaa). We keep letters and the apostrophe.
        words = re.findall(r"[a-z']+", text.lower())
        for word in words:
            self.words_db[word] += 1

    def train_from_file(self, path):
        print(f"📚 Loading corpus: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().lower()
        self.train_from_text(text)
        print(f"✅ Vocabulary size: {len(self.words_db)} unique words")

    def _get_edits(self, word):
        """Generates all possible corrections 1 edit away"""
        letters = "abcdefghijklmnopqrstuvwxyz'"
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def _known(self, words):
        """Returns subset of words that appear in our vocabulary"""
        return set(w for w in words if w in self.words_db)

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

    def ai_correct_sentence(self, sentence):
        """Corrects spelling using statistical methods (edit distance + frequency)"""
        words = sentence.split()
        corrected_words = []
        
        for word in words:
            # Strip punctuation for checking
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            # Correct the word
            corrected = self.correct_word(clean_word)
            corrected_words.append(corrected + punctuation)
        
        return " ".join(corrected_words)
