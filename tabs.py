from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QLineEdit, QHBoxLayout, QLabel,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QInputDialog, QFileDialog, QMessageBox, QTableWidgetItem, QPushButton, QComboBox, QSlider, QListWidget, QCheckBox, QHBoxLayout, QListWidgetItem
)
from PyQt6.QtCore import Qt

class FilterWindow(QDialog):
    def __init__(self, parent=None, filter_fields=None, prev_filters=None):
        super().__init__(parent)
        self.setWindowTitle("Filter")
        self.filter_fields = filter_fields if filter_fields else {}
        self.prev_filters = prev_filters if prev_filters else {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.field_widgets = {}
        self.checkboxes = {}
        
        for field, options in self.filter_fields.items():
            field_layout = QHBoxLayout()
            checkbox = QCheckBox(self)
            checkbox.setChecked(self.prev_filters.get(field, {}).get("enabled", False))
            self.checkboxes[field] = checkbox

            field_label = QLabel(f"{field.capitalize()}:")
            field_layout.addWidget(checkbox)
            field_layout.addWidget(field_label)
            field_layout.addStretch(1)  # Add stretch to push the label and checkbox together
            form_layout.addRow(field_layout)

            if isinstance(options, list):
                list_widget = QListWidget(self)
                list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
                for option in options:
                    item = QListWidgetItem(str(option))
                    if str(option) in self.prev_filters.get(field, {}).get("values", []):
                        item.setSelected(True)
                    list_widget.addItem(item)
                form_layout.addRow(list_widget)
                self.field_widgets[field] = list_widget
            elif isinstance(options, tuple) and len(options) == 2:
                min_val, max_val = options
                min_input = QLineEdit(self)
                max_input = QLineEdit(self)
                min_input.setPlaceholderText(str(min_val))
                max_input.setPlaceholderText(str(max_val))
                min_input.setText(self.prev_filters.get(field, {}).get("min", ""))
                max_input.setText(self.prev_filters.get(field, {}).get("max", ""))
                slider_layout = QHBoxLayout()
                slider_layout.addWidget(min_input)
                slider_layout.addWidget(QLabel(" to "))
                slider_layout.addWidget(max_input)
                form_layout.addRow(slider_layout)
                self.field_widgets[field] = (min_input, max_input)
        
        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_filters(self):
        filters = {}
        for field, widget in self.field_widgets.items():
            if self.checkboxes[field].isChecked():
                if isinstance(widget, QListWidget):
                    filters[field] = {
                        "enabled": True,
                        "values": [item.text() for item in widget.selectedItems()]
                    }
                elif isinstance(widget, tuple) and len(widget) == 2:
                    min_input, max_input = widget
                    filters[field] = {
                        "enabled": True,
                        "min": min_input.text(),
                        "max": max_input.text()
                    }
            else:
                filters[field] = {
                    "enabled": False
                }
        return filters

class BaseTab(QWidget):
    def __init__(self, db, columns):
        super().__init__()
        self.db = db
        self.columns = columns
        self.filters = {}
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
        filter_window = FilterWindow(self, filter_fields, self.filters)
        if filter_window.exec() == QDialog.DialogCode.Accepted:
            self.filters = filter_window.get_filters()
            self.apply_filters(self.filters)

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
        filters = self.filters
        query = "SELECT * FROM customers WHERE name LIKE ?"
        params = [f"%{search_text}%"]
        
        city_filters = filters.get("City", {})
        if city_filters.get("enabled", False):
            city = city_filters.get("values", [])
            if city:
                query += f" AND city IN ({','.join(['?'] * len(city))})"
                params.extend(city)
        
        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        cities = self.db.get_column_unique_values("customers", "city")
        return {"City": cities}

    def apply_filters(self, filters):
        self.filters = filters
        self.search_data()

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

    def search_data(self):
        search_text = self.search_textbox.text()
        filters = self.filters
        query = "SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE name LIKE ?)"
        params = [f"%{search_text}%"]

        customer_filters = filters.get("Customer ID", {})
        product_filters = filters.get("Product ID", {})
        status_filters = filters.get("Status", {})
        amount_filters = filters.get("Amount", {})

        if customer_filters.get("enabled", False):
            customers = customer_filters.get("values", [])
            if customers:
                query += f" AND customer_id IN ({','.join(['?'] * len(customers))})"
                params.extend(customers)

        if product_filters.get("enabled", False):
            products = product_filters.get("values", [])
            if products:
                query += f" AND product_id IN ({','.join(['?'] * len(products))})"
                params.extend(products)

        if status_filters.get("enabled", False):
            statuses = status_filters.get("values", [])
            if statuses:
                query += f" AND status IN ({','.join(['?'] * len(statuses))})"
                params.extend(statuses)

        if amount_filters.get("enabled", False):
            min_amount = amount_filters.get("min", 0)
            max_amount = amount_filters.get("max", float('inf'))
            query += " AND amount BETWEEN ? AND ?"
            params.extend([min_amount, max_amount])

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        customers = self.db.get_column_unique_values("orders", "customer_id")
        products = self.db.get_column_unique_values("orders", "product_id")
        statuses = self.db.get_column_unique_values("orders", "status")
        min_amount, max_amount = self.db.get_min_max_value("orders", "amount")
        return {
            "Customer ID": customers,
            "Product ID": products,
            "Status": statuses,
            "Amount": (min_amount, max_amount)
        }

    def apply_filters(self, filters):
        self.filters = filters
        self.search_data()

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
        filters = self.filters
        query = "SELECT * FROM products WHERE name LIKE ?"
        params = [f"%{search_text}%"]

        category_filters = filters.get("Category", {})
        price_filters = filters.get("Price", {})
        stock_filters = filters.get("Stock", {})

        if category_filters.get("enabled", False):
            categories = category_filters.get("values", [])
            if categories:
                query += f" AND category IN ({','.join(['?'] * len(categories))})"
                params.extend(categories)

        if price_filters.get("enabled", False):
            min_price = price_filters.get("min", 0)
            max_price = price_filters.get("max", float('inf'))
            query += " AND price BETWEEN ? AND ?"
            params.extend([min_price, max_price])

        if stock_filters.get("enabled", False):
            min_stock = stock_filters.get("min", 0)
            max_stock = stock_filters.get("max", float('inf'))
            query += " AND stock BETWEEN ? AND ?"
            params.extend([min_stock, max_stock])

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        categories = self.db.get_column_unique_values("products", "category")
        min_price, max_price = self.db.get_min_max_value("products", "price")
        min_stock, max_stock = self.db.get_min_max_value("products", "stock")
        return {"Category": categories, "Price": (min_price, max_price), "Stock": (min_stock, max_stock)}

    def apply_filters(self, filters):
        self.filters = filters
        self.search_data()

class SuppliersTab(BaseTab):
    def __init__(self, db):
        columns = ["ID", "Name", "Contact", "Address", "Email"]
        super().__init__(db, columns)
        self.table_name = "suppliers"
        self.entity_name = "Supplier"
        self.reload_data()

    def init_ui(self):
        self.table_widget = QTableWidget()
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_widget)

        self.table_widget.cellDoubleClicked.connect(self.cell_double_clicked)

    def reload_data(self):
        self.db.c.execute("SELECT * FROM suppliers")
        records = self.db.c.fetchall()
        self.load_data(records)

