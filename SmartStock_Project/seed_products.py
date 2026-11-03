"""Seed a demo inventory and low-stock examples in smartstock.db."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("smartstock.db")

PRODUCT_GROUPS = {
    "Grocery": (["Rice", "Pasta", "Cooking Oil", "Flour", "Sugar"], ["Premium", "Everyday", "Harvest", "Select", "Value"]),
    "Beverages": (["Bottled Water", "Orange Juice", "Iced Tea", "Coffee", "Green Tea"], ["Classic", "Zero Sugar", "Original", "Refreshing", "Light"]),
    "Snacks": (["Potato Chips", "Crackers", "sCookies", "Popcorn", "Chocolate Bar"], ["Original", "Cheese", "Barbecue", "Sea Salt", "Spicy"]),
    "Canned Goods": (["Tuna", "Sardines", "Corn", "Beef Loaf", "Fruit Cocktail"], ["Original", "Hot and Spicy", "Tomato Sauce", "Sweet Style", "Family Size"]),
    "Personal Care": (["Bath Soap", "Shampoo", "Toothpaste", "Body Lotion", "Deodorant"], ["Fresh", "Sensitive", "Moisture Care", "Herbal", "Daily"]),
    "Household": (["Laundry Detergent", "Dishwashing Liquid", "Fabric Conditioner", "Multipurpose Cleaner", "Trash Bags"], ["Lemon", "Fresh Breeze", "Original", "Antibacterial", "Value Pack"]),
    "School Supplies": (["Notebook", "Ballpoint Pen", "Pencil", "Crayons", "Bond Paper"], ["Blue", "Black", "Assorted", "Ruled", "Premium"]),
    "Electronics": (["USB Cable", "Earphones", "Wireless Mouse", "LED Bulb", "Power Bank"], ["Basic", "Plus", "Compact", "Pro", "Travel"]),
    "Pet Supplies": (["Dog Food", "Cat Food", "Pet Shampoo", "Cat Litter", "Dog Treats"], ["Puppy", "Adult", "Chicken", "Beef", "Salmon"]),
    "Kitchenware": (["Dinner Plate", "Drinking Glass", "Food Container", "Frying Pan", "Water Bottle"], ["Small", "Medium", "Large", "Classic", "Durable"]),
}

LOW_STOCK_PRODUCTS = [
    ("Brown Sugar 1kg", "Grocery", 78.00),
    ("Chicken Instant Noodles", "Grocery", 18.00),
    ("UHT Milk 1L", "Grocery", 92.00),
    ("Lime Sparkling Water", "Beverages", 45.00),
    ("Apple Juice Box", "Beverages", 22.00),
    ("Trail Mix Pack", "Snacks", 65.00),
    ("Roasted Seaweed Snack", "Snacks", 38.00),
    ("Mackerel in Tomato Sauce", "Canned Goods", 54.00),
    ("Chickpeas Can", "Canned Goods", 49.00),
    ("Hand Sanitizer 100ml", "Personal Care", 35.00),
    ("Cotton Buds Pack", "Personal Care", 28.00),
    ("Paper Towels 2-Pack", "Household", 88.00),
    ("AA Batteries 4-Pack", "Household", 115.00),
    ("Highlighter Set", "School Supplies", 72.00),
    ("Correction Tape", "School Supplies", 32.00),
    ("USB-C Wall Charger", "Electronics", 399.00),
    ("Wireless Earbuds Case", "Electronics", 249.00),
    ("Cat Litter 5L", "Pet Supplies", 189.00),
    ("Dog Training Pads", "Pet Supplies", 159.00),
    ("Measuring Cup Set", "Kitchenware", 135.00),
]


def main():
    with sqlite3.connect(DB_PATH) as conn:
        existing = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        remaining = max(0, 250 - existing)
        rows = []
        for category_index, (category, (products, variants)) in enumerate(PRODUCT_GROUPS.items()):
            for product in products:
                for variant_index, variant in enumerate(variants):
                    if len(rows) >= remaining:
                        break
                    name = f"{variant.strip()} {product}"
                    price = round(25 + category_index * 17.5 + variant_index * 8.25 + products.index(product) * 3.5, 2)
                    quantity = 10 + ((category_index * 19 + variant_index * 7 + products.index(product) * 11) % 91)
                    rows.append((name, category, price, quantity))
                if len(rows) >= remaining:
                    break
            if len(rows) >= remaining:
                break
        conn.executemany(
            "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
            rows,
        )
        existing_names = {
            row[0] for row in conn.execute("SELECT name FROM products").fetchall()
        }
        low_stock_rows = [
            (name, category, price, 1 + index % 5)
            for index, (name, category, price) in enumerate(LOW_STOCK_PRODUCTS)
            if name not in existing_names
        ]
        conn.executemany(
            "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
            low_stock_rows,
        )
        total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        low_stock = conn.execute(
            "SELECT COUNT(*) FROM products WHERE quantity <= 5"
        ).fetchone()[0]
        print(
            f"Added {len(rows)} regular products and {len(low_stock_rows)} low-stock products. "
            f"Database now contains {total} products, including {low_stock} low-stock items."
        )


if __name__ == "__main__":
    main()
