from .base_tab import BaseTab

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