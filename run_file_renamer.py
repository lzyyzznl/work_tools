from src.file_renamer.gui import FileRenamer
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamer()
    window.show()
    sys.exit(app.exec_()) 