# Deployment Guide - Qubee AI to Render

## 🚀 Deploy to Render (Free Tier)

### **Step 1: Sign Up for Render**

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (use your hawitariku account)
4. Authorize Render to access your repositories

### **Step 2: Create New Web Service**

1. After logging in, click "New +" button (top right)
2. Select "Web Service"
3. Connect your GitHub repository:
   - Click "Connect account" if not connected
   - Find and select: **qubee-ai**
4. Click "Connect"

### **Step 3: Configure Service**

Fill in these settings:

**Basic Settings:**
- **Name**: `qubee-ai` (or any name you like)
- **Region**: Choose closest to Ethiopia (e.g., Frankfurt, Singapore)
- **Branch**: `main`
- **Root Directory**: (leave empty)

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select: **Free** (0.1 CPU, 512 MB RAM)

**Environment Variables:**
- Click "Add Environment Variable"
- Key: `PYTHON_VERSION`
- Value: `3.12.0`

### **Step 4: Deploy**

1. Click "Create Web Service" button at the bottom
2. Render will start building your app
3. Wait 5-10 minutes for:
   - Installing dependencies
   - Loading vocabulary (59K words)
   - Starting server

### **Step 5: Get Your URL**

After deployment succeeds:
- Your app will be at: `https://qubee-ai.onrender.com`
- Or: `https://qubee-ai-XXXX.onrender.com` (with random suffix)
- Copy this URL - you'll need it for AdSense!

### **Step 6: Test Your Deployed App**

1. Click the URL Render provides
2. Wait 30-60 seconds (free tier spins down when idle)
3. You should see your spell checker!
4. Test with: "akam jirta"
5. Should correct to: "akka jirta" with alternatives

---

## 🎯 Add Website to AdSense

Now that your app is deployed:

### **Step 1: Log in to AdSense**

1. Go to https://www.google.com/adsense
2. Log in with your Google account

### **Step 2: Add Your Site**

1. Click "Sites" in the left menu
2. Click "Add site"
3. Enter your Render URL: `https://qubee-ai.onrender.com`
4. Click "Save and continue"

### **Step 3: Add AdSense Code**

1. AdSense will give you a code snippet
2. Copy your Publisher ID: `ca-pub-XXXXXXXXXXXXXXXX`
3. We already added the code to your site!
4. Just replace the placeholder in `templates/index.html`:
   - Find: `ca-pub-XXXXXXXXXXXXXXXX`
   - Replace with: YOUR actual Publisher ID

### **Step 4: Verify Your Site**

1. AdSense will check if the code is on your site
2. Click "Request Review"
3. Wait 1-7 days for approval

---

## 📊 Expected Performance

### **Free Tier Limits:**
- ✅ 750 hours/month (enough for 24/7)
- ✅ 512 MB RAM (enough for your app)
- ✅ Spins down after 15 min of inactivity
- ✅ First request after spin-down takes 30-60 seconds

### **Upgrade to Paid ($7/month) for:**
- No spin-down (always fast)
- More RAM (1 GB)
- Better performance

---

## 🔧 Troubleshooting

### **Problem: Build Failed**

**Solution:**
- Check build logs in Render dashboard
- Make sure all files are committed to GitHub
- Verify `requirements.txt` is correct

### **Problem: App Crashes**

**Solution:**
- Check logs in Render dashboard
- Corpus files might be too large for free tier
- Consider reducing vocabulary size

### **Problem: Slow First Load**

**Solution:**
- This is normal for free tier (spins down when idle)
- Upgrade to paid tier ($7/month) for always-on
- Or use a "ping" service to keep it awake

### **Problem: Out of Memory**

**Solution:**
- Free tier has 512 MB RAM
- Your app uses ~400 MB with full vocabulary
- If it crashes, reduce `min_frequency` in `spell_checker_ml.py`:
  ```python
  self.optimize_vocabulary(min_frequency=10)  # Increase from 5 to 10
  ```

---

## 💰 Cost Breakdown

### **Free Tier (Render):**
- **Cost**: $0/month
- **Limits**: Spins down after 15 min idle
- **Good for**: Testing, low traffic (< 1,000 users/day)

### **Paid Tier (Render):**
- **Cost**: $7/month
- **Benefits**: Always on, faster, 1 GB RAM
- **Good for**: Production, high traffic (1,000+ users/day)

### **When to Upgrade:**
- When you have 500+ daily users
- When you're earning $20+/month from ads
- When slow first load annoys users

---

## 🎯 Next Steps After Deployment

1. ✅ **Test your deployed app**
2. ✅ **Add site to AdSense**
3. ✅ **Replace AdSense placeholder IDs**
4. ✅ **Wait for AdSense approval** (1-7 days)
5. ✅ **Start marketing** to get users
6. ✅ **Track earnings** in AdSense dashboard

---

## 📱 Alternative: Deploy to Railway

If Render doesn't work, try Railway:

1. Go to https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select: qubee-ai
5. Railway auto-detects Python and deploys
6. Your URL: `https://qubee-ai.up.railway.app`

**Railway Free Tier:**
- $5 credit/month (enough for ~500 hours)
- No spin-down
- Faster than Render free tier

---

## 🚀 You're Ready!

Your app is now:
- ✅ Deployed to the cloud
- ✅ Publicly accessible
- ✅ Ready for AdSense
- ✅ Ready to earn money!

**Good luck!** 🎉
