import os
import sys
import yaml
import logging
from logging.handlers import RotatingFileHandler

import shotgun_api3 as sa


class Model:
    def __init__(self):
        self.make_log()

        self.sg_url = 'Shotgun URL'
        self.sg_admin_id = 'Admin ID'
        self.sg_admin_pw = 'Admin Shotgun PW'

    @property
    def sys_path(self):
        sys_path = os.path.expanduser('~')
        if sys.platform.startswith('win'):
            sys_path = os.path.join(sys_path, 'AppData\\Roaming\\Shotgun')
        elif sys.platform.startswith('linux'):
            sys_path = os.path.join(sys_path, '.shotgun')
        return sys_path
    
    @property
    def version_path(self):
        if sys.platform.startswith('win'):
            version_path = os.path.join(self.sys_path, 'west\\ww_sg_controller_version.txt')
        elif sys.platform.startswith('linux'):
            version_path = os.path.join(self.sys_path, 'west/ww_sg_controller_version.txt')
        
        return version_path
    
    @property
    def version(self):
        version_path = self.version_path
        if not os.path.exists(version_path):
            with open(version_path, 'w') as fp:
                fp.write('1.0.1')
                return '1.0.1'
        
        with open(version_path, 'r') as fp:
            version = fp.read().strip()
            return version

    @property
    def authentication_path(self):
        if sys.platform.startswith('win'):
            authentication_path = os.path.join(self.sys_path, 'west\\authentication.yml')
        elif sys.platform.startswith('linux'):
            authentication_path = os.path.join(self.sys_path, 'west/authentication.yml')
        
        return authentication_path

    @property
    def user_email(self):
        with open(self.authentication_path, 'r') as fp:
            datas = yaml.safe_load(fp)
            data = datas.get('users')
            if data:
                user_email = data[0]['login'].strip()
                return user_email
            else:
                return

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
    
    @property
    def sg(self):
        sg = sa.Shotgun(
            self.sg_url,
            login=self.sg_admin_id,
            password=self.sg_admin_pw,
        )

        return sg

    def find_email(self, email):
        filters = [
            ['email', 'is', email],
        ]

        fields = [ 'name', 'email', 'sg_status_list' ]

        result = self.sg.find_one('HumanUser', filters, fields)
        print(result)

        return result

    def workout_email(self, email):
        datas = self.find_email(email)
        id = datas['id']
        data = {'sg_status_list': 'dis'}
        
        result = self.sg.update('HumanUser', id, data)

        return result
    
    def workin_email(self, email):
        datas = self.find_email(email)

        id = datas['id']
        data = {'sg_status_list': 'act'}

        result = self.sg.update('HumanUser', id, data)
        
        return result