class JoinTab(BaseTab):
    def __init__(self, db):
        columns = ["Customer ID", "Customer Name", "Order Date", "Order Amount", "Product Name", "Product Price"]
        super().__init__(db, columns)
        self.table_name = "customer_orders"
        self.entity_name = "Customer Order"
        self.reload_data()

    def reload_data(self):
        records = self.db.fetch_customer_orders()
        self.load_data(records)

    def search_data(self):
        search_text = self.search_textbox.text()
        filters = self.filters
        query = '''
            SELECT customers.id, customers.name, orders.date, orders.amount, products.name, products.price
            FROM customers
            JOIN orders ON customers.id = orders.customer_id
            JOIN products ON orders.product_id = products.id
            WHERE customers.name LIKE ?
        '''
        params = [f"%{search_text}%"]

        amount_filters = filters.get("Order Amount", {})
        price_filters = filters.get("Product Price", {})

        if amount_filters.get("enabled", False):
            min_amount = amount_filters.get("min", 0)
            max_amount = amount_filters.get("max", float('inf'))
            query += " AND orders.amount BETWEEN ? AND ?"
            params.extend([min_amount, max_amount])

        if price_filters.get("enabled", False):
            min_price = price_filters.get("min", 0)
            max_price = price_filters.get("max", float('inf'))
            query += " AND products.price BETWEEN ? AND ?"
            params.extend([min_price, max_price])

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.load_data(records)

    def get_filter_fields(self):
        min_amount, max_amount = self.db.get_min_max_value("orders", "amount")
        min_price, max_price = self.db.get_min_max_value("products", "price")
        return {
            "Order Amount": (min_amount, max_amount),
            "Product Price": (min_price, max_price)
        }

    def apply_filters(self, filters):
        self.filters = filters
        self.search_data()
        
    # Override the following methods to disable editing, adding, and deleting records
    def cell_double_clicked(self, row, column):
        QMessageBox.warning(self, "Warning", "Editing is not allowed in this tab.")
        
    def add_record(self):
        QMessageBox.warning(self, "Warning", "Adding is not allowed in this tab.")
        
    def delete_record(self):
        QMessageBox.warning(self, "Warning", "Deleting is not allowed in this tab.")