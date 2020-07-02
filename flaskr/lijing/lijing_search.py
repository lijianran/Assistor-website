from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

from flaskr.db import get_db, get_lijing_db

from flaskr.lijing.lijing_index import float_int_string

# from random import choice
# import os
# import xlrd
# import xlsxwriter
# import json
# import datetime
# from pypinyin import lazy_pinyin

bp = Blueprint('lijing_search', __name__, url_prefix='/lijing_search')


@bp.route('/hello')
@login_required
def hello():
    db = get_lijing_db()

    year_data = db.execute('select year from year_list').fetchall()
    year_list = []
    if len(year_data) == 0:
        year_list = ['暂无数据']
        session['year_current'] = year_list[0]
        return render_template('lijing/honorInfo.html', year_list=year_list)
    else:
        for year in year_data:
            year_list.insert(0, year['year'])

    session['year_current'] = year_list[0]

    # flag_table = db.execute(
    #     'select honorinfo from year_list where year = ?', (year_list[0], )).fetchone()['honorinfo']
    # if flag_table == 0:
    #     sql_data = {}
    #     with open('flaskr\sql_lijing.json', 'r') as f:
    #         sql_data = json.load(f)

    #     sql_create = 'CREATE TABLE honor_' + \
    #         session['year_current'] + sql_data['honor']

    #     db.execute(sql_create)

    #     db.execute('update year_list set honorinfo = 1 where year = ?',
    #                (session['year_current'], ))
    #     db.commit()

    return render_template('lijing/search.html', year_list=year_list)
