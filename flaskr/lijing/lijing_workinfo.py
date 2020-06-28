from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session, send_file, send_from_directory
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db, get_lijing_db

from random import choice
import os
import xlrd
import xlsxwriter
import json
from pypinyin import lazy_pinyin


bp = Blueprint('lijing_workinfo', __name__, url_prefix='/lijing_workinfo')


@bp.route('/hello')
def hello():
    db = get_lijing_db()

    year_data = db.execute('select year, workinfo from year_list').fetchall()
    year_list = []
    if len(year_data) == 0:
        year_list = ['暂无数据']
        session['year_current'] = year_list[0]
        return render_template('lijing/workInfo.html', year_list=year_list, school_list=['暂无分校'], class_list={})
    else:
        for year in year_data:
            year_list.insert(0, year['year'])
        # if 'year_current' not in session:
    session['year_current'] = year_list[0]

    flag_table = db.execute(
        'select workinfo from year_list where year = ?', (year_list[0], )).fetchone()['workinfo']
    if flag_table == 0:
        sql_data = {}
        with open('flaskr\sql_lijing.json', 'r') as f:
            sql_data = json.load(f)
            sql_create = ['', '', '', '', '']
            sql_create[0] = 'CREATE TABLE school_' + \
                session['year_current'] + sql_data['school']
            sql_create[1] = 'CREATE TABLE job_' + \
                session['year_current']+sql_data['job']
            sql_create[2] = 'CREATE TABLE class_' + \
                session['year_current']+sql_data['class']
            sql_create[3] = 'CREATE TABLE rank_' + \
                session['year_current']+sql_data['rank']
            sql_create[4] = 'CREATE TABLE workload_' + \
                session['year_current']+sql_data['workload']

        for sql in sql_create:
            db.execute(sql)
        db.execute('insert into school_' +
                   session['year_current']+' (school_name) values (?)', ('暂无分校', ))
        db.execute('update year_list set workinfo = 1 where year = ?',
                   (session['year_current'], ))
        db.commit()

    school_list = []
    school_id = []
    school_data = db.execute(
        'select school_id, school_name from school_'+session['year_current']).fetchall()
    for i in school_data:
        school_list.append(i['school_name'])
        school_id.append(i['school_id'])

    class_list = {}
    for i in range(len(school_list)):
        class_data = db.execute('select class_name from class_' +
                                session['year_current']+' where school_id = ?', (school_id[i],)).fetchall()
        clas = []
        for j in class_data:
            clas.append(j['class_name'])

        class_list[str(school_list[i])] = clas

    if len(school_list) != 1:
        school_list = school_list[1:]
        del class_list['暂无分校']

    return render_template('lijing/workInfo.html', year_list=year_list, school_list=school_list, class_list=class_list)


