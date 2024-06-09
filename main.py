import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QPushButton, QLineEdit, QLabel, QTableWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
import csv
from database import Database
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
        self.create_customers_tab()
        self.create_orders_tab()
        self.create_products_tab()
        self.create_suppliers_tab()
        self.create_join_tab()
        
        # Create a layout and add the tab widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
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
        
        # Create buttons
        add_button = QPushButton("Add")
        delete_button = QPushButton("Delete")
        export_button = QPushButton("Export")
        import_button = QPushButton("Import")
        
        add_button.clicked.connect(self.add_customer)
        delete_button.clicked.connect(self.delete_customers)
        export_button.clicked.connect(self.export_customers)
        import_button.clicked.connect(self.import_customers)
        
        button_layout = QHBoxLayout()
        buttons = [add_button, delete_button, export_button, import_button]
        for button in buttons:
            button.setFixedWidth(100)
            button_layout.addWidget(button)
        layout.addLayout(button_layout)
        
        self.customers_table_widget.cellDoubleClicked.connect(self.cell_double_clicked_customers)
        self.tab_widget.addTab(self.customers_tab, "Customers")
    
    def create_orders_tab(self):
        self.orders_tab = QWidget()
        layout = QVBoxLayout(self.orders_tab)
        
        self.orders_table_widget = QTableWidget()
        self.orders_table_widget.setSortingEnabled(True)
        layout.addWidget(self.orders_table_widget)
        
        self.tab_widget.addTab(self.orders_tab, "Orders")
    
    def create_products_tab(self):
        self.products_tab = QWidget()
        layout = QVBoxLayout(self.products_tab)
        
        self.products_table_widget = QTableWidget()
        self.products_table_widget.setSortingEnabled(True)
        layout.addWidget(self.products_table_widget)
        
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
        self.orders_table_widget.setColumnCount(5)
        self.orders_table_widget.setHorizontalHeaderLabels(["ID", "Customer ID", "Date", "Amount", "Status"])
        
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
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            email = email_input.text()
            phone = phone_input.text()
            city = city_input.text()
            
            self.db.insert_customer(name, email, phone, city)
            self.load_customers_data()

    def delete_customers(self):
        selected_items = self.customers_table_widget.selectedItems()
        if selected_items:
            rows = list(set(item.row() for item in selected_items))
            rows.sort(reverse=True)  # Sortujemy odwrotnie, aby usuwać od końca

            for row in rows:
                record_id = self.customers_table_widget.item(row, 0).text()
                self.db.delete_customer(record_id)

            self.load_customers_data()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

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

    def export_customers(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                self.db.c.execute("SELECT * FROM customers")
                records = self.db.c.fetchall()
                writer.writerow([i[0] for i in self.db.c.description])
                writer.writerows(records)
            QMessageBox.information(self, "Export", f"Exported to {file_name}")

    def import_customers(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            with open(file_name, mode='r') as file:
                reader = csv.reader(file)
                headers = next(reader)
                records = [tuple(row) for row in reader]
                for record in records:
                    try:
                        self.db.c.execute("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?)", record)
                    except sqlite3.Error as e:
                        print(f"Error importing record: {record}. {e}")
                self.db.conn.commit()
            self.load_customers_data()

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

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()