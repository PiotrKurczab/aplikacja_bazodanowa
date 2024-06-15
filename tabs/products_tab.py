from .base_tab import BaseTab

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