@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    db = get_lijing_db()

    data = []
    year = session['year_current']
    if year == '暂无数据':
        return jsonify({'total': len(data), 'rows': data})
    person = 'person_'+year
    rank = 'rank_'+year
    clas = 'class_'+year
    school = 'school_'+year
    job = 'job_'+year

    person_list = []
    person_id_list = []
    person_data = db.execute(
        'select person_id, person_name from '+person).fetchall()
    for i in person_data:
        person_list.append(i['person_name'])
        person_id_list.append(i['person_id'])

    school_name_list = []
    for i in person_id_list:
        school_data = db.execute('select school_name from '+job+' join '+school+' on '+job +
                                 '.school_id = '+school+'.school_id where person_id = ?', (i, )).fetchone()
        if school_data is None:
            # if db.execute('select job_name from job_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
            #     db.execute('insert into job_'+year_select+' (person_id, job_name) values (?,?)')
            db.execute(
                'insert into '+job+' (job_name, school_id, person_id) values (?,?,?)', ('无', 1, i, ))
            db.commit()
            school_name_list.append('暂无分校')
        else:
            school_name_list.append(school_data['school_name'])

    for i in range(len(person_id_list)):
        d = {}
        d['id'] = person_id_list[i]
        d['name'] = person_list[i]
        d['school'] = school_name_list[i]
        data.append(d)

    if request.method == 'POST':
        print('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        # print('get', limit)
        # print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
        # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
        # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了


@bp.route('/add_school', methods=('GET', 'POST'))
def add_school():
    school_name = request.args.get('school')
    year_select = request.args.get('year')

    db = get_lijing_db()

    school_data = db.execute(
        'select school_name from school_'+year_select).fetchall()
    school_list = []
    for s in school_data:
        school_list.append(s['school_name'])
    if school_name in school_list:
        return jsonify({'msg': 'error', 'error': '分校已经存在'})

    sql_school = 'insert into school_' + \
        year_select + ' (school_name) values (?)'
    db.execute(sql_school, (school_name,))
    db.commit()

    school_list = []
    school_data = db.execute(
        'select school_name from school_'+year_select).fetchall()
    for i in school_data:
        school_list.append(i['school_name'])

    class_list = {}
    for i in range(len(school_list)):
        class_data = db.execute('select class_name from class_' +
                                year_select+' where school_id = ?', (i+1,)).fetchall()
        clas = []
        for j in class_data:
            clas.append(j['class_name'])

        class_list[str(school_list[i])] = clas

    if len(school_list) != 1:
        school_list = school_list[1:]
        del class_list['暂无分校']

    return jsonify({'msg': '成功添加' + school_name, 'school_list': school_list, 'class_list': class_list})


@bp.route('/add_class', methods=('GET', 'POST'))
def add_class():
    year_select = request.args.get('year')
    school_name = request.args.get('school')
    class_name = request.args.get('class')
    person_name = request.args.get('person')
    # print(year_select, school_name, class_name, person_name)

    db = get_lijing_db()

    school_id = db.execute(
        'select school_id from school_'+year_select+' where school_name = ?', (school_name,)).fetchone()['school_id']
    person_data = db.execute(
        'select person_id from person_'+year_select+' where person_name = ?', (person_name,)).fetchone()
    class_data = db.execute(
        'select class_name from class_'+year_select+' where school_id = ?', (school_id, )).fetchall()
    class_list = []
    for clas in class_data:
        class_list.append(clas['class_name'])

    # print(school_id, person_data, class_list)
    if class_name in class_list:
        return jsonify({'msg': 'error', 'error': '班级已经存在'})
    if person_data == None:
        return jsonify({'msg': 'error', 'error': '不存在该教师'})

    sql_class = 'insert into class_' + year_select + \
        '(class_name, school_id, person_id) values (?,?,?)'

    db.execute(sql_class, (class_name, school_id, person_data['person_id'], ))
    db.commit()

    school_list = []
    school_data = db.execute(
        'select school_name from school_'+year_select).fetchall()
    for i in school_data:
        school_list.append(i['school_name'])

    class_lists = {}
    for i in range(len(school_list)):
        class_data = db.execute('select class_name from class_' +
                                year_select+' where school_id = ?', (i+1,)).fetchall()
        clas = []
        for j in class_data:
            clas.append(j['class_name'])

        class_lists[str(school_list[i])] = clas

    if len(school_list) != 1:
        school_list = school_list[1:]
        del class_lists['暂无分校']

    return jsonify({'msg': '成功添加班级', 'school_list': school_list, 'class_list': class_lists})


@bp.route('/readfile', methods=('GET', 'POST'))
def readfile():
    if request.method == "POST":
        msg = '成功'
        table_title = []

        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))
        print(filename)

        if filename.endswith('.xlsx'):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(
                basepath, '..\\static\\uploads', filename)
            # print(upload_path)
            f.save(upload_path)

            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)
            print("总行数：" + str(table.nrows))
            print("总列数：" + str(table.ncols))
            table_title = table.row_values(0)

            # print(table_title)
            # print(len(table_title))

            os.remove(upload_path)
        else:
            msg = '请导入xlsx格式的文件'

    return jsonify({'msg': msg, 'table_title': table_title})


