# GitHub Repository Setup for Deployment

## 🚀 Quick Setup

### 1. Create GitHub Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Wayfair MCP Server"

# Create repository on GitHub.com
# Then push to GitHub:
git remote add origin https://github.com/YOUR_USERNAME/wayfair-mcp-server.git
git branch -M main
git push -u origin main
```

### 2. Files to Include

Make sure these files are in your repository:

```
wayfair-mcp-server/
├── wayfair_improved_scraper.py    # Main server
├── requirements.txt                # Dependencies
├── render.yaml                    # Render config
├── Procfile                       # Railway config
├── railway.json                   # Railway config
├── product_data.json              # Sample data
├── README.md                      # Documentation
├── DEPLOYMENT_GUIDE.md           # Deployment guide
└── SCRAPER_TEST_RESULTS.md       # Test results
```

## 📋 Deployment Options

### Option 1: Render (Recommended)

1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `wayfair-mcp-server`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python wayfair_improved_scraper.py`
6. Click "Create Web Service"

**Your URL**: `https://wayfair-mcp-server.onrender.com`

### Option 2: Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway auto-detects Python and deploys

**Your URL**: `https://wayfair-mcp-server.railway.app`

### Option 3: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create wayfair-mcp-server

# Deploy
git push heroku main
```

**Your URL**: `https://wayfair-mcp-server.herokuapp.com`

## 🧪 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Web interface
curl https://your-app-name.onrender.com/web

# API search
curl -X POST "https://your-app-name.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "sofa", "limit": 3}'
```

## 🎯 Share with ChatGPT

Once deployed, share your URL with ChatGPT:

```
"Check out this real-time Wayfair product scraper that demonstrates 
structured data access for AI agents: https://your-url.com/web

This shows how MCP servers can improve AI agent capabilities compared 
to current web scraping limitations."
```

## 📊 Expected Results

Your deployed server will show:

- ✅ **Web interface** with real-time search
- ✅ **Structured product data** (even with fallback)
- ✅ **API endpoints** for programmatic access
- ✅ **Health monitoring** for reliability
- ✅ **Value proposition** demonstration

## 🔧 Troubleshooting

### Common Issues:

1. **Build fails**: Check `requirements.txt` has all dependencies
2. **Port issues**: Make sure server runs on port 8000
3. **Timeout**: Add health check endpoint
4. **CORS errors**: Already handled in the code

### Debug Commands:

```bash
# Check logs
heroku logs --tail

# Test locally first
python wayfair_improved_scraper.py
curl http://localhost:8000/health
```

## 🎉 Success!

Once deployed, you'll have a public URL that ChatGPT can access to demonstrate the value of MCP servers for retailers! 