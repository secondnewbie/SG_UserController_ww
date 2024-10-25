import datetime
import time
import psutil
from pynput import keyboard, mouse

from PyQt5 import QtCore

class Signal(QtCore.QObject):
    finished = QtCore.pyqtSignal(bool)

class Monitor(QtCore.QThread):
    def __init__(self):
        super().__init__()

        self._signal = Signal()
        self.off_work_time = 9
        self.timeout = 10
        self.last_user_time = datetime.datetime.now()
        self.end_program = False

    @property
    def finished(self):
        _finished = self._signal.finished
        return _finished

    def on_press(self, key):
        self.last_user_time = datetime.datetime.now()
    
    def on_click(self, x, y, button, pressed):
        self.last_user_time = datetime.datetime.now()
    
    def key_mouse_monitor(self):
        with keyboard.Listener(on_press=self.on_press) as key_listen, mouse.Listener(on_click=self.on_click) as mouse_listen:
            while not self.end_program:
                current_time = datetime.datetime.now()
                time_gap = current_time - self.last_user_time
                cpu_use = psutil.cpu_percent(interval=0)

                if cpu_use < 6:
                    if time_gap.seconds > self.timeout:
                        key_listen.stop()
                        mouse_listen.stop()
                        self.end_program = True
                        return

                time.sleep(1)

    def run(self):
        while not self.end_program:
            current_time = datetime.datetime.now()
            if current_time.hour >= self.off_work_time:
                self.key_mouse_monitor()
                break
        
        if self.end_program:
            self.finished.emit(self.end_program)
