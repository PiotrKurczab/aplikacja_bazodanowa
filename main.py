import sys
import sqlite3
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QTabWidget, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, 
    QInputDialog, QFileDialog, QLabel
)
from PyQt6.QtCore import Qt
import qdarktheme
from database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplikacja bazodanowa")
        self.resize(800, 600)

        self.db = Database()

        self.tab_widget = QTabWidget()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_record)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_record)
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.export_database)
        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_database)
        
        button_layout = QHBoxLayout()
        buttons = [add_button, delete_button, export_button, import_button]
        for button in buttons:
            button.setFixedWidth(100)
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)

        # Central widget setup
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.create_tabs()
        self.load_customers_data()
        self.load_orders_data()
        self.load_products_data()
        self.load_suppliers_data()
        self.load_join_data()
    
    def create_tabs(self):
        self.create_customers_tab()
        self.create_orders_tab()
        self.create_products_tab()
        self.create_suppliers_tab()
        self.create_join_tab()
    
    def create_customers_tab(self):
        self.customers_tab = QWidget()
        layout = QVBoxLayout(self.customers_tab)

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

        self.customers_table_widget = QTableWidget()
        self.customers_table_widget.setSortingEnabled(True)
        self.customers_table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.customers_table_widget)

        self.customers_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_customers)
        self.tab_widget.addTab(self.customers_tab, "Customers")

    def create_orders_tab(self):
        self.orders_tab = QWidget()
        layout = QVBoxLayout(self.orders_tab)

        self.orders_table_widget = QTableWidget()
        self.orders_table_widget.setSortingEnabled(True)
        self.orders_table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.orders_table_widget)

        self.orders_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_orders)
        self.tab_widget.addTab(self.orders_tab, "Orders")

    def create_products_tab(self):
        self.products_tab = QWidget()
        layout = QVBoxLayout(self.products_tab)

        self.products_table_widget = QTableWidget()
        self.products_table_widget.setSortingEnabled(True)
        self.products_table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.products_table_widget)

        self.products_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_products)
        self.tab_widget.addTab(self.products_tab, "Products")

    def create_suppliers_tab(self):
        self.suppliers_tab = QWidget()
        layout = QVBoxLayout(self.suppliers_tab)

        self.suppliers_table_widget = QTableWidget()
        self.suppliers_table_widget.setSortingEnabled(True)
        self.suppliers_table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.suppliers_table_widget)

        self.tab_widget.addTab(self.suppliers_tab, "Suppliers")

    def create_join_tab(self):
        self.join_tab = QWidget()
        layout = QVBoxLayout(self.join_tab)

        self.join_table_widget = QTableWidget()
        self.join_table_widget.setSortingEnabled(True)
        self.join_table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
        self.join_table_widget.setColumnCount(6)
        self.join_table_widget.setHorizontalHeaderLabels(["Customer ID", "Customer Name", "Order Date", "Order Amount", "Product Name", "Product Price"])

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

            self.db.c.execute("INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)", (name, email, phone, city))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_customers(self):
        selected_items = self.customers_table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No customer selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            customer_id = self.customers_table_widget.item(row, 0).text()
            self.db.delete_record("customers", customer_id)

        self.refresh_all_tabs()

    def cell_double_clicked_customers(self, row, column):
        customer_id = self.customers_table_widget.item(row, 0).text()
        column_name = self.customers_table_widget.horizontalHeaderItem(column).text()

        new_value, ok = QInputDialog.getText(self, "Edit Customer", f"New value for {column_name}:")

        if ok:
            self.db.update_record("customers", customer_id, column_name.lower(), new_value)
            self.refresh_all_tabs()

    def cell_double_clicked_orders(self, row, column):
        order_id = self.orders_table_widget.item(row, 0).text()
        column_name = self.orders_table_widget.horizontalHeaderItem(column).text()

        if column_name == "Amount":
            new_value, ok = QInputDialog.getDouble(self, "Edit Order Amount", f"New value for {column_name}:")
        else:
            new_value, ok = QInputDialog.getText(self, "Edit Order", f"New value for {column_name}:")

        if ok:
            self.db.update_record("orders", order_id, column_name.lower(), new_value)
            self.refresh_all_tabs()

    def cell_double_clicked_products(self, row, column):
        product_id = self.products_table_widget.item(row, 0).text()
        column_name = self.products_table_widget.horizontalHeaderItem(column).text()

        if column_name == "Price":
            new_value, ok = QInputDialog.getDouble(self, "Edit Product Price", f"New value for {column_name}:")
        else:
            new_value, ok = QInputDialog.getText(self, "Edit Product", f"New value for {column_name}:")

        if ok:
            self.db.update_record("products", product_id, column_name.lower(), new_value)
            self.refresh_all_tabs()

    def cell_double_clicked_join(self, row, column):
        # Editing join data should update relevant tables
        column_name = self.join_table_widget.horizontalHeaderItem(column).text()
        if column_name in ["Order Amount", "Product Price"]:
            record_id = self.join_table_widget.item(row, 0).text()  # assuming first column is ID

            if column_name == "Order Amount":
                new_value, ok = QInputDialog.getDouble(self, "Edit Order Amount", f"New value for {column_name}:")
                if ok:
                    self.db.update_record("orders", record_id, "amount", new_value)
            elif column_name == "Product Price":
                product_id = self.join_table_widget.item(row, 4).text()  # assuming fifth column is product ID
                new_value, ok = QInputDialog.getDouble(self, "Edit Product Price", f"New value for {column_name}:")
                if ok:
                    self.db.update_record("products", product_id, "price", new_value)
            
            self.refresh_all_tabs()
        else:
            QMessageBox.information(self, "Information", "Editing this data is not supported")

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
            
            self.db.c.execute("INSERT INTO orders (customer_id, product_id, date, amount, status) VALUES (?, ?, ?, ?, ?)", (customer_id, product_id, date, amount, status))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_orders(self):
        selected_items = self.orders_table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No order selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            order_id = self.orders_table_widget.item(row, 0).text()
            self.db.delete_record("orders", order_id)
        
        self.refresh_all_tabs()

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
            
            self.db.c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", (name, category, price, stock))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_products(self):
        selected_items = self.products_table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No product selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            product_id = self.products_table_widget.item(row, 0).text()
            self.db.delete_record("products", product_id)
        
        self.refresh_all_tabs()

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
            
            self.db.c.execute("INSERT INTO suppliers (name, contact, address, email) VALUES (?, ?, ?, ?)", (name, contact, address, email))
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_suppliers(self):
        selected_items = self.suppliers_table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No supplier selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            supplier_id = self.suppliers_table_widget.item(row, 0).text()
            self.db.delete_record("suppliers", supplier_id)
        
        self.refresh_all_tabs()

    def search_customers(self):
        search_text = self.search_customers_textbox.text().lower()
        self.filter_customers_data(search_text, self.filter_customers_textbox.text().lower())

    def filter_customers(self):
        filter_text = self.filter_customers_textbox.text().lower()
        self.filter_customers_data(self.search_customers_textbox.text().lower(), filter_text)

    def filter_customers_data(self, search_text, filter_text):
        filtered_data = []
        for row in range(self.customers_table_widget.rowCount()):
            name_item = self.customers_table_widget.item(row, 1)
            email_item = self.customers_table_widget.item(row, 2)
            phone_item = self.customers_table_widget.item(row, 3)
            city_item = self.customers_table_widget.item(row, 4)

            if (name_item and search_text in name_item.text().lower()) or \
                (email_item and search_text in email_item.text().lower()) or \
                (phone_item and search_text in phone_item.text().lower()) or \
                (city_item and filter_text in city_item.text().lower()):
                filtered_data.append(row)

        for row in range(self.customers_table_widget.rowCount()):
            self.customers_table_widget.setRowHidden(row, row not in filtered_data)

    def export_database(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("CSV Files (*.csv)")
        if file_dialog.exec():
            file_name = file_dialog.selectedFiles()[0]
            self.db.export_to_csv(file_name)
            QMessageBox.information(self, "Export Successful", f"Database exported to {file_name}")

    def import_database(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setNameFilter("CSV Files (*.csv)")
        if file_dialog.exec():
            file_name = file_dialog.selectedFiles()[0]
            self.db.import_from_csv(file_name)
            self.refresh_all_tabs()
            QMessageBox.information(self, "Import Successful", f"Database imported from {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())