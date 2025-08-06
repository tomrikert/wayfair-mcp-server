#!/usr/bin/env python3
"""
Render-Optimized Wayfair MCP Server

This version is optimized for Render deployment with simplified dependencies
and better error handling for cloud environments.
"""

import json
import logging
import time
import re
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wayfair MCP Server", version="2.2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for products")
    category: Optional[str] = Field(None, description="Filter by category")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    min_rating: Optional[float] = Field(None, description="Minimum rating filter")
    limit: Optional[int] = Field(10, description="Maximum number of results")

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
            "image_url": "https://images.wayfair.com/sofa-1.jpg",
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
            "image_url": "https://images.wayfair.com/sofa-2.jpg",
            "description": "Plush 3-seater sofa perfect for living rooms"
        }
    ],
    "bed": [
        {
            "id": "WF_BED_001",
            "name": "Queen Platform Bed Frame",
            "price": 299.99,
            "original_price": 399.99,
            "discount_percentage": 25,
            "rating": 4.4,
            "review_count": 892,
            "availability": "In Stock",
            "url": "https://www.wayfair.com/furniture/pdp/queen-platform-bed-frame",
            "image_url": "https://images.wayfair.com/bed-1.jpg",
            "description": "Sleek platform bed frame with upholstered headboard"
        }
    ],
    "dining": [
        {
            "id": "WF_DINING_001",
            "name": "Dining Table Set for 6",
            "price": 599.99,
            "original_price": 799.99,
            "discount_percentage": 25,
            "rating": 4.5,
            "review_count": 423,
            "availability": "In Stock",
            "url": "https://www.wayfair.com/furniture/pdp/dining-table-set-for-6",
            "image_url": "https://images.wayfair.com/dining-1.jpg",
            "description": "Complete dining set includes table and 6 chairs"
        }
    ]
}

