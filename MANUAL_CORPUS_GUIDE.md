# 📖 Manual Bible Text Collection Guide

## Problem
The ebible.org website blocks automated downloads (returns 404 errors).

## Solution: Manual Copy-Paste Method

### Step-by-Step Instructions

#### Option 1: Copy from Web Browser (Easiest!)

1. **Open browser and go to:**
   ```
   https://ebible.org/gaz/
   ```

2. **Navigate to any book:**
   - Click on "Matthew" (Matayosii)
   - Or any other New Testament book

3. **Select all text:**
   - Press `Ctrl + A` (select all)
   - Press `Ctrl + C` (copy)

4. **Paste into file:**
   - Open `oromo_corpus.txt`
   - Scroll to bottom
   - Press `Ctrl + V` (paste)
   - Save file

5. **Repeat for more books** (optional)

---

#### Option 2: Use Wikipedia Afaan Oromo

**URL:** https://om.wikipedia.org/

**Steps:**
1. Go to Wikipedia Afaan Oromo
2. Browse articles on topics you like
3. Copy interesting paragraphs
4. Paste into `oromo_corpus.txt`
5. Save

**Benefits:**
- Modern vocabulary
- Various topics (science, history, culture)
- No download restrictions

---

#### Option 3: Use OMN News Website

**URL:** https://www.omn.gov.et/

**Steps:**
1. Visit OMN news site
2. Read articles in Afaan Oromo
3. Copy article text
4. Paste into corpus file
5. Save

**Benefits:**
- Current events vocabulary
- Modern language usage
- Professional journalism quality

---

### Quick Corpus Expansion Template

Create a new file called `add_to_corpus.txt`:

```
# Add your collected texts here
# One sentence per line works best

Inni gara mana barumsaa deeme
Isheen bishaan dhuguu fedha
Yesuus dubbate waa'ee mootummaa waaqayyoo
...

(Paste copied Bible verses or articles here)
```

Then merge with main corpus:

```bash
# Windows PowerShell
Get-Content add_to_corpus.txt, oromo_corpus.txt | Set-Content oromo_corpus_new.txt
Move-Item oromo_corpus_new.txt oromo_corpus.txt -Force
```

---

### Sample Texts to Get Started

Here are some authentic Afaan Oromo sentences you can use right now:

```
Ani bishaan dhuguu fedha
Inni gara mana deeme
Isheen barattuu dha
Natti tola kootu
Deemi mana barumsaa
Inni barataa dha
Isheen ogeessa dha
Afaan Oromoo baradhaa
Gara mana kootti deemi
Bishaan qulqulluu dhugi
Nyaata gaarii nyaadhu
Barumsaan bu'ura jireenyaa dha
Hojiin jireenya ni fooyyessa
Nagayaan jiraadhaa
Wal jaaladhaa
Waaqayyo nagaa kenna
Yesuus Kristos fayyisaa dha
Ruhni Qulqulluun nu haa gargaaru
Kitaabni Qulqulluun jecha Waaqayyoo dha
Imaanaa qabaadhu
Jaalalli Waaqayyoo guddaa dha
```

**Add these to your `oromo_corpus.txt` file immediately!**

---

### How Much Text Do You Need?

| Amount | Words Added | Impact | Time Required |
|--------|-------------|---------|---------------|
| **Quick** | ~500 words | Basic improvement | 5 minutes |
| **Good** | ~2,000 words | Noticeable improvement | 20 minutes |
| **Excellent** | ~5,000+ words | Major improvement | 1 hour |
| **Professional** | ~10,000+ words | Best results | 2-3 hours |

---

### Testing Your Expanded Corpus

After adding text:

1. **Restart web server:**
   ```bash
   # Stop current server (Ctrl+C)
   C:\Python312\python.exe main.py
   ```

2. **Test with new vocabulary:**
   - Type sentences using words you added
   - Check if corrections improve
   - Compare before/after results

---

### Pro Tips

✅ **Do:**
- Add diverse topics (religion, science, daily life)
- Include proper names (people, places)
- Mix simple and complex sentences
- Keep original formatting minimal

❌ **Don't:**
- Add duplicate content
- Include non-Oromo text
- Add HTML/formatting codes
- Forget to backup original file

---

### Backup Strategy

Before making changes:

```bash
# Create backup
Copy-Item oromo_corpus.txt oromo_corpus_backup.txt
```

If something goes wrong:

```bash
# Restore backup
Copy-Item oromo_corpus_backup.txt oromo_corpus.txt -Force
```

---

### Next Steps

1. **Right now:** Add the sample sentences above
2. **Today:** Copy 1-2 Bible chapters manually
3. **This week:** Expand with Wikipedia articles
4. **Ongoing:** Add new words as you find them

---

**Remember:** Quality matters more than quantity! 
Better to have 1000 good sentences than 10,000 messy ones.
