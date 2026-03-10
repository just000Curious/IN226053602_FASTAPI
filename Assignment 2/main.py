from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ── Temporary data — acting as our database for now ──────────

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook', 'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',  'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand', 'price': 399, 'category': 'Accessories', 'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 999, 'category': 'Electronics', 'in_stock': False},
    {'id': 7, 'name': 'Webcam', 'price': 899, 'category': 'Electronics', 'in_stock': True }
]

# ── DAY 1 ENDPOINTS ────────────────────────────────────────

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/category/{category}')
def get_products_by_category(category: str):
    filtered = [p for p in products if p['category'].lower() == category.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {'products': filtered, 'total': len(filtered)}

@app.get('/products/instock')
def get_products_instock():
    available = [p for p in products if p['in_stock'] == True]
    return {
        "in_stock_products": available,
        "count": len(available)
    }

@app.get('/store/summary')
def store_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p['in_stock'])
    out_of_stock_count = total_products - in_stock_count    
    category_list = list(set(p['category'] for p in products))
    return {
        'store_name': 'My E-commerce Store',
        'total_products': total_products,
        'in_stock': in_stock_count,
        'out_of_stock': out_of_stock_count,
        'categories': category_list
    }

@app.get('/products/search/{product_name}')
def search_products(product_name: str):
    results = [p for p in products if product_name.lower() in p['name'].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {'products': results, 'total': len(results)}

@app.get('/products/deals')
def get_deals():
    best_deal = min(products, key=lambda p: p['price'])
    premium_pick = max(products, key=lambda p: p['price'])
    return {
        'best_deal': best_deal,
        'premium_pick': premium_pick
    }

# ── DAY 2 ENDPOINTS ────────────────────────────────────────

# Q1 - Filter Products by Minimum Price
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price")
):
    result = products.copy()
    
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    
    return result

# Q2 - Get Only the Price of a Product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    return {"error": "Product not found"}

# Q3 - Customer Feedback
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, description="Customer name (min 2 chars)")
    product_id: int = Field(..., gt=0, description="ID of the product being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=300, description="Optional comment (max 300 chars)")

feedback_list = []

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback_list.append(data.model_dump())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.model_dump(),
        "total_feedback": len(feedback_list)
    }

# Q4 - Product Summary Dashboard
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    categories = sorted(list(set(p["category"] for p in products)))
    
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

# Q5 - Bulk Order System
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, le=50, description="Quantity (1-50)")

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2, description="Company name")
    contact_email: str = Field(..., min_length=5, description="Contact email")
    items: List[OrderItem] = Field(..., min_length=1, description="List of items to order")

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0
    
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        
        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })
    
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# ⭐ BONUS - Order Status Tracker (CORRECTED)
orders = []

class OrderRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity")

@app.post("/orders")
def place_order(order: OrderRequest):
    order_id = len(orders) + 1
    new_order = {
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }
    orders.append(new_order)
    return {
        "message": "Order placed successfully",
        "order": new_order
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }
    return {"error": "Order not found"}