from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session, send_file, send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

from flaskr.db import get_db, get_lijing_db

from flaskr.lijing.lijing_index import float_int_string

from random import choice
import os
import xlrd
import xlsxwriter
import json
from pypinyin import lazy_pinyin


bp = Blueprint('lijing_workinfo', __name__, url_prefix='/lijing_workinfo')


@bp.route('/hello')
@login_required
def hello():
    db = get_lijing_db()

    year_data = db.execute('select year from year_list').fetchall()
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
            person_name = float_int_string(row[update_item['person_name']])
            if person_name not in person_name_list:
                return jsonify({'msg': '教师姓名：“'+person_name+'” 不存在'})
                # 表中有不存在基本信息的教师
            person_id = person_id_dict[person_name]

            if 'lesson_number' in update_item:
                lesson_number = float_int_string(
                    row[update_item['lesson_number']])
                if db.execute('select workload_id from workload_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
                    db.execute('insert into workload_'+year_select +
                               ' (lesson_number, year_result, person_id) values (?,?,?)', (lesson_number, '', person_id, ))
                else:
                    db.execute('update workload_' + year_select +
                               ' set lesson_number = ? where person_id = ?', (lesson_number, person_id, ))

            if 'year_result' in update_item:
                year_result = float_int_string(row[update_item['year_result']])
                if db.execute('select workload_id from workload_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
                    db.execute('insert into workload_'+year_select +
                               ' (lesson_number, year_result, person_id) values (?,?,?)', ('', year_result, person_id, ))
                else:
                    db.execute('update workload_' + year_select +
                               ' set year_result = ? where person_id = ?', (year_result, person_id, ))

            if 'school_name' in update_item:
                school_name = float_int_string(row[update_item['school_name']])
                school_id_data = db.execute(
                    'select school_id from school_'+year_select+' where school_name = ?', (school_name, )).fetchone()
                if school_id_data is None:
                    return jsonify({'msg': '分校：“'+school_name+'” 不存在'})
                school_id = school_id_data['school_id']

                db.execute('update job_'+year_select +
                           ' set school_id = ? where person_id = ?', (school_id, person_id, ))

            if 'job_name' in update_item:
                job_name = float_int_string(row[update_item['job_name']])
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


@bp.route('/exportData', methods=('GET', 'POST'))
def exportData():
    db = get_lijing_db()

    year = session['year_current']
    person = 'person_'+year
    clas = 'class_'+year
    school = 'school_'+year
    job = 'job_'+year
    workload = 'workload_'+year
    rank = 'rank_'+year
    sql_search = 'select p.person_name, class.class_name, school.school_name, job.job_name, work.lesson_number, work.year_result from '+person+' as p left join '+clas+' as class on p.person_id = class.person_id left join ' + \
        job+' as job on p.person_id = job.person_id left join '+workload+' as work on p.person_id = work.person_id left join ' + \
            school+' as school on job.school_id = school.school_id where p.person_id = ?'
    sql_rank = 'select subject, class_name, rank_up_school, rank_up_country, rank_down_school, rank_down_country from ' + \
        rank+' as r join '+clas+' as c on r.class_id = c.class_id where r.person_id = ?'
    print(sql_rank)

    flag_search = request.args.get('flag_search')
    id_list = []
    if flag_search == 'true':
        id_list = request.args.getlist("id_list[]")
    else:
        person_data = db.execute('select person_id from '+person).fetchall()
        for i in person_data:
            id_list.append(i['person_id'])

    export_item = ['person_name', 'class_name', 'school_name',
                   'job_name', 'lesson_number', 'year_result']
    rank_item = ['subject', 'class_name', 'rank_up_school',
                 'rank_up_country', 'rank_down_school', 'rank_down_country']
    table_data = []
    rank_number = 0
    for i in id_list:
        result = db.execute(sql_search, (i, )).fetchone()
        rank = db.execute(sql_rank, (i, )).fetchall()
        if len(rank) >= rank_number:
            rank_number = len(rank)
        row = []
        for item in export_item:
            row.append(result[item])
        for r in rank:
            for item in rank_item:
                row.append(r[item])

        table_data.append(row)

    item_name_dict = {'person_name': '姓名', 'class_name': '是否班主任', 'school_name': '所在分校',
                      'job_name': '行政职务', 'lesson_number': '总课时数', 'year_result': '年度考核'}
    rank_name_list = ['任教班级', '任教学科', '上学期全校排名',
                      '上学期全县排名', '下学期全校排名', '下学期全县排名']

    workbook = xlsxwriter.Workbook(
        'flaskr\\static\\downloads\\exportData.xlsx')
    worksheet = workbook.add_worksheet('Sheet1')
    for i in range(len(export_item)):
        worksheet.write(0, i, item_name_dict[export_item[i]])
    num = 6
    for i in range(0, rank_number):
        for j in range(len(rank_name_list)):
            worksheet.write(0, num+j, rank_name_list[j]+str(i+1))
        num = num + 6
    for i in range(len(id_list)):
        for j in range(len(table_data[i])):
            worksheet.write(i+1, j, table_data[i][j])

    workbook.close()

    msg = str(len(id_list))
    return jsonify({'msg': msg, 'filename': 'exportData.xlsx'})


@ bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id')

    db = get_lijing_db()
    datas = {}

    item = ['person_name', 'school_name', 'job_name',
            'lesson_number', 'year_result', 'class_master']
    year = session['year_current']
    person_name = db.execute('select person_name from person_' +
                             year+' where person_id = ?', (person_id, )).fetchone()['person_name']
    job_data = db.execute('select school_id, job_name from job_' +
                          year+' where person_id = ?', (person_id, )).fetchone()
    school_id = job_data['school_id']
    job_name = job_data['job_name']
    school_name = db.execute('select school_name from school_' +
                             year+' where school_id = ?', (school_id, )).fetchone()['school_name']

    workload_data = db.execute('select lesson_number, year_result from workload_' +
                               year+' where person_id = ?', (person_id, )).fetchone()
    if workload_data is None:
        lesson_number = '暂无'
        year_result = '暂无'
    else:
        lesson_number = workload_data['lesson_number']
        year_result = workload_data['year_result']

    class_data = db.execute('select class_name from class_' +
                            year+' where person_id = ?', (person_id, )).fetchone()
    if class_data is None:
        class_master = '否'
    else:
        class_master = class_data['class_name']

    datas['person_name'] = person_name
    datas['school_name'] = school_name
    datas['job_name'] = job_name
    datas['lesson_number'] = lesson_number
    datas['year_result'] = year_result
    datas['class_master'] = class_master

    rank_data = db.execute('select subject, class_id, rank_up_school, rank_up_country, rank_down_school, rank_down_country from rank_' +
                           year+' where person_id = ?', (person_id, )).fetchall()
    rank_list = []
    for i in rank_data:
        d = []
        d.append(db.execute('select class_name from class_'+year +
                            ' where class_id = ?', (i['class_id'], )).fetchone()['class_name'])
        d.append(i['subject'])
        d.append(i['rank_up_school'])
        d.append(i['rank_up_country'])
        d.append(i['rank_down_school'])
        d.append(i['rank_down_country'])
        rank_list.append(d)
    datas['rank'] = rank_list

    return jsonify(datas)


@ bp.route('/update_data', methods=('GET', 'POST'))
def update_data():
    item = ['person_name', 'school_name', 'job_name',
            'lesson_number', 'year_result', 'class_master']
    rank_item = ['class_id', 'subject', 'rank_up_school',
                 'rank_up_country', 'rank_down_school', 'rank_down_country']

    update_data = {}
    update_data['person_id'] = int(request.args.get('person_id'))
    for i in item:
        update_data[i] = request.args.get(i)

    rank_number = int(request.args.get('rank_number'))
    rank_data = []
    for i in range(rank_number):
        rank = []
        for r in rank_item:
            rank.append(request.args.get(r+str(i)))
        rank_data.append(rank)

    db = get_lijing_db()
    year_select = session['year_current']
    person_id = update_data['person_id']

    school_name = update_data['school_name']
    school_id_data = db.execute(
        'select school_id from school_'+year_select+' where school_name = ?', (school_name, )).fetchone()
    if school_id_data is None:
        return jsonify({'msg': 'error', 'error': '分校：“'+school_name+'” 不存在'})
    school_id = school_id_data['school_id']
    db.execute('update job_'+year_select +
               ' set school_id = ? where person_id = ?', (school_id, person_id, ))

    job_name = update_data['job_name']
    db.execute('update job_'+year_select +
               ' set job_name = ? where person_id = ?', (job_name, person_id, ))

    lesson_number = update_data['lesson_number']
    if db.execute('select workload_id from workload_'+year_select+' where person_id = ?', (person_id, )).fetchone() is None:
        db.execute('insert into workload_'+year_select +
                   ' (lesson_number, year_result, person_id) values (?,?,?)', (lesson_number, '', person_id, ))
    else:
        db.execute('update workload_' + year_select +
                   ' set lesson_number = ? where person_id = ?', (lesson_number, person_id, ))

    year_result = update_data['year_result']
    db.execute('update workload_' + year_select +
               ' set year_result = ? where person_id = ?', (year_result, person_id, ))

    # 更新排名信息
    for rank in rank_data:
        class_name = rank[0]
        class_id_data = db.execute(
            'select class_id from class_'+year_select+' where school_id = ? and class_name = ? ', (school_id, class_name, )).fetchone()
        if class_id_data is None:
            return jsonify({'msg': 'error', 'error': '分校“'+school_name+'”中不存在班级：“'+class_name+'”'})
        class_id = class_id_data['class_id']

        subject = rank[1]
        rank_data = db.execute('select rank_up_school from rank_'+year_select +
                               ' where person_id = ? and subject = ? and class_id = ?', (person_id, subject, class_id, )).fetchone()
        if rank_data is None:
            db.execute('insert into rank_'+year_select + ' (subject, class_id, person_id, rank_up_school, rank_up_country, rank_down_school, rank_down_country) values (?,?,?,?,?,?,?)',
                       (subject, class_id, person_id, rank[2], rank[3], rank[4], rank[5], ))
        else:
            # db.execute('delete from rank_'+year_select +
            #            ' where person_id = ? and subject = ? and class_id = ?', (person_id, subject, class_id, ))
            db.execute('update rank_'+year_select+' set rank_up_school = ?, rank_up_country = ?, rank_down_school = ?, rank_down_country = ? where person_id = ? and subject = ? and class_id = ?',
                       (rank[2], rank[3], rank[4], rank[5], person_id, subject, class_id, ))
            # db.execute('insert into rank_'+year_select + ' (subject, class_id, person_id, rank_up_school, rank_up_country, rank_down_school, rank_down_country) values (?,?,?,?,?,?,?)',
            #            (subject, class_id, person_id, rank[2], rank[3], rank[4], rank[5], ))

    db.commit()
    return jsonify({'msg': '成功更新教师“' + update_data['person_name'] + '”的业务档案'})


@ bp.route('/search_data', methods=('GET', 'POST'))
def search_data():
    search_item = request.args.get('search_item', '暂无', type=str)
    search_string = request.args.get('search_string', '暂无', type=str)
    search_school = request.args.get('school_select', '暂无', type=str)

    db = get_lijing_db()
    year = session['year_current']
    print(search_school, search_item, search_string)

    # var item = {
    #     '姓名': 'person_name', '所在分校': 'school_name', '行政职务': 'job_name', '总课时数': 'lesson_number',
    #     '年度考核': 'year_result', '班主任': 'class_master', '任教班级': 'class_name', '任教学科': 'subject'
    # };
    person_dict = {}

    if search_school != '#全部数据':
        person_data = db.execute('select person_'+year+'.person_id, person_name from job_'+year+' join school_'+year+', person_'+year+' on job_'+year +
                                 '.school_id = school_' + year+'.school_id and job_'+year+'.person_id = person_'+year+'.person_id where school_name = ?', (search_school, )).fetchall()
    else:
        person_data = db.execute(
            'select person_id, person_name from person_'+year).fetchall()
    for person in person_data:
        person_dict[person['person_id']] = person['person_name']

    data = []
    if search_item == 'person_name':
        result = db.execute('select person_id from person_'+year +
                            ' where person_name like "%'+search_string+'%"').fetchall()

    if search_item == 'school_name':
        school_data = db.execute('select school_id from school_' +
                                 year+' where school_name like "%'+search_string+'%"').fetchone()
        if school_data is None:
            return jsonify({'msg': '不存在该分校', 'total': len(data), 'rows': data})
        result = db.execute('select person_id from job_' +
                            year+' where school_id = ?', (school_data['school_id'],)).fetchall()

    if search_item == 'job_name':
        result = db.execute('select person_id from job_' +
                            year+' where job_name like "%'+search_string+'%"').fetchall()

    if search_item == 'lesson_number':
        result = db.execute('select person_id from workload_'+year +
                            ' where lesson_number like "%'+search_string+'%"').fetchall()

    if search_item == 'year_result':
        result = db.execute('select person_id from workload_'+year +
                            ' where year_result like "%'+search_string+'%"').fetchall()

    if search_item == 'class_master':
        result = db.execute('select person_id from class_'+year +
                            ' where class_name like "%'+search_string+'%"').fetchall()

    if search_item == 'class_name':
        class_data = db.execute('select class_id from class_'+year +
                                ' where class_name like "%'+search_string+'%"').fetchall()
        if len(class_data) == 0:
            return jsonify({'msg': '不存在该班级', 'total': len(data), 'rows': data})
        elif len(class_data) == 1:
            result = db.execute('select person_id from rank_'+year +
                                ' where class_id = ?', (class_data[0]['class_id'], )).fetchall()
        else:
            if search_school == '#全部数据':
                return jsonify({'msg': '请选择分校', 'total': len(data), 'rows': data})
            else:
                class_id = db.execute('select class_id from class_'+year+' join school_'+year+' on class_'+year +
                                      '.school_id = school_'+year+'.school_id where class_name like "%'+search_string+'%"').fetchone()['class_id']
                result = db.execute('select person_id from rank_' +
                                    year + ' where class_id = ?', (class_id, )).fetchall()

    if search_item == 'subject':
        result = db.execute('select person_id from rank_' +
                            year + ' where subject like "%'+search_string+'%"').fetchall()

    person_id_list = []
    for i in result:
        person_id = i['person_id']
        if type(person_id) != int:
            person_id = int(person_id)
        if person_id not in person_dict:
            continue
        person_id_list.append(person_id)
    person_id_list = list(set(person_id_list))

    for person_id in person_id_list:
        d = {}
        d['id'] = person_id
        d['name'] = person_dict[person_id]
        data.append(d)

    msg = '成功查询到 '+str(len(data))+' 条信息'

    return jsonify({'msg': msg, 'total': len(data), 'rows': data})
