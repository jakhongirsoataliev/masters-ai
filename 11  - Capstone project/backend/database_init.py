#!/usr/bin/env python3
"""
Database initialization and data management script
"""
import sqlite3
import random
from datetime import datetime, timedelta
import json

class DatabaseInitializer:
    def __init__(self, db_path: str = "business_data.db"):
        self.db_path = db_path
    
    def create_extended_schema(self):
        """Create extended database schema with more realistic business data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS customers")
        cursor.execute("DROP TABLE IF EXISTS suppliers")
        cursor.execute("DROP TABLE IF EXISTS inventory_logs")
        
        # Create suppliers table
        cursor.execute('''
            CREATE TABLE suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact_email TEXT,
                phone TEXT,
                address TEXT,
                rating REAL DEFAULT 5.0
            )
        ''')
        
        # Create customers table with more fields
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                registration_date DATE,
                total_spent REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                preferred_category TEXT,
                last_purchase_date DATE
            )
        ''')
        
        # Create products table with more details
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                cost_price REAL,
                stock_quantity INTEGER,
                min_stock_level INTEGER DEFAULT 10,
                supplier_id INTEGER,
                last_updated DATE,
                description TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE,
                total_amount REAL,
                status TEXT,
                shipping_address TEXT,
                payment_method TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Create order_items table for detailed order information
        cursor.execute('''
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Create inventory logs table
        cursor.execute('''
            CREATE TABLE inventory_logs (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                change_type TEXT,
                quantity_change INTEGER,
                new_quantity INTEGER,
                timestamp DATETIME,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Extended database schema created successfully!")
    
    def populate_with_realistic_data(self):
        """Populate database with realistic business data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert suppliers
        suppliers = [
            ("TechCorp Supplies", "sales@techcorp.com", "+1-555-0101", "123 Tech Street, Silicon Valley, CA", 4.8),
            ("Global Electronics", "orders@globalelec.com", "+1-555-0102", "456 Circuit Ave, Austin, TX", 4.5),
            ("Furniture Plus", "contact@furnitureplus.com", "+1-555-0103", "789 Oak Lane, Portland, OR", 4.7),
            ("Home Appliances Co", "support@homeappliances.com", "+1-555-0104", "321 Main St, Chicago, IL", 4.6),
            ("Office Solutions", "sales@officesol.com", "+1-555-0105", "654 Business Blvd, New York, NY", 4.9)
        ]
        
        cursor.executemany(
            "INSERT INTO suppliers (name, contact_email, phone, address, rating) VALUES (?, ?, ?, ?, ?)",
            suppliers
        )
        
        # Insert realistic customers
        customers = [
            ("Alice Johnson", "alice.johnson@email.com", "+1-555-1001", "123 Elm St, Springfield, IL", "2024-01-15", 2450.75, "premium", "Electronics", "2024-08-01"),
            ("Bob Smith", "bob.smith@email.com", "+1-555-1002", "456 Oak Ave, Madison, WI", "2024-02-20", 1890.50, "active", "Furniture", "2024-07-28"),
            ("Carol Davis", "carol.davis@email.com", "+1-555-1003", "789 Pine Rd, Denver, CO", "2024-03-10", 3200.25, "premium", "Electronics", "2024-08-03"),
            ("David Wilson", "david.wilson@email.com", "+1-555-1004", "321 Maple Dr, Seattle, WA", "2024-01-05", 950.00, "active", "Appliances", "2024-07-30"),
            ("Emma Brown", "emma.brown@email.com", "+1-555-1005", "654 Cedar St, Boston, MA", "2024-02-28", 1650.80, "active", "Furniture", "2024-08-02"),
            ("Frank Miller", "frank.miller@email.com", "+1-555-1006", "987 Birch Ave, Miami, FL", "2024-04-12", 2890.45, "premium", "Electronics", "2024-08-04"),
            ("Grace Lee", "grace.lee@email.com", "+1-555-1007", "147 Spruce Ln, Phoenix, AZ", "2024-03-22", 1200.30, "active", "Appliances", "2024-07-29"),
            ("Henry Clark", "henry.clark@email.com", "+1-555-1008", "258 Willow St, Portland, OR", "2024-05-08", 1750.90, "active", "Furniture", "2024-08-01")
        ]
        
        cursor.executemany(
            "INSERT INTO customers (name, email, phone, address, registration_date, total_spent, status, preferred_category, last_purchase_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            customers
        )
        
        # Insert products with realistic data
        products = [
            ("MacBook Pro 14\"", "Electronics", 1999.99, 1600.00, 25, 5, 1, "2024-08-01", "Latest MacBook Pro with M3 chip"),
            ("iPhone 15 Pro", "Electronics", 999.99, 750.00, 45, 10, 1, "2024-08-01", "Latest iPhone with titanium design"),
            ("Samsung 65\" QLED TV", "Electronics", 1299.99, 950.00, 15, 3, 2, "2024-08-01", "4K QLED Smart TV"),
            ("Sony WH-1000XM5", "Electronics", 399.99, 280.00, 60, 15, 2, "2024-08-01", "Noise-canceling headphones"),
            ("Executive Office Chair", "Furniture", 599.99, 350.00, 20, 5, 3, "2024-08-01", "Ergonomic leather office chair"),
            ("Standing Desk", "Furniture", 449.99, 300.00, 12, 3, 3, "2024-08-01", "Height-adjustable standing desk"),
            ("Conference Table", "Furniture", 899.99, 600.00, 8, 2, 3, "2024-08-01", "Large conference room table"),
            ("Bookshelf Unit", "Furniture", 299.99, 180.00, 25, 8, 3, "2024-08-01", "5-tier wooden bookshelf"),
            ("Dyson V15 Vacuum", "Appliances", 749.99, 500.00, 30, 8, 4, "2024-08-01", "Cordless vacuum with laser detection"),
            ("KitchenAid Mixer", "Appliances", 379.99, 250.00, 18, 5, 4, "2024-08-01", "Stand mixer with multiple attachments"),
            ("Ninja Air Fryer", "Appliances", 129.99, 80.00, 40, 12, 4, "2024-08-01", "Large capacity air fryer"),
            ("Instant Pot Duo", "Appliances", 99.99, 65.00, 35, 10, 4, "2024-08-01", "Multi-use pressure cooker")
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, price, cost_price, stock_quantity, min_stock_level, supplier_id, last_updated, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            products
        )
        
        # Generate realistic orders for the past 3 months
        base_date = datetime(2024, 5, 1)
        order_id = 1
        
        for i in range(150):  # Generate 150 orders
            customer_id = random.randint(1, 8)
            order_date = base_date + timedelta(days=random.randint(0, 95))
            status = random.choices(
                ["completed", "pending", "shipped", "cancelled"],
                weights=[70, 15, 10, 5]
            )[0]
            payment_method = random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"])
            
            # Insert order
            cursor.execute(
                "INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                (customer_id, order_date.strftime("%Y-%m-%d"), 0, status, f"Address for customer {customer_id}", payment_method)
            )
            
            # Add order items
            num_items = random.randint(1, 4)
            total_amount = 0
            
            for _ in range(num_items):
                product_id = random.randint(1, 12)
                quantity = random.randint(1, 3)
                
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                unit_price = cursor.fetchone()[0]
                
                total_amount += unit_price * quantity
                
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, quantity, unit_price)
                )
            
            # Update order total
            cursor.execute(
                "UPDATE orders SET total_amount = ? WHERE id = ?",
                (total_amount, order_id)
            )
            
            order_id += 1
        
        # Generate inventory logs
        for product_id in range(1, 13):
            for _ in range(random.randint(5, 15)):
                change_type = random.choice(["restock", "sale", "adjustment", "return"])
                quantity_change = random.randint(-10, 50) if change_type != "sale" else -random.randint(1, 5)
                timestamp = base_date + timedelta(days=random.randint(0, 95), hours=random.randint(0, 23))
                
                cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
                current_stock = cursor.fetchone()[0]
                new_quantity = max(0, current_stock + quantity_change)
                
                cursor.execute(
                    "INSERT INTO inventory_logs (product_id, change_type, quantity_change, new_quantity, timestamp, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (product_id, change_type, quantity_change, new_quantity, timestamp.strftime("%Y-%m-%d %H:%M:%S"), f"Automated {change_type} entry")
                )
        
        conn.commit()
        conn.close()
        print(f"Database populated with realistic data!")
        print(f"- {len(suppliers)} suppliers")
        print(f"- {len(customers)} customers")
        print(f"- {len(products)} products")
        print(f"- 150 orders with multiple items")
        print(f"- Inventory logs for all products")

def main():
    """Main function to initialize database"""
    print("Initializing Business Intelligence Database...")
    
    db_init = DatabaseInitializer()
    
    # Create schema
    db_init.create_extended_schema()
    
    # Populate with data
    db_init.populate_with_realistic_data()
    
    print("\nDatabase initialization complete!")
    print("You can now run the main application with: streamlit run main.py")

if __name__ == "__main__":
    main()
