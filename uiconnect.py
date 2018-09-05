# -*- coding: utf-8 -*-

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication, QMainWindow

import pandas as pd

import citpay
from citpayui import Ui_MainWindow

# Этот класс необходим для отображения Pandas Dataframe в QTableView
# In the case of QTableView the data must be provided through a model since it implements
# the MVC (Model-View-Controller) paradigm, in the case of pandas there is no default model but we can create
# a custom as shown in the following part:
class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):

        if role == QtCore.Qt.BackgroundRole:
            # Вычислить нужный цвет и вернуть его из функции (которая определена ниже)
            # (возвращать надо QBrush объект с установленным необходимым цветом)
            return QtGui.QBrush(QtGui.QColor.fromRgb(177, 160, 199))

        if role != QtCore.Qt.DisplayRole:
            return None  # QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return None  # QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return None  # QtCore.QVariant()

    # Метод который вычисляет необходимый цвет, принимает 1 параметр: index - это индекс ячейки
    def getcolorforrow(self, aindex):
        # Определяем модель по индексу
        #lmodel = aindex.model()

        # Если это 2й или 3й столбец то..
        if aindex.column() in [0, 1]:
            # определить 4 столбец этой же строки в таблице (с текстом резолюции)
            #lcolumn = lmodel.index(aindex.row(), 1, QtCore.QModelIndex())

            # Определить значение по только что вычисленному индексу
            #lvalue = lmodel.data(lcolumn, QtCore.Qt.DisplayRole)
            lvalue = self._df.iloc[aindex.row(), 1]

            if not lvalue:
                return QtGui.QColor.fromRgb(255, 255, 255)

            if lvalue == 100:
                return QtGui.QColor.fromRgb(216, 228, 188)
            elif lvalue < 100:
                return QtGui.QColor.fromRgb(253, 233, 217)
            else:
                return QtGui.QColor.fromRgb(255, 255, 255)


    # Переопределяем метод дата, он принимает обычно 2 параметра,
    # 1-й индекс ячейки, 2-й роль - то есть этот параметр укажет к чему именно применяется этот метод,
    # например к цвету фона, к цвету текста, к отображению данных,
    # к подсвеченному цвету выбранной ячейки и т.д. (насколько я понял)

    def data(self, index, role=QtCore.Qt.DisplayRole):

        # if not index.isValid():
        #     return None  # QtCore.QVariant()

        # Если метод вызвался системой Qt для того чтобы выяснить
        # какой цвет фона использовать (для ячейки index) то..
        # if role == QtCore.Qt.BackgroundRole:
        #     # Вычислить нужный цвет и вернуть его из функции (которая определена ниже)
        #     # (возвращать надо QBrush объект с установленным необходимым цветом)
        #     return QtGui.QBrush(self.getcolorforrow(index))
        # Иначе, если метод вызывался системой Qt для того, чтобы определить цвет текста то..
        # elif role == QtCore.Qt.TextColorRole:
        #     # Вернуть цвет текста, который мне нравится
        #     return QtGui.QBrush(QtGui.QColor.fromRgb(64, 64, 64))
        # Иначе (Не забывайте выполнить метод дата определенный в родителе,
        # потому что, мы переопределили только 2 роли, а их много, поэтому,
        # мы должны вызвать метод data родительского класса и передать ему те же самые параметры
        # которые принимает наш метод data, а метод data родительского класса уже сам решит
        # в какой ситуации что использовать (по умолчанию))
        # if role == QtCore.Qt.DisplayRole:
        #     str(self._df.iloc[index.row(), index.column()])
        # else:
        #     return None

        if role == QtCore.Qt.FontRole:
            if index.column() == 0:
                lfont = QtGui.QFont()
                lfont.setBold(True)
                return lfont

        if role == QtCore.Qt.TextAlignmentRole:
            if index.column() == 1:
                return QtCore.Qt.AlignRight

        if role == QtCore.Qt.BackgroundRole:
            # Вычислить нужный цвет и вернуть его из функции (которая определена ниже)
            # (возвращать надо QBrush объект с установленным необходимым цветом)
            return QtGui.QBrush(self.getcolorforrow(index))

        if role != QtCore.Qt.DisplayRole:
            return None  # QtCore.QVariant()

        if not index.isValid():
            return None  # QtCore.QVariant()

        return str(self._df.iloc[index.row(), index.column()])

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.citpay = citpay.Tcitpay()
        self.citpay.onlog += self.setprogress
        self.connect(self.btnstart, SIGNAL('clicked()'), self.makepg)

    def setprogress(self, alogcount):
        if alogcount>100:
            self.progressBar.setValue(100)
        else:
            self.progressBar.setValue(alogcount)

    def makepg(self):
        try:
            self.statusBar().showMessage('Выпоняется расчет рейтинга...')
            ldf = self.citpay.pgmain(self.cbmonth.currentIndex()+1, self.cbyear.currentText())
            model = PandasModel(ldf.iloc[:,[1,7]])
            self.tvdata.setModel(model)
            # self.tvdata.resizeRowsToContents()
            self.tvdata.resizeColumnsToContents()
            hh = self.tvdata.horizontalHeader()
            #hh.setResizeMode(3)

            self.statusBar().showMessage('Отчет успешно сформирован!')
        except Exception as e:
            self.statusBar().showMessage(str(e))


def main():
    # функция для инициализации и отображения нашего основного окна приложения
    # Класс QApplication руководит управляющей логикой ГПИ и основными настройками.
    #Здеь мы создаем экземпляр класса QAplication передавая ему аргументы из коммандной строки.
    app = QApplication(sys.argv)  # где sys.argv список аргументов командной строки, передаваемых сценарию Python.
    main = MainWindow()  # Здесь мы создаем экземпляр класса MainWindow.
    main.show()  # Метод show() отображает виджет на экране.Виджет сначала создаётся в памяти, и
                 # только потом(с помощью метода show) показывается на экране.
    sys.exit(app.exec_())  # exec_ запускает цикл обработки сообщений
                           # и ждет, пока не будет вызвана exit() или не
                           # будет разрушен главный виджет, и возвращает значение установленное в exit().
                           # Здесь sys.exit обеспечивает чистый выход из приложения.

main()