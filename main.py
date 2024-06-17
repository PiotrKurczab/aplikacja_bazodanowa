import sys
from PyQt6.QtWidgets import QApplication
import qdarktheme
from app.mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())