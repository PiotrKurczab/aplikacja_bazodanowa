import sys
import unittest
from PyQt6.QtWidgets import QApplication
from mainwindow import MainWindow
from unittest.mock import patch

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

    def tearDown(self):
        self.app.quit()

    @patch('mainwindow.CustomersTab.add_record')
    def test_add_record(self, mock_add_record):
        self.main_window.tab_widget.setCurrentIndex(0)
        self.main_window.add_record()
        mock_add_record.assert_called_once()

    @patch('mainwindow.CustomersTab.delete_record')
    def test_delete_record(self, mock_delete_record):
        self.main_window.tab_widget.setCurrentIndex(0)
        self.main_window.delete_record()
        mock_delete_record.assert_called_once()

    @patch('mainwindow.Database.export_to_csv')
    def test_export_database(self, mock_export_to_csv):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('test.csv', '')):
            self.main_window.export_database()
            mock_export_to_csv.assert_called_once_with('test.csv')

    @patch('mainwindow.Database.import_from_csv')
    def test_import_database(self, mock_import_from_csv):
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=('test.csv', '')):
            self.main_window.import_database()
            mock_import_from_csv.assert_called_once_with('test.csv')

if __name__ == '__main__':
    unittest.main()