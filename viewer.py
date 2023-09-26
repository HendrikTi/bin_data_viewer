from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, uic, QtCore, QtNetwork 
from PyQt5.QtOpenGL import *
from PyQt5.QtCore import QTimer,QDateTime
import pyqtgraph as pg
import sys
from collections import deque
import json
from pathlib import Path
import pandas as pd
import numpy as np
import struct


data_sel = {} 
dataqueue = deque([])

    



class MainWindow(QMainWindow):
    plots = []
    widgets = []
    curves = []
    plotcnt = 0
    layout = None
    timer = None


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data-Viewer")
        self.layout = QtWidgets.QGridLayout()
        self.label = QtWidgets.QLabel("")
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 6)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 10)
        mainwidget = QWidget()
        mainwidget.setLayout(self.layout)
        self.setCentralWidget(mainwidget)
        self.fileselect = QPushButton()
        self.fileselect.setText("Select Files")
        self.fileselect.clicked.connect(self.select_files)
        self.file_list = QListWidget(self)
        dialog = QFileDialog(self)
        dialog.setDirectory(r'~/')
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("CSV or BIN (*.csv *.CSV *.BIN *.bin)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                self.file_list.addItems([str(Path(filename)) for filename in filenames])

        self.file_list.setGeometry(QtCore.QRect(0, 0, 1270, 100))
        self.layout.addWidget(self.fileselect)
        self.layout.addWidget(self.file_list)
        self.layout.addWidget(self.label)       
        self.add_plot(["x","y","z"], ["r", "g", "b"])
        self.file_list.itemSelectionChanged.connect(self.updatePlot)

    def select_files(self):
        dialog = QFileDialog(self)
        dialog.setDirectory(r'~/')
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("CSV or BIN (*.csv *.CSV *.BIN *.bin)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            self.file_list.clear()
            if filenames:
                self.file_list.addItems([str(Path(filename)) for filename in filenames])

    def add_plot(self, curvename, curvecolor):
        self.plots.append(pg.PlotWidget())
        self.widgets.append(QtWidgets.QWidget())
        self.widgets[self.plotcnt].setGeometry(QtCore.QRect(0, 0, 1270, 400))
        self.widgets[self.plotcnt].setObjectName(str(self.plotcnt))
        self.plots[self.plotcnt].addLegend()
        self.plots[self.plotcnt].showGrid(x = True, y = True, alpha = 0.8)   
        self.curves.append(list())
        cur_len = len(self.curves)
        for i in range(0, len(curvename)):
            self.curves[cur_len-1].append(self.plots[self.plotcnt].plot(name=curvename[i], pen=pg.mkPen(curvecolor[i], width=1)))
        self.layout.addWidget(self.plots[self.plotcnt], self.plotcnt+3, 0)
        self.plotcnt = self.plotcnt + 1

    def get_plotcnt(self):
        return self.plotcnt

    def updatePlot(self):
        item = self.file_list.selectedItems()[0]

        if item.text().lower().endswith(".csv"):
            df = pd.read_csv(item.text())
        else:
            with open(item.text(), "rb") as datafile:
                struct_fmt = 'hhh'
                struct_len = struct.calcsize(struct_fmt)
                struct_unpack = struct.Struct(struct_fmt).unpack_from
                results = []
                while True:
                    try:
                            data = datafile.read(6)
                            if not data: break
                            s = struct_unpack(data)
                            results.append(s)
                    except:
                            break
            df = pd.DataFrame()
            val = results
            val = np.array(val)
            if val.ndim == 2:
                df["x"] = val[:,0]
                df["y"] = val[:,1]
                df["z"] = val[:,2]
        dataqueue = []
        sub_dataqueue = []
        sub_dataqueue.append(df["x"])
        sub_dataqueue.append(df["y"])
        sub_dataqueue.append(df["z"])
        if item.text().lower().endswith(".csv"):
            self.label.setText(df.head(1).to_string())
        else:
            try:
                with open(item.text()[:-3] + "TXT", "r") as f:
                    textfile_data = f.read()
                    self.label.setText(textfile_data)
            except:
                pass
        dataqueue.append(sub_dataqueue)
        cnt = 0
        subcnt = 0
        
        for curve in self.curves:
            subcnt = 0
            for subcurves in curve:
                subcurves.setData(dataqueue[cnt][subcnt])
                subcnt = subcnt + 1
            cnt = cnt + 1

if __name__ == "__main__":
    global window
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()