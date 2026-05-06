# 🎯 QUICK START - 3 Simple Steps

## ⚡ How to Use (User Flow)

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Install (One time only)                         │
│ └─> Run: pip install -r requirements.txt                │
│ └─> Wait: 5-10 minutes                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Start Server (Every session)                    │
│ └─> Double-click: start_server.bat                      │
│    OR run: python main.py                               │
│ └─> Wait: First time 5-15 min (model download)          │
│ └─> Next times: 2-5 seconds                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Open Browser                                    │
│ └─> Go to: http://localhost:5000                        │
│ └─> Type text and click "Check Spelling"                │
│ └─> See corrected results instantly!                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 STEP 1: Install Dependencies (One Time)

### Option A: Using Terminal
```bash
cd c:\Users\hp\Desktop\app7
pip install -r requirements.txt
```

### Option B: Using PowerShell
Right-click in the `app7` folder → "Open in Terminal" → Run:
```bash
pip install -r requirements.txt
```

**What happens:**
- Downloads ~2GB of Python packages
- Takes 5-10 minutes depending on internet speed
- Installs: transformers, fastapi, uvicorn, torch, numpy, scipy, etc.

**You'll know it's done when you see:**
```
Successfully installed fastapi-xxx uvicorn-xxx transformers-xxx ...
```

---

## 🚀 STEP 2: Start the Web Server

### Method 1: Double-click (Easiest!)
```
📁 Navigate to: c:\Users\hp\Desktop\app7
🖱️ Double-click: start_server.bat
```

### Method 2: Command Line
```bash
cd c:\Users\hp\Desktop\app7
python main.py
```

**First Time Startup Messages:**
```
🔄 Loading AI Model (AfriBERTa)... This happens only once.
[Downloading: 500MB...] ████████████░░░░░░░░ 65%  ETA: 3:45
✅ Model loaded successfully!

🚀 Starting Afaan Oromo Spell Checker Web Server...
📍 Open your browser and go to: http://localhost:5000
💡 Press Ctrl+C to stop the server
```

**Subsequent Startups (Instant!):**
```
✅ Model loaded successfully!

🚀 Starting Afaan Oromo Spell Checker Web Server...
📍 Open your browser and go to: http://localhost:5000
💡 Press Ctrl+C to stop the server
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**Keep this terminal/PowerShell window open while using the web interface!**

---

## 🌐 STEP 3: Open Your Browser

### Access the Web Interface

1. **Open any browser:**
   - Google Chrome (recommended)
   - Mozilla Firefox
   - Microsoft Edge
   - Safari

2. **Type in address bar:**
   ```
   http://localhost:5000
   ```

3. **You'll see:**
   - Purple gradient background
   - Large text area
   - "🔍 Check Spelling" button
   - Feature grid at bottom

---

## ✨ Using the Web Interface

### Test It Out

**Step-by-step:**

1. **In the text area, type:**
   ```
   Ani bishaan dhuguu fedh
   ```

2. **Click:** 🔍 **Check Spelling** button

3. **Wait 2-3 seconds**

4. **See results appear:**
   ```
   ✅ Corrected Text
   
   Original:
   Ani bishaan dhuguu fedh
   
   Corrected:
   ani bishaan dhuguu fedha
   ```

### Try More Examples

| What to Type | Expected Result |
|--------------|-----------------|
| `Inni gara mana deeme` | `inni gara mana deeme` |
| `Isheen barattuu dha` | `isheen barattuu dha` |
| `Natti tola kootu` | `natti tola kootu` |

---

## 🎨 What You'll See (Interface Tour)

### Top Section
```
┌──────────────────────────────────────┐
│ 🔤 Afaan Oromo Spell Checker         │
│ AI-powered spelling correction       │
└──────────────────────────────────────┘
```

### Input Area
```
┌──────────────────────────────────────┐
│ [Large text box - type here]         │
│                                      │
│ Placeholder shows examples           │
└──────────────────────────────────────┘
        [🔍 Check Spelling]
```

### Results Area (after clicking)
```
┌──────────────────────────────────────┐
│ ✅ Corrected Text                    │
├──────────────────────────────────────┤
│ Original:                            │
│ Ani bishaan dhuguu fedh              │
├──────────────────────────────────────┤
│ ani bishaan dhuguu fedha             │
└──────────────────────────────────────┘
```

### Features Section (bottom)
```
✨ Features
🤖 AI-Powered      ⚡ Fast Correction
🎯 Context Aware   📝 Hudhaa Support
```

---

## 🛑 Stopping the Server

When you're done using it:

### If using .bat file:
- Close the command prompt window

### If using terminal:
- Press `Ctrl + C`
- Confirm if asked

---

## ⏱️ Time Expectations

| Action | First Time | Later Times |
|--------|------------|-------------|
| Install dependencies | 5-10 min | N/A |
| Start server | 5-15 min* | 2-5 sec |
| Load webpage | <1 sec | <1 sec |
| Check spelling | 2-5 sec | 2-5 sec |

*First time only - downloading AfriBERTa model (~500MB)

---

## 🎯 Quick Reference Card

### Commands You Need

```bash
# Install (one time)
pip install -r requirements.txt

# Start server (two ways)
python main.py
# OR double-click: start_server.bat

# Stop server
Ctrl + C
```

### URLs to Remember

```
Local access: http://localhost:5000
Network access: http://YOUR_IP:5000
```

---

## ❓ Troubleshooting

### "Port already in use"
**Solution:** Another app is using port 5000
- Close other servers
- Or change port in `main.py` line 47

### "Module not found"
**Solution:** Dependencies not installed
```bash
pip install -r requirements.txt
```

### Page won't load
**Solution:** Server not running
- Check terminal for errors
- Make sure you see "Uvicorn running on..."
- Refresh browser page

### Very slow first startup
**Normal!** Model is downloading (~500MB)
- Be patient (5-15 minutes)
- Don't close the window
- Progress bar will show download status

---

## ✅ Success Checklist

Before you start using it:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Terminal/PowerShell opened in `app7` folder
- [ ] Server started (`python main.py` or `start_server.bat`)
- [ ] Message "Uvicorn running on http://0.0.0.0:5000" appears
- [ ] Browser opened to `http://localhost:5000`
- [ ] Web page loads with purple gradient

**If all checked → You're ready! Start typing and checking spelling! 🎉**

---

## 📞 Need Help?

Check the full README.md for detailed documentation.

**Happy spell checking! 🎊**
