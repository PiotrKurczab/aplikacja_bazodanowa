from .base_tab import BaseTab

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