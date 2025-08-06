# Deployment Guide: Wayfair MCP Server for ChatGPT

This guide shows how to deploy the Wayfair MCP Server to make it accessible to ChatGPT via a public URL.

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended - Free Tier)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy to Railway:**
   ```bash
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

3. **Get your public URL:**
   ```bash
   railway domain
   ```

### Option 2: Render (Free Tier)

1. **Create a `render.yaml` file:**
   ```yaml
   services:
     - type: web
       name: wayfair-mcp-server
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python wayfair_scraper_mcp.py
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
   ```

2. **Deploy to Render:**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Deploy automatically

### Option 3: Heroku (Free Tier)

1. **Create a `Procfile`:**
   ```
   web: python wayfair_scraper_mcp.py
   ```

2. **Create `runtime.txt`:**
   ```
   python-3.9.18
   ```

3. **Deploy to Heroku:**
   ```bash
   # Install Heroku CLI
   brew install heroku/brew/heroku
   
   # Login and deploy
   heroku login
   heroku create wayfair-mcp-server
   git push heroku main
   ```

### Option 4: DigitalOcean App Platform

1. **Create `app.yaml`:**
   ```yaml
   name: wayfair-mcp-server
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/wayfair-mcp-server
       branch: main
     run_command: python wayfair_scraper_mcp.py
     environment_slug: python
   ```

2. **Deploy via DigitalOcean dashboard**

## 🔧 Local Development & Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python wayfair_scraper_mcp.py
```

### 3. Test Endpoints
```bash
# Test search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "sofa", "limit": 5}'

# Test web interface
open http://localhost:8000/web
```

## 🌐 Making it Accessible to ChatGPT

### 1. Get Your Public URL
After deployment, you'll get a URL like:
- Railway: `https://wayfair-mcp-server.railway.app`
- Render: `https://wayfair-mcp-server.onrender.com`
- Heroku: `https://wayfair-mcp-server.herokuapp.com`

### 2. Test Your Deployment
```bash
# Test the web interface
curl https://your-domain.com/web

# Test the API
curl -X POST "https://your-domain.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "sofa"}'
```

### 3. Share with ChatGPT
You can now share your URL with ChatGPT:

```
"Here's a web interface that scrapes real product data from Wayfair.com:
https://your-domain.com/web

You can search for products and get real-time data from Wayfair's website."
```

## 📊 API Endpoints Available

### For ChatGPT Integration

1. **Web Interface:** `https://your-domain.com/web`
   - Interactive search interface
   - Real-time product data
   - User-friendly for demonstrations

2. **API Endpoints:**
   - `POST /search` - Search products
   - `GET /product/details` - Get product details
   - `GET /api/docs` - API documentation

### Example Usage

```python
# Search for products
import requests

response = requests.post("https://your-domain.com/search", json={
    "query": "sofa",
    "limit": 5,
    "max_price": 1000
})

products = response.json()
print(f"Found {products['total_results']} products")
```

## 🔒 Security & Rate Limiting

### 1. Add Rate Limiting
```python
# Add to wayfair_scraper_mcp.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/search")
@limiter.limit("10/minute")
async def search_products(request: SearchRequest):
    return server.search_products(request)
```

### 2. Add CORS for Web Access
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Monitoring & Analytics

### 1. Add Logging
```python
import logging
from datetime import datetime

# Add to your server
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = datetime.now() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {duration}")
    return response
```

### 2. Add Health Check
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }
```

## 🚀 Production Deployment Checklist

- [ ] Deploy to cloud platform
- [ ] Test all endpoints
- [ ] Add rate limiting
- [ ] Add CORS headers
- [ ] Add health check endpoint
- [ ] Test with ChatGPT
- [ ] Monitor performance
- [ ] Set up logging

## 💡 ChatGPT Integration Tips

### 1. Direct URL Sharing
Share your web interface URL directly with ChatGPT:
```
"Check out this real-time Wayfair product scraper: https://your-domain.com/web"
```

### 2. API Documentation
ChatGPT can use your API endpoints:
```
"API documentation: https://your-domain.com/api/docs"
```

### 3. Example Queries
Demonstrate the value:
```
"Search for 'sofa' at: https://your-domain.com/web"
"Compare this to ChatGPT's current limitations with web scraping"
```

## 🔄 Continuous Deployment

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
      - uses: railway/action@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📞 Support & Troubleshooting

### Common Issues

1. **CORS Errors:** Add CORS middleware
2. **Rate Limiting:** Implement proper delays
3. **Scraping Blocked:** Update User-Agent headers
4. **Timeout Errors:** Increase timeout values

### Monitoring Commands
```bash
# Check server status
curl https://your-domain.com/health

# Test search functionality
curl -X POST "https://your-domain.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## 🎯 Next Steps

1. **Deploy your server** using one of the options above
2. **Test the web interface** at your public URL
3. **Share with ChatGPT** to demonstrate the value
4. **Monitor usage** and performance
5. **Iterate and improve** based on feedback

Your MCP server will now be accessible to ChatGPT and can demonstrate the real value of structured data access for AI agents! 