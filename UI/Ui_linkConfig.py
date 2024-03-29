# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\MM\gitworks\10.3.2.202\embeded-group2\mm32program\UI\linkConfig.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(356, 233)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/icon/MM32_Logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.vNone = QtWidgets.QRadioButton(self.groupBox)
        self.vNone.setObjectName("vNone")
        self.horizontalLayout_5.addWidget(self.vNone)
        self.v3 = QtWidgets.QRadioButton(self.groupBox)
        self.v3.setObjectName("v3")
        self.horizontalLayout_5.addWidget(self.v3)
        self.v5 = QtWidgets.QRadioButton(self.groupBox)
        self.v5.setObjectName("v5")
        self.horizontalLayout_5.addWidget(self.v5)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.beepCK = QtWidgets.QCheckBox(self.groupBox_2)
        self.beepCK.setObjectName("beepCK")
        self.horizontalLayout_6.addWidget(self.beepCK)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(100, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ok = QtWidgets.QPushButton(Dialog)
        self.ok.setObjectName("ok")
        self.horizontalLayout.addWidget(self.ok)
        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout.addWidget(self.cancel)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)

        self.retranslateUi(Dialog)
        self.cancel.clicked.connect(Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "MM32LINK Config"))
        self.groupBox_3.setTitle(_translate("Dialog", "Operate"))
        self.label.setText(_translate("Dialog", "Link speed"))
        self.comboBox.setItemText(0, _translate("Dialog", "Lower"))
        self.comboBox.setItemText(1, _translate("Dialog", "Low"))
        self.comboBox.setItemText(2, _translate("Dialog", "Normal"))
        self.comboBox.setItemText(3, _translate("Dialog", "High"))
        self.comboBox.setItemText(4, _translate("Dialog", "Higher"))
        self.groupBox.setTitle(_translate("Dialog", "Voltage output"))
        self.vNone.setText(_translate("Dialog", "None"))
        self.v3.setText(_translate("Dialog", "3.3V"))
        self.v5.setText(_translate("Dialog", "5.5V"))
        self.groupBox_2.setTitle(_translate("Dialog", "Misc"))
        self.beepCK.setText(_translate("Dialog", "Beep when working"))
        self.ok.setText(_translate("Dialog", "OK"))
        self.cancel.setText(_translate("Dialog", "Cancel"))