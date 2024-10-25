import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from model import Model
from monitor import Monitor
from mail import Mail

class View(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = Model()
        self.logger = self.model.logger
        
        self._version = self.model.version
        
        self.ui_setup()
        self.ui_signal()
        self.load_email()
        self.systray()

        self.workin_flag = True

        self.monitor = None
        self.start_monitor()

    def ui_setup(self):
        self.setWindowTitle(f"Shotgun User Controller_{self._version}")
        self.setGeometry(100, 100, 600, 170)
        self.center()

        font = QtGui.QFont()
        font.setPointSize(17)
        self.setFont(font)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.email = QtWidgets.QLineEdit()
        self.email.setPlaceholderText("Enter Shotgun email")
        self.email.setFixedHeight(50)

        self.btn_workin = QtWidgets.QPushButton("WorkIn")
        self.btn_workin.setFixedHeight(50)
        self.btn_workout = QtWidgets.QPushButton("WorkOut")
        self.btn_workout.setFixedHeight(50)
        btn_layout_1 = QtWidgets.QHBoxLayout()
        btn_layout_1.addWidget(self.btn_workin)
        btn_layout_1.addWidget(self.btn_workout)

        version = QtWidgets.QLabel(f'Version : {self._version}')
        spacer = QtWidgets.QSpacerItem(0, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.btn_report = QtWidgets.QPushButton("Report")
        self.btn_report.setFixedHeight(50)
        self.btn_report.setFixedWidth(100)
        btn_layout_2 = QtWidgets.QHBoxLayout()
        btn_layout_2.addWidget(version)
        btn_layout_2.addItem(spacer)
        btn_layout_2.addWidget(self.btn_report)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.email)
        main_layout.addLayout(btn_layout_1)
        main_layout.addLayout(btn_layout_2)
        central_widget.setLayout(main_layout)

        self.logger.info('-'*50)
        self.logger.info(f"Start Program :: Success setup (Version {self._version})")
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def ui_signal(self):
        self.btn_workin.clicked.connect(self.workin_email)
        self.btn_workout.clicked.connect(self.workout_email)
        self.btn_report.clicked.connect(self.send_report)
    
    def load_email(self):
        email = self.model.user_email
        if email:
            self.email.setText(email)
            self.logger.info(f"Load Email :: {email}\n")

    def workin_email(self):
        email = self.email.text().strip()
        sg_email = self.model.user_email
        
        if email:
            msg = QtWidgets.QMessageBox.question(self, 'Question', f'Want to WorkIn : {email}?')
        
            if msg == QtWidgets.QMessageBox.Yes:
                self.logger.info("Try to WorkIn email")
                if email == sg_email:
                    self.model.workin_email(email)
                    if not self.workin_flag:
                        self.workin_flag = True
                        self.start_monitor()
                    self.logger.info(f"WorkIn :: {email}\n")
                    QtWidgets.QMessageBox.information(self, 'SUCCESS', f'WorkIn : {email}')
                elif sg_email is None:
                    self.logger.debug(f"Not LOGIN Shotgun\n")
                    QtWidgets.QMessageBox.warning(self, 'Warning', 'Need to LOGIN Shotgun App')
                else:
                    self.logger.debug(f"Wrong Email :: sg_email = {sg_email}")
                    self.logger.debug(f"Wrong Email :: gui_email = {email}\n")
                    QtWidgets.QMessageBox.warning(self, 'Wrong Email', f'Do NOT match your Shotgun Email : {email}')

    def workout_email(self):
        email = self.email.text().strip()
        sg_email = self.model.user_email

        msg = QtWidgets.QMessageBox.question(self, 'Question', f'Want to WorkOut : {email}?')

        if msg == QtWidgets.QMessageBox.Yes:
            self.logger.info("Try to WorkOut email")
            if email == sg_email:
                workout = self.model.workout_email(email)

                if workout:
                    self.workin_flag = False
                    self.stop_monitor()
                    self.logger.info(f"WorkOut :: {email}\n")
                    QtWidgets.QMessageBox.information(self, 'SUCCESS', f'WorkOut : {email}')
            elif sg_email is None:
                self.logger.debug(f"Not LOGIN Shotgun\n")
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Need to LOGIN Shotgun App')
            else:
                self.logger.debug(f"Wrong Email :: sg_email = {sg_email}")
                self.logger.debug(f"Wrong Email :: gui_email = {email}\n")               
                QtWidgets.QMessageBox.warning(self, 'Wrong Email', f'Do NOT match your Shotgun Email : {email}')

    def systray(self):
        self.tray = QtWidgets.QSystemTrayIcon(self)
        icon = QtGui.QIcon(self.resource_path('../images/switch.png'))
        self.tray.setIcon(icon)
        self.tray.setToolTip('Shotgun User Controller')

        tray_menu = QtWidgets.QMenu(self)
        tray_show = tray_menu.addAction("Show")
        tray_exit = tray_menu.addAction("Exit")

        tray_show.triggered.connect(self.show_program)
        tray_exit.triggered.connect(self.exit_program)

        self.tray.setContextMenu(tray_menu)

        self.tray.show()
    
    def show_program(self):
        self.logger.info("Show program from system tray")
        self.show()
    
    def exit_program(self):
        self.stop_monitor()
        self.logger.info(f"Close Program (Version {self._version})")
        self.logger.info('-'*50 + '\n')
        QtWidgets.qApp.quit()

    def closeEvent(self, event):
        if hasattr(self, 'tray') and self.tray:
            self.logger.info("Minimized to system tray\n")
            event.ignore()
            self.hide()
            self.tray.showMessage(
                'Shotgun User Controller',
                'The application was minimized to the system tray.',
                msecs=2000
            )
    
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            return os.path.join(os.path.abspath("."), relative_path)
    
    def start_monitor(self):
        if self.monitor and self.monitor.isRunning():
            self.workin_flag = False
            self.stop_monitor()
        
        self.monitor = Monitor()
        self.monitor.finished.connect(self.auto_workout)
        self.monitor.start()
    
    def stop_monitor(self):
        self.monitor.end_program = True
        self.monitor.wait()

    @QtCore.pyqtSlot(bool)
    def auto_workout(self, end_program):
        email = self.email.text().strip()
        sg_email = self.model.user_email
        if email == sg_email and self.workin_flag:
            workout = self.model.workout_email(email)

            if workout:
                self.workin_flag = False
                self.logger.info(f"Auto WorkOut :: {email}\n")

    def send_report(self):
        log_path = self.model.log_path
        if os.path.exists(log_path):
            report = QtWidgets.QMessageBox.question(self, 'Question', f'Want to Report LOG to TD?')
            if report == QtWidgets.QMessageBox.Yes:
                email = self.email.text().strip()
                sg_email = self.model.user_email
                mail = Mail(email, sg_email, log_path)
                mail.send_mail()
                self.logger.info("Send Message & LOG file to TD\n")
                QtWidgets.QMessageBox.information(self, 'SUCCESS', 'Send Message & LOG file to TD')
    
if '__main__'==__name__:
    app = QtWidgets.QApplication(sys.argv)
    vi = View()
    vi.show()
    sys.exit(app.exec_())
