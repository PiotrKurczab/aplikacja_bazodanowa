from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QLineEdit, QHBoxLayout, QLabel,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QInputDialog, QFileDialog, QMessageBox, QTableWidgetItem, QPushButton, QComboBox, QSlider
)
from PyQt6.QtCore import Qt

class BaseTab(QWidget):
    def __init__(self, db, columns):
        super().__init__()
        self.db = db
        self.columns = columns
        self.init_ui()

    def init_ui(self):
        self.table_widget = QTableWidget()
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_widget)

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)
        
        search_label = QLabel("Search:")
        self.search_textbox = QLineEdit()
        self.search_textbox.textChanged.connect(self.search_data)

        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.open_filter_window)

        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_textbox)
        search_layout.addWidget(self.filter_button)

        layout.addLayout(search_layout)

    def open_filter_window(self):
        filter_fields = self.get_filter_fields()
        filter_window = FilterWindow(self, filter_fields)
        if filter_window.exec() == QDialog.DialogCode.Accepted:
            filters = filter_window.get_filters()
            self.apply_filters(filters)

    def get_filter_fields(self):
        return {}

    def apply_filters(self, filters):
        pass

    def load_data(self, records):
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(len(self.columns))
        self.table_widget.setHorizontalHeaderLabels(self.columns)

        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def cell_double_clicked(self, row, column):
        record_id = self.table_widget.item(row, 0).text()
        column_name = self.table_widget.horizontalHeaderItem(column).text().lower()

        if column_name == "id":
            QMessageBox.warning(self, "Warning", "Editing the primary ID field is not allowed.")
            return

        if column_name == "amount" or column_name == "price":
            new_value, ok = self.get_input_dialog_double(f"New value for {column_name.capitalize()}:")
        else:
            new_value, ok = self.get_input_dialog_text(f"New value for {column_name.capitalize()}:")

        if ok:
            try:
                self.db.update_record(self.table_name, record_id, column_name, new_value)
                self.reload_data()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def add_record(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {self.entity_name}")

        layout = QFormLayout(dialog)
        inputs = {column: QLineEdit() for column in self.columns[1:]}  # exclude ID column

        for column, input_widget in inputs.items():
            layout.addRow(f"{column.capitalize()}:", input_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = [input_widget.text() for input_widget in inputs.values()]
            self.db.insert_record(self.table_name, values)
            self.reload_data()

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", f"No {self.entity_name.lower()} selected for deletion")
            return

        for item in selected_items:
            row = item.row()
            record_id = self.table_widget.item(row, 0).text()
            self.db.delete_record(self.table_name, record_id)

        self.reload_data()

    def get_input_dialog_text(self, label_text):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Edit Record")
        dialog.setLabelText(label_text)
        dialog.setOkButtonText("OK")
        dialog.setCancelButtonText("Cancel")
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.setTextValue(self.table_widget.currentItem().text())
            
        text_edit = dialog.findChild(QLineEdit)
        text_edit.returnPressed.connect(dialog.accept)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return text_edit.text(), True
        else:
            return "", False

    def get_input_dialog_double(self, label_text):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Edit Record")
        dialog.setLabelText(label_text)
        dialog.setOkButtonText("OK")
        dialog.setCancelButtonText("Cancel")
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.setDoubleDecimals(2)
        dialog.setDoubleMaximum(float('inf'))

        try:
            default_value = float(self.table_widget.currentItem().text())
        except ValueError:
            default_value = 0.0

        dialog.setDoubleValue(default_value)

        text_edit = dialog.findChild(QLineEdit)
        text_edit.returnPressed.connect(dialog.accept)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.doubleValue(), True
        else:
            return 0, False

    def search_data(self):
        pass

class FilterWindow(QDialog):
    def __init__(self, parent=None, filter_fields=None):
        super().__init__(parent)
        self.setWindowTitle("Filter")
        self.filter_fields = filter_fields if filter_fields else {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.field_widgets = {}
        
        for field, options in self.filter_fields.items():
            if isinstance(options, list):
                combo = QComboBox(self)
                combo.addItems([str(option) for option in options]) 
                form_layout.addRow(QLabel(f"{field.capitalize()}:"), combo)
                self.field_widgets[field] = combo
            elif isinstance(options, tuple) and len(options) == 2:
                min_val, max_val = options
                slider_layout = QHBoxLayout()
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(min_val)
                slider.setMaximum(max_val)
                slider.setTickPosition(QSlider.TickPosition.TicksBelow)
                slider.setTickInterval((max_val - min_val) // 10)
                slider_layout.addWidget(QLabel(f"{min_val}"))
                slider_layout.addWidget(slider)
                slider_layout.addWidget(QLabel(f"{max_val}"))
                form_layout.addRow(QLabel(f"{field.capitalize()}:"), slider_layout)
                self.field_widgets[field] = slider
        
        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_filters(self):
        filters = {}
        for field, widget in self.field_widgets.items():
            if isinstance(widget, QComboBox):
                filters[field] = widget.currentText()
            elif isinstance(widget, QSlider):
                filters[field] = widget.value()
        return filters

class CustomersTab(BaseTab):
    def __init__(self, db):
        columns = ["ID", "Name", "Email", "Phone", "City"]
        super().__init__(db, columns)
        self.table_name = "customers"
        self.entity_name = "Customer"
        self.reload_data()

    def reload_data(self):
        records = self.db.fetch_all_customers()
        self.load_data(records)

    def search_data(self):
        search_text = self.search_textbox.text()
        self.db.c.execute("SELECT * FROM customers WHERE name LIKE ?", (f"%{search_text}%",))
        records = self.db.c.fetchall()
        self.load_data(records)
    
    def get_filter_fields(self):
        cities = self.db.get_column_unique_values("customers", "city")
        return {"City": cities}

    def apply_filters(self, filters):
        city = filters.get("City", "")
        query = "SELECT * FROM customers WHERE city = ?" if city else "SELECT * FROM customers"
        params = (city,) if city else ()
        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

class OrdersTab(BaseTab):
    def __init__(self, db):
        columns = ["ID", "Customer ID", "Product ID", "Date", "Amount", "Status"]
        super().__init__(db, columns)
        self.table_name = "orders"
        self.entity_name = "Order"
        self.reload_data()

    def reload_data(self):
        self.db.c.execute("SELECT * FROM orders")
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        customers = self.db.get_column_unique_values("orders", "customer_id")
        products = self.db.get_column_unique_values("orders", "product_id")
        statuses = self.db.get_column_unique_values("orders", "status")
        return {
            "Customer ID": customers,
            "Product ID": products,
            "Status": statuses,
            "Date": (1, 31),  # Example date range
            "Amount": (1, 100)  # Example amount range
        }

    def apply_filters(self, filters):
        query = "SELECT * FROM orders WHERE 1=1"
        params = []

        for field, value in filters.items():
            if field in ["Customer ID", "Product ID", "Status"] and value:
                query += f" AND {field.lower().replace(' ', '_')} = ?"
                params.append(value)
            elif field == "Date":
                query += " AND date = ?"
                params.append(value)
            elif field == "Amount":
                query += " AND amount <= ?"
                params.append(value)
        
        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

class ProductsTab(BaseTab):
    def __init__(self, db):
        columns = ["ID", "Name", "Category", "Price", "Stock"]
        super().__init__(db, columns)
        self.table_name = "products"
        self.entity_name = "Product"
        self.reload_data()

    def reload_data(self):
        self.db.c.execute("SELECT * FROM products")
        records = self.db.c.fetchall()
        self.load_data(records)

    def search_data(self):
        search_text = self.search_textbox.text()
        self.db.c.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{search_text}%",))
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        categories = self.db.get_column_unique_values("products", "category")
        return {"Category": categories, "Price": (0, 10000), "Stock": (0, 100)}

    def apply_filters(self, filters):
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        for field, value in filters.items():
            if field == "Category" and value:
                query += f" AND {field.lower()} = ?"
                params.append(value)
            elif field == "Price":
                query += " AND price <= ?"
                params.append(value)
            elif field == "Stock":
                query += " AND stock <= ?"
                params.append(value)
        
        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

class SuppliersTab(BaseTab):
    def __init__(self, db):
        columns = ["ID", "Name", "Contact", "Address", "Email"]
        super().__init__(db, columns)
        self.table_name = "suppliers"
        self.entity_name = "Supplier"

        search_label = QLabel("Search:")
        self.search_textbox = QLineEdit()
        self.search_textbox.textChanged.connect(self.search_suppliers)

        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_textbox)

        self.layout().addLayout(search_layout)
        self.reload_data()

    def reload_data(self):
        self.db.c.execute("SELECT * FROM suppliers")
        records = self.db.c.fetchall()
        self.load_data(records)

    def search_suppliers(self):
        search_text = self.search_textbox.text()
        self.db.c.execute("SELECT * FROM suppliers WHERE name LIKE ?", (f"%{search_text}%",))
        records = self.db.c.fetchall()
        self.load_data(records)

class JoinTab(BaseTab):
    def __init__(self, db):
        columns = ["Customer ID", "Customer Name", "Order Date", "Order Amount", "Product Name", "Product Price"]
        super().__init__(db, columns)
        self.table_name = "customer_orders"
        self.entity_name = "Customer Order"

        search_label = QLabel("Search:")
        self.search_textbox = QLineEdit()
        self.search_textbox.textChanged.connect(self.search_customer_orders)

        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_textbox)

        self.layout().addLayout(search_layout)
        self.reload_data()

    def reload_data(self):
        records = self.db.fetch_customer_orders()
        self.load_data(records)

    def search_customer_orders(self):
        search_text = self.search_textbox.text()
        query = '''
            SELECT customers.id, customers.name, orders.date, orders.amount, products.name, products.price
            FROM customers
            JOIN orders ON customers.id = orders.customer_id
            JOIN products ON orders.product_id = products.id
            WHERE customers.name LIKE ?
        '''
        self.db.c.execute(query, (f"%{search_text}%",))
        records = self.db.c.fetchall()
        self.load_data(records)
        
    def get_filter_fields(self):
        return {
            "Order Date": (1, 31),  # Example date range
            "Order Amount": (1, 100),  # Example amount range
            "Product Name": self.db.get_column_unique_values("products", "name"),
            "Product Price": (0, 10000)
        }

    def apply_filters(self, filters):
        query = '''
            SELECT customers.id, customers.name, orders.date, orders.amount, products.name, products.price
            FROM customers
            JOIN orders ON customers.id = orders.customer_id
            JOIN products ON orders.product_id = products.id
            WHERE 1=1
        '''
        params = []

        if "Order Date" in filters:
            query += " AND orders.date = ?"
            params.append(filters["Order Date"])
        if "Order Amount" in filters:
            query += " AND orders.amount <= ?"
            params.append(filters["Order Amount"])
        if "Product Name" in filters:
            query += " AND products.name = ?"
            params.append(filters["Product Name"])
        if "Product Price" in filters:
            query += " AND products.price <= ?"
            params.append(filters["Product Price"])

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)