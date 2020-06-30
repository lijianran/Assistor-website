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
import datetime
from pypinyin import lazy_pinyin

bp = Blueprint('lijing_honorinfo', __name__, url_prefix='/lijing_honorinfo')


@bp.route('/hello')
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

    flag_table = db.execute(
        'select honorinfo from year_list where year = ?', (year_list[0], )).fetchone()['honorinfo']
    if flag_table == 0:
        sql_data = {}
        with open('flaskr\sql_lijing.json', 'r') as f:
            sql_data = json.load(f)

        sql_create = 'CREATE TABLE honor_' + \
            session['year_current'] + sql_data['honor']

        db.execute(sql_create)

        db.execute('update year_list set honorinfo = 1 where year = ?',
                   (session['year_current'], ))
        db.commit()

    return render_template('lijing/honorInfo.html', year_list=year_list)


@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    db = get_lijing_db()

    data = []

    try:
        sql = 'select p.person_id, p.person_name, count(h.person_id) num from person_'+session['year_current'] + \
            ' as p LEFT JOIN honor_' + \
            session['year_current'] + \
            ' as h on p.person_id = h.person_id GROUP by p.person_id'
        result = db.execute(sql).fetchall()

        for row in result:
            d = {}
            d['id'] = row['person_id']
            d['name'] = row['person_name']
            if row['num'] == 0:
                d['num'] = '无'
            else:
                d['num'] = row['num']
            data.append(d)
    except:
        return jsonify({'total': len(data), 'rows': data})

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


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':

        db = get_lijing_db()
        # year_select = request.form.get('year_select')
        year_select = session['year_current']

        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        if filename.endswith('.xlsx'):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(
                basepath, '..\\static\\uploads', filename)
            f.save(upload_path)

            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)
            print("总行数：" + str(table.nrows))
            print("总列数：" + str(table.ncols))

            # 找到标题
            dict_title = {'姓名': 0, '所在分校': 1, '发证时间': 2, '获得时间': 3,
                          '发证单位': 4, '获奖名称': 5, '证书级别': 6, '证书编号': 7, '备注': 8}
            row_title = table.row_values(0)
            title_id = [-1 for i in range(9)]
            for i in range(0, len(row_title)):
                title_name = row_title[i]
                if title_name in dict_title:
                    title_id[dict_title[title_name]] = i

            # 教师基本信息
            person_data = db.execute(
                'select person_id, person_name from person_'+year_select).fetchall()
            person_id_dict = {}
            # person_name_list = []
            for i in person_data:
                person_id_dict[i['person_name']] = i['person_id']
                # person_name_list.append(i['person_name'])

            # 导入数据
            for i in range(1, table.nrows):
                row_value = table.row_values(i)
                person_name = float_int_string(row_value[title_id[0]])
                if person_name not in person_id_dict:
                    error = '教师姓名：“'+person_name+'” 不存在'
                    flash(error)
                    return redirect(url_for('lijing_honorinfo.hello'))
                    # 表中有不存在基本信息的教师
                person_id = person_id_dict[person_name]
                print(person_id, person_name)

                insert_data = [0 for i in range(9)]
                for j in range(0, len(title_id)):
                    if title_id[j] == -1:
                        insert_data[j] = '待添加'
                    else:
                        insert_data[j] = float_int_string(
                            row_value[title_id[j]])
                        if len(insert_data[j]) == 0:
                            insert_data[j] = '待添加'
                print(insert_data)

                db.execute('insert into honor_' + year_select + ' (person_id, school_name, honor_time, get_time, honor_unit, honor_name, honor_grade, honor_number, honor_remark) values (?,?,?,?,?,?,?,?,?)',
                           (person_id, insert_data[1], insert_data[2], insert_data[3], insert_data[4], insert_data[5], insert_data[6], insert_data[7], insert_data[8], ))

                db.commit()

            os.remove(upload_path)

            return redirect(url_for('lijing_honorinfo.hello'))
        else:
            error = '请导入xlsx格式的文件'
            flash(error)
            return redirect(url_for('lijing_honorinfo.hello'))


@bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id', 0, type=int)
    db = get_lijing_db()
    print(person_id)

    data = []
    item = ['school_name', 'honor_time', 'get_time', 'honor_unit',
            'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
    result = db.execute('select school_name, honor_time, get_time, honor_unit, honor_name, honor_grade, honor_number, honor_remark from honor_' +
                        session['year_current']+' where person_id = ?', (person_id, )).fetchall()
    for row in result:
        d = {}
        for i in range(len(row)):
            d[item[i]] = row[item[i]]
        data.append(d)

    return jsonify({'data_list': data})


@bp.route('/add_honor', methods=('GET', 'POST'))
def add_honor():
    if request.method == 'POST':
        person_name = request.form['person_name']

        db = get_lijing_db()
        # 教师基本信息
        person_data = db.execute(
            'select person_id, person_name from person_'+session['year_current']).fetchall()
        person_id_dict = {}
        # person_name_list = []
        for i in person_data:
            person_id_dict[i['person_name']] = i['person_id']

        if person_name not in person_id_dict:
            flash('教师 “'+person_name+'” 不存在')
            return redirect(url_for('lijing_honorinfo.hello'))

        person_id = person_id_dict[person_name]

        item = ['school_name', 'honor_time', 'get_time', 'honor_unit',
                'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
        add_data = []
        for i in item:
            add_data.append(request.form[i])

        db.execute('insert into honor_' + session['year_current'] + ' (person_id, school_name, honor_time, get_time, honor_unit, honor_name, honor_grade, honor_number, honor_remark) values (?,?,?,?,?,?,?,?,?)',
                   (person_id, add_data[0], add_data[1], add_data[2], add_data[3], add_data[4], add_data[5], add_data[6], add_data[7], ))
        db.commit()

        return redirect(url_for('lijing_honorinfo.hello'))


@bp.route('/update_honor', methods=('GET', 'POST'))
def update_honor():

    person_id = request.args.get('person_id')
    update_number = int(request.args.get('update_number'))
    print(person_id, update_number)

    item = ['school_name', 'honor_time', 'get_time', 'honor_unit', 'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
    honor_data = []
    for i in range(update_number):
        honor = []
        for r in item:
            honor.append(request.args.get(r+str(i)))
        honor_data.append(honor)
    print(honor_data)
    # update_data = [0 for i in range(25)]
    # item = ['person_name', "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
    #         "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
    #         "skill_title", "time_skill", "skill_unit", "skill_number",
    #         "time_school", "work_kind", "job_post", "time_retire"]

    # for i in range(0, len(item)):
    #     update_data[i] = request.args.get(item[i], '暂无', type=str)
    #     if update_data[i] == '':
    #         update_data[i] = '暂无'

    # person_id = request.args.get("person_id", '暂无', type=str)
    # print(update_data)
    # print(person_id)

    # db = get_lijing_db()
    # sql_person = 'update person_' + \
    #     session['year_current'] + \
    #     ' set person_name = ?,gender = ?,id_number = ?,phone = ?,political_status = ?,time_Party = ?,time_work = ?,address = ?,resume = ? where person_id = ?'
    # db.execute(sql_person,
    #            (update_data[0], update_data[1], update_data[2], update_data[3], update_data[4],
    #             update_data[5], update_data[6], update_data[7], update_data[8], person_id))

    # sql_education = 'update education_' + \
    #     session['year_current'] + \
    #     ' set edu_start = ?,time_edu_start = ?,school_edu_start = ?,major_edu_start = ?,edu_end = ?,time_edu_end = ?,school_edu_end = ?,major_edu_end = ? where person_id = ?'
    # db.execute(sql_education,
    #            (update_data[9], update_data[10], update_data[11], update_data[12], update_data[13],
    #             update_data[14], update_data[15], update_data[16], person_id))

    # sql_skill = 'update skill_' + \
    #     session['year_current'] + \
    #     ' set skill_title = ?,time_skill = ?,skill_unit = ?,skill_number = ? where person_id = ?'
    # db.execute(sql_skill,
    #            (update_data[17], update_data[18], update_data[19], update_data[20], person_id))

    # sql_workinfo = 'update workinfo_' + \
    #     session['year_current'] + \
    #     ' set time_school = ?,work_kind = ?,job_post = ?,time_retire = ? where person_id = ?'
    # db.execute(sql_workinfo,
    #            (update_data[21], update_data[22],
    #             update_data[23], update_data[24], person_id))
    # db.commit()
    # msg = '成功修改教师“' + update_data[0] + '”的基本信息'
    msg = '成功修改'
    return {'msg': msg}


def float_int_string(float_num):
    if type(float_num) != str:
        float_num = str(int(float_num))
    return float_num


@bp.route('/set_year')
def set_year():
    year = request.args.get('year')
    session['year_current'] = year
    msg = 'success'
    return {'msg': msg}
