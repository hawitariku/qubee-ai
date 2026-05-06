import re
import collections
from transformers import AutoModelForMaskedLM, AutoTokenizer

class AfaanOromoSpellChecker:
    def __init__(self, corpus_path=None):
        self.words_db = collections.Counter()
        
        # 1. Load the AI Model (AfriBERTa is trained on Afaan Oromo)
        print("Loading AI Model (AfriBERTa)... Please wait.")
        try:
            # Load model and tokenizer separately to avoid fast tokenizer issues
            self.model = AutoModelForMaskedLM.from_pretrained("castorini/afriberta_small")
            self.tokenizer = AutoTokenizer.from_pretrained("castorini/afriberta_small")
            self.model_loaded = True
            print("✅ AI Model loaded successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not load AI model: {e}")
            print("   Continuing with statistical method only...")
            self.model_loaded = False
        
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

    def train_from_file(self, path):
        print(f"Training from corpus: {path}")
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
        
        # Generate candidates
        candidates = self._known([word_lower]) or \
                    self._known(self._get_edits(word_lower)) or \
                    [word_lower]
        
        # Return most frequent candidate
        best = max(candidates, key=self.words_db.get)
        return best

    def ai_correct_sentence(self, sentence):
        """Uses AI + statistical methods to correct spelling"""
        words = sentence.split()
        corrected_words = []
        
        for word in words:
            # Strip punctuation for checking
            clean_word = re.sub(r'[^\w\']', '', word)
            punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            # First try statistical correction
            stat_corrected = self.correct_word(clean_word)
            
            # If we have AI model and word was corrected, use AI for context
            if self.model_loaded and stat_corrected != clean_word.lower():
                try:
                    # Use AI to verify the correction fits context
                    masked_sentence = sentence.replace(clean_word, "[MASK]")
                    inputs = self.tokenizer(masked_sentence, return_tensors="pt", truncation=True, max_length=512)
                    
                    with inputs:
                        outputs = self.model(**inputs)
                    
                    # Get top predictions
                    mask_token_index = (inputs.input_ids == self.tokenizer.mask_token_id).nonzero(as_tuple=True)[1][0].item()
                    mask_logits = outputs.logits[0, mask_token_index]
                    top_k = 5
                    top_indices = mask_logits.topk(top_k).indices.tolist()
                    
                    # Check if our statistical correction is in top AI predictions
                    predicted_tokens = self.tokenizer.convert_ids_to_tokens(top_indices)
                    if stat_corrected in predicted_tokens:
                        corrected_words.append(stat_corrected + punctuation)
                    else:
                        # Use AI's top prediction
                        corrected_words.append(predicted_tokens[0] + punctuation)
                except Exception as e:
                    # Fallback to statistical correction
                    corrected_words.append(stat_corrected + punctuation)
            else:
                corrected_words.append(stat_corrected + punctuation)
        
        return " ".join(corrected_words)
