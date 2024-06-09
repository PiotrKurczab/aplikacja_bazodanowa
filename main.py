import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
import sqlite3
import csv

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Database Operations')
        self.resize(800, 600)
        
        # Connect to database
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.create_tables()
        self.populate_tables()
        
        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create a grid layout for the central widget
        grid_layout = QGridLayout(central_widget)

        # Create search and filter textboxes
        search_label = QLabel("Search:")
        self.search_textbox = QLineEdit()
        self.search_textbox.textChanged.connect(self.search_record)
        filter_label = QLabel("Filter by city:")
        self.filter_textbox = QLineEdit()
        self.filter_textbox.textChanged.connect(self.filter_records)
        
        filter_name_label = QLabel("Filter by name:")
        self.filter_name_textbox = QLineEdit()
        self.filter_name_textbox.textChanged.connect(self.filter_records)

        filter_email_label = QLabel("Filter by email:")
        self.filter_email_textbox = QLineEdit()
        self.filter_email_textbox.textChanged.connect(self.filter_records)

        # Add search and filter textboxes to the grid layout
        grid_layout.addWidget(search_label, 0, 0)
        grid_layout.addWidget(self.search_textbox, 0, 1)
        grid_layout.addWidget(filter_label, 0, 2)
        grid_layout.addWidget(self.filter_textbox, 0, 3)
        grid_layout.addWidget(filter_name_label, 0, 4)
        grid_layout.addWidget(self.filter_name_textbox, 0, 5)
        grid_layout.addWidget(filter_email_label, 0, 6)
        grid_layout.addWidget(self.filter_email_textbox, 0, 7)

        # Create a table widget
        self.table_widget = QTableWidget()
        grid_layout.addWidget(self.table_widget, 1, 0, 1, 8)
        
        # Create buttons
        add_button = QPushButton("Add")
        delete_button = QPushButton("Delete")
        sort_button = QPushButton("Sort by name")
        export_button = QPushButton("Export")
        import_button = QPushButton("Import")
        
        add_button.clicked.connect(self.add_record)
        delete_button.clicked.connect(self.delete_record)
        sort_button.clicked.connect(self.sort_records)
        export_button.clicked.connect(self.export_records)
        import_button.clicked.connect(self.import_records)
        
        button_layout = QVBoxLayout()
        buttons = [add_button, delete_button, sort_button, export_button, import_button]
        for button in buttons:
            button.setFixedWidth(100)
            button_layout.addWidget(button)
        grid_layout.addLayout(button_layout, 1, 8, 1, 1)

        self.load_data()
        
        # Connect the cell double-clicked signal to the edit method
        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        self.sort_order = Qt.AscendingOrder

    def create_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, city TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer_id INTEGER, date TEXT, amount REAL, status TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, address TEXT, email TEXT)''')
        self.conn.commit()

    def populate_tables(self):
        self.c.execute("DELETE FROM customers")
        self.c.execute("DELETE FROM orders")
        self.c.execute("DELETE FROM products")
        self.c.execute("DELETE FROM suppliers")

        customers = [
            (1, 'Alice', 'alice@example.com', '555-0100', 'New York'),
            (2, 'Bob', 'bob@example.com', '555-0150', 'Los Angeles'),
            (3, 'Charlie', 'charlie@example.com', '555-0200', 'Chicago'),
            (4, 'David', 'david@example.com', '555-0250', 'Houston'),
            (5, 'Eva', 'eva@example.com', '555-0300', 'Phoenix')
        ]
        
        orders = [
            (1, 1, '2023-06-01', 150.00, 'Shipped'),
            (2, 2, '2023-06-02', 200.00, 'Pending'),
            (3, 3, '2023-06-03', 300.00, 'Delivered'),
            (4, 4, '2023-06-04', 400.00, 'Cancelled'),
            (5, 5, '2023-06-05', 500.00, 'Returned')
        ]
        
        products = [
            (1, 'Laptop', 'Electronics', 999.99, 10),
            (2, 'Smartphone', 'Electronics', 499.99, 25),
            (3, 'Tablet', 'Electronics', 299.99, 30),
            (4, 'Monitor', 'Electronics', 199.99, 20),
            (5, 'Keyboard', 'Accessories', 49.99, 50)
        ]
        
        suppliers = [
            (1, 'Supplier A', 'contactA@example.com', 'Address A', 'supplierA@example.com'),
            (2, 'Supplier B', 'contactB@example.com', 'Address B', 'supplierB@example.com'),
            (3, 'Supplier C', 'contactC@example.com', 'Address C', 'supplierC@example.com'),
            (4, 'Supplier D', 'contactD@example.com', 'Address D', 'supplierD@example.com'),
            (5, 'Supplier E', 'contactE@example.com', 'Address E', 'supplierE@example.com')
        ]

        self.c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)
        self.c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
        self.c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
        self.c.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?)", suppliers)
        self.conn.commit()

    def load_data(self):
        self.c.execute("SELECT * FROM customers")
        records = self.c.fetchall()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def add_record(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Record")
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        city_input = QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("City:", city_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            email = email_input.text()
            phone = phone_input.text()
            city = city_input.text()
            
            self.c.execute("INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)", (name, email, phone, city))
            self.conn.commit()
            self.load_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.table_widget.item(row, 0).text()
                self.c.execute("DELETE FROM customers WHERE id = ?", (record_id,))

            self.conn.commit()
            self.load_data()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    def search_record(self, text):
        self.c.execute("SELECT * FROM customers WHERE name LIKE ?", ('%' + text + '%',))
        records = self.c.fetchall()
        self.update_table(records)

    def sort_records(self):
        self.c.execute("SELECT * FROM customers ORDER BY name")
        records = self.c.fetchall()
        self.update_table(records)

    def filter_records(self):
        filter_city = self.filter_textbox.text()
        filter_name = self.filter_name_textbox.text()
        filter_email = self.filter_email_textbox.text()

        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if filter_city:
            query += " AND city LIKE ?"
            params.append('%' + filter_city + '%')
        if filter_name:
            query += " AND name LIKE ?"
            params.append('%' + filter_name + '%')
        if filter_email:
            query += " AND email LIKE ?"
            params.append('%' + filter_email + '%')

        self.c.execute(query, params)
        records = self.c.fetchall()
        self.update_table(records)

    def export_records(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                self.c.execute("SELECT * FROM customers")
                records = self.c.fetchall()
                writer.writerow([i[0] for i in self.c.description])
                writer.writerows(records)
            QMessageBox.information(self, "Export", f"Exported to {file_name}")

    def import_records(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, mode='r') as file:
                reader = csv.reader(file)
                headers = next(reader)
                records = [tuple(row) for row in reader]
                for record in records:
                    try:
                        self.c.execute("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?)", record)
                    except sqlite3.Error as e:
                        print(f"Error importing record: {record}. {e}")
                self.conn.commit()
            self.load_data()

    def update_table(self, records):
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
    
    def cell_double_clicked(self, row, column):
        self.table_widget.editItem(self.table_widget.item(row, column))
        self.table_widget.itemChanged.connect(self.update_database)

    def update_database(self, item):
        row = item.row()
        column = item.column()
        record_id = self.table_widget.item(row, 0).text()  # Assuming the ID is in the first column
        new_value = item.text()

        column_name = self.table_widget.horizontalHeaderItem(column).text().lower()
        
        self.c.execute(f"UPDATE customers SET {column_name} = ? WHERE id = ?", (new_value, record_id))
        self.conn.commit()
        self.table_widget.itemChanged.disconnect(self.update_database)

    def sort_by_column(self, column_index):
        header = self.table_widget.horizontalHeaderItem(column_index).text().lower()
        query = f"SELECT * FROM customers ORDER BY {header}"

        if self.sort_order == Qt.AscendingOrder:
            self.sort_order = Qt.DescendingOrder
        else:
            self.sort_order = Qt.AscendingOrder
        
        self.c.execute(query)
        records = self.c.fetchall()
        self.update_table(records)

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()