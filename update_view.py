import sys

from PyQt5 import QtWidgets, QtGui

class UpdateView(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui_setup()

    def ui_setup(self):
        self.setWindowTitle("Open Shotgun User Controller")
        self.setGeometry(100, 100, 400, 150)
        self.center()

        font = QtGui.QFont()
        font.setPointSize(17)
        self.setFont(font)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.lbl_notice = QtWidgets.QLabel()

        self.progress = QtWidgets.QProgressBar()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.lbl_notice)
        main_layout.addWidget(self.progress)

        central_widget.setLayout(main_layout)


    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    