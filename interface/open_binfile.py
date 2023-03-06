from UI.Ui_openBinFile import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

class OpenBinFile(QDialog, Ui_Dialog):
    def __init__(self, flashsize: int, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initUI(flashsize)
    
    def initUI(self, flashsize): # 做输入验证
        size = 0x08000000 + flashsize * 1024 - 1
        self.start.setText("08000000")
        self.end.setText("{:08X}".format(size))
        self.checkBox.setChecked(True)

        # 验证输入
        reHex8 = QRegExp("[A-Fa-f0-9]{8}")
        optionValid = QRegExpValidator(reHex8)
        self.start.setValidator(optionValid)
        self.end.setValidator(optionValid)

# todo：
#   1. 除了限制十六进制长度，还需要限制大小，start的值是end的最小值+1