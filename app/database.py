import sqlite3
import csv
from PyQt6.QtCore import pyqtSignal, QObject

class Database(QObject):
    """
    Database class that handles all database operations.
    
    Attributes:
        record_updated (pyqtSignal): Signal emitted when a record is updated.
    """
    
    record_updated = pyqtSignal()

    def __init__(self):
        """
        Initializes the Database object.
        - Connects to an in-memory SQLite database.
        - Creates necessary tables.
        - Populates initial data.
        """
        super().__init__()
        self.conn = sqlite3.connect(":memory:")
        self.c = self.conn.cursor()
        self.create_tables()
        self.populate_initial_data()

    def create_tables(self):
        """
        Creates necessary tables in the SQLite database.
        - customers
        - orders
        - products
        - suppliers
        """
        self.c.execute('''CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL
        )''')
        
        self.c.execute('''CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )''')
        
        self.c.execute('''CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )''')
        
        self.c.execute('''CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            address TEXT NOT NULL,
            email TEXT NOT NULL
        )''')

    def populate_initial_data(self):
        """
        Populates the tables with initial data:
        - customers
        - products
        - orders
        - suppliers
        """
        customers = [
            ("Michał Kowalski", "michal.kowalski@gmail.com", "501-234-567", "Warszawa"),
            ("Anna Nowak", "a.nowak@example.com", "694-567-890", "Kraków"),
            ("Piotr Wiśniewski", "p.wisniewski@firma.pl", "789-012-345", "Gdańsk"),
            ("Katarzyna Wójcik", "kwojcik@mail.com", "234-567-890", "Wrocław"),
        ]
        self.c.executemany("INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)", customers)

        products = [
            ("Smartfon XYZ Pro", "Elektronika", 2499.99, 75),
            ("Laptop GamePro 5000", "Komputery", 4999.00, 20),
            ("Odkurzacz Turbo 2000", "AGD", 799.99, 50),
            ("Zestaw garnków Premium", "Dom i ogród", 599.00, 30),
        ]
        self.c.executemany("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products)

        orders = [
            (1, 3, "2023-04-22", 1, "Wysłane"),
            (2, 1, "2023-05-11", 2, "W realizacji"),
            (4, 2, "2023-06-03", 1, "Dostarczone"),
            (3, 4, "2023-05-28", 3, "Anulowane"),
        ]
        self.c.executemany("INSERT INTO orders (customer_id, product_id, date, amount, status) VALUES (?, ?, ?, ?, ?)", orders)

        suppliers = [
            ("MegaElektro S.A.", "Jan Kowalski", "ul. Przemysłowa 5, 00-123 Warszawa", "kontakt@megaelektro.pl"),
            ("AGDMaster", "Anna Wiśniewska", "ul. Handlowa 27, 80-200 Gdańsk", "obslugarc@agdmaster.com"),
            ("DomBytHouse", "Piotr Zieliński", "ul. Ogrodowa 12, 30-500 Kraków", "kontakt@dombyt.pl"),
            ("TopKomputery", "Katarzyna Adamczyk", "Al. Narodowa 31, 40-100 Wrocław", "biuro@topkomputery.pl"),
        ]
        self.c.executemany("INSERT INTO suppliers (name, contact, address, email) VALUES (?, ?, ?, ?)", suppliers)
        self.conn.commit()

    def fetch_all_customers(self):
        """
        Fetches all customers from the database.
        
        Returns:
            list: A list of tuples representing customers.
        """
        self.c.execute("SELECT * FROM customers")
        return self.c.fetchall()

    def fetch_customer_orders(self):
        """
        Fetches customer orders with customer and product details.
        
        Returns:
            list: A list of tuples representing customer orders.
        """
        self.c.execute('''SELECT customers.id, customers.name, orders.date, orders.amount, products.name, products.price
                          FROM customers
                          JOIN orders ON customers.id = orders.customer_id
                          JOIN products ON orders.product_id = products.id''')
        return self.c.fetchall()

    def delete_record(self, table, record_id):
        """
        Deletes a record from a table.
        
        Args:
            table (str): The name of the table.
            record_id (int): The ID of the record to delete.
        """
        self.c.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
        self.conn.commit()

    def update_record(self, table, record_id, column_name, new_value):
        """
        Updates a record in a table.
        
        Args:
            table (str): The name of the table.
            record_id (int): The ID of the record to update.
            column_name (str): The name of the column to update.
            new_value (str): The new value to set for the column.
        
        Raises:
            ValueError: If column_name is 'id' (primary key), as it cannot be updated.
        """
        if column_name.lower() == "id":
            raise ValueError("Cannot update the primary ID field")
        column_name = column_name.replace(" ", "_")
        self.c.execute(f'UPDATE "{table}" SET "{column_name}"=? WHERE id=?', (new_value, record_id))
        self.conn.commit()
        self.record_updated.emit()

    def export_to_csv(self, file_name):
        """
        Exports the database to a CSV file.
        
        Args:
            file_name (str): The name of the CSV file to export to.
        """
        tables = ["customers", "orders", "products", "suppliers"]

        with open(file_name, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            for table in tables:
                writer.writerow([table.capitalize()])
                self.c.execute(f"SELECT * FROM {table}")
                records = self.c.fetchall()
                writer.writerows(records)
                writer.writerow([])

    def import_from_csv(self, file_name):
        """
        Imports a database from a CSV file.
        
        Args:
            file_name (str): The name of the CSV file to import from.
        """
        for table in ["customers", "orders", "products", "suppliers"]:
            self.c.execute(f"DROP TABLE IF EXISTS {table}")
        
        self.create_tables()

        with open(file_name, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            table = None

            for row in reader:
                if not row:
                    continue
                if row[0].lower() in ["customers", "orders", "products", "suppliers"]:
                    table = row[0].lower()
                    continue
                if table:
                    if table == "customers":
                        self.c.execute("INSERT INTO customers (id, name, email, phone, city) VALUES (?, ?, ?, ?, ?)", row)
                    elif table == "orders":
                        self.c.execute("INSERT INTO orders (id, customer_id, product_id, date, amount, status) VALUES (?, ?, ?, ?, ?, ?)", row)
                    elif table == "products":
                        self.c.execute("INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)", row)
                    elif table == "suppliers":
                        self.c.execute("INSERT INTO suppliers (id, name, contact, address, email) VALUES (?, ?, ?, ?, ?)", row)

        self.conn.commit()

    def insert_record(self, table, values):
        """
        Inserts a new record into a table.
        
        Args:
            table (str): The name of the table.
            values (tuple): Tuple of values to insert into the table.
        """
        placeholders = ', '.join(['?'] * len(values))
        query = f"INSERT INTO {table} ({', '.join(self.get_column_names(table)[1:])}) VALUES ({placeholders})"
        self.c.execute(query, values)
        self.conn.commit()

    def get_column_names(self, table):
        """
        Retrieves column names for a given table.
        
        Args:
            table (str): The name of the table.
        
        Returns:
            list: A list of column names.
        """
        self.c.execute(f"PRAGMA table_info({table})")
        return [info[1] for info in self.c.fetchall()]

    def get_column_unique_values(self, table, column):
        """
        Retrieves unique values for a given column in a table.
        
        Args:
            table (str): The name of the table.
            column (str): The name of the column.
        
        Returns:
            list: A list of unique values in the specified column.
        """
        self.c.execute(f"SELECT DISTINCT {column} FROM {table}")
        return [row[0] for row in self.c.fetchall()]

    def get_min_max_value(self, table, column):
        """
        Retrieves the minimum and maximum value for a given column in a table.
        
        Args:
            table (str): The name of the table.
            column (str): The name of the column.
        
        Returns:
            tuple: A tuple containing the minimum and maximum values of the column.
        """
        self.c.execute(f"SELECT MIN({column}), MAX({column}) FROM {table}")
        return self.c.fetchone()