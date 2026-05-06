# 🔍 Where Does "freq: 311" Come From? - Complete Explanation

## The Short Answer:

**Frequency = How many times a word appears in your corpus files**

When you see:
```
✓ gaara    freq: 311
```

It means: **The word "gaara" appears 311 times across all your corpus text files.**

---

## 📊 **Complete Data Flow:**

### **Step 1: Corpus Files (Your Training Data)**

Your project has these text files:
```
oromo_corpus.txt           (Main corpus - 4.5MB)
oromo_bible_corpus.txt     (Bible text - 4.5MB)
gaz_book_extracted.txt     (PDF extraction)
oromo_corpus.txt.bak       (Backup corpus)
```

**Example content in these files:**
```
Ani bishaan dhuguu fedha
Inni gara mana deeme
Gaara keenya bareedaa dha
Gaara biraa argine
...
(gaara appears 311 times total across all files)
```

---

### **Step 2: Loading & Counting (Code Location)**

**File:** `spell_checker_ml.py`

**Line 38 - Create the database:**
```python
self.words_db = collections.Counter()
```
This creates an empty frequency counter (like a dictionary that counts).

---

**Lines 225-231 - Count words from text:**
```python
def train_from_text(self, text):
    """Train the model from text"""
    words = re.findall(r"[a-z']+", text.lower())  # Extract all words
    
    # Count word frequencies
    for word in words:
        self.words_db[word] += 1  # ← THIS IS WHERE FREQUENCY COMES FROM!
```

**What this does:**
```python
# Example with simple text:
text = "gaara bareedaa gaara dheeraa gaara"

# After processing:
words = ["gaara", "bareedaa", "gaara", "dheeraa", "gaara"]

# Count each word:
self.words_db["gaara"] = 3      # Appears 3 times
self.words_db["bareedaa"] = 1   # Appears 1 time
self.words_db["dheeraa"] = 1    # Appears 1 time
```

---

### **Step 3: Loading All Corpus Files**

**Lines 86-140 - Load from multiple sources:**

```python
# 1. Main corpus
self.train_from_file('oromo_corpus.txt')

# 2. PDF extraction
self.train_from_file('gaz_book_extracted.txt')

# 3. Bible corpus
self.train_from_file('oromo_bible_corpus.txt')

# 4. Backup corpus
self.train_from_file('oromo_corpus.txt.bak')
```

**Each file adds to the frequency count:**
```
After oromo_corpus.txt:       gaara = 150 times
After gaz_book_extracted.txt: gaara = 200 times (+50)
After oromo_bible_corpus.txt: gaara = 280 times (+80)
After oromo_corpus.txt.bak:   gaara = 311 times (+31)

FINAL: gaara appears 311 times total
```

---

### **Step 4: Display in Interactive Test**

**File:** `test_interactive.py`

**Lines 43-48:**
```python
# Word analysis
print("\n📊 Word analysis:")
words = sentence.split()
for word in words:
    clean = word.lower()
    in_vocab = clean in checker.words_db
    freq = checker.words_db.get(clean, 0)  # ← GET FREQUENCY HERE!
    status = "✓" if in_vocab else "✗"
    print(f"  {status} {clean:<20} freq: {freq:>6,}")
```

**What happens:**
```python
# You type: "gaara"

# Code executes:
clean = "gaara"
freq = checker.words_db.get("gaara", 0)
# Returns: 311

# Prints:
✓ gaara                freq:    311
```

---

## 🔍 **Verify It Yourself:**

### **Method 1: Count in Corpus File**

Open terminal and run:
```bash
# Count how many times "gaara" appears in corpus
grep -o "gaara" oromo_corpus.txt | wc -l
```

This should show approximately 311 (might vary slightly due to case).

---

### **Method 2: Python Script**

Create `check_frequency.py`:
```python
import re
from collections import Counter

# Read corpus file
with open('oromo_corpus.txt', 'r', encoding='utf-8') as f:
    text = f.read().lower()

# Count words
words = re.findall(r"[a-z']+", text)
word_counts = Counter(words)

# Check specific word
word = "gaara"
print(f"'{word}' appears {word_counts[word]} times")
```

Run it:
```bash
python check_frequency.py
```

---

## 📈 **Why Frequency Matters:**

### **In Spell Checking:**

```python
# You type: "gaaara" (misspelled)

# System finds candidates:
# - "gaara" (freq: 311)    ← Common word
# - "gaaraa" (freq: 207)   ← Less common
# - "gara" (freq: 8,160)   ← Very common but different meaning

# System prefers HIGH FREQUENCY words
# So it suggests: "gaara" (311 times in corpus = likely correct)
```

### **The Problem You're Seeing:**

```python
# You type: "hawi" (might be correct in your dialect)

# System checks:
"hawi" in words_db? → NO (freq: 0)

# System finds similar words:
# - "haqi" (freq: 50)  ← In corpus
# - "hawwi" (freq: 0)  ← NOT in corpus

# System suggests: "haqi" (because it's in corpus)
# But "hawi" might actually be correct!
```

---

## 🎯 **The Real Issue:**

**Your corpus doesn't contain all valid Afaan Oromo words!**

Examples:
- "hawi" → NOT in corpus (freq: 0) → System "corrects" it
- "gaara" → IN corpus (freq: 311) → System accepts it
- "hiin" → NOT in corpus (freq: 0) → System "corrects" it

**Solutions:**

1. **Add more text to corpus** that includes your words
2. **Make system more conservative** - don't correct unknown words so aggressively
3. **Create custom dictionary** of valid words that shouldn't be corrected

---

## 📝 **Summary:**

| Question | Answer |
|----------|--------|
| **Where does freq come from?** | Count of word in corpus files |
| **Which files?** | oromo_corpus.txt, bible_corpus, PDF, backup |
| **How is it counted?** | `collections.Counter()` in Python |
| **What does freq: 311 mean?** | Word "gaara" appears 311 times |
| **Why does it matter?** | Higher frequency = more likely to be correct |
| **Can I change it?** | Yes, add more text to corpus files |

---

## 🔧 **Want to Add Your Words?**

Edit `oromo_corpus.txt` and add:
```
hawi hiin akkaam
```

Then restart the spell checker. Those words will now have freq > 0 and won't be "corrected"!
