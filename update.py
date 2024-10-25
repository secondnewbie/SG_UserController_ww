import ftputil
import ftplib
import os
import sys
import time
import subprocess
import threading
import ctypes

from update_view import UpdateView
from update_model import UpdateModel

from PyQt5 import QtWidgets, QtCore

HOST = 'FTP Server'
USER = 'FTP ID'
PASSWORD = 'FTP PW'

PORT = 'FTP Port'

FTP_PATH = "FTP PATH"

class PortConnect(ftplib.FTP):
    def __init__(self, host, user, passwd, port) :
        super().__init__()
        self.connect(host, port)
        self.login(user, passwd)

class FTPMain():
    def __init__(self):
        self._program_name = 'SG_UserController'
        self._run_flag = False
        self._thread_flag = False
        
        self._subprocess = None

        self.model = UpdateModel()
        self.logger = self.model.logger

    def change_current_version(self, server_version):
        with open(self.model._current_version_path, 'w') as fp:
            fp.write(server_version)
    
    def _server_version(self, retries = 0):
        try:
            with ftputil.FTPHost(HOST, USER, PASSWORD, port=PORT, session_factory=PortConnect) as ftphost:
                ftphost.chdir(FTP_PATH)
                files = ftphost.listdir(ftphost.curdir)
            
                version_list = []
                for file in files:
                    if self._program_name in file and '.' in file :
                        tmp_version = os.path.basename(file).split('_')[-1]
                        version_list.append(tmp_version)
                version_list.sort()
                server_version = version_list[-1].strip()
            
            self.logger.info(f'Check Server Version : {server_version}')
            return server_version
        
        except:
            retries += 1
            if retries <= 5:
                self.logger.debug('Temporary Fail to Connect FTP :: Find Server Version')
                self.logger.debug(f'Try again to Find Server Version (Try {retries})')

                time.sleep(5)
                return self._server_version(retries)
            else:
                self.logger.debug(f'Fail to Connect FTP :: Find Server Version (Try more than {retries} times)')
                QtWidgets.QApplication.quit()
                return None

    def download_server_program(self, server_version, current_program_path, retries=0):
        try:
            with ftputil.FTPHost(HOST, USER, PASSWORD, port=PORT, session_factory=PortConnect) as ftphost:
                ftphost.chdir(FTP_PATH)
                files = ftphost.listdir(ftphost.curdir)

                for file in files:
                    if server_version in file:
                        if 'exe' in file:
                            if sys.platform.startswith('win'):
                                server_program_path = f'{FTP_PATH}/{file}'
                                new_program_path = f'{os.path.dirname(current_program_path)}\\{file}'

                                ftphost.download(server_program_path, new_program_path)

                                ctypes.windll.kernel32.SetFileAttributesW(new_program_path, 0x02)
                                os.chmod(new_program_path, 0o755)
                                
                                self.logger.info('Download New Program from Server to Local')
                                return new_program_path

                        elif 'exe' not in file:
                            if sys.platform.startswith('linux'):
                                server_program_path = f'{FTP_PATH}/{file}'
                                new_program_path = f'{os.path.dirname(current_program_path)}/.{file}'
                                
                                ftphost.download(server_program_path, new_program_path)
                            
                                os.chmod(new_program_path, 0o755)
                            
                                self.logger.info('Download New Program from Server to Local')
                                return new_program_path
        except:
            retries += 1

            if retries <= 5:
                self.logger.debug('Temporary Fail to Connect FTP :: Download Server Program')
                self.logger.debug(f'Try again to Download Server Program (Try {retries})')
                
                time.sleep(5)
                return self.download_server_program(server_version, current_program_path, retries)
            else:
                self.logger.debug(f'Fail to Connect FTP :: Download Server Program (Try more than {retries} times)')
                QtWidgets.QApplication.quit()
                return None
    
    def ui_setup(self, notice, num):
        self._view.lbl_notice.setText(notice)
        self._view.progress.setValue(num)
        QtCore.QCoreApplication.processEvents()

    def main(self):
        app = QtWidgets.QApplication(sys.argv)
        self._view = UpdateView()
        self._view.show()
        
        self.logger.info('='*50)
        self.logger.info('Start Program')
        self.ui_setup('Open Shotgun User Controller', 0)

        current_version = self.model._current_version
        server_version = self._server_version()

        self.logger.info(f'Check Version :: current version = {current_version} / server_version = {server_version}')        
        self.ui_setup('Check Version', 25)
        
        if current_version == server_version:
            self.logger.info(f'Prepare to Open Program (Version {current_version})')
            self.ui_setup('Prepare to Open Program', 75)
            
            current_path = self.model.current_program_path
            current_data = [current_path] + sys.argv[1:]
            
            self.logger.info('Ready to Run Program\n')
            self.ui_setup(f'Run SG_UserController_{current_version}', 100)

            self._subprocess = subprocess.Popen(current_data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

        elif current_version < server_version:
            self.logger.info('Prepare to Download Program')
            self.ui_setup('Download New Program', 50)
            new_program_path = self.download_server_program(server_version, self.model.current_program_path)

            if new_program_path:
                self.change_current_version(server_version)
            
                self.logger.info(f'Prepare to Open Program (Version {server_version})')
                self.ui_setup('Prepare to Open Program', 75)

                new_data = [new_program_path] + sys.argv[1:] 
            
                self.logger.info('Ready to Run Program\n')
                self.ui_setup(f'Run SG_UserController_{server_version}', 100)

                self._subprocess = subprocess.Popen(new_data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

        if self._subprocess:
            self.background_thread = threading.Thread(target=self.background_run)
            self._thread_flag = True
            self.background_thread.start()

            self._view.close()

            app.exec_()

            self.logger.info('Close Program')
            self.logger.info('='*50)
        else:
            self.logger.info('Close Program')
            self.logger.info('='*50)

            self._view.close()
            QtWidgets.QApplication.quit()

    def background_run(self):
        while self._thread_flag:

            if self._subprocess and self._subprocess.poll() is not None:
                self._thread_flag = False
                QtWidgets.QApplication.quit()
                return

            current_version = self.model._current_version
            server_version = self._server_version()

            if current_version == server_version:
                pass
            else:
                if self._subprocess.poll() is None:
                    self.logger.debug(f'Shutdown Current Program (Version {current_version})')
                    self._subprocess.terminate()

                self.logger.info('Prepare to Download Program')
                new_program_path = self.download_server_program(server_version, self.model.current_program_path)
                
                if new_program_path:
                    self.change_current_version(server_version)
                
                    self.logger.info(f'Prepare to Open Program (Version {server_version})')
                    new_data = [new_program_path] + sys.argv[1:]

                    self.logger.info('Ready to Run Program\n')
                    self._subprocess = subprocess.Popen(new_data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

                    time.sleep(1)

            time.sleep(20)



if __name__ == '__main__':
    ma = FTPMain()
    ma.main()
