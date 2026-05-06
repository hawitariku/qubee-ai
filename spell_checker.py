import re
import collections
from transformers import pipeline

class AfaanOromoSpellChecker:
    def __init__(self, corpus_path=None):
        self.words_db = collections.Counter()
        
        # 1. Load the AI Model (AfriBERTa is trained on Afaan Oromo)
        print("Loading AI Model (AfriBERTa)... Please wait.")
        self.ai_filler = pipeline("fill-mask", model="castorini/afriberta_small", use_fast=False)
        
        # 2. Train the frequency dictionary
        if corpus_path:
            self.train_from_file(corpus_path)
        else:
            # Small sample for demonstration
            sample_text = "Ani bishaan dhuguu fedha. Inni gara mana deeme. Isheen barattuu dha."
            self.train_from_text(sample_text)

    def train_from_text(self, text):
        # Afaan Oromo includes ' (hudhaa). We keep letters and the apostrophe.
        words = re.findall(r"[a-z']+", text.lower())
        for word in words:
            self.words_db[word] += 1

    def train_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.train_from_text(f.read())

    def _get_edits(self, word):
        """Generates all possible corrections 1 edit away (deletions, swaps, etc.)"""
        letters    = "abcdefghijklmnopqrstuvwxyz'"
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def get_candidates(self, word):
        """Finds likely candidates for a misspelled word."""
        # 1. If word is correct, return it
        if word in self.words_db:
            return [word]
        
        # 2. Get words 1 or 2 edits away
        suggestions = self._get_edits(word)
        known_suggestions = [w for w in suggestions if w in self.words_db]
        
        # If no 1-edit suggestions, try 2-edits (slower but more accurate)
        if not known_suggestions:
            suggestions_2 = set(e2 for e1 in suggestions for e2 in self._get_edits(e1))
            known_suggestions = [w for w in suggestions_2 if w in self.words_db]
        
        # Sort by frequency
        return sorted(known_suggestions, key=lambda w: self.words_db[w], reverse=True)[:5]

    def ai_correct_sentence(self, sentence):
        """Uses AI to suggest the best word based on sentence context."""
        words = sentence.lower().split()
        corrected_sentence = []

        for i, word in enumerate(words):
            # Clean word for checking
            clean_word = re.sub(r"[^a-z']", "", word)
            
            if clean_word not in self.words_db and clean_word != "":
                print(f"\nDetected error: '{clean_word}'")
                candidates = self.get_candidates(clean_word)
                
                if not candidates:
                    corrected_sentence.append(word)
                    continue

                # Use AI to pick the best candidate
                # We replace the error with <mask> and ask the AI to rank candidates
                masked_sentence = " ".join(words[:i] + ["<mask>"] + words[i+1:])
                try:
                    # AI predictions for the mask
                    predictions = self.ai_filler(masked_sentence)
                    ai_words = [p['token_str'].strip().lower() for p in predictions]
                    
                    # Pick the candidate that the AI likes most
                    best_match = None
                    for ai_w in ai_words:
                        if ai_w in candidates:
                            best_match = ai_w
                            break
                    
                    # If AI isn't sure, pick the most frequent word from dictionary
                    chosen = best_match if best_match else candidates[0]
                    print(f"AI Suggestion: {chosen}")
                    corrected_sentence.append(chosen)
                    
                except Exception:
                    # Fallback to dictionary
                    corrected_sentence.append(candidates[0])
            else:
                corrected_sentence.append(word)

        return " ".join(corrected_sentence)

# --- EXECUTION ---
if __name__ == "__main__":
    # Create the checker
    checker = AfaanOromoSpellChecker()

    # Add some common Oromo words to dictionary for testing
    # In a real app, you would load a huge file here.
    checker.train_from_text("""
        ani bishaan dhuguu fedha natti tola kootu deemi mana 
        barumsaa deeme isheen barattuu jabaadha 
    """)

    # Test sentence with a typo: "bishaan" misspelled as "bishaan" (extra 'a') 
    # and "fedha" misspelled as "fedh"
    test_input = "ani bishaan dhuguu fedh"
    
    print(f"\nOriginal: {test_input}")
    result = checker.ai_correct_sentence(test_input)
    print(f"Final Corrected: {result}")
