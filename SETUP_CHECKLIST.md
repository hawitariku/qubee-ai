# ✅ Setup Checklist - Afaan Oromo Spell Checker Web Interface

## 📋 Pre-Installation Checklist

Before you start, make sure you have:

- [ ] Python 3.8+ installed
- [ ] Internet connection (for first-time setup)
- [ ] About 2GB free disk space
- [ ] 10-15 minutes for initial setup
- [ ] A web browser (Chrome, Firefox, Edge, etc.)

---

## 🎯 Installation Steps

### Step 1: Install Dependencies ⏱️ 5-10 minutes

```bash
cd c:\Users\hp\Desktop\app7
pip install -r requirements.txt
```

**Progress indicators:**
- [ ] Command runs successfully
- [ ] Download progress bars appear
- [ ] "Successfully installed..." message shows
- [ ] No error messages

**What's being installed:**
- [ ] transformers (AI library)
- [ ] fastapi (web framework)
- [ ] uvicorn (server)
- [ ] torch (ML backend)
- [ ] numpy, scipy, scikit-learn
- [ ] jinja2, python-multipart

---

### Step 2: Start the Server ⏱️ First time: 5-15 min | Later: 2-5 sec

**Option A: Using batch file (Recommended)**
```
📁 Navigate to: c:\Users\hp\Desktop\app7
🖱️ Double-click: start_server.bat
```

**Option B: Using terminal**
```bash
cd c:\Users\hp\Desktop\app7
python main.py
```

**First run - Watch for these messages:**
- [ ] `🔄 Loading AI Model (AfriBERTa)...` appears
- [ ] Download progress bar shows (if first time)
- [ ] `✅ Model loaded successfully!` appears
- [ ] `🚀 Starting Afaan Oromo Spell Checker Web Server...` appears
- [ ] `📍 Open your browser and go to: http://localhost:5000` appears
- [ ] `INFO: Uvicorn running on http://0.0.0.0:5000` appears

**⚠️ DO NOT close this window yet!**

---

### Step 3: Open Browser ⏱️ < 1 minute

- [ ] Open any web browser (Chrome recommended)
- [ ] Type in address bar: `http://localhost:5000`
- [ ] Press Enter

**Page should load with:**
- [ ] Purple gradient background visible
- [ ] Title "🔤 Afaan Oromo Spell Checker" at top
- [ ] Large text area in the middle
- [ ] "🔍 Check Spelling" button below text area
- [ ] Feature grid at bottom (4 boxes with icons)

---

## ✨ First Test

### Try Your First Spelling Check

- [ ] In the text area, type: `Ani bishaan dhuguu fedh`
- [ ] Click the "🔍 Check Spelling" button
- [ ] Wait 2-5 seconds
- [ ] Results appear below the button

**Expected results:**
- [ ] Yellow box shows: "Original: Ani bishaan dhuguu fedh"
- [ ] Green box shows: "ani bishaan dhuguu fedha"
- [ ] Green checkmark emoji ✅ visible
- [ ] No error messages

**Congratulations! It's working! 🎉**

---

## 🔧 Troubleshooting Checklist

### If Something Goes Wrong

**Problem: Terminal shows errors immediately**
- [ ] Check you're in correct folder: `c:\Users\hp\Desktop\app7`
- [ ] Verify all files exist (main.py, templates/, etc.)
- [ ] Run: `pip install -r requirements.txt` again

**Problem: "Module not found" error**
- [ ] Dependencies not installed properly
- [ ] Run: `pip install -r requirements.txt`
- [ ] Wait for completion
- [ ] Try starting server again

**Problem: Port already in use**
- [ ] Another program using port 5000
- [ ] Close other servers/terminals
- [ ] Or edit main.py line 47, change port to 8080

**Problem: Browser shows "Can't connect"**
- [ ] Check if server is running (terminal should show "Uvicorn running...")
- [ ] Verify URL is exactly: `http://localhost:5000`
- [ ] Try refreshing browser page (F5)
- [ ] Check firewall isn't blocking Python

**Problem: Very slow first startup (>20 minutes)**
- [ ] This can be normal (large model download)
- [ ] Check internet connection speed
- [ ] Don't close the terminal window
- [ ] Wait for download to complete
- [ ] Subsequent runs will be fast!

**Problem: Page loads but button doesn't work**
- [ ] Check browser console for errors (F12)
- [ ] Try different browser
- [ ] Clear browser cache
- [ ] Restart server (Ctrl+C, then run again)

---

## 📊 File Structure Verification

Make sure all these files exist:

```
app7/
├── [✓] main.py                    (1.6 KB)
├── [✓] spell_checker.py           (5.2 KB)
├── [✓] oromo_corpus.txt          (0.3 KB)
├── [✓] requirements.txt          (0.1 KB)
├── [✓] start_server.bat          (0.2 KB)
├── [✓] README.md                 (6.3 KB)
├── [✓] QUICKSTART.md             (variable)
├── [✓] WEB_INTERFACE_GUIDE.md    (variable)
└── [✓] templates/
    └── [✓] index.html            (7.5 KB)
```

