import functools

from flask import(
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '用户名不能为空'
        elif not password:
            error = '密码不能为空'
        elif db.execute(
            'select users_id from users where username=?', (username,)
        ).fetchone() is not None:
            error = '用户名{}已经被注册'.format(username)

        table = 'users'
        sql = 'insert into '+table+' (username, password) values (?, ?)'
        if error is None:
            db.execute(
                sql,
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('lijing.index'))

        flash(error)

    return render_template('lijing/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '账号错误'
        elif not check_password_hash(user['password'], password):
            error = '密码错误'

        if error is None:
            session.clear()
            session['user_id'] = user['users_id']
            return redirect(url_for('lijing.board'))

        flash(error)

    return redirect(url_for('lijing.index'))
    # return render_template('lijing/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE users_id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('lijing.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
