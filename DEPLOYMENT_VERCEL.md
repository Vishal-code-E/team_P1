# MemOrg AI - Deployment Guide

## 🚀 Deploy to Vercel (Frontend)

### Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Vishal-code-E/team_P1/tree/main/enterprise-rag-frontend)

### Manual Deployment

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy Frontend**:
```bash
cd enterprise-rag-frontend
vercel login
vercel --prod
```

3. **Configure Environment Variables** in Vercel Dashboard:
   - Go to your project settings
   - Add Environment Variables:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.com
     ```

4. **Custom Domain** (Optional):
   - Go to Settings → Domains
   - Add custom domain: `memorg-ai.com` or `app.memorg.ai`

---

## 🔧 Backend Deployment Options

### Option 1: Vercel (Recommended for Demo)

```bash
cd enterprise-rag
vercel --prod
```

**Environment Variables**:
- `OPENAI_API_KEY`
- `SLACK_BOT_TOKEN` (optional)
- `CONFLUENCE_URL` (optional)
- `CONFLUENCE_USERNAME` (optional)
- `CONFLUENCE_API_TOKEN` (optional)

### Option 2: Railway

```bash
railway login
railway init
railway up
```

### Option 3: Render

1. Connect GitHub repository
2. Create new Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python api_server.py`
5. Add environment variables

### Option 4: Google Cloud Run

```bash
gcloud run deploy memorg-ai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🌐 Live URLs

**Production Frontend**: https://memorg-ai.vercel.app  
**Staging Frontend**: https://memorg-ai-staging.vercel.app  
**Backend API**: https://memorg-ai-backend.vercel.app

---

## 📋 Pre-Deployment Checklist

### Frontend
- [x] Updated `package.json` with project name
- [x] Updated `layout.tsx` metadata
- [x] Updated UI header to "MemOrg AI"
- [x] Created `vercel.json` configuration
- [x] Set API URL environment variable

### Backend
- [ ] Add `Procfile` for deployment
- [ ] Add `runtime.txt` for Python version
- [ ] Ensure all dependencies in `requirements.txt`
- [ ] Set environment variables in platform
- [ ] Test CORS settings for production domain

### Documentation
- [x] Updated README with live URL
- [x] Updated demo script with deployment link
- [ ] Added deployment guide

---

## 🔐 Security for Production

1. **Environment Variables**:
   - Never commit `.env` files
   - Use platform secret management
   - Rotate API keys regularly

2. **CORS Configuration**:
```python
# In api_server.py
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://memorg-ai.vercel.app",
            "https://memorg-ai-staging.vercel.app",
            "http://localhost:3000"  # For development
        ]
    }
})
```

3. **API Rate Limiting**:
   - Implement rate limiting on backend
   - Use Vercel Edge Config for IP blocking
   - Monitor usage in OpenAI dashboard

---

## 📊 Post-Deployment Monitoring

### Vercel Analytics
- Enable Analytics in project settings
- Monitor page load times
- Track user interactions

### Backend Monitoring
- Use platform logs (Vercel, Railway, Render)
- Set up error tracking (Sentry)
- Monitor OpenAI API usage

### Health Checks
```bash
# Frontend
curl https://memorg-ai.vercel.app

# Backend
curl https://memorg-ai-backend.vercel.app/api/health
```

---

## 🔄 Continuous Deployment

### GitHub Integration

1. **Connect Repository** to Vercel
2. **Auto-deploy** on push to main branch
3. **Preview deployments** for pull requests

### Environment Branches

- `main` → Production (memorg-ai.vercel.app)
- `staging` → Staging (memorg-ai-staging.vercel.app)
- `dev` → Development (memorg-ai-dev.vercel.app)

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Clear cache
vercel --force

# Check build logs
vercel logs <deployment-url>
```

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration on backend
- Ensure backend is deployed and running

### Environment Variables Not Working
- Redeploy after adding new env vars
- Check variable names match code
- Use `NEXT_PUBLIC_` prefix for client-side vars

---

## 📱 Custom Domain Setup

1. **Buy Domain** (e.g., memorg.ai)
2. **Add to Vercel**:
   - Project Settings → Domains
   - Add `memorg.ai` and `www.memorg.ai`
3. **Configure DNS**:
   ```
   A     @       76.76.21.21
   CNAME www     cname.vercel-dns.com
   ```

---

## 🎯 Performance Optimization

### Frontend
- Enable ISR (Incremental Static Regeneration)
- Use Next.js Image optimization
- Enable Vercel Edge Network

### Backend
- Use caching for vector searches
- Implement request queuing
- Consider serverless functions for scaling

---

**Live Demo**: https://memorg-ai.vercel.app  
**Documentation**: https://github.com/Vishal-code-E/team_P1  
**Support**: Open GitHub issue
