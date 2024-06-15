from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from .filter_window import FilterWindow

# Base class for tab widgets
class BaseTab(QWidget):
   def __init__(self, db, columns):
       super().__init__()
       self.db = db
       self.columns = columns
       self.filters = {}
       self.init_ui()

   # Initialize the user interface
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

   # Open the filter window
   def open_filter_window(self):
       filter_fields = self.get_filter_fields()
       filter_window = FilterWindow(self, filter_fields, self.filters)
       if filter_window.exec() == QDialog.DialogCode.Accepted:
           self.filters = filter_window.get_filters()
           self.apply_filters(self.filters)

   # Get filter fields for the current tab
   def get_filter_fields(self):
       return {}

   # Apply filters to the data
   def apply_filters(self, filters):
       pass

   # Load data into the table widget
   def load_data(self, records):
       self.table_widget.setRowCount(len(records))
       self.table_widget.setColumnCount(len(self.columns))
       self.table_widget.setHorizontalHeaderLabels(self.columns)

       for row_num, row_data in enumerate(records):
           for col_num, col_data in enumerate(row_data):
               self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

   # Handle double-click on a table cell
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

   # Add a new record to the table
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

   # Delete selected records from the table
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

   # Open an input dialog for text input
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

   # Open an input dialog for double input
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

   # Search data in the table
   def search_data(self):
       pass