#!/usr/bin/env python3
"""
Minimal Wayfair MCP Server for Render

This is the most basic version guaranteed to work on Render.
"""

import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Wayfair MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple Pydantic model
class SearchRequest(BaseModel):
    query: str

# Fallback product data
FALLBACK_PRODUCTS = {
    "sofa": [
        {
            "id": "WF_SOFA_001",
            "name": "Modern L-Shaped Sectional Sofa",
            "price": 899.99,
            "original_price": 1299.99,
            "discount_percentage": 31,
            "rating": 4.6,
            "review_count": 1247,
            "availability": "In Stock",
            "url": "https://www.wayfair.com/furniture/pdp/modern-l-shaped-sectional-sofa",
            "description": "Contemporary L-shaped sectional with premium fabric upholstery"
        },
        {
            "id": "WF_SOFA_002", 
            "name": "Comfortable 3-Seater Sofa",
            "price": 599.99,
            "original_price": 799.99,
            "discount_percentage": 25,
            "rating": 4.4,
            "review_count": 892,
            "availability": "In Stock",
            "url": "https://www.wayfair.com/furniture/pdp/comfortable-3-seater-sofa",
            "description": "Plush 3-seater sofa perfect for living rooms"
        }
    ]
}

def get_products(query: str):
    """Get products based on query"""
    query_lower = query.lower()
    
    if any(term in query_lower for term in ['sofa', 'couch', 'sectional']):
        return FALLBACK_PRODUCTS.get('sofa', [])
    else:
        return FALLBACK_PRODUCTS.get('sofa', [])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wayfair MCP Server - Minimal Version",
        "version": "1.0.0",
        "status": "Active",
        "endpoints": ["/search", "/web", "/health"]
    }

@app.post("/search")
async def search_products(request: SearchRequest):
    """Search products"""
    products = get_products(request.query)
    
    return {
        "query": request.query,
        "total_results": len(products),
        "products": products,
        "scraped_at": datetime.now().isoformat(),
        "data_source": {
            "scraped_products": 0,
            "fallback_products": len(products),
            "scraping_successful": False
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "deployment": "minimal-version"
    }

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wayfair MCP Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .search-section { margin-bottom: 30px; }
            .search-box { width: 100%; padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; margin-bottom: 10px; }
            .search-button { background: #3498db; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            .search-button:hover { background: #2980b9; }
            .results { margin-top: 30px; }
            .product-card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; background: #fafafa; }
            .product-name { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .product-price { font-size: 20px; color: #e74c3c; font-weight: bold; }
            .loading { text-align: center; padding: 20px; color: #7f8c8d; }
            .stats { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Wayfair MCP Server</h1>
            <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
                Structured product data for AI agents
            </p>
            
            <div class="search-section">
                <input type="text" id="searchQuery" class="search-box" placeholder="Search for products (e.g., 'sofa')" value="sofa">
                <button onclick="searchProducts()" class="search-button">🔍 Search Products</button>
            </div>
            
            <div id="results" class="results"></div>
            
            <div class="stats">
                <h3>📊 Server Information</h3>
                <p><strong>Status:</strong> <span style="color: #27ae60;">✅ Active - Minimal Version</span></p>
                <p><strong>Purpose:</strong> Demonstrate structured data access for AI agents</p>
                <p><strong>Value:</strong> Shows how MCP servers improve AI capabilities</p>
            </div>
        </div>
        
        <script>
            async function searchProducts() {
                const query = document.getElementById('searchQuery').value;
                const resultsDiv = document.getElementById('results');
                
                if (!query) {
                    alert('Please enter a search query');
                    return;
                }
                
                resultsDiv.innerHTML = '<div class="loading">🔍 Searching for structured product data...</div>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.products && data.products.length > 0) {
                        let html = `<h2>📋 Search Results for "${query}"</h2>`;
                        html += `<p><strong>Found ${data.total_results} products</strong></p>`;
                        
                        data.products.forEach(product => {
                            html += `
                                <div class="product-card">
                                    <div class="product-name">${product.name}</div>
                                    <div class="product-price">$${product.price?.toFixed(2) || 'Price not available'}</div>
                                    ${product.original_price ? `<div style="text-decoration: line-through; color: #7f8c8d;">$${product.original_price.toFixed(2)}</div>` : ''}
                                    ${product.discount_percentage ? `<div style="color: #27ae60;">${product.discount_percentage}% OFF</div>` : ''}
                                    ${product.rating ? `<div style="color: #f39c12;">⭐ ${product.rating}/5 (${product.review_count || 0} reviews)</div>` : ''}
                                    <div style="margin-top: 10px;">
                                        <strong>Availability:</strong> ${product.availability}<br>
                                        <strong>Data Source:</strong> Structured fallback data<br>
                                        <strong>Scraped at:</strong> ${data.scraped_at}
                                    </div>
                                    ${product.url ? `<a href="${product.url}" target="_blank" style="color: #3498db; text-decoration: none;">View on Wayfair →</a>` : ''}
                                </div>
                            `;
                        });
                        
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = '<div style="color: #e74c3c; padding: 10px; background: #fdf2f2; border-radius: 5px; margin: 10px 0;">No products found. Try a different search term.</div>';
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div style="color: #e74c3c; padding: 10px; background: #fdf2f2; border-radius: 5px; margin: 10px 0;">Error searching products: ${error.message}</div>`;
                }
            }
            
            // Auto-search on page load
            window.onload = function() {
                searchProducts();
            };
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Wayfair MCP Server - Minimal Version...")
    print(f"🌐 Server will be available at: http://0.0.0.0:{port}")
    print("🔧 MCP tools available for AI agents")
    print("⚡ Minimal version for guaranteed deployment")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="0.0.0.0", port=port) 