class WayfairRenderScraper:
    """Render-optimized scraper with fallback data"""
    
    def __init__(self):
        self.base_url = "https://www.wayfair.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for products with fallback data"""
        try:
            # Try to scrape real data first
            logger.info(f"Attempting to scrape Wayfair for: {query}")
            scraped_products = self._scrape_wayfair(query, limit)
            
            if scraped_products:
                logger.info(f"Successfully scraped {len(scraped_products)} products")
                return scraped_products
            else:
                logger.warning("Scraping failed, using fallback data")
                return self._get_fallback_products(query, limit)
                
        except Exception as e:
            logger.error(f"Error in search_products: {e}")
            return self._get_fallback_products(query, limit)
    
    def _scrape_wayfair(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Attempt to scrape real data from Wayfair"""
        try:
            # Construct search URL
            search_url = f"{self.base_url}/search?query={query.replace(' ', '+')}"
            
            logger.info(f"Scraping URL: {search_url}")
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try multiple selectors for product containers
            selectors = [
                '[data-testid*="product"]',
                '[class*="product"]',
                '[class*="item"]',
                '[class*="card"]',
                'article',
                '.product-card',
                '.search-result-item'
            ]
            
            product_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements[:limit]
                    logger.info(f"Found {len(elements)} products using selector: {selector}")
                    break
            
            if not product_elements:
                # Try finding any elements with price-like content
                price_elements = soup.find_all(text=re.compile(r'\$\d+'))
                logger.info(f"Found {len(price_elements)} price elements")
                return []
            
            for element in product_elements:
                try:
                    product = self._extract_product_data(element)
                    if product and product.get('name') and product.get('price'):
                        products.append(product)
                        if len(products) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"Error extracting product data: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Wayfair: {e}")
            return []
    
    def _extract_product_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract product data from HTML element"""
        try:
            # Extract product name - try multiple approaches
            name = None
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '[class*="title"]', '[class*="name"]', '[class*="product-name"]',
                'a[href*="/pdp/"]', '.product-title', '.item-title'
            ]
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and len(name) > 3:
                        break
            
            if not name:
                # Try to find any text that looks like a product name
                text_elements = element.find_all(text=True)
                for text in text_elements:
                    text = text.strip()
                    if len(text) > 10 and len(text) < 100 and not text.isdigit():
                        name = text
                        break
            
            if not name:
                return None
            
            # Extract price
            price = None
            price_text = ""
            price_selectors = [
                '[class*="price"]', '[class*="cost"]', '.price', '.cost',
                'span:contains("$")', 'div:contains("$")'
            ]
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price:
                        break
            
            # If no price found, try to find any text with dollar signs
            if not price:
                all_text = element.get_text()
                price = self._extract_price(all_text)
            
            # Generate product ID
            product_id = f"WF_{hash(name + str(price or 0)) % 10000:04d}"
            
            # Extract URL
            url = ""
            link_elem = element.find('a')
            if link_elem and link_elem.get('href'):
                url = urljoin(self.base_url, link_elem['href'])
            
            # Extract image
            image_url = ""
            img_elem = element.find('img')
            if img_elem and img_elem.get('src'):
                image_url = urljoin(self.base_url, img_elem['src'])
            
            return {
                "id": product_id,
                "name": name,
                "price": price,
                "original_price": None,
                "discount_percentage": None,
                "rating": None,
                "review_count": None,
                "availability": "In Stock",
                "url": url,
                "image_url": image_url,
                "description": name,
                "scraped": True
            }
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract number
        price_match = re.search(r'[\$£€]?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text.replace(',', ''))
        if price_match:
            return float(price_match.group(1))
        return None
    
    def _get_fallback_products(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Get fallback products based on query"""
        query_lower = query.lower()
        
        # Determine category based on query
        if any(term in query_lower for term in ['sofa', 'couch', 'sectional']):
            category = 'sofa'
        elif any(term in query_lower for term in ['bed', 'bedroom', 'mattress']):
            category = 'bed'
        elif any(term in query_lower for term in ['dining', 'table', 'chair']):
            category = 'dining'
        else:
            category = 'sofa'  # Default
        
        products = FALLBACK_PRODUCTS.get(category, FALLBACK_PRODUCTS['sofa'])
        return products[:limit]

# Initialize scraper
scraper = WayfairRenderScraper()

class WayfairMCPServer:
    """MCP Server implementation optimized for Render"""
    
    def __init__(self):
        self.scraper = scraper
    
    def search_products(self, request: SearchRequest) -> Dict[str, Any]:
        """Search products with improved scraping"""
        logger.info(f"Searching for: {request.query}")
        
        # Perform search
        products = self.scraper.search_products(request.query, request.limit)
        
        # Apply filters
        if request.category:
            products = [p for p in products if request.category.lower() in p.get('name', '').lower()]
        
        if request.max_price:
            products = [p for p in products if p.get('price', 0) <= request.max_price]
        
        if request.min_rating:
            products = [p for p in products if p.get('rating', 0) >= request.min_rating]
        
        # Determine data source
        scraped_count = sum(1 for p in products if p.get('scraped', False))
        fallback_count = len(products) - scraped_count
        
        result = {
            "query": request.query,
            "filters_applied": {
                "category": request.category,
                "max_price": request.max_price,
                "min_rating": request.min_rating
            },
            "total_results": len(products),
            "products": products,
            "scraped_at": datetime.now().isoformat(),
            "data_source": {
                "scraped_products": scraped_count,
                "fallback_products": fallback_count,
                "scraping_successful": scraped_count > 0
            }
        }
        
        return result

# Initialize server
server = WayfairMCPServer()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "Wayfair MCP Server - Render Optimized",
        "version": "2.2.0",
        "description": "Real-time scraping of Wayfair product data with fallback",
        "endpoints": [
            "/search",
            "/web",
            "/health"
        ],
        "status": "Active - Optimized for Render deployment"
    }

@app.post("/search")
async def search_products(request: SearchRequest):
    """Search products with improved scraping"""
    return server.search_products(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "scraper_status": "active",
        "deployment": "render-optimized"
    }

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web interface for ChatGPT to access"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wayfair MCP Server - Web Interface</title>
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
            .product-rating { color: #f39c12; margin: 5px 0; }
            .product-url { color: #3498db; text-decoration: none; }
            .loading { text-align: center; padding: 20px; color: #7f8c8d; }
            .error { color: #e74c3c; padding: 10px; background: #fdf2f2; border-radius: 5px; margin: 10px 0; }
            .stats { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .data-source { background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .fallback-notice { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; color: #856404; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏪 Wayfair MCP Server - Web Interface</h1>
            <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
                Real-time product data scraping from Wayfair.com with fallback data<br>
                Accessible to AI agents like ChatGPT
            </p>
            
            <div class="search-section">
                <input type="text" id="searchQuery" class="search-box" placeholder="Search for products on Wayfair (e.g., 'sofa', 'bed', 'dining table')" value="sofa">
                <button onclick="searchProducts()" class="search-button">🔍 Search Products</button>
            </div>
            
            <div id="results" class="results"></div>
            
            <div class="stats">
                <h3>📊 Server Information</h3>
                <p><strong>Status:</strong> <span style="color: #27ae60;">✅ Active - Render Optimized</span></p>
                <p><strong>API Endpoint:</strong> <code>https://your-domain.com/api/search</code></p>
                <p><strong>MCP Tools Available:</strong> Product search, detailed information, real-time data</p>
                <p><strong>Data Source:</strong> Direct scraping from Wayfair.com + fallback data</p>
                <p><strong>Features:</strong> Handles anti-scraping measures gracefully</p>
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
                
                resultsDiv.innerHTML = '<div class="loading">🔍 Searching Wayfair for real product data...</div>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            limit: 10
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.products && data.products.length > 0) {
                        let html = `<h2>📋 Search Results for "${query}"</h2>`;
                        html += `<p><strong>Found ${data.total_results} products</strong></p>`;
                        
                        // Show data source information
                        if (data.data_source) {
                            if (data.data_source.scraping_successful) {
                                html += `<div class="data-source">✅ <strong>Real-time data scraped from Wayfair.com</strong> (${data.data_source.scraped_products} products)</div>`;
                            } else {
                                html += `<div class="fallback-notice">⚠️ <strong>Using fallback data</strong> - Scraping blocked, but still providing structured product information</div>`;
                            }
                        }
                        
                        data.products.forEach(product => {
                            html += `
                                <div class="product-card">
                                    <div class="product-name">${product.name}</div>
                                    <div class="product-price">$${product.price?.toFixed(2) || 'Price not available'}</div>
                                    ${product.original_price ? `<div style="text-decoration: line-through; color: #7f8c8d;">$${product.original_price.toFixed(2)}</div>` : ''}
                                    ${product.discount_percentage ? `<div style="color: #27ae60;">${product.discount_percentage}% OFF</div>` : ''}
                                    ${product.rating ? `<div class="product-rating">⭐ ${product.rating}/5 (${product.review_count || 0} reviews)</div>` : ''}
                                    <div style="margin-top: 10px;">
                                        <strong>Availability:</strong> ${product.availability}<br>
                                        <strong>Data Source:</strong> ${product.scraped ? 'Real-time scraping' : 'Fallback data'}<br>
                                        <strong>Scraped at:</strong> ${data.scraped_at}
                                    </div>
                                    ${product.url ? `<a href="${product.url}" target="_blank" class="product-url">View on Wayfair →</a>` : ''}
                                </div>
                            `;
                        });
                        
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = '<div class="error">No products found. Try a different search term.</div>';
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">Error searching products: ${error.message}</div>`;
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
    # Get port from environment variable (Render requirement)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Wayfair MCP Server - Render Optimized...")
    print("📊 Real-time scraping from Wayfair.com with fallback data")
    print(f"🌐 Server will be available at: http://0.0.0.0:{port}")
    print("🔧 MCP tools available for AI agents")
    print("🛡️  Handles anti-scraping measures gracefully")
    print("⚡ Optimized for Render deployment")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="0.0.0.0", port=port) 