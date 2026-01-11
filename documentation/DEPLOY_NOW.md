# 🚀 Deploy MemOrg AI to Vercel - Quick Start

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- OpenAI API key

---

## 🎯 1-Click Deploy (Fastest)

### Step 1: Fork Repository

1. Go to https://github.com/Vishal-code-E/team_P1
2. Click "Fork" button
3. Create fork in your account

### Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your forked repository
3. Select `enterprise-rag-frontend` as root directory
4. Click "Deploy"

**Your frontend is now live!** 🎉

---

## ⚙️ Configure Environment Variables

### In Vercel Dashboard:

1. Go to your project → Settings → Environment Variables
2. Add:
   ```
   NEXT_PUBLIC_API_URL = http://localhost:8000 (for now)
   ```

---

## 🔧 Deploy Backend (Multiple Options)

### Option A: Vercel (Recommended for Demo)

```bash
cd enterprise-rag
vercel login
vercel --prod
```

Then update frontend env var with your backend URL.

### Option B: Railway

```bash
cd enterprise-rag
railway login
railway init
railway up
```

### Option C: Render

1. Connect your GitHub repo
2. Create new "Web Service"
3. Root: `enterprise-rag`
4. Build: `pip install -r requirements.txt`
5. Start: `python api_server.py`
6. Add environment variable: `OPENAI_API_KEY`

---

## 🔗 Update Frontend with Backend URL

1. Go to Vercel project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` with your backend URL
3. Redeploy frontend

---

## ✅ Verify Deployment

### Check Frontend
```bash
curl https://memorg-ai.vercel.app
```

### Check Backend
```bash
curl https://your-backend-url.com/api/health
```

### Test Full Flow
1. Open https://memorg-ai.vercel.app
2. Upload a document
3. Ask a question
4. Verify you get an answer with sources

---

## 🎨 Custom Domain (Optional)

1. Buy domain (e.g., memorg.ai)
2. In Vercel: Settings → Domains
3. Add domain
4. Update DNS records as instructed

---

## 📊 Environment Variables Reference

### Frontend (.env.local or Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (Vercel/Railway/Render)
```bash
OPENAI_API_KEY=sk-...
SLACK_BOT_TOKEN=xoxb-... (optional)
CONFLUENCE_URL=https://... (optional)
CONFLUENCE_USERNAME=... (optional)
CONFLUENCE_API_TOKEN=... (optional)
```

---

## 🐛 Troubleshooting

### Frontend builds but shows errors
- Check `NEXT_PUBLIC_API_URL` is set
- Ensure backend is deployed and running

### Backend deployment fails
- Verify `requirements.txt` is complete
- Check `OPENAI_API_KEY` is set
- Review deployment logs

### CORS errors
- Update CORS settings in `api_server.py`
- Add your Vercel domain to allowed origins

---

## 📈 What's Next?

✅ **Deployed** - Your app is live!  
✅ **Secure** - Add authentication  
✅ **Scale** - Monitor usage, add caching  
✅ **Enhance** - Add more data sources  

---

**Live Demo**: https://memorg-ai.vercel.app  
**Full Guide**: [DEPLOYMENT_VERCEL.md](DEPLOYMENT_VERCEL.md)  
**Need Help?** Open a GitHub issue