**To verify:**
```bash
dir c:\Users\hp\Desktop\app7
```

---

## 🎯 Usage Scenarios

### Scenario 1: Quick Personal Use

**Workflow:**
1. [ ] Double-click `start_server.bat`
2. [ ] Wait for "Uvicorn running..." message
3. [ ] Open `http://localhost:5000`
4. [ ] Type text, click button
5. [ ] Copy corrected text
6. [ ] Close terminal when done

**Time needed:** 1-2 minutes per session (after setup)

---

### Scenario 2: Testing Multiple Sentences

**Workflow:**
1. [ ] Start server
2. [ ] Open browser
3. [ ] Test sentence 1 → Check spelling
4. [ ] Review results
5. [ ] Clear text area
6. [ ] Test sentence 2 → Check spelling
7. [ ] Repeat as needed
8. [ ] Take notes of corrections

**Tip:** Keep terminal open for multiple tests

---

### Scenario 3: Sharing with Others (Network)

**Additional steps:**
1. [ ] Find your IP: `ipconfig` → Look for IPv4 Address
2. [ ] Share URL: `http://YOUR_IP:5000`
3. [ ] Ensure computer stays awake
4. [ ] Keep terminal/server running
5. [ ] Others on same WiFi can access

---

## 📈 Performance Benchmarks

After setup, expect these speeds:

| Action | Expected Time | Status |
|--------|---------------|--------|
| Server startup (cached) | 2-5 seconds | [ ] ✓ |
| Page load | < 1 second | [ ] ✓ |
| Spelling check (short) | 1-3 seconds | [ ] ✓ |
| Spelling check (long) | 3-5 seconds | [ ] ✓ |

If slower, check troubleshooting section.

---

## 🌟 Feature Verification

Test each feature works:

**Core Features:**
- [ ] Text input works (can type/paste)
- [ ] Button is clickable
- [ ] Results display after clicking
- [ ] Original text shown in yellow
- [ ] Corrected text shown in green

**Visual Features:**
- [ ] Purple gradient displays correctly
- [ ] Emoji icons show properly
- [ ] Feature grid at bottom visible
- [ ] Responsive on mobile (try resizing)

**AI Features:**
- [ ] Corrections are accurate
- [ ] Context-aware suggestions work
- [ ] Handles Hudhaa (apostrophe) correctly
- [ ] Processes full sentences

---

## 🎓 Learning Progress

As you use it, understand these concepts:

**Beginner:**
- [ ] Know how to start the server
- [ ] Can navigate to web interface
- [ ] Successfully test first sentence
- [ ] Understand color coding (yellow/green)

**Intermediate:**
- [ ] Understand what AfriBERTa does
- [ ] Know difference between CLI and web version
- [ ] Can troubleshoot common issues
- [ ] Understand data flow (frontend → backend → AI)

**Advanced:**
- [ ] Read and understand main.py code
- [ ] Can modify HTML/CSS styling
- [ ] Know how to change port/configuration
- [ ] Ready to customize or extend features

---

## 📝 Optional Enhancements (Future)

Consider these improvements later:

**Content:**
- [ ] Expand oromo_corpus.txt with more text
- [ ] Add example sentences to interface
- [ ] Create tutorial for other users

**Visual:**
- [ ] Change color theme
- [ ] Add logo or branding
- [ ] Customize fonts
- [ ] Add animations

**Features:**
- [ ] Add grammar checking
- [ ] Support multiple languages
- [ ] Export corrections to file
- [ ] User history/saved corrections

**Deployment:**
- [ ] Deploy to Hugging Face Spaces
- [ ] Set up custom domain
- [ ] Add user authentication
- [ ] Enable public access

---

## ✅ Final Success Criteria

You've successfully set up everything when:

**Technical:**
- [x] All files created in app7 folder
- [x] Dependencies installed without errors
- [x] Server starts successfully
- [x] Web interface accessible
- [x] Spelling corrections work

**User Experience:**
- [x] Can navigate to interface easily
- [x] Understand how to use it
- [x] See corrections appear quickly
- [x] No confusing errors or issues

**Understanding:**
- [x] Know what happens behind the scenes
- [x] Understand AI model role
- [x] Can explain to someone else
- [x] Comfortable troubleshooting

---

## 🎉 Completion Certificate

When all boxes are checked:

```
╔══════════════════════════════════════════════╗
║                                              ║
║     ✅ SETUP COMPLETE!                       ║
║                                              ║
║   You now have a fully functional            ║
║   AI-powered Afaan Oromo Spell Checker       ║
║   with a beautiful web interface!            ║
║                                              ║
║   Ready to use anytime at:                   ║
║   http://localhost:5000                      ║
║                                              ║
╚══════════════════════════════════════════════╝
```

---

## 📞 Next Resources

After completing setup:

1. **Read:** README.md for detailed documentation
2. **Review:** WEB_INTERFACE_GUIDE.md for visual tour
3. **Experiment:** Try different sentences
4. **Customize:** Modify colors/features
5. **Share:** Deploy online for others to use

---

**Start with Step 1 above. Good luck! 🚀**
