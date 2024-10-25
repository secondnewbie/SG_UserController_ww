import os
import sys
import logging
from logging.handlers import RotatingFileHandler

class UpdateModel:
    def __init__(self):
        self.make_log()

        self._program_name = 'SG_UserController'
    
    @property
    def sys_path(self):
        sys_path = os.path.expanduser('~')
        if sys.platform.startswith('win'):
            sys_path = os.path.join(sys_path, 'AppData\\Roaming\\Shotgun')
        elif sys.platform.startswith('linux'):
            sys_path = os.path.join(sys_path, '.shotgun')
        return sys_path

    @property
    def _current_version_path(self):
        if sys.platform.startswith('win'):
            version_path = os.path.join(self.sys_path, 'west\\ww_sg_controller_version.txt')
        elif sys.platform.startswith('linux'):
            version_path = os.path.join(self.sys_path, 'west/ww_sg_controller_version.txt')
        
        return version_path
    
    @property
    def _current_version(self):
        version_path = self._current_version_path
        if not os.path.exists(version_path):
            with open(version_path, 'w') as fp:
                fp.write('1.0.1')
                return '1.0.1'
        
        with open(version_path, 'r') as fp:
            current_version = fp.read().strip()
        
        return current_version
    
    @property
    def current_program_path(self):
        current_program_name = self._program_name + '_' + self._current_version
        for root, dirs, files in os.walk(os.path.expanduser('~')):
            if current_program_name in files:
                current_program_path = os.path.join(root, current_program_name)
                return current_program_path
        
        root = os.path.expanduser('~')
        current_program_path = os.path.join(root, current_program_name)
        return current_program_path

    @property
    def log_path(self):
        if sys.platform.startswith('win'):
            log_path = os.path.join(self.sys_path, 'Logs\\ww_sg_controller.log')
        elif sys.platform.startswith('linux'):
            log_path = os.path.join(self.sys_path, 'logs/ww_sg_controller.log')
        
        return log_path
    
    def make_log(self):
        log_path = self.log_path
        max_bytes = 5*1024*1024

        handler = RotatingFileHandler(log_path, maxBytes=max_bytes)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s [%(process)d %(levelname)s] %(message)s')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)