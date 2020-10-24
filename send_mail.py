import smtplib, ssl

from email import message
from config import _config

def send_mail(receiver, subject, body):
    smtp_server = _config['notification']['smtp_server']
    port = _config['notification']['smtp_port']
    sender_email = _config['notification']['from']
    password = _config['notification']['password']
    receiver_email = receiver

    msg = message.Message()
    msg.add_header('from', sender_email)
    msg.add_header('to', receiver_email)
    msg.add_header('subject', subject)
    msg.set_payload(body)

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls() # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string().encode('utf-8'))