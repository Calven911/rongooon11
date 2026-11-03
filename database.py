import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Activity Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL
        )
    ''')

    # Default Admin User
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'Admin')")
    
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def log_activity(username, action):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, username, action) VALUES (?, ?, ?)", (now, username, action))
    conn.commit()
    conn.close()

def add_product(name, category, price, quantity):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
                   (name, category, price, quantity))
    conn.commit()
    conn.close()

def fetch_products(search_query=""):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    if search_query:
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", 
                       (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(product_id, name, category, price, quantity):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products 
        SET name = ?, category = ?, price = ?, quantity = ? 
        WHERE id = ?
    ''', (name, category, price, quantity, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()