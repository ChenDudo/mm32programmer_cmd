import sys
from interface.programmer_main_window import Programmer
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    programmer = Programmer()
    programmer.show()
    sys.exit(app.exec_())
