# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'citpayui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1117, 816)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Z:/Python/citpay/ico/user32.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 70))
        self.groupBox.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        self.groupBox.setFont(font)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(147, 0))
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.cbmonth = QtGui.QComboBox(self.groupBox)
        self.cbmonth.setObjectName(_fromUtf8("cbmonth"))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.cbmonth.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cbmonth)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.cbyear = QtGui.QComboBox(self.groupBox)
        self.cbyear.setObjectName(_fromUtf8("cbyear"))
        self.cbyear.addItem(_fromUtf8(""))
        self.cbyear.addItem(_fromUtf8(""))
        self.cbyear.addItem(_fromUtf8(""))
        self.cbyear.addItem(_fromUtf8(""))
        self.cbyear.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cbyear)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.btnstart = QtGui.QPushButton(self.centralwidget)
        self.btnstart.setObjectName(_fromUtf8("btnstart"))
        self.verticalLayout.addWidget(self.btnstart)
        self.tvdata = QtGui.QTableView(self.centralwidget)
        self.tvdata.setObjectName(_fromUtf8("tvdata"))
        self.verticalLayout.addWidget(self.tvdata)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1117, 31))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.cbmonth.setCurrentIndex(6)
        self.cbyear.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Дисциплина предоставления платы граждан за КУ", None))
        self.groupBox.setTitle(_translate("MainWindow", "Отчетный период", None))
        self.label.setText(_translate("MainWindow", "Месяц :", None))
        self.cbmonth.setItemText(0, _translate("MainWindow", "январь", None))
        self.cbmonth.setItemText(1, _translate("MainWindow", "февраль", None))
        self.cbmonth.setItemText(2, _translate("MainWindow", "март", None))
        self.cbmonth.setItemText(3, _translate("MainWindow", "апрель", None))
        self.cbmonth.setItemText(4, _translate("MainWindow", "май", None))
        self.cbmonth.setItemText(5, _translate("MainWindow", "июнь", None))
        self.cbmonth.setItemText(6, _translate("MainWindow", "июль", None))
        self.cbmonth.setItemText(7, _translate("MainWindow", "август", None))
        self.cbmonth.setItemText(8, _translate("MainWindow", "сентябрь", None))
        self.cbmonth.setItemText(9, _translate("MainWindow", "октябрь", None))
        self.cbmonth.setItemText(10, _translate("MainWindow", "ноябрь", None))
        self.cbmonth.setItemText(11, _translate("MainWindow", "декабрь", None))
        self.label_2.setText(_translate("MainWindow", "Год :", None))
        self.cbyear.setItemText(0, _translate("MainWindow", "2016", None))
        self.cbyear.setItemText(1, _translate("MainWindow", "2017", None))
        self.cbyear.setItemText(2, _translate("MainWindow", "2018", None))
        self.cbyear.setItemText(3, _translate("MainWindow", "2019", None))
        self.cbyear.setItemText(4, _translate("MainWindow", "2020", None))
        self.btnstart.setText(_translate("MainWindow", "Сформировать отчет", None))

