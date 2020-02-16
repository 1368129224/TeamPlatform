from flask import Blueprint, render_template
from flask_mail import Message
from CUIT_TP import mail


bp = Blueprint('home', __name__)
@bp.route('/')
def index():
    # msg = Message(
    #     subject="Hello World!",
    #     body="test!",
    #     sender="zzc1368129224@qq.com",
    #     recipients=["zooter_z@126.com"]
    # )
    # mail.send(msg)
    return render_template('home/index.html')
