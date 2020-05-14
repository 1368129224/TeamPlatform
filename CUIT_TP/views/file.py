import json
from flask import Blueprint, render_template, request, url_for, abort, make_response, send_file
from flask_login import current_user, login_required
from CUIT_TP.models import User, File
from CUIT_TP import db, app, login


bp = Blueprint('file', __name__)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# 上传文件
@bp.route('/upload/', methods=('GET', 'POST'))
@login_required
def upload():
    from uuid import uuid4
    import os
    if request.method == 'POST':
        if request.files.get('file'):
            file = request.files.get('file')
            origin_filename = file.filename
            ext = os.path.splitext(origin_filename)[1]
            if ext not in {'.doc', '.docx', '.xls', '.xlsx', '.pdf', '.ppt', 'pptx', '.md', '.txt'}:
                return make_response('-1', 200)
            uuid = uuid4().hex
            new_filename = uuid + ext
            filepath = os.path.join(os.path.join(app.config['BASEDIR'], 'upload'), new_filename)
            new_file = File()
            is_team_file = request.form.get('is_team_file')
            if is_team_file == '0':
                new_file.is_lab_file = True
            else:
                new_file.is_lab_file = False
            if current_user.role == 'admin':
                new_file.is_lab_file = True
            new_file.file_origin_name = origin_filename
            new_file.file_uuid = uuid
            new_file.file_new_name = new_filename
            new_file.file_path = filepath
            new_file.uploader = current_user
            current_user.files.append(new_file)
            if not os.path.exists(os.path.join(app.config['BASEDIR'], 'upload')):
                os.mkdir(os.path.join(app.config['BASEDIR'], 'upload'))
            file.save(filepath)
            db.session.add(new_file)
            db.session.commit()
            return make_response('true', 200)
        else:
            return make_response('false', 200)
    else:
        return render_template('file/upload.html')

# 文件列表
@bp.route('/files/')
@login_required
def files():
    return render_template('file/files.html')

# 小组文件
@bp.route('/team_files/<int:page>/')
@login_required
def team_files(page=1):
    if File.query.join(User).filter(File.is_lab_file==False, User.belong_team_id==current_user.belong_team_id).all():
        files = File.query.join(User).filter(File.is_lab_file==False, User.belong_team_id==current_user.belong_team_id).order_by(File.upload_datetime.desc()).paginate(page, 5, False)
    else:
        files = None
    return render_template('file/team_files.html', files=files)

# 实验室文件
@bp.route('/lab_files/<int:page>/')
@login_required
def lab_files(page=1):
    if File.query.filter(File.is_lab_file==True).all():
        files = File.query.filter(File.is_lab_file==True).order_by(File.upload_datetime.desc()).paginate(page, 5, False)
    else:
        files = None
    return render_template('file/lab_files.html', files=files)

# 我的文件
@bp.route('/my_files/<int:page>/')
@login_required
def my_files(page=1):
    files = File.query.filter(File.uploader==current_user).order_by(File.upload_datetime.desc()).paginate(page, 5, False)
    return render_template('file/my_files.html', files=files)

# 所有文件
@bp.route('/all_files/<int:page>/')
@login_required
def all_files(page=1):
    files = File.query.order_by(File.upload_datetime.desc()).paginate(page, 5, False)
    return render_template('file/all_files.html', files=files)

# 删除文件
@bp.route('/delete/', methods=('POST', 'GET'))
@login_required
def delete():
    file_id = json.loads(request.get_data().decode(encoding='utf-8')).get('file_id')
    file = File.query.filter(File.id==file_id).first_or_404()
    if file.uploader == current_user or current_user.role == 'admin':
        db.session.delete(file)
        import os
        os.remove(file.file_path)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 下载文件
@bp.route('/download/<int:file_id>/')
@login_required
def download(file_id):
    file = File.query.filter(File.id==file_id).first()
    return send_file(file.file_path, file.file_new_name, as_attachment=True, attachment_filename=file.file_origin_name)
