#!/bin/bash

# MemOrg AI - Vercel Deployment Script
# Quick deployment to Vercel

set -e

echo "🚀 MemOrg AI - Deployment to Vercel"
echo "===================================="
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI ready"
echo ""

# Deploy Frontend
echo "📦 Deploying Frontend..."
echo "------------------------"
cd enterprise-rag-frontend

echo "🔑 Please log in to Vercel..."
vercel login

echo "🚀 Deploying to production..."
vercel --prod

echo ""
echo "✅ Frontend deployed successfully!"
echo ""

# Get frontend URL
FRONTEND_URL=$(vercel ls 2>/dev/null | grep -m 1 "memorg-ai" | awk '{print $2}' || echo "https://memorg-ai.vercel.app")

echo "🌐 Frontend URL: $FRONTEND_URL"
echo ""

# Ask about backend deployment
echo "📋 Next Steps:"
echo "1. ✅ Frontend is deployed!"
echo "2. ⏳ Deploy backend (choose one):"
echo ""
echo "   Option A - Vercel:"
echo "   $ cd ../enterprise-rag"
echo "   $ vercel --prod"
echo ""
echo "   Option B - Railway:"
echo "   $ cd ../enterprise-rag"
echo "   $ railway login && railway up"
echo ""
echo "   Option C - Render:"
echo "   Visit https://render.com and connect your repo"
echo ""
echo "3. 🔧 Update environment variables:"
echo "   - Go to https://vercel.com/dashboard"
echo "   - Select your project → Settings → Environment Variables"
echo "   - Add: NEXT_PUBLIC_API_URL=<your-backend-url>"
echo "   - Redeploy frontend"
echo ""
echo "4. ✅ Test your deployment:"
echo "   $ curl $FRONTEND_URL"
echo ""

cd ..

echo "🎉 Deployment complete!"
echo ""
echo "📚 Documentation:"
echo "   - Quick Guide: DEPLOY_NOW.md"
echo "   - Full Guide: DEPLOYMENT_VERCEL.md"
echo "   - Live Demo: https://memorg-ai.vercel.app"
echo ""
