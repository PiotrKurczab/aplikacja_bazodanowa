import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QTableWidget, QPushButton, QLineEdit, QLabel, QTableWidgetItem, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
import csv
from database import Database
import sqlite3
import qdarktheme

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Database Operations')
        self.resize(800, 600)
        
        self.db = Database('database.db')
        self.db.populate_tables()
        
        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create a tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_customers_tab()
        self.create_orders_tab()
        self.create_products_tab()
        self.create_suppliers_tab()
        self.create_join_tab()
        
        # Create a layout and add the tab widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # Create buttons
        add_button = QPushButton("Add")
        delete_button = QPushButton("Delete")
        export_button = QPushButton("Export")
        import_button = QPushButton("Import")
        
        add_button.clicked.connect(self.add_record)
        delete_button.clicked.connect(self.delete_record)
        export_button.clicked.connect(self.export_database)
        import_button.clicked.connect(self.import_database)
        
        button_layout = QHBoxLayout()
        buttons = [add_button, delete_button, export_button, import_button]
        for button in buttons:
            button.setFixedWidth(100)
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)
        
        self.load_customers_data()
        self.load_orders_data()
        self.load_products_data()
        self.load_suppliers_data()
        self.load_join_data()
    
    def create_customers_tab(self):
        self.customers_tab = QWidget()
        layout = QVBoxLayout(self.customers_tab)
        
        # Search and filter textboxes
        search_label = QLabel("Search:")
        self.search_customers_textbox = QLineEdit()
        self.search_customers_textbox.textChanged.connect(self.search_customers)
        filter_label = QLabel("Filter by city:")
        self.filter_customers_textbox = QLineEdit()
        self.filter_customers_textbox.textChanged.connect(self.filter_customers)
        
        filter_name_label = QLabel("Filter by name:")
        self.filter_customers_name_textbox = QLineEdit()
        self.filter_customers_name_textbox.textChanged.connect(self.filter_customers)
        
        filter_email_label = QLabel("Filter by email:")
        self.filter_customers_email_textbox = QLineEdit()
        self.filter_customers_email_textbox.textChanged.connect(self.filter_customers)
        
        # Add search and filter textboxes to the layout
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_customers_textbox)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.filter_customers_textbox)
        search_layout.addWidget(filter_name_label)
        search_layout.addWidget(self.filter_customers_name_textbox)
        search_layout.addWidget(filter_email_label)
        search_layout.addWidget(self.filter_customers_email_textbox)
        
        layout.addLayout(search_layout)
        
        # Create a table widget
        self.customers_table_widget = QTableWidget()
        self.customers_table_widget.setSortingEnabled(True)
        layout.addWidget(self.customers_table_widget)
        
        self.customers_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_customers)
        self.tab_widget.addTab(self.customers_tab, "Customers")
    
    def create_orders_tab(self):
        self.orders_tab = QWidget()
        layout = QVBoxLayout(self.orders_tab)
        
        self.orders_table_widget = QTableWidget()
        self.orders_table_widget.setSortingEnabled(True)
        layout.addWidget(self.orders_table_widget)
        
        self.orders_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_orders)
        self.tab_widget.addTab(self.orders_tab, "Orders")
    
    def create_products_tab(self):
        self.products_tab = QWidget()
        layout = QVBoxLayout(self.products_tab)
        
        self.products_table_widget = QTableWidget()
        self.products_table_widget.setSortingEnabled(True)
        layout.addWidget(self.products_table_widget)
        
        self.products_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_products)
        self.tab_widget.addTab(self.products_tab, "Products")
    
    def create_suppliers_tab(self):
        self.suppliers_tab = QWidget()
        layout = QVBoxLayout(self.suppliers_tab)
        
        self.suppliers_table_widget = QTableWidget()
        self.suppliers_table_widget.setSortingEnabled(True)
        layout.addWidget(self.suppliers_table_widget)
        
        self.tab_widget.addTab(self.suppliers_tab, "Suppliers")
    
    def create_join_tab(self):
        self.join_tab = QWidget()
        layout = QVBoxLayout(self.join_tab)
        
        self.join_table_widget = QTableWidget()
        self.join_table_widget.setSortingEnabled(True)
        layout.addWidget(self.join_table_widget)
        
        self.join_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_join)
        self.tab_widget.addTab(self.join_tab, "Customer Orders")

    def load_customers_data(self):
        records = self.db.fetch_all_customers()
        self.customers_table_widget.setRowCount(len(records))
        self.customers_table_widget.setColumnCount(5)
        self.customers_table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.customers_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def load_orders_data(self):
        self.db.c.execute("SELECT * FROM orders")
        records = self.db.c.fetchall()
        self.orders_table_widget.setRowCount(len(records))
        self.orders_table_widget.setColumnCount(6)
        self.orders_table_widget.setHorizontalHeaderLabels(["ID", "Customer ID", "Product ID", "Date", "Amount", "Status"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.orders_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def load_products_data(self):
        self.db.c.execute("SELECT * FROM products")
        records = self.db.c.fetchall()
        self.products_table_widget.setRowCount(len(records))
        self.products_table_widget.setColumnCount(5)
        self.products_table_widget.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Stock"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.products_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def load_suppliers_data(self):
        self.db.c.execute("SELECT * FROM suppliers")
        records = self.db.c.fetchall()
        self.suppliers_table_widget.setRowCount(len(records))
        self.suppliers_table_widget.setColumnCount(5)
        self.suppliers_table_widget.setHorizontalHeaderLabels(["ID", "Name", "Contact", "Address", "Email"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.suppliers_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def load_join_data(self):
        records = self.db.fetch_customer_orders()
        self.join_table_widget.setRowCount(len(records))
        self.join_table_widget.setColumnCount(4)
        self.join_table_widget.setHorizontalHeaderLabels(["Customer ID", "Customer Name", "Order Date", "Order Amount"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.join_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def refresh_all_tabs(self):
        self.load_customers_data()
        self.load_orders_data()
        self.load_products_data()
        self.load_suppliers_data()
        self.load_join_data()

    def add_record(self):
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.customers_tab:
            self.add_customer()
        elif current_tab == self.orders_tab:
            self.add_order()
        elif current_tab == self.products_tab:
            self.add_product()
        elif current_tab == self.suppliers_tab:
            self.add_supplier()
        else:
            QMessageBox.warning(self, "Warning", "Add operation not supported for this tab")

    def delete_record(self):
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.customers_tab:
            self.delete_customers()
        elif current_tab == self.orders_tab:
            self.delete_orders()
        elif current_tab == self.products_tab:
            self.delete_products()
        elif current_tab == self.suppliers_tab:
            self.delete_suppliers()
        else:
            QMessageBox.warning(self, "Warning", "Delete operation not supported for this tab")

    def add_customer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Customer")
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        city_input = QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("City:", city_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            email = email_input.text()
            phone = phone_input.text()
            city = city_input.text()
            
            self.db.insert_customer(name, email, phone, city)
            self.refresh_all_tabs()

    def delete_customers(self):
        selected_items = self.customers_table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.customers_table_widget.item(row, 0).text()
                self.db.delete_customer(record_id)

            self.refresh_all_tabs()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    def add_order(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Order")
        
        layout = QFormLayout(dialog)
        
        customer_id_input = QLineEdit()
        product_id_input = QLineEdit()
        date_input = QLineEdit()
        amount_input = QLineEdit()
        status_input = QLineEdit()
        
        layout.addRow("Customer ID:", customer_id_input)
        layout.addRow("Product ID:", product_id_input)
        layout.addRow("Date:", date_input)
        layout.addRow("Amount:", amount_input)
        layout.addRow("Status:", status_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer_id = customer_id_input.text()
            product_id = product_id_input.text()
            date = date_input.text()
            amount = amount_input.text()
            status = status_input.text()
            
            self.db.c.execute("INSERT INTO orders (customer_id, product_id, date, amount, status) VALUES (?, ?, ?, ?, ?)", 
                              (customer_id, product_id, date, amount, status))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_orders(self):
        selected_items = self.orders_table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.orders_table_widget.item(row, 0).text()
                self.db.c.execute("DELETE FROM orders WHERE id = ?", (record_id,))
                self.db.conn.commit()

            self.refresh_all_tabs()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    def add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Product")
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        category_input = QLineEdit()
        price_input = QLineEdit()
        stock_input = QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Category:", category_input)
        layout.addRow("Price:", price_input)
        layout.addRow("Stock:", stock_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            category = category_input.text()
            price = price_input.text()
            stock = stock_input.text()
            
            self.db.c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?, ?)", 
                              (name, category, price, stock))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_products(self):
        selected_items = self.products_table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.products_table_widget.item(row, 0).text()
                self.db.c.execute("DELETE FROM products WHERE id = ?", (record_id,))
                self.db.conn.commit()

            self.refresh_all_tabs()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    def add_supplier(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Supplier")
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        contact_input = QLineEdit()
        address_input = QLineEdit()
        email_input = QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Contact:", contact_input)
        layout.addRow("Address:", address_input)
        layout.addRow("Email:", email_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_input.text()
            contact = contact_input.text()
            address = address_input.text()
            email = email_input.text()
            
            self.db.c.execute("INSERT INTO suppliers (name, contact, address, email) VALUES (?, ?, ?, ?, ?)", 
                              (name, contact, address, email))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_suppliers(self):
        selected_items = self.suppliers_table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.suppliers_table_widget.item(row, 0).text()
                self.db.c.execute("DELETE FROM suppliers WHERE id = ?", (record_id,))
                self.db.conn.commit()

            self.refresh_all_tabs()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    def export_database(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            tables = ["customers", "orders", "products", "suppliers"]
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for table in tables:
                    self.db.c.execute(f"SELECT * FROM {table}")
                    records = self.db.c.fetchall()
                    writer.writerow([table])
                    writer.writerow([i[0] for i in self.db.c.description])
                    writer.writerows(records)
                    writer.writerow([])  # Dodajemy pusty wiersz między tabelami
            QMessageBox.information(self, "Export", f"Exported to {file_name}")

    def import_database(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            with open(file_name, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                table = None
                headers = None
                self.db.conn.execute("PRAGMA foreign_keys = OFF;")
                for row in reader:
                    if not row:
                        continue
                    if row[0] in ["customers", "orders", "products", "suppliers"]:
                        table = row[0]
                        headers = next(reader)  # Skip the headers
                        self.db.c.execute(f"DELETE FROM {table}")  # Clear old data
                    else:
                        try:
                            columns = ', '.join(headers)
                            placeholders = ', '.join(['?' for _ in headers])
                            self.db.c.execute(f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})", row)
                        except sqlite3.Error as e:
                            print(f"Error importing record: {row}. {e}")
                self.db.conn.commit()
                self.db.conn.execute("PRAGMA foreign_keys = ON;")
            self.refresh_all_tabs()

    def search_customers(self, text):
        self.db.c.execute("SELECT * FROM customers WHERE name LIKE ?", ('%' + text + '%',))
        records = self.db.c.fetchall()
        self.update_customers_table(records)

    def filter_customers(self):
        filter_city = self.filter_customers_textbox.text()
        filter_name = self.filter_customers_name_textbox.text()
        filter_email = self.filter_customers_email_textbox.text()

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

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.update_customers_table(records)

    def update_customers_table(self, records):
        self.customers_table_widget.setRowCount(len(records))
        self.customers_table_widget.setColumnCount(5)
        self.customers_table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])
        
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.customers_table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def cell_double_clicked_customers(self, row, column):
        self.customers_table_widget.editItem(self.customers_table_widget.item(row, column))
        self.customers_table_widget.itemChanged.connect(self.update_database_customers)

    def update_database_customers(self, item):
        row = item.row()
        column = item.column()
        record_id = self.customers_table_widget.item(row, 0).text()  # Assuming the ID is in the first column
        new_value = item.text()

        column_name = self.customers_table_widget.horizontalHeaderItem(column).text().lower()
        
        self.db.update_customer(record_id, column_name, new_value)
        self.customers_table_widget.itemChanged.disconnect(self.update_database_customers)
        self.refresh_all_tabs()
        
    def cell_double_clicked_join(self, row, column):
        self.join_table_widget.editItem(self.join_table_widget.item(row, column))
        self.join_table_widget.itemChanged.connect(self.update_database_join)
        
    def update_database_join(self, item):
        row = item.row()
        column = item.column()
        record_id = self.join_table_widget.item(row, 0).text()
        new_value = item.text()

        column_name = self.join_table_widget.horizontalHeaderItem(column).text().lower()
        
        self.db.update_order(record_id, column_name, new_value)
        self.join_table_widget.itemChanged.disconnect(self.update_database_join)
        self.refresh_all_tabs()

    def cell_double_clicked_products(self, row, column):
        self.products_table_widget.editItem(self.products_table_widget.item(row, column))
        self.products_table_widget.itemChanged.connect(self.update_database_products)

    def update_database_products(self, item):
        row = item.row()
        column = item.column()
        record_id = self.products_table_widget.item(row, 0).text()
        new_value = item.text()

        column_name = self.products_table_widget.horizontalHeaderItem(column).text().lower()
        
        self.db.update_product(record_id, column_name, new_value)
        if column_name == 'price':
            self.db.update_orders_after_product_price_change(record_id, new_value)
        
        self.products_table_widget.itemChanged.disconnect(self.update_database_products)
        self.refresh_all_tabs()

    def cell_double_clicked_orders(self, row, column):
        self.orders_table_widget.editItem(self.orders_table_widget.item(row, column))
        self.orders_table_widget.itemChanged.connect(self.update_database_orders)

    def update_database_orders(self, item):
        row = item.row()
        column = item.column()
        record_id = self.orders_table_widget.item(row, 0).text()
        new_value = item.text()

        column_name = self.orders_table_widget.horizontalHeaderItem(column).text().lower()
        
        self.db.update_order(record_id, column_name, new_value)
        if column_name == 'amount':
            self.db.update_product_price_from_order(record_id, new_value)
        
        self.orders_table_widget.itemChanged.disconnect(self.update_database_orders)
        self.refresh_all_tabs()

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    qdarktheme.setup_theme("auto")
    
    mainWin.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()