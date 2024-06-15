from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QListWidget, QCheckBox, QListWidgetItem, QDialogButtonBox, QLineEdit

class FilterWindow(QDialog):
    def __init__(self, parent=None, filter_fields=None, prev_filters=None):
        super().__init__(parent)
        self.setWindowTitle("Filter")
        self.filter_fields = filter_fields if filter_fields else {}
        self.prev_filters = prev_filters if prev_filters else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.field_widgets = {}
        self.checkboxes = {}

        for field, options in self.filter_fields.items():
            field_layout = QHBoxLayout()
            checkbox = QCheckBox(self)
            checkbox.setChecked(self.prev_filters.get(field, {}).get("enabled", False))
            self.checkboxes[field] = checkbox

            field_label = QLabel(f"{field.capitalize()}:")
            field_layout.addWidget(checkbox)
            field_layout.addWidget(field_label)
            field_layout.addStretch(1)
            form_layout.addRow(field_layout)

            if isinstance(options, list):
                list_widget = QListWidget(self)
                list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
                for option in options:
                    item = QListWidgetItem(str(option))
                    if str(option) in self.prev_filters.get(field, {}).get("values", []):
                        item.setSelected(True)
                    list_widget.addItem(item)
                form_layout.addRow(list_widget)
                self.field_widgets[field] = list_widget
            elif isinstance(options, tuple) and len(options) == 2:
                min_val, max_val = options
                min_input = QLineEdit(self)
                max_input = QLineEdit(self)
                min_input.setPlaceholderText(str(min_val))
                max_input.setPlaceholderText(str(max_val))
                min_input.setText(self.prev_filters.get(field, {}).get("min", ""))
                max_input.setText(self.prev_filters.get(field, {}).get("max", ""))
                slider_layout = QHBoxLayout()
                slider_layout.addWidget(min_input)
                slider_layout.addWidget(QLabel(" to "))
                slider_layout.addWidget(max_input)
                form_layout.addRow(slider_layout)
                self.field_widgets[field] = (min_input, max_input)

        layout.addLayout(form_layout)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_filters(self):
        filters = {}
        for field, widget in self.field_widgets.items():
            if self.checkboxes[field].isChecked():
                if isinstance(widget, QListWidget):
                    filters[field] = {
                        "enabled": True,
                        "values": [item.text() for item in widget.selectedItems()]
                    }
                elif isinstance(widget, tuple) and len(widget) == 2:
                    min_input, max_input = widget
                    filters[field] = {
                        "enabled": True,
                        "min": min_input.text(),
                        "max": max_input.text()
                    }
            else:
                filters[field] = {
                    "enabled": False
                }
        return filters