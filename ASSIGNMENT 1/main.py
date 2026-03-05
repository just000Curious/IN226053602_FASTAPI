from fastapi import FastAPI
app = FastAPI()
from fastapi import Query

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

# ── Endpoint 0 — Home ────────────────────────────────────────

@app.get('/')

def home():

    return {'message': 'Welcome to our E-commerce API'}


# ── Endpoint 1 — Return all products ──────────────────────────

@app.get('/products')

def get_all_products():

    return {'products': products, 'total': len(products)}

#  ── Endpoint 2 — Filter products by category ──────────────────────────

@app.get('/products/category/{category}')
def get_products_by_category(category: str):

    filtered = [p for p in products if p['category'].lower() == category.lower()]
    if not filtered:
        return {"error":"No products found in this category"}

    return {'products': filtered, 'total': len(filtered)}

#  ── Endpoint 3 — Filter products by in stock status ──────────────────────────

@app.get('/products/instock')
def get_products_instock():
    available = [p for p in products if p['in_stock'] == True]
    return {
    "in_stock_products": available,
    "count": len(available)
    }



# endpoint 4 — Store Info Endpoint ────────────────────────────────────────

@app.get('/store/summary')
def store_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p['in_stock'])
    out_of_stock_count = total_products - in_stock_count    
    category_list = [c for c in set(p['category'] for p in products)]
    return {
        'store_name': 'My E-commerce Store',
        'total_products': total_products,
        'in_stock': in_stock_count,
        'out_of_stock': out_of_stock_count,
        'categories': category_list
    }


# Endpoint 5 — Search products by name ──────────────────────────
@app.get('/products/search/{product_name}')
def search_products(product_name: str):
    results = [p for p in products if product_name.lower() in p['name'].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {'products': results, 'total': len(results)}

#  Endpoint 6 — Filter products by price range ──────────────────────────
@app.get('/products/deals')
def get_deals():
    best_deal = min(products, key=lambda p: p['price'])
    premium_pick = max(products, key=lambda p: p['price'])
    return {
        'best_deal': best_deal,
        'premium_pick': premium_pick
    }