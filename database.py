import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY, 
                            name TEXT, 
                            email TEXT, 
                            phone TEXT, 
                            city TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY, 
                            customer_id INTEGER,
                            product_id INTEGER,
                            date TEXT, 
                            amount REAL, 
                            status TEXT,
                            FOREIGN KEY(customer_id) REFERENCES customers(id),
                            FOREIGN KEY(product_id) REFERENCES products(id))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY, 
                            name TEXT, 
                            category TEXT, 
                            price REAL, 
                            stock INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                            id INTEGER PRIMARY KEY, 
                            name TEXT, 
                            contact TEXT, 
                            address TEXT, 
                            email TEXT)''')
        self.conn.commit()

    def populate_tables(self):
        # Clear tables
        self.c.execute("DELETE FROM customers")
        self.c.execute("DELETE FROM orders")
        self.c.execute("DELETE FROM products")
        self.c.execute("DELETE FROM suppliers")
        
        # Sample data
        customers = [
            (1, 'Michał Kowalski', 'mkowalski@example.com', '501-123-456', 'Warszawa'),
            (2, 'Anna Wiśniewska', 'awisnia@example.com', '502-234-567', 'Kraków'),
            (3, 'Piotr Nowak', 'pnowak@example.com', '503-345-678', 'Wrocław'),
            (4, 'Katarzyna Lewandowska', 'klewand@example.com', '504-456-789', 'Gdańsk'),
            (5, 'Tomasz Zając', 'tzajac@example.com', '505-567-890', 'Poznań')
        ]
        
        orders = [
            (1, 1, 1, '2023-06-01', 2499.99, 'Zrealizowane'),
            (2, 2, 2, '2023-06-02', 499.99, 'W realizacji'),
            (3, 3, 3, '2023-06-03', 1299.99, 'Dostarczone'),
            (4, 4, 4, '2023-06-04', 899.99, 'Anulowane'),
            (5, 5, 5, '2023-06-05', 399.99, 'Zwrócone')
        ]

        products = [
            (1, 'Smartfon XYZ', 'Elektronika', 2499.99, 15),
            (2, 'Laptop GamePro', 'Elektronika', 4999.99, 8),
            (3, 'Tablet ArtPad', 'Elektronika', 1299.99, 20),
            (4, 'Monitor UltraHD', 'Elektronika', 1499.99, 12),
            (5, 'Drukarka LaserPro', 'Biuro', 399.99, 25)
        ]

        suppliers = [
            (1, 'TechPro Sp. z o.o.', 'info@techpro.pl', 'ul. Innowacyjna 1, Warszawa', 'zakupy@techpro.pl'),
            (2, 'GadgetMasters S.A.', 'kontakt@gadgetmasters.pl', 'Al. Cyfrowa 10, Kraków', 'zamowienia@gadgetmasters.pl'),
            (3, 'ElektroGalaktyka Sp.k.', 'biuro@elektrogalaktyka.pl', 'ul. Elektroniczna 25, Wrocław', 'zakupy@elektrogalaktyka.pl'),
            (4, 'CyberTech Sp. z o.o.', 'info@cybertech.pl', 'ul. Bitowa 12, Gdańsk', 'zamowienia@cybertech.pl'),
            (5, 'PrintExpert S.A.', 'kontakt@printexpert.pl', 'Al. Drukarska 5, Poznań', 'zakupy@printexpert.pl')
        ]

        # Populate tables
        self.c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)
        self.c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)
        self.c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
        self.c.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?)", suppliers)
        self.conn.commit()


    def fetch_all_customers(self):
        self.c.execute("SELECT * FROM customers")
        return self.c.fetchall()

    def fetch_customer_orders(self):
        self.c.execute('''SELECT customers.id, customers.name, orders.date, orders.amount 
                          FROM customers 
                          JOIN orders ON customers.id = orders.customer_id''')
        return self.c.fetchall()

    def insert_customer(self, name, email, phone, city):
        self.c.execute("INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)", (name, email, phone, city))
        self.conn.commit()

    def delete_customer(self, customer_id):
        self.c.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.conn.commit()

    def update_customer(self, customer_id, column, value):
        self.c.execute(f"UPDATE customers SET {column} = ? WHERE id = ?", (value, customer_id))
        self.conn.commit()
    
    def update_product(self, product_id, column, value):
        self.c.execute(f"UPDATE products SET {column} = ? WHERE id = ?", (value, product_id))
        self.conn.commit()

    def update_order(self, order_id, column, value):
        if column == "amount":
            self.c.execute("UPDATE orders SET amount = ? WHERE id = ?", (value, order_id))
        else:
            self.c.execute(f"UPDATE orders SET {column} = ? WHERE id = ?", (value, order_id))
        self.conn.commit()

    def update_supplier(self, supplier_id, column, value):
        self.c.execute(f"UPDATE suppliers SET {column} = ? WHERE id = ?", (value, supplier_id))
        self.conn.commit()

    def update_order_amount(self, order_id, value):
        self.c.execute("UPDATE orders SET amount = ? WHERE id = ?", (value, order_id))
        self.conn.commit()

    def update_order_date(self, order_id, value):
        self.c.execute("UPDATE orders SET date = ? WHERE id = ?", (value, order_id))
        self.conn.commit()
    
    def update_orders_after_product_price_change(self, product_id, new_price):
        self.c.execute('''UPDATE orders SET amount = ? WHERE product_id = ?''', (new_price, product_id))
        self.conn.commit()
        
    def update_product_price_from_order(self, order_id, new_price):
        self.c.execute('''UPDATE products 
                        SET price = ? 
                        WHERE id = (SELECT product_id 
                                    FROM orders 
                                    WHERE id = ?)''', (new_price, order_id))
        self.conn.commit()