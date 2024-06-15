from PyQt6.QtWidgets import (
   QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QHBoxLayout, QFileDialog
)
from database import Database
from tabs.tabs import CustomersTab, OrdersTab, ProductsTab, SuppliersTab, JoinTab

class MainWindow(QMainWindow):
    """
    Main Window class that represents the application's main window.
    """

    def __init__(self):
        """
        Initializes the MainWindow object.
        - Sets window title and size.
        - Initializes the database instance.
        - Connects signals to corresponding methods.
        - Creates the tab widget and buttons.
        """
        super().__init__()
        self.setWindowTitle("Database Application")
        self.resize(800, 600)

        # Initialize the database instance
        self.db = Database()
        # Connect the record_updated signal to the update_join_tab method
        self.db.record_updated.connect(self.update_join_tab)

        self.tab_widget = QTabWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)

        button_layout = QHBoxLayout()
        for button_text in ["Add", "Delete", "Export", "Import"]:
            button = QPushButton(button_text)
            button.setFixedWidth(100)
            button_layout.addWidget(button)
            # Connect button clicks to corresponding methods
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
        """
        Creates tabs for different database tables:
        - Customers
        - Orders
        - Products
        - Suppliers
        - Customer Orders (JoinTab)
        """
        self.tab_widget.addTab(CustomersTab(self.db), "Customers")
        self.tab_widget.addTab(OrdersTab(self.db), "Orders")
        self.tab_widget.addTab(ProductsTab(self.db), "Products")
        self.tab_widget.addTab(SuppliersTab(self.db), "Suppliers")
        self.tab_widget.addTab(JoinTab(self.db), "Customer Orders")

    def add_record(self):
        """
        Adds a new record to the current tab's table.
        """
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "add_record"):
            current_tab.add_record()
            self.update_join_tab()

    def delete_record(self):
        """
        Deletes a record from the current tab's table.
        """
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, "delete_record"):
            current_tab.delete_record()
            self.update_join_tab()

    def export_database(self):
        """
        Exports the database to a CSV file.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Database", "", "CSV Files (*.csv)")
        if file_name:
            self.db.export_to_csv(file_name)

    def import_database(self):
        """
        Imports a database from a CSV file.
        - Clears existing tabs.
        - Creates tabs again with updated data.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Database", "", "CSV Files (*.csv)")
        if file_name:
            self.db.import_from_csv(file_name)
            self.tab_widget.clear()
            self.create_tabs()

    def update_join_tab(self):
        """
        Updates the JoinTab with the latest data.
        """
        for i in range(self.tab_widget.count()):
            if isinstance(self.tab_widget.widget(i), JoinTab):
                self.tab_widget.widget(i).reload_data()
                break