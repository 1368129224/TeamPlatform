from flask_mail import Message
from threading import Thread
from CUIT_TP import app, mail


def send_async_email(myapp, msg):
    with myapp.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()