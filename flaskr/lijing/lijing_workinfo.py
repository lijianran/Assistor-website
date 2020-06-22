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


bp = Blueprint('lijing_workinfo', __name__, url_prefix='/lijing_workinfo')


@bp.route('/hello')
def hello():
    db = get_lijing_db()
    year_data = db.execute('select year from year_list').fetchall()
    year_list = []
    year_new = datetime.datetime.now().year
    if len(year_data) == 0:
        year_list = ['暂无数据']
    else:
        for year in year_data:
            year_list.insert(0, year['year'])
        year_new = int(year_list[0]) + 1
        if 'year_current' not in session:
            session['year_current'] = year_list[0]
    return render_template('lijing/workInfo.html', year_list=year_list, year_new=year_new)


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':
        db = get_lijing_db()

        year_select = request.form.get('year_select')
        print(year_select)

        sql_data = {}
        with open('flaskr\sql_lijing.json', 'r') as f:
            sql_data = json.load(f)

        sql_create = ['', '', '', '', '']
        sql_create[0] = 'CREATE TABLE school_' + \
            year_select + sql_data['school']
        sql_create[1] = 'CREATE TABLE job_' + \
            year_select+sql_data['job']
        sql_create[2] = 'CREATE TABLE class_' + \
            year_select+sql_data['class']
        sql_create[3] = 'CREATE TABLE rank_' + \
            year_select+sql_data['rank']
        sql_create[4] = 'CREATE TABLE workload_' + \
            year_select+sql_data['workload']

        year_data = db.execute(
            'select workinfo from year_list where year = ?', (year_select,)).fetchall()
        flag_table = year_data[0]['workinfo']

        if flag_table == 0:
            for sql in sql_create:
                db.execute(sql)
            db.execute(
                'update year_list set workinfo = 1 where year = ?', (year_select,))
            db.commit()

        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        if filename.endswith('.xlsx'):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(
                basepath, '..\\static\\uploads', filename)
            print(upload_path)
            f.save(upload_path)

            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)
            print("总行数：" + str(table.nrows))
            print("总列数：" + str(table.ncols))

            dict_title = {
                '姓名': 0, '所在分校': 1, '行政职务': 2, '总课时数': 3, '年度考核': 4, '是否班主任': 5
            }

            rank_dict = {'任教学科': [], '任教班级': [], '上学期末排名': [],
                         '上学期全县排名': [], '下学期末排名': [], '下学期全县排名': []}

            row_title = table.row_values(0)
            title_id = [-1 for i in range(6)]
            for i in range(0, len(row_title)):
                title_name = row_title[i]
                if title_name in dict_title:
                    title_id[dict_title[title_name]] = i

            for key in rank_dict.keys():
                for i in range(1, 6):
                    title = key + str(i)
                    for j in range(0, len(row_title)):
                        title_name = row_title[j]
                        if title_name == title:
                            rank_dict[key].append(j)
                            break
            print(rank_dict)

            school_data = []
            for i in range(1, table.nrows):
                row_value = table.row_values(i)
                school_data.append(row_value[title_id[dict_title['所在分校']]])

            school_data = list(set(school_data))
            for school in school_data:
                sql_school = 'insert into school_' + year_select + \
                    ' (school_name) values (?)'
                db.execute(sql_school, (school,))
                db.commit()

            for i in range(1, table.nrows):
                row_value = table.row_values(i)
                job_name = row_value[title_id[dict_title['行政职务']]]
                name = row_value[title_id[dict_title['姓名']]]
                school = row_value[title_id[dict_title['所在分校']]]
                lesson_number = row_value[title_id[dict_title['总课时数']]]
                year_result = row_value[title_id[dict_title['年度考核']]]
                class_name = row_value[title_id[dict_title['是否班主任']]]
                person_id = db.execute(
                    'select person_id from person_'+year_select+' where person_name = ?', (name,)).fetchone()['person_id']
                school_id = db.execute(
                    'select school_id from school_'+year_select+' where school_name = ?', (school,)).fetchone()['school_id']

                sql_job = 'insert into job_' + year_select + \
                    '(job_name, person_id, school_id) values (?,?,?)'
                sql_workload = 'insert into workload_' + year_select + \
                    '(lesson_number, year_result, person_id) values (?,?,?)'
                sql_class = 'insert into class_' + year_select + \
                    '(class_name, school_id, person_id) values (?,?,?)'

                db.execute(sql_workload, (lesson_number,
                                          year_result, person_id, ))
                if job_name != '':
                    db.execute(sql_job, (job_name, person_id, school_id, ))
                if class_name != '':
                    db.execute(sql_class, (class_name, school_id, person_id, ))
                db.commit()
                sql_rank = 'insert into rank_' + year_select + \
                    '(subject, class_id, person_id, rank_up_school, rank_up_country, rank_down_school, rank_down_country) values (?,?,?,?,?,?,?)'
                for i in range(5):
                    subject = row_value[rank_dict['任教学科'][i]]
                    if subject == '':
                        break
                    rank_up_school = row_value[rank_dict['上学期末排名'][i]]
                    rank_up_country = row_value[rank_dict['上学期全县排名'][i]]
                    rank_down_school = row_value[rank_dict['下学期末排名'][i]]
                    rank_down_country = row_value[rank_dict['下学期全县排名'][i]]
                    classname = row_value[rank_dict['任教班级'][i]]
                    print(classname, subject)
                    print(school, name)
                    # class_id = db.execute(
                    #     'select class_id from class_'+year_select+' where class_name = ? and school_id = ?', (classname, school_id,)).fetchone()['class_id']
                    # print(class_id, subject, person_id)
                    
                    # db.execute(sql_rank, (subject, class_id, person_id, rank_up_school,
                    #                       rank_up_country, rank_down_school, rank_down_country,))
                db.commit()

            os.remove(upload_path)

            return redirect(url_for('lijing_workinfo.hello'))
        else:
            error = '请导入xlsx格式的文件'
            flash(error)
            return redirect(url_for('lijing_workinfo.hello'))
