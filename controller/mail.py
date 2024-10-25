import os
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import socket

class Mail():
    def __init__(self, email, sg_email, log_path):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.email = email
        self.sg_email = sg_email
        self.log_path = log_path

        self.url = "Office URL"
        self.admin_id = "Admin ID"
        self.admin_pw = "Admin PW"
        self.admin = "TD"

    def send_mail(self):
        smtp = smtplib.SMTP(self.url)
        smtp.login( self.admin_id, self.admin_pw )

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'SG_Controller Log Report : {self.email}'
        msg['From'] = 'WestWorld'
        msg['To'] = self.admin

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(self.log_path, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename = os.path.basename(self.log_path))
        msg.attach(part)

        msg.attach(MIMEText(self.mail_content(), 'plain', _charset='utf-8'))
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())

    def mail_content(self):
        content = '''
            Auto Send mail about LOG of SG_Controller
            
            ** User Detail **
            IP : {0}
            GUI_email : {1}
            Shotgun_email : {2}
        '''.format(self.ip, self.email, self.sg_email)
        return content