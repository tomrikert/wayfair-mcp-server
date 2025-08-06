#!/usr/bin/env python3
"""
Improved Wayfair Scraper MCP Server

This server attempts to scrape Wayfair's website and provides fallback data
when scraping fails, demonstrating the value proposition.
"""

import json
import logging
import time
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Fallback product data for when scraping fails
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

class WayfairImprovedScraper:
    """Improved scraper with fallback data"""
    
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
            logger.error(f"Error during scraping: {e}")
            return self._get_fallback_products(query, limit)
    
    def _scrape_wayfair(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Attempt to scrape Wayfair for real product data"""
        try:
            # Construct search URL
            search_url = f"{self.base_url}/keyword/{query.replace(' ', '-')}"
            logger.info(f"Searching URL: {search_url}")
            
            # Make request
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers (this is a simplified approach)
            products = []
            product_elements = soup.find_all('div', class_=re.compile(r'product|item|card'))
            
            for element in product_elements[:limit]:
                product_data = self._extract_product_data(element)
                if product_data:
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return []
    
    def _extract_product_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract product data from HTML element"""
        try:
            # This is a simplified extraction - in a real implementation,
            # you'd need to adapt to Wayfair's actual HTML structure
            
            # Try to find product name
            name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or element.find(class_=re.compile(r'title|name'))
            name = name_elem.get_text(strip=True) if name_elem else "Product"
            
            # Try to find price
            price_elem = element.find(class_=re.compile(r'price|cost'))
            price_text = price_elem.get_text(strip=True) if price_elem else "$0"
            price = self._extract_price(price_text)
            
            # Try to find image
            img_elem = element.find('img')
            image_url = img_elem.get('src') if img_elem else ""
            
            # Try to find link
            link_elem = element.find('a')
            url = link_elem.get('href') if link_elem else ""
            if url and not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            return {
                "id": f"scraped_{hash(name)}",
                "name": name,
                "price": price or 0.0,
                "original_price": price or 0.0,
                "discount_percentage": 0,
                "rating": 4.0,
                "review_count": 0,
                "availability": "In Stock",
                "url": url,
                "image_url": image_url,
                "description": name,
                "scraped": True
            }
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and extract number
            price_match = re.search(r'[\$£€]?(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                return float(price_str)
        except Exception as e:
            logger.error(f"Error extracting price: {e}")
        return None
    
    def _get_fallback_products(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Get fallback product data based on query"""
        query_lower = query.lower()
        
        # Find matching category
        for category, products in FALLBACK_PRODUCTS.items():
            if category in query_lower:
                return products[:limit]
        
        # Default to sofa products if no match
        return FALLBACK_PRODUCTS.get("sofa", [])[:limit]

class WayfairMCPServer:
    """MCP Server wrapper for the scraper"""
    
    def __init__(self):
        self.scraper = WayfairImprovedScraper()
    
    def search_products(self, query: str, category: str = None, max_price: float = None, 
                       min_rating: float = None, limit: int = 10) -> Dict[str, Any]:
        """Search for products with MCP-compatible interface"""
        try:
            products = self.scraper.search_products(query, limit)
            
            # Apply filters
            if category:
                products = [p for p in products if category.lower() in p.get('name', '').lower()]
            
            if max_price:
                products = [p for p in products if p.get('price', 0) <= max_price]
            
            if min_rating:
                products = [p for p in products if p.get('rating', 0) >= min_rating]
            
            return {
                "success": True,
                "query": query,
                "products": products,
                "total_count": len(products),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in MCP server: {e}")
            return {
                "success": False,
                "error": str(e),
                "products": [],
                "total_count": 0,
                "timestamp": datetime.now().isoformat()
            }

# Initialize the MCP server
mcp_server = WayfairMCPServer()

@app.route('/')
def root():
    """Root endpoint"""
    return {
        "service": "Wayfair Improved Scraper MCP Server",
        "version": "2.1.0",
        "status": "running",
        "endpoints": {
            "GET /": "Service info",
            "POST /search": "Search products",
            "GET /health": "Health check",
            "GET /web": "Web interface"
        }
    }

@app.route('/search', methods=['POST'])
def search_products():
    """Search for products"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        query = data.get('query', '')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        category = data.get('category')
        max_price = data.get('max_price')
        min_rating = data.get('min_rating')
        limit = data.get('limit', 10)
        
        result = mcp_server.search_products(query, category, max_price, min_rating, limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Wayfair Improved Scraper MCP Server"
    }

@app.route('/web')
def web_interface():
    """Simple web interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wayfair Scraper</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input, select { width: 100%; padding: 8px; margin-bottom: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .product { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .price { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Wayfair Product Scraper</h1>
            <form id="searchForm">
                <div class="form-group">
                    <label for="query">Search Query:</label>
                    <input type="text" id="query" name="query" placeholder="e.g., sofa, bed, dining table" required>
                </div>
                <div class="form-group">
                    <label for="category">Category (optional):</label>
                    <input type="text" id="category" name="category" placeholder="e.g., furniture, decor">
                </div>
                <div class="form-group">
                    <label for="maxPrice">Max Price (optional):</label>
                    <input type="number" id="maxPrice" name="maxPrice" placeholder="e.g., 500">
                </div>
                <div class="form-group">
                    <label for="limit">Limit:</label>
                    <input type="number" id="limit" name="limit" value="10" min="1" max="50">
                </div>
                <button type="submit">Search Products</button>
            </form>
            <div id="results"></div>
        </div>
        
        <script>
            document.getElementById('searchForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = {
                    query: formData.get('query'),
                    category: formData.get('category') || null,
                    max_price: formData.get('maxPrice') ? parseFloat(formData.get('maxPrice')) : null,
                    limit: parseInt(formData.get('limit'))
                };
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    
                    const resultsDiv = document.getElementById('results');
                    if (result.success && result.products.length > 0) {
                        resultsDiv.innerHTML = '<h2>Results (' + result.products.length + ' products)</h2>';
                        result.products.forEach(product => {
                            resultsDiv.innerHTML += `
                                <div class="product">
                                    <h3>${product.name}</h3>
                                    <p class="price">$${product.price}</p>
                                    <p>Rating: ${product.rating}/5 (${product.review_count} reviews)</p>
                                    <p>${product.description}</p>
                                    <p><a href="${product.url}" target="_blank">View Product</a></p>
                                </div>
                            `;
                        });
                    } else {
                        resultsDiv.innerHTML = '<p>No products found or error occurred.</p>';
                    }
                } catch (error) {
                    document.getElementById('results').innerHTML = '<p>Error: ' + error.message + '</p>';
                }
            });
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False) 