#!/bin/bash

echo "🚀 Wayfair MCP Server Deployment"
echo "=================================="
echo ""

echo "Choose your deployment platform:"
echo "1. Render (Recommended - Free tier)"
echo "2. Railway (Free tier)"
echo "3. Heroku (Free tier)"
echo "4. Manual deployment instructions"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📋 Render Deployment Instructions:"
        echo "=================================="
        echo ""
        echo "1. Go to https://render.com and sign up/login"
        echo "2. Click 'New +' and select 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Configure the service:"
        echo "   - Name: wayfair-mcp-server"
        echo "   - Environment: Python"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python wayfair_improved_scraper.py"
        echo "5. Click 'Create Web Service'"
        echo ""
        echo "Your app will be available at: https://wayfair-mcp-server.onrender.com"
        echo ""
        echo "✅ After deployment, test your endpoints:"
        echo "   - Web interface: https://your-app-name.onrender.com/web"
        echo "   - Health check: https://your-app-name.onrender.com/health"
        echo "   - API search: POST https://your-app-name.onrender.com/search"
        ;;
    2)
        echo ""
        echo "📋 Railway Deployment Instructions:"
        echo "==================================="
        echo ""
        echo "1. Go to https://railway.app and sign up/login"
        echo "2. Click 'New Project'"
        echo "3. Select 'Deploy from GitHub repo'"
        echo "4. Choose your repository"
        echo "5. Railway will automatically detect Python and deploy"
        echo ""
        echo "Your app will be available at: https://wayfair-mcp-server.railway.app"
        echo ""
        echo "✅ After deployment, test your endpoints:"
        echo "   - Web interface: https://your-app-name.railway.app/web"
        echo "   - Health check: https://your-app-name.railway.app/health"
        ;;
    3)
        echo ""
        echo "📋 Heroku Deployment Instructions:"
        echo "=================================="
        echo ""
        echo "1. Install Heroku CLI: brew install heroku/brew/heroku"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create wayfair-mcp-server"
        echo "4. Deploy: git push heroku main"
        echo ""
        echo "Your app will be available at: https://wayfair-mcp-server.herokuapp.com"
        ;;
    4)
        echo ""
        echo "📋 Manual Deployment Options:"
        echo "============================="
        echo ""
        echo "Other platforms you can use:"
        echo "- DigitalOcean App Platform"
        echo "- Google Cloud Run"
        echo "- AWS Elastic Beanstalk"
        echo "- Azure App Service"
        echo ""
        echo "All you need is:"
        echo "1. Python 3.9+"
        echo "2. pip install -r requirements.txt"
        echo "3. python wayfair_improved_scraper.py"
        echo "4. Expose port 8000"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Deploy using the instructions above"
echo "2. Get your public URL"
echo "3. Test the endpoints"
echo "4. Share with ChatGPT:"
echo "   'Check out this real-time Wayfair product scraper: https://your-url.com/web'"
echo ""
echo "💡 The web interface will show:"
echo "   - Real-time product search"
echo "   - Structured data vs web scraping"
echo "   - Value proposition demonstration" 