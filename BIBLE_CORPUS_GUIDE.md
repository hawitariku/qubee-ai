# 📖 Using Bible Texts from ebible.org

## What You'll Get

**Authentic Afaan Oromo Bible texts will:**
- ✅ Expand vocabulary by 10x-50x
- ✅ Improve spelling suggestions
- ✅ Add proper grammar patterns
- ✅ Include historical/cultural terms
- ✅ Provide diverse sentence structures

---

## 🎯 How It Works (User Flow)

```
Step 1: Install PDF library
   ↓
Step 2: Run download script
   ↓
Step 3: Wait for downloads (5-10 min)
   ↓
Step 4: Script automatically updates corpus
   ↓
Step 5: Restart web server
   ↓
Step 6: Test with improved spell checker!
```

---

## 📋 Step-by-Step Instructions

### Step 1: Install PyPDF2 Library ⏱️ 1 minute

**In terminal/PowerShell:**
```bash
C:\Python312\python.exe -m pip install PyPDF2 requests
```

**What this does:**
- `PyPDF2` - Extracts text from PDF files
- `requests` - Downloads files from internet

---

### Step 2: Run the Download Script ⏱️ 5-10 minutes

**Command:**
```bash
C:\Python312\python.exe download_bible_corpus.py
```

**What happens:**
1. Script connects to `https://ebible.org/pdf/gaz/`
2. Downloads first 5 New Testament books:
   - MAT (Matthew)
   - MRK (Mark)
   - LUK (Luke)
   - JHN (John)
   - ACT (Acts)
3. Extracts text from each PDF
4. Cleans and filters the text
5. Merges with your existing corpus
6. Creates backup of original

**Progress indicators:**
```
📖 Afaan Oromo Bible Corpus Expander
============================================================

Downloading MAT...
✓ Downloaded MAT
✓ Processed MAT (45,234 characters)

Downloading MRK...
✓ Downloaded MRK
✓ Processed MRK (32,156 characters)

...

✅ Successfully processed 5 books

💾 Saved to: oromo_bible_corpus.txt
📊 Total size: 187,456 characters

🔄 Updating main corpus...
✓ Backed up original to: oromo_corpus.txt.bak
✓ Merged Bible corpus with existing corpus
📊 New total size: 187,521 characters

============================================================
✨ DONE!
============================================================
```

---

### Step 3: Restart Your Web Server ⏱️ 2-5 seconds

**Stop current server:**
- Press `Ctrl + C` in terminal

**Start new server:**
```bash
C:\Python312\python.exe main.py
```

**Why restart?**
- Server loads corpus at startup
- New words need to be indexed
- AI model uses expanded vocabulary

---

### Step 4: Test the Improved Spell Checker! ⏱️ Instant

**Open browser:** `http://localhost:5000`

**Try these test sentences:**

| Sentence Type | Example | Expected Result |
|---------------|---------|-----------------|
| **Bible verse** | `Yesuus deeme gara galilaa` | Better context understanding |
| **Names** | `Petros akkas jedhe` | Recognizes biblical names |
| **Complex sentences** | `Inni dubbate waa'ee mootummaa waaqayyoo` | Handles theological terms |

---

## 📊 Before vs After Comparison

### Before (Small Corpus)

**Vocabulary size:** ~100 words  
**Example input:** `Inni deeme mana kiristaanaa`  
**Result:** May not recognize "kiristaanaa"

### After (Bible Corpus)

**Vocabulary size:** ~10,000+ words  
**Same input:** `Inni deeme mana kiristaanaa`  
**Result:** Recognizes all words, better suggestions!

---

## 🎨 UI Button-to-Feature Mapping

After expansion, your interface works the same but with better results:

| UI Element | What It Does | Improvement After Expansion |
|------------|--------------|----------------------------|
| **Text Area** | Type text | Now recognizes more words |
| **🔍 Check Spelling** | Submit for correction | AI has larger vocabulary to choose from |
| **Yellow Box** | Shows original | Same display |
| **Green Box** | Shows corrected | More accurate corrections! |

---

## 📥 What Gets Downloaded

**First run (5 books):**
- Matthew (GAZMAT.pdf) - ~2 MB
- Mark (GAZMRK.pdf) - ~1 MB
- Luke (GAZLUK.pdf) - ~2 MB
- John (GAZJHN.pdf) - ~1.5 MB
- Acts (GAZACT.pdf) - ~1.5 MB

**Total:** ~8 MB of PDFs → ~200KB of text

**Full New Testament (optional):**
- 27 books total
- ~30-40 MB of PDFs
- ~1-2 MB of text

---

## 🔧 Advanced Options

