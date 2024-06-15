from .base_tab import BaseTab
from PyQt6.QtWidgets import QVBoxLayout, QTableWidget

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