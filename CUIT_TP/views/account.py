from flask import Blueprint, render_template
from CUIT_TP.forms.account import RegisterForm


bp = Blueprint('account', __name__)
@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print('register ok')
        return 'ok'
    else:
        print(form.validate())
    return render_template('account/register.html', form=form)