### Option A: Download Full New Testament

**Edit file:** `download_bible_corpus.py`

**Change line 30 from:**
```python
for book_code in BIBLE_BOOKS[:5]:  # First 5 books
```

**To:**
```python
for book_code in BIBLE_BOOKS:  # All New Testament
```

**Then run again:**
```bash
C:\Python312\python.exe download_bible_corpus.py
```

---

### Option B: Download Old Testament Too

**Edit file:** `download_bible_corpus.py`

**Uncomment lines 40-49** (remove the `#` symbols):
```python
# OLD TESTAMENT
"GEN", "EXO", "LEV", "NUM", "DEU", 
"JOS", "JDG", "RUT", "1SA", "2SA",
# ... etc
```

**Warning:** This will download 39 more books (~100 MB, 30+ minutes)

---

### Option C: Manual Text Addition

If you prefer manual control:

1. **Download PDFs yourself:**
   - Go to https://ebible.org/pdf/gaz/
   - Click desired books
   - Save to `temp_pdfs/` folder

2. **Extract text manually:**
   ```bash
   C:\Python312\python.exe download_bible_corpus.py
   ```

3. **Or just copy-paste verses** into `oromo_corpus.txt`

---

## 💡 Best Practices

### Do's ✅
- Start with just 5 books (fast testing)
- Keep the backup file (`.bak`)
- Test after each expansion
- Monitor file sizes

### Don'ts ❌
- Don't download everything at once (slow)
- Don't delete the backup
- Don't expect instant perfection (AI needs training)
- Don't mix different translations

---

## 🐛 Troubleshooting

### Issue: "PyPDF2 not found"
**Solution:**
```bash
C:\Python312\python.exe -m pip install PyPDF2
```

### Issue: "Failed to download"
**Causes:**
- No internet connection
- Website temporarily down
- Firewall blocking

**Solutions:**
- Check internet
- Try again later
- Manually download from website

### Issue: "No text extracted"
**Possible causes:**
- PDF is image-based (not text)
- Corrupted download
- PyPDF2 compatibility issue

**Solutions:**
- Re-download the PDF
- Try different book
- Use manual copy-paste method

---

## 📈 Expected Results

### Vocabulary Growth

| Stage | Words | Characters | Source |
|-------|-------|------------|--------|
| Original | ~100 | ~500 | Your sample |
| + 5 Bible books | ~2,000 | ~200,000 | New Testament start |
| + Full NT | ~5,000 | ~500,000 | All 27 books |
| + Full Bible | ~10,000+ | ~1,000,000+ | Complete |

### Correction Quality Improvement

**Test sentence:** `"Inni lola godhate"`

| Corpus Size | Result | Confidence |
|-------------|--------|------------|
| Original (100 words) | May fail | Low |
| + 5 books | ✓ Correct | Medium |
| + Full NT | ✓ Correct + alternatives | High |

---

## 🎓 Understanding the Process

### How PDF Extraction Works

```
PDF File (ebible.org)
    ↓
Downloaded to temp_pdfs/
    ↓
PyPDF2 reads binary data
    ↓
Extracts text layer
    ↓
Cleaner removes formatting
    ↓
Filter keeps Oromo sentences
    ↓
Merged into corpus
    ↓
Spell checker learns new words
```

### Why Bible Texts?

1. **Professional translation** - Expert linguists
2. **Consistent orthography** - Standardized spelling
3. **Rich vocabulary** - Diverse topics
4. **Proper grammar** - Well-edited
5. **Cultural relevance** - Contextual examples
6. **Public domain** - Free to use

---

## 🌐 Alternative Sources

If you want more variety:

### Other Online Resources:

1. **Wikipedia Afaan Oromo**
   - URL: https://om.wikipedia.org/
   - Topics: Science, history, culture
   
2. **OMN News**
   - URL: https://www.omn.gov.et/
   - Modern vocabulary, news

3. **Leipzig Corpora**
   - URL: https://corpora.uni-leipzig.de/
   - Already formatted for NLP

---

## ✨ Quick Start Command

**Everything in one line:**
```bash
C:\Python312\python.exe -m pip install PyPDF2 && C:\Python312\python.exe download_bible_corpus.py
```

This installs dependencies AND runs the script!

---

## 📞 Support

**Files created:**
- `download_bible_corpus.py` - Main script
- `oromo_bible_corpus.txt` - Extracted text
- `oromo_corpus.txt` - Your expanded corpus
- `oromo_corpus.txt.bak` - Backup of original

**Next step:** Run the script and watch your spell checker get smarter!

---

**Ready to expand? Let's download! 📖✨**