def float_int_string(float_num):
    if type(float_num) == float:
        float_num = str(int(float_num))
    return float_num


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':

        db = get_lijing_db()

        # year_select = session['year_current']
        # print(session['year_current'])

        f = request.files['file']
        year_select = request.form.get('year')
        item_id_list = request.form.get('item_id_list').split(',')

        filename = secure_filename(''.join(lazy_pinyin(f.filename)))
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(
            basepath, '..\\static\\uploads', filename)

        f.save(upload_path)

        data = xlrd.open_workbook(upload_path)
        table = data.sheet_by_index(0)
        item = ['person_name', 'school_name', 'job_name', 'lesson_number', 'year_result',
                'class_id', 'subject', 'rank_up_school', 'rank_up_country', 'rank_down_school', 'rank_down_country']

        update_item = {}
        for i in range(len(item)):
            if item_id_list[i] != '0':
                update_item[item[i]] = int(item_id_list[i]) - 1

        print(update_item)

        person_data = db.execute(
            'select person_id, person_name from person_'+year_select).fetchall()
        person_id_dict = {}
        person_name_list = []
        for i in person_data:
            person_id_dict[i['person_name']] = i['person_id']
            person_name_list.append(i['person_name'])

        for i in range(1, table.nrows):
            row = table.row_values(i)
            person_name = row[update_item['person_name']]
            if person_name not in person_name_list:
                return jsonify({'msg': '教师姓名：“'+person_name+'” 不存在'})
                # 表中有不存在基本信息的教师
            person_id = person_id_dict[person_name]

            if 'lesson_number' in update_item:
                lesson_number = row[update_item['lesson_number']]
                if db.execute('select workload_id from workload_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
                    db.execute('insert into workload_'+year_select +
                               ' (lesson_number, year_result, person_id) values (?,?,?)', (lesson_number, '', person_id, ))
                else:
                    db.execute('update workload_' + year_select +
                               ' set lesson_number = ? where person_id = ?', (lesson_number, person_id, ))

            if 'year_result' in update_item:
                year_result = row[update_item['year_result']]
                if db.execute('select workload_id from workload_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
                    db.execute('insert into workload_'+year_select +
                               ' (lesson_number, year_result, person_id) values (?,?,?)', ('', year_result, person_id, ))
                else:
                    db.execute('update workload_' + year_select +
                               ' set year_result = ? where person_id = ?', (year_result, person_id, ))

            if 'school_name' in update_item:
                school_name = row[update_item['school_name']]
                school_id_data = db.execute(
                    'select school_id from school_'+year_select+' where school_name = ?', (school_name, )).fetchone()
                if school_id_data is None:
                    return jsonify({'msg': '分校：“'+school_name+'” 不存在'})
                school_id = school_id_data['school_id']

                db.execute('update job_'+year_select +
                           ' set school_id = ? where person_id = ?', (school_id, person_id, ))

            if 'job_name' in update_item:
                job_name = row[update_item['job_name']]
                if job_name == '':
                    job_name = '无'
                db.execute('update job_'+year_select +
                           ' set job_name = ? where person_id = ?', (job_name, person_id, ))

            if 'class_id' in update_item:
                school_name = row[update_item['school_name']]
                school_id = db.execute(
                    'select school_id from school_'+year_select+' where school_name = ?', (school_name, )).fetchone()['school_id']

                class_name = float_int_string(row[update_item['class_id']])
                class_id_data = db.execute(
                    'select class_id from class_'+year_select+' where school_id = ? and class_name = ? ', (school_id, class_name, )).fetchone()
                if class_id_data is None:
                    return jsonify({'msg': '分校“'+school_name+'”中不存在班级：“'+class_name+'”'})
                class_id = class_id_data['class_id']

                subject = row[update_item['subject']]
                rank_data = db.execute('select rank_up_school from rank_'+year_select +
                                       ' where person_id = ? and subject = ? and class_id = ?', (person_id, subject, class_id, )).fetchone()
                if rank_data is None:
                    db.execute('insert into rank_'+year_select + ' (subject, class_id, person_id, rank_up_school, rank_up_country, rank_down_school, rank_down_country) values (?,?,?,?,?,?,?)',
                               (subject, class_id, person_id, '暂无', '暂无', '暂无', '暂无',))

            if 'rank_up_school' in update_item:
                rank_up_school = float_int_string(
                    row[update_item['rank_up_school']])
                db.execute('update rank_'+year_select+' set rank_up_school = ? where subject = ? and person_id = ? and class_id = ?',
                           (rank_up_school, subject, person_id, class_id, ))

            if 'rank_up_country' in update_item:
                rank_up_country = float_int_string(
                    row[update_item['rank_up_country']])
                db.execute('update rank_'+year_select+' set rank_up_country = ? where subject = ? and person_id = ? and class_id = ?',
                           (rank_up_country, subject, person_id, class_id, ))

            if 'rank_down_school' in update_item:
                rank_down_school = float_int_string(
                    row[update_item['rank_down_school']])
                db.execute('update rank_'+year_select+' set rank_down_school = ? where subject = ? and person_id = ? and class_id = ?',
                           (rank_down_school, subject, person_id, class_id, ))

            if 'rank_down_country' in update_item:
                rank_down_country = float_int_string(
                    row[update_item['rank_down_country']])
                db.execute('update rank_'+year_select+' set rank_down_country = ? where subject = ? and person_id = ? and class_id = ?',
                           (rank_down_country, subject, person_id, class_id, ))

        db.commit()
        os.remove(upload_path)

        return jsonify({'msg': '成功导入'})


@bp.route('/set_year')
def set_year():
    year = request.args.get('year')
    session['year_current'] = year
    msg = 'success'
    return jsonify({'msg': msg})
