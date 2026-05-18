# Google AdSense Setup Guide for Qubee AI

## 🎯 Goal: Earn $15-60/month with 1,000 daily users

---

## **Step 1: Deploy Your App to the Cloud**

Before you can use AdSense, your app must be publicly accessible online.

### **Option A: Deploy to Render (Free)**
1. Go to https://render.com
2. Sign up with GitHub
3. Connect your repository: https://github.com/hawitariku/qubee-ai
4. Create new "Web Service"
5. Build command: `pip install -r requirements.txt`
6. Start command: `python main.py`
7. Your app will be at: `https://qubee-ai.onrender.com`

### **Option B: Deploy to Railway (Free)**
1. Go to https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select: qubee-ai
5. Your app will be at: `https://qubee-ai.up.railway.app`

### **Option C: Deploy to Heroku**
1. Go to https://heroku.com
2. Create new app
3. Connect GitHub repository
4. Deploy

---

## **Step 2: Sign Up for Google AdSense**

### **Requirements:**
- ✅ Your app must be deployed (have a public URL)
- ✅ Must have original content (you do!)
- ✅ Must comply with AdSense policies
- ✅ Must be 18+ years old

### **Sign Up Process:**
1. Go to https://www.google.com/adsense
2. Click "Get Started"
3. Enter your website URL (e.g., `https://qubee-ai.onrender.com`)
4. Fill in your details:
   - Name: Hawi Tariku
   - Country: Ethiopia
   - Email: your email
5. Accept terms and conditions
6. Submit application

### **Approval Time:**
- Usually: 1-7 days
- Sometimes: up to 2 weeks
- Google will review your site

---

## **Step 3: Add AdSense Code to Your App**

### **After Approval:**

1. **Get Your Publisher ID:**
   - Log in to AdSense
   - Go to "Account" → "Account Information"
   - Copy your Publisher ID: `ca-pub-XXXXXXXXXXXXXXXX`

2. **Update templates/index.html:**

Find this line (line 9):
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
```

Replace `ca-pub-XXXXXXXXXXXXXXXX` with YOUR actual Publisher ID.

3. **Get Ad Unit Codes:**
   - In AdSense dashboard, go to "Ads" → "By ad unit"
   - Click "Display ads"
   - Create 2 ad units:
     - **Top Banner**: Responsive, name it "Top Banner"
     - **Middle Banner**: Responsive, name it "Middle Banner"
   - Copy the `data-ad-slot` codes

4. **Update Ad Placements:**

Find these sections in `templates/index.html` and replace:

**Ad Placement 1 (line ~395):**
```html
data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"  ← Replace with YOUR ID
data-ad-slot="XXXXXXXXXX"  ← Replace with Top Banner slot ID
```

**Ad Placement 2 (line ~492):**
```html
data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"  ← Replace with YOUR ID
data-ad-slot="XXXXXXXXXX"  ← Replace with Middle Banner slot ID
```

5. **Commit and Deploy:**
```bash
git add templates/index.html
git commit -m "Add Google AdSense"
git push origin main
```

Your hosting platform will auto-deploy the changes.

---

## **Step 4: Verify Ads are Working**

1. Visit your deployed site
2. You should see ad spaces (may show blank initially)
3. Wait 10-30 minutes for ads to appear
4. **Don't click your own ads!** (Google will ban you)

---

## **Step 5: Track Your Earnings**

### **AdSense Dashboard:**
- Go to https://www.google.com/adsense
- View "Reports" to see:
  - Page views
  - Clicks
  - Earnings
  - CPM (earnings per 1,000 views)

### **Expected Timeline:**

**Month 1:**
- 100 daily users
- 3,000 monthly views
- Earnings: **$1.50 - $6**

**Month 3:**
- 500 daily users
- 15,000 monthly views
- Earnings: **$7.50 - $30**

**Month 6:**
- 1,000 daily users
- 30,000 monthly views
- Earnings: **$15 - $60**

**Month 12:**
- 5,000 daily users
- 150,000 monthly views
- Earnings: **$75 - $300**

---

## **Step 6: Get More Users (Marketing)**

To reach 1,000 daily users, you need to market your app:

### **Free Marketing:**
1. **Social Media:**
   - Share on Facebook groups (Ethiopian/Oromo communities)
   - Post on Twitter with hashtags: #AfaanOromo #Oromia #Ethiopia
   - Share on LinkedIn

2. **Ethiopian Forums:**
   - Post on Ethiopian forums
   - Oromo language learning groups
   - Student groups

3. **Schools & Universities:**
   - Email Ethiopian schools
   - Offer free tool for students
   - Ask teachers to share

4. **SEO (Search Engine Optimization):**
   - Your app already has good meta tags
   - Google will index it automatically
   - People searching "Afaan Oromo spell checker" will find you

5. **Word of Mouth:**
   - Ask users to share
   - Add "Share" buttons
   - Offer incentives

---

## **💰 Revenue Calculation:**

### **Formula:**
```
Monthly Revenue = (Monthly Page Views ÷ 1,000) × CPM
```

### **CPM Estimates:**
- **Low**: $0.50 (developing countries)
- **Medium**: $1.00 (average)
- **High**: $2.00 (good niche)

### **Examples:**

| Daily Users | Monthly Views | Low ($0.50) | Medium ($1.00) | High ($2.00) |
|-------------|---------------|-------------|----------------|--------------|
| 100         | 3,000         | $1.50       | $3             | $6           |
| 500         | 15,000        | $7.50       | $15            | $30          |
| 1,000       | 30,000        | $15         | $30            | $60          |
| 5,000       | 150,000       | $75         | $150           | $300         |
| 10,000      | 300,000       | $150        | $300           | $600         |

---

## **📋 Checklist:**

- [ ] Deploy app to cloud (Render/Railway/Heroku)
- [ ] Sign up for Google AdSense
- [ ] Wait for approval (1-7 days)
- [ ] Get Publisher ID
- [ ] Create 2 ad units (Top Banner, Middle Banner)
- [ ] Update `templates/index.html` with your IDs
- [ ] Commit and push changes
- [ ] Verify ads appear on your site
- [ ] Start marketing to get users
- [ ] Track earnings in AdSense dashboard

---

## **⚠️ Important Rules:**

1. **Never click your own ads** - Google will ban you permanently
2. **Don't ask others to click** - Against AdSense policy
3. **Don't place too many ads** - Bad user experience
4. **Follow AdSense policies** - Read: https://support.google.com/adsense/answer/48182

---

## **🎯 Next Steps:**

1. **First**: Deploy your app (Step 1)
2. **Then**: Apply for AdSense (Step 2)
3. **While waiting**: Start marketing to get users
4. **After approval**: Add AdSense code (Step 3)
5. **Finally**: Track and optimize (Steps 4-6)

---

## **💡 Pro Tips:**

1. **Quality Content**: More users = more views = more money
2. **Mobile-Friendly**: Your app is already responsive ✅
3. **Fast Loading**: Optimize images and code
4. **SEO**: Add more keywords to attract Google search traffic
5. **User Retention**: Make users come back daily

---

## **🚀 Ready to Start?**

Your app is now **AdSense-ready**! Just:
1. Deploy it
2. Apply for AdSense
3. Add your codes after approval
4. Start earning!

**Good luck!** 🎉
