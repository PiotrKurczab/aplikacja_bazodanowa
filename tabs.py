from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QLineEdit, QHBoxLayout, QLabel,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QInputDialog, QFileDialog, QMessageBox, QTableWidgetItem
)

class BaseTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.table_widget = QTableWidget()
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_widget)

    def load_data(self):
        raise NotImplementedError

    def add_record(self):
        raise NotImplementedError

    def delete_record(self):
        raise NotImplementedError

class CustomersTab(BaseTab):
    def __init__(self, db):
        super().__init__(db)
        search_label = QLabel("Search:")
        self.search_textbox = QLineEdit()
        self.search_textbox.textChanged.connect(self.search_customers)

        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_textbox)

        self.layout().addLayout(search_layout)

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)
        self.load_data()

    def load_data(self):
        records = self.db.fetch_all_customers()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def search_customers(self):
        search_text = self.search_textbox.text()
        self.db.c.execute("SELECT * FROM customers WHERE name LIKE ?", (f"%{search_text}%",))
        records = self.db.c.fetchall()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "City"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def cell_double_clicked(self, row, column):
        customer_id = self.table_widget.item(row, 0).text()
        column_name = self.table_widget.horizontalHeaderItem(column).text()

        new_value, ok = QInputDialog.getText(self, "Edit Customer", f"New value for {column_name}:")

        if ok:
            self.db.update_record("customers", customer_id, column_name.lower(), new_value)
            self.load_data()

    def add_record(self):
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
            self.load_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No customer selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            customer_id = self.table_widget.item(row, 0).text()
            self.db.delete_record("customers", customer_id)

        self.load_data()

class OrdersTab(BaseTab):
    def __init__(self, db):
        super().__init__(db)
        self.load_data()
    
    def load_data(self):
        self.db.c.execute("SELECT * FROM orders")
        records = self.db.c.fetchall()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Customer ID", "Product ID", "Date", "Amount", "Status"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)

    def cell_double_clicked(self, row, column):
        order_id = self.table_widget.item(row, 0).text()
        column_name = self.table_widget.horizontalHeaderItem(column).text()

        if column_name == "Amount":
            new_value, ok = QInputDialog.getDouble(self, "Edit Order Amount", f"New value for {column_name}:")
        else:
            new_value, ok = QInputDialog.getText(self, "Edit Order", f"New value for {column_name}:")

        if ok:
            self.db.update_record("orders", order_id, column_name.lower(), new_value)
            self.load_data()

    def add_record(self):
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
            self.load_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No order selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            order_id = self.table_widget.item(row, 0).text()
            self.db.delete_record("orders", order_id)

        self.load_data()

class ProductsTab(BaseTab):
    def __init__(self, db):
        super().__init__(db)
        self.load_data()
        
    def load_data(self):
        self.db.c.execute("SELECT * FROM products")
        records = self.db.c.fetchall()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Stock"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)

    def cell_double_clicked(self, row, column):
        product_id = self.table_widget.item(row, 0).text()
        column_name = self.table_widget.horizontalHeaderItem(column).text()

        if column_name == "Price":
            new_value, ok = QInputDialog.getDouble(self, "Edit Product Price", f"New value for {column_name}:")
        else:
            new_value, ok = QInputDialog.getText(self, "Edit Product", f"New value for {column_name}:")

        if ok:
            self.db.update_record("products", product_id, column_name.lower(), new_value)
            self.load_data()

    def add_record(self):
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
            self.load_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No product selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            product_id = self.table_widget.item(row, 0).text()
            self.db.delete_record("products", product_id)

        self.load_data()

class SuppliersTab(BaseTab):
    def __init__(self, db):
        super().__init__(db)
        self.load_data()
        
    def load_data(self):
        self.db.c.execute("SELECT * FROM suppliers")
        records = self.db.c.fetchall()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Contact", "Address", "Email"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def add_record(self):
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
            self.load_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No supplier selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            supplier_id = self.table_widget.item(row, 0).text()
            self.db.delete_record("suppliers", supplier_id)

        self.load_data()

class JoinTab(BaseTab):
    def __init__(self, db):
        super().__init__(db)
        self.load_data()
        
    def load_data(self):
        records = self.db.fetch_customer_orders()
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Customer ID", "Customer Name", "Order Date", "Order Amount", "Product Name", "Product Price"])

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)

    def cell_double_clicked(self, row, column):
        column_name = self.table_widget.horizontalHeaderItem(column).text()
        if column_name in ["Order Amount", "Product Price"]:
            record_id = self.table_widget.item(row, 0).text()  # assuming first column is ID

            if column_name == "Order Amount":
                new_value, ok = QInputDialog.getDouble(self, "Edit Order Amount", f"New value for {column_name}:")
                if ok:
                    self.db.update_record("orders", record_id, "amount", new_value)
            elif column_name == "Product Price":
                product_id = self.table_widget.item(row, 4).text()  # assuming fifth column is product ID
                new_value, ok = QInputDialog.getDouble(self, "Edit Product Price", f"New value for {column_name}:")
                if ok:
                    self.db.update_record("products", product_id, "price", new_value)

            self.load_data()
        else:
            QMessageBox.information(self, "Information", "Editing this data is not supported")