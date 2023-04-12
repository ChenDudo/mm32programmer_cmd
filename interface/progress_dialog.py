from UI.Ui_progressBar import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt, QTimer

class ProgressDialog(QDialog, Ui_Dialog):
    sigOutPut = pyqtSignal(str)
    sigNormalOutPut = pyqtSignal(str)

    def __init__(self, parent:None, value: int):
        QDialog.__init__(self, parent, flags=Qt.WindowTitleHint)
        self.value = value
        self.step = 0
        self.setupUi(self)
        self.initUI()
    
    def initUI(self):
        self.label.setText(f"total {self.value} KByte")
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, self.value)
        self.progressBar.setFormat("%v KByte")
    
    def updataProgress(self, step: int):
        self.step += step
        if self.step < self.value:
            self.progressBar.setValue(self.step)
        else:
            self.progressBar.setValue(self.step)
            self.waitAndClose(1000) # 1秒后关闭页面
    
    def waitAndClose(self, cnt: int):
        timer = QTimer(self)
        timer.timeout.connect(self.close)
        timer.start(cnt)

    def normalAndClose(self, output: str):
        self.sigNormalOutPut.emit(output)
        self.close()

    def errorAndClose(self, output: str):
        self.sigOutPut.emit(output)
        self.close()

