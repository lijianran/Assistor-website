from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db, get_lijing_db

from random import choice
import os

bp = Blueprint('lijing', __name__, url_prefix='/lijing')


@bp.route('/hello')
def hello():
    return render_template('lijing/hello.html')


@bp.route('/basicInfo')
def basicInfo():
    return render_template('lijing/basicInfo.html')


@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    db = get_lijing_db()

    data = []
    result = db.execute('select * from person').fetchall()
    for row in result:
        d = {}
        d['id'] = row['person_id']
        d['name'] = row['person_name']
        d['price'] = row['gender']
        data.append(d)

    print(data)

    if request.method == 'POST':
        print('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
        # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
        # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了


@bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id', 0, type=int)
    db = get_lijing_db()

    data = {}
    result = db.execute(
        'select * from person where person_id = ?', (person_id,)).fetchall()
    for row in result:
        data['id'] = row['person_id']
        data['name'] = row['person_name']
        data['price'] = row['gender']

    print(data)
    return data


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':
        f = request.files['file']
        print(secure_filename(f.filename))
        # flash(f)
    return redirect(url_for('lijing.basicInfo'))

