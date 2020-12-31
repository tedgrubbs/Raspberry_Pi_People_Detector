import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import timeit
from os import path,mkdir,listdir,remove
import json
from shutil import copyfile

# Author: Taylor Grubbs
# Date: 12-31-2020
# Adapted from this simple tutorial https://realpython.com/python-send-email/

class Mailer:
    def __init__(self):

        with open('config.json') as f:
            config = json.load(f)

        self.port = 465  # For SSL
        self.sender_email = config['sender_email']  # Enter your address
        self.receiver_email = config['receiver_email']  # Enter receiver address
        self.password = config['password']
        self.error_times = []
        self.wait_time = 10
        self.timer = timeit.default_timer() - self.wait_time
        self.err_folder = 'error_backlog/'
        if not path.exists(self.err_folder): mkdir(self.err_folder)

    def check_time(self):
        return (timeit.default_timer() - self.timer) > self.wait_time

    def create_message(self, body, subject):
        self.message = MIMEMultipart()
        self.message["From"] = self.sender_email
        self.message["To"] = self.receiver_email
        self.message["Subject"] = subject
        self.message.attach(MIMEText(body, "plain"))

    def attach(self, images, folder=''):
        for img in images:
            filename = folder + img  # In same directory as script

            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            self.message.attach(part)

    def send_message(self):
        text = self.message.as_string()
        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.receiver_email, text)

    def send_alert(self, images):

        subject = "Little_Brother - " +  str(datetime.datetime.now()).split('.')[0]
        body = """Someone is at your house."""

        self.create_message(body, subject)
        self.attach(images=images)

        print('Sending alert email\n')
        try:
            self.send_message()
            print('Message sent successfully\n')
        except Exception as e:
            print(e)
            print('No message sent. Error recorded\n')
            self.error_times.append(str(datetime.datetime.now()).split('.')[0])
            copyfile('Someone_here_0.png', self.err_folder + str(datetime.datetime.now()).split('.')[0] + '.png')

    def check_errors(self):
        # Similar to timing method in Object detection script
        # will only retry error message every 10 seconds
        if len(self.error_times) != 0 and self.check_time():
            subject = "Little_Brother Error! - " +  str(datetime.datetime.now()).split('.')[0]
            body = """Errors occurred at the following times. Backlog incoming.\n"""
            for e_time in self.error_times:
                body += e_time + "\n"

            self.create_message(body, subject)

            print('Sending error email\n')
            try:
                self.send_message()
                print('Error email sent successfully\n')
                self.error_times = []
            except Exception as e:
                print(e)
                print('Error message failed. Will try again\n')
                self.timer = timeit.default_timer()

    def send_backlog(self):
        backlog = listdir(self.err_folder)
        if len(backlog) != 0 and self.check_time():
            images = backlog[:10]
            subject = "Little_Brother Error backlog- " +  str(datetime.datetime.now()).split('.')[0]
            body = """"""

            self.create_message(body, subject)
            self.attach(images=images, folder=self.err_folder)

            print('Sending backlog email\n')
            try:
                self.send_message()
                print('Message sent successfully\n')
                for img in images:
                    filename = self.err_folder + img
                    remove(filename)

            except Exception as e:
                print(e)
                print('Error message failed. Will try again\n')
                self.timer = timeit.default_timer()
