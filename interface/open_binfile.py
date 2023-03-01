from UI.Ui_openBinFile import Ui_Dialog
from PyQt5.QtWidgets import QDialog

class OpenBinFile(QDialog, Ui_Dialog):
    def __init__(self, flashsize: int, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initUI(flashsize)
    
    def initUI(self, flashsize):
        size = 0x08000000 + flashsize * 1024 - 1
        self.start.setText("08000000")
        self.end.setText("{:08X}".format(size))
        self.checkBox.setChecked(True)
