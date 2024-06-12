import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        tables = {
            "customers": '''CREATE TABLE IF NOT EXISTS customers (
                                id INTEGER PRIMARY KEY, 
                                name TEXT, 
                                email TEXT, 
                                phone TEXT, 
                                city TEXT)''',
            "orders": '''CREATE TABLE IF NOT EXISTS orders (
                             id INTEGER PRIMARY KEY, 
                             customer_id INTEGER,
                             product_id INTEGER,
                             date TEXT, 
                             amount REAL, 
                             status TEXT,
                             FOREIGN KEY(customer_id) REFERENCES customers(id),
                             FOREIGN KEY(product_id) REFERENCES products(id))''',
            "products": '''CREATE TABLE IF NOT EXISTS products (
                               id INTEGER PRIMARY KEY, 
                               name TEXT, 
                               category TEXT, 
                               price REAL, 
                               stock INTEGER)''',
            "suppliers": '''CREATE TABLE IF NOT EXISTS suppliers (
                                id INTEGER PRIMARY KEY, 
                                name TEXT, 
                                contact TEXT, 
                                address TEXT, 
                                email TEXT)'''
        }

        for table_name, create_statement in tables.items():
            self.c.execute(create_statement)
        self.conn.commit()

    def populate_tables(self):
        # Clear tables
        self.clear_table("customers")
        self.clear_table("orders")
        self.clear_table("products")
        self.clear_table("suppliers")

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

        self.bulk_insert("customers", customers)
        self.bulk_insert("orders", orders)
        self.bulk_insert("products", products)
        self.bulk_insert("suppliers", suppliers)

    def clear_table(self, table_name):
        self.c.execute(f"DELETE FROM {table_name}")
        self.conn.commit()

    def bulk_insert(self, table, data):
        placeholders = ', '.join(['?' for _ in data[0]])
        self.c.executemany(f"INSERT INTO {table} VALUES ({placeholders})", data)
        self.conn.commit()

    def fetch_all(self, table):
        self.c.execute(f"SELECT * FROM {table}")
        return self.c.fetchall()

    def fetch_customer_orders(self):
        self.c.execute('''SELECT customers.id, customers.name, orders.date, orders.amount 
                          FROM customers 
                          JOIN orders ON customers.id = orders.customer_id''')
        return self.c.fetchall()

    def insert_customer(self, name, email, phone, city):
        self.c.execute("INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)", (name, email, phone, city))
        self.conn.commit()

    def delete_record(self, table, record_id):
        self.c.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        self.conn.commit()

    def update_record(self, table, record_id, column, value):
        self.c.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (value, record_id))
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

    def update_customer_name_in_orders(self, customer_id, new_name):
        self.c.execute('''UPDATE orders 
                          SET customer_name = ? 
                          WHERE customer_id = ?''', (new_name, customer_id))
        self.conn.commit()

    def update_order_amount_in_customer_orders(self, order_id, new_amount):
        self.c.execute('''UPDATE customer_orders 
                          SET order_amount = ? 
                          WHERE order_id = ?''', (new_amount, order_id))
        self.conn.commit()

    def update_product_price_in_customer_orders(self, product_id, new_price):
        self.c.execute('''UPDATE customer_orders 
                          SET product_price = ? 
                          WHERE product_id = ?''', (new_price, product_id))
        self.conn.commit()

    def get_product_id_from_order(self, order_id):
        self.c.execute('''SELECT product_id FROM orders WHERE id = ?''', (order_id,))
        return self.c.fetchone()[0]