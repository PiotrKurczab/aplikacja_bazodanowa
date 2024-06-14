from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QHBoxLayout
)
from database import Database
from tabs import CustomersTab, OrdersTab, ProductsTab, SuppliersTab, JoinTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Application")
        self.resize(800, 600)

        self.db = Database()

        self.tab_widget = QTabWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        for button_text in ["Add", "Delete", "Export", "Import"]:
            button = QPushButton(button_text)
            button.setFixedWidth(100)
            button_layout.addWidget(button)
            if button_text == "Add":
                button.clicked.connect(self.add_record)
            elif button_text == "Delete":
                button.clicked.connect(self.delete_record)
            elif button_text == "Export":
                button.clicked.connect(self.export_database)
            elif button_text == "Import":
                button.clicked.connect(self.import_database)
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.create_tabs()

    def create_tabs(self):
        self.tab_widget.addTab(CustomersTab(self.db), "Customers")
        self.tab_widget.addTab(OrdersTab(self.db), "Orders")
        self.tab_widget.addTab(ProductsTab(self.db), "Products")
        self.tab_widget.addTab(SuppliersTab(self.db), "Suppliers")
        self.tab_widget.addTab(JoinTab(self.db), "Customer Orders")

    def add_record(self):
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "add_record"):
            current_tab.add_record()

    def delete_record(self):
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "delete_record"):
            current_tab.delete_record()

    def export_database(self):
        self.db.export_to_csv()

    def import_database(self):
        self.db.import_from_csv()
        self.create_tabs()