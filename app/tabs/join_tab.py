from .base_tab import BaseTab
from PyQt6.QtWidgets import QMessageBox

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

    def cell_double_clicked(self, row, column):
        QMessageBox.warning(self, "Warning", "Editing is not allowed in this tab.")
        
    def add_record(self):
        QMessageBox.warning(self, "Warning", "Adding is not allowed in this tab.")
        
    def delete_record(self):
        QMessageBox.warning(self, "Warning", "Deleting is not allowed in this tab.")