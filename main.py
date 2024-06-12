import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QTableWidget, QPushButton, QLineEdit, QLabel, QTableWidgetItem, QDialog,
    QDialogButtonBox, QFormLayout, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
import csv
from database import Database
import qdarktheme
import sqlite3

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
        self.create_tab("Customers", self.create_customers_tab, self.load_data)
        self.create_tab("Orders", self.create_orders_tab, self.load_data)
        self.create_tab("Products", self.create_products_tab, self.load_data)
        self.create_tab("Suppliers", self.create_suppliers_tab, self.load_data)
        self.create_tab("Customer Orders", self.create_join_tab, self.load_join_data)
        
        # Create a layout and add the tab widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # Create buttons
        self.create_buttons(main_layout)
        
        self.refresh_all_tabs()
    
    def create_tab(self, name, create_method, load_method):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        create_method(layout)
        self.tab_widget.addTab(tab, name)
        load_method(name.lower())
    
    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        buttons = [
            ("Add", self.add_record),
            ("Delete", self.delete_record),
            ("Export", self.export_database),
            ("Import", self.import_database)
        ]
        for text, slot in buttons:
            button = QPushButton(text)
            button.setFixedWidth(100)
            button.clicked.connect(slot)
            button_layout.addWidget(button)
        layout.addLayout(button_layout)
    
    def create_customers_tab(self, layout):
        self.create_search_filter_layout(layout, [
            ("Search:", self.search_customers),
            ("Filter by city:", self.filter_customers),
            ("Filter by name:", self.filter_customers),
            ("Filter by email:", self.filter_customers)
        ])
        self.customers_table_widget = self.create_table(layout)
    
    def create_orders_tab(self, layout):
        self.orders_table_widget = self.create_table(layout)
    
    def create_products_tab(self, layout):
        self.products_table_widget = self.create_table(layout)
    
    def create_suppliers_tab(self, layout):
        self.suppliers_table_widget = self.create_table(layout)
    
    def create_join_tab(self, layout):
        self.join_table_widget = self.create_table(layout)
    
    def create_search_filter_layout(self, layout, fields):
        search_layout = QHBoxLayout()
        for label_text, slot in fields:
            label = QLabel(label_text)
            textbox = QLineEdit()
            textbox.textChanged.connect(slot)
            search_layout.addWidget(label)
            search_layout.addWidget(textbox)
        layout.addLayout(search_layout)
    
    def create_table(self, layout):
        table_widget = QTableWidget()
        table_widget.setSortingEnabled(True)
        layout.addWidget(table_widget)
        return table_widget
    
    def load_data(self, table_name):
        table_widget = getattr(self, f"{table_name}_table_widget")
        records = self.db.fetch_all(table_name)
        self.update_table(table_widget, records, table_name)
    
    def load_join_data(self, _):
        records = self.db.fetch_customer_orders()
        self.update_table(self.join_table_widget, records, "customer orders")
    
    def update_table(self, table_widget, records, table_name):
        headers = {
            "customers": ["ID", "Name", "Email", "Phone", "City"],
            "orders": ["ID", "Customer ID", "Product ID", "Date", "Amount", "Status"],
            "products": ["ID", "Name", "Category", "Price", "Stock"],
            "suppliers": ["ID", "Name", "Contact", "Address", "Email"],
            "customer orders": ["Customer ID", "Customer Name", "Order Date", "Order Amount"]
        }
        table_widget.setRowCount(len(records))
        table_widget.setColumnCount(len(headers[table_name]))
        table_widget.setHorizontalHeaderLabels(headers[table_name])
        for row_num, row_data in enumerate(records):
            for col_num, col_data in enumerate(row_data):
                table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def refresh_all_tabs(self):
        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i).lower()
            if tab_name == "customer orders":
                self.load_join_data(tab_name)
            else:
                self.load_data(tab_name)

    def add_record(self):
        current_tab = self.tab_widget.currentWidget()
        tab_name = self.tab_widget.tabText(self.tab_widget.indexOf(current_tab)).lower()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {tab_name.capitalize()[:-1]}")
        layout = QFormLayout(dialog)
        
        fields = {
            "customers": [("Name", "name"), ("Email", "email"), ("Phone", "phone"), ("City", "city")],
            "orders": [("Customer ID", "customer_id"), ("Product ID", "product_id"), ("Date", "date"), ("Amount", "amount"), ("Status", "status")],
            "products": [("Name", "name"), ("Category", "category"), ("Price", "price"), ("Stock", "stock")],
            "suppliers": [("Name", "name"), ("Contact", "contact"), ("Address", "address"), ("Email", "email")]
        }
        
        inputs = {}
        for label, field in fields[tab_name]:
            input_widget = QLineEdit()
            layout.addRow(label, input_widget)
            inputs[field] = input_widget
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = [inputs[field].text() for field in inputs]
            self.db.c.execute(f"INSERT INTO {tab_name} ({', '.join(inputs.keys())}) VALUES ({', '.join(['?' for _ in inputs])})", values)
            self.db.conn.commit()
            self.refresh_all_tabs()

    def delete_record(self):
        current_tab = self.tab_widget.currentWidget()
        tab_name = self.tab_widget.tabText(self.tab_widget.indexOf(current_tab)).lower()
        table_widget = getattr(self, f"{tab_name}_table_widget")
        
        selected_items = table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sort in reverse order to delete from the end
            
            for row in rows:
                record_id = table_widget.item(row, 0).text()
                self.db.delete_record(tab_name, record_id)
            
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
                    records = self.db.fetch_all(table)
                    writer.writerow([table])
                    writer.writerow([desc[0] for desc in self.db.c.description])
                    writer.writerows(records)
                    writer.writerow([])  # Add an empty row between tables
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
                        self.db.clear_table(table)  # Clear old data
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
        self.filter_customers(text, self.filter_customers_textbox.text(), self.filter_customers_name_textbox.text(), self.filter_customers_email_textbox.text())

    def filter_customers(self, search="", city="", name="", email=""):
        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if search:
            query += " AND name LIKE ?"
            params.append(f'%{search}%')
        if city:
            query += " AND city LIKE ?"
            params.append(f'%{city}%')
        if name:
            query += " AND name LIKE ?"
            params.append(f'%{name}%')
        if email:
            query += " AND email LIKE ?"
            params.append(f'%{email}%')

        self.db.c.execute(query, params)
        records = self.db.c.fetchall()
        self.update_table(self.customers_table_widget, records, "customers")

    def cell_double_clicked(self, table_name, row, column):
        table_widget = getattr(self, f"{table_name}_table_widget")
        table_widget.editItem(table_widget.item(row, column))
        table_widget.itemChanged.connect(lambda item: self.update_database(table_name, item))

    def update_database(self, table_name, item):
        table_widget = getattr(self, f"{table_name}_table_widget")
        row = item.row()
        column = item.column()
        record_id = table_widget.item(row, 0).text()
        new_value = item.text()
        column_name = table_widget.horizontalHeaderItem(column).text().lower()
        
        self.db.update_record(table_name, record_id, column_name, new_value)
        table_widget.itemChanged.disconnect(lambda item: self.update_database(table_name, item))
        self.refresh_all_tabs()

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    qdarktheme.setup_theme("auto")
    
    mainWin.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()