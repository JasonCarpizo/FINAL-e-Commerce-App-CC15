import sys
from PyQt6.QtWidgets import QApplication
from windows.Access_Window import AccessWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccessWindow()
    window.show()
    sys.exit(app.exec())
