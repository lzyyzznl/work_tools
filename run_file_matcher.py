from src.file_matcher.gui import FileMatcherGUI
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileMatcherGUI()
    window.show()
    sys.exit(app.exec_())
