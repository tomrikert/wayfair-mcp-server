#!/usr/bin/env python3
"""
Wayfair MCP Server Prototype

This server demonstrates how retailers can provide structured access to their product data
through the Model Context Protocol (MCP), enabling AI agents to better assist customers
with product discovery and purchasing decisions.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load product data
with open('product_data.json', 'r') as f:
    PRODUCT_DATA = json.load(f)

app = FastAPI(title="Wayfair MCP Server", version="1.0.0")

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for products")
    category: Optional[str] = Field(None, description="Filter by category")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    min_rating: Optional[float] = Field(None, description="Minimum rating filter")
    limit: Optional[int] = Field(10, description="Maximum number of results")

class ProductInfo(BaseModel):
    id: str
    name: str
    category: str
    brand: str
    price: float
    original_price: Optional[float]
    discount_percentage: Optional[int]
    rating: float
    review_count: int
    availability: str
    delivery_estimate: str
    description: str
    features: List[str]
    colors: List[str]
    materials: List[str]

class ProductComparison(BaseModel):
    product_ids: List[str] = Field(..., description="List of product IDs to compare")

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)

class CartOperation(BaseModel):
    operation: str = Field(..., description="add, remove, or update")
    items: List[CartItem]

# In-memory shopping cart (in production, this would be persistent)
shopping_cart = {}

class WayfairMCPServer:
    """MCP Server implementation for Wayfair product data"""
    
    def __init__(self):
        self.products = PRODUCT_DATA['products']
        self.categories = PRODUCT_DATA['categories']
        self.subcategories = PRODUCT_DATA['subcategories']
        self.brands = PRODUCT_DATA['brands']
    
    def search_products(self, request: SearchRequest) -> Dict[str, Any]:
        """Search products with filters"""
        results = []
        query_lower = request.query.lower()
        
        for product in self.products:
            # Basic text search
            if (query_lower in product['name'].lower() or 
                query_lower in product['description'].lower() or
                query_lower in product['category'].lower() or
                query_lower in product['brand'].lower()):
                
                # Apply filters
                if request.category and product['category'] != request.category:
                    continue
                    
                if request.max_price and product['price'] > request.max_price:
                    continue
                    
                if request.min_rating and product['rating'] < request.min_rating:
                    continue
                
                results.append(product)
        
        # Sort by relevance (rating * review_count for popularity)
        results.sort(key=lambda x: x['rating'] * x['review_count'], reverse=True)
        
        # Apply limit
        if request.limit:
            results = results[:request.limit]
        
        return {
            "query": request.query,
            "filters_applied": {
                "category": request.category,
                "max_price": request.max_price,
                "min_rating": request.min_rating
            },
            "total_results": len(results),
            "products": results
        }
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product"""
        for product in self.products:
            if product['id'] == product_id:
                return {
                    "product": product,
                    "related_products": self._get_related_products(product)
                }
        
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    def compare_products(self, request: ProductComparison) -> Dict[str, Any]:
        """Compare multiple products side by side"""
        products_to_compare = []
        
        for product_id in request.product_ids:
            product = next((p for p in self.products if p['id'] == product_id), None)
            if product:
                products_to_compare.append(product)
        
        if not products_to_compare:
            raise HTTPException(status_code=404, detail="No valid products found for comparison")
        
        return {
            "comparison": {
                "products": products_to_compare,
                "summary": self._generate_comparison_summary(products_to_compare)
            }
        }
    
    def get_categories(self) -> Dict[str, Any]:
        """Get all available categories and subcategories"""
        return {
            "categories": self.categories,
            "subcategories": self.subcategories
        }
    
    def get_brands(self) -> Dict[str, Any]:
        """Get all available brands"""
        return {"brands": self.brands}
    
    def get_deals(self, min_discount: int = 20) -> Dict[str, Any]:
        """Get products with significant discounts"""
        deals = [p for p in self.products if p.get('discount_percentage', 0) >= min_discount]
        deals.sort(key=lambda x: x['discount_percentage'], reverse=True)
        
        return {
            "deals": deals,
            "min_discount": min_discount,
            "total_deals": len(deals)
        }
    
    def cart_operations(self, request: CartOperation) -> Dict[str, Any]:
        """Perform shopping cart operations"""
        if request.operation == "add":
            for item in request.items:
                product = next((p for p in self.products if p['id'] == item.product_id), None)
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                
                if item.product_id in shopping_cart:
                    shopping_cart[item.product_id]['quantity'] += item.quantity
                else:
                    shopping_cart[item.product_id] = {
                        "product": product,
                        "quantity": item.quantity
                    }
        
        elif request.operation == "remove":
            for item in request.items:
                if item.product_id in shopping_cart:
                    del shopping_cart[item.product_id]
        
        elif request.operation == "update":
            for item in request.items:
                if item.product_id in shopping_cart:
                    shopping_cart[item.product_id]['quantity'] = item.quantity
        
        return {
            "operation": request.operation,
            "cart_contents": self._get_cart_summary(),
            "total_items": sum(item['quantity'] for item in shopping_cart.values()),
            "total_value": sum(item['product']['price'] * item['quantity'] for item in shopping_cart.values())
        }
    
    def get_cart(self) -> Dict[str, Any]:
        """Get current shopping cart contents"""
        return self._get_cart_summary()
    
    def _get_related_products(self, product: Dict[str, Any], limit: int = 4) -> List[Dict[str, Any]]:
        """Get related products based on category and price range"""
        related = []
        price_range = (product['price'] * 0.7, product['price'] * 1.3)
        
        for p in self.products:
            if (p['id'] != product['id'] and 
                p['category'] == product['category'] and
                price_range[0] <= p['price'] <= price_range[1]):
                related.append(p)
                if len(related) >= limit:
                    break
        
        return related
    
    def _generate_comparison_summary(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary comparison of products"""
        prices = [p['price'] for p in products]
        ratings = [p['rating'] for p in products]
        
        return {
            "price_range": {
                "lowest": min(prices),
                "highest": max(prices),
                "average": sum(prices) / len(prices)
            },
            "rating_range": {
                "lowest": min(ratings),
                "highest": max(ratings),
                "average": sum(ratings) / len(ratings)
            },
            "best_value": min(products, key=lambda x: x['price'] / x['rating'])['id'],
            "highest_rated": max(products, key=lambda x: x['rating'])['id']
        }
    
    def _get_cart_summary(self) -> Dict[str, Any]:
        """Get formatted cart summary"""
        items = []
        total_value = 0
        
        for product_id, cart_item in shopping_cart.items():
            item_total = cart_item['product']['price'] * cart_item['quantity']
            total_value += item_total
            
            items.append({
                "product_id": product_id,
                "name": cart_item['product']['name'],
                "price": cart_item['product']['price'],
                "quantity": cart_item['quantity'],
                "item_total": item_total
            })
        
        return {
            "items": items,
            "total_value": total_value,
            "item_count": len(items),
            "total_quantity": sum(item['quantity'] for item in items)
        }

# Initialize server
server = WayfairMCPServer()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "Wayfair MCP Server",
        "version": "1.0.0",
        "description": "Structured access to Wayfair product data for AI agents",
        "endpoints": [
            "/search",
            "/product/{product_id}",
            "/compare",
            "/categories",
            "/brands",
            "/deals",
            "/cart",
            "/cart/operations"
        ]
    }

@app.post("/search")
async def search_products(request: SearchRequest):
    """Search products with filters"""
    return server.search_products(request)

@app.get("/product/{product_id}")
async def get_product(product_id: str):
    """Get detailed product information"""
    return server.get_product_details(product_id)

@app.post("/compare")
async def compare_products(request: ProductComparison):
    """Compare multiple products"""
    return server.compare_products(request)

@app.get("/categories")
async def get_categories():
    """Get all categories and subcategories"""
    return server.get_categories()

@app.get("/brands")
async def get_brands():
    """Get all brands"""
    return server.get_brands()

@app.get("/deals")
async def get_deals(min_discount: int = 20):
    """Get products with significant discounts"""
    return server.get_deals(min_discount)

@app.get("/cart")
async def get_cart():
    """Get current shopping cart"""
    return server.get_cart()

@app.post("/cart/operations")
async def cart_operations(request: CartOperation):
    """Perform cart operations"""
    return server.cart_operations(request)

# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "search_wayfair_products",
        "description": "Search for products on Wayfair with various filters",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for products"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (Living Room, Bedroom, Dining Room, Office, Storage)"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price filter"
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum rating filter (1-5)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_wayfair_product_details",
        "description": "Get detailed information about a specific Wayfair product",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Product ID to get details for"
                }
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "compare_wayfair_products",
        "description": "Compare multiple Wayfair products side by side",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of product IDs to compare"
                }
            },
            "required": ["product_ids"]
        }
    },
    {
        "name": "get_wayfair_categories",
        "description": "Get all available Wayfair categories and subcategories",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_wayfair_deals",
        "description": "Get Wayfair products with significant discounts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_discount": {
                    "type": "integer",
                    "description": "Minimum discount percentage (default: 20)"
                }
            }
        }
    },
    {
        "name": "add_to_wayfair_cart",
        "description": "Add products to Wayfair shopping cart",
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string"},
                            "quantity": {"type": "integer", "default": 1}
                        },
                        "required": ["product_id"]
                    },
                    "description": "List of items to add to cart"
                }
            },
            "required": ["items"]
        }
    },
    {
        "name": "get_wayfair_cart",
        "description": "Get current Wayfair shopping cart contents",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get MCP tool definitions"""
    return {"tools": MCP_TOOLS}

if __name__ == "__main__":
    print("🚀 Starting Wayfair MCP Server...")
    print("📊 Loaded", len(PRODUCT_DATA['products']), "products")
    print("🏪 Available categories:", ", ".join(PRODUCT_DATA['categories']))
    print("🔧 MCP Tools available:", len(MCP_TOOLS))
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 