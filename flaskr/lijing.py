from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db, get_lijing_db

from random import choice
import os
import xlrd
from pypinyin import lazy_pinyin

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
        d['gender'] = row['gender']
        data.append(d)

    # print(data)

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


@bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id', 0, type=int)
    db = get_lijing_db()

    data = {}
    result = db.execute('select person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume,\
        edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,\
        skill_title,time_skill,skill_unit,skill_number,\
        time_school,work_kind,job_post,time_retire \
        from person join education, skill, workinfo \
        on person.person_id = education.person_id and person.person_id = skill.person_id and person.person_id = workinfo.person_id \
        where person.person_id = ?', (person_id,)).fetchall()

    db.commit()
    row = result[0]

    item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
            "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
            "skill_title", "time_skill", "skill_unit", "skill_number",
            "time_school", "work_kind", "job_post", "time_retire"]

    for i in range(len(row)):
        data[item[i]] = row[item[i]]

    return data


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        if filename.endswith('.xlsx'):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, 'static\\uploads', filename)
            f.save(upload_path)

            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)
            print("总行数：" + str(table.nrows))
            print("总列数：" + str(table.ncols))

            dict_title = {
                '姓名': 0, '性别': 1, '身份证号': 2, '联系电话': 3, '政治面貌': 4, '入党时间': 5, '参加工作时间': 6, '家庭住址': 7, '工作简历': 8,
                '第一学历': 9, '第一学历毕业时间': 10, '第一学历毕业学校': 11, '第一学历专业': 12, '最高学历': 13, '最高学历毕业时间': 14, '最高学历毕业学校': 15, '最高学历专业': 16,
                '专业技术职称': 17, '取得时间': 18, '发证单位': 19, '发证文件批号': 20,
                '调入大集中学时间': 21, '用工性质': 22, '工作岗位': 23, '退休时间': 24
            }
            rowVale = table.row_values(0)
            title_id = [-1 for i in range(25)]
            for i in range(0, len(rowVale)):
                title_name = rowVale[i]
                if title_name in dict_title:
                    title_id[dict_title[title_name]] = i

            db = get_lijing_db()
            for i in range(1, table.nrows):
                row_value = table.row_values(i)
                insert_data = [0 for i in range(25)]
                for j in range(0, len(title_id)):
                    if title_id[j] == -1:
                        insert_data[j] = '暂无'
                    else:
                        insert_data[j] = row_value[title_id[j]]
                        if type(insert_data) != 'str':
                            insert_data[j] = str(insert_data[j])
                        if len(insert_data[j]) == 0:
                            insert_data[j] = '暂无'

                sql_person = 'insert into person (person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume) values (?,?,?,?,?,?,?,?,?)'
                db.execute(sql_person,
                           (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4],
                            insert_data[5], insert_data[6], insert_data[7], insert_data[8]))
                person_id = db.execute(
                    'select person_id from person where id_number=?', (insert_data[2],)).fetchone()

                sql_education = 'insert into education (edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,person_id) values (?,?,?,?,?,?,?,?,?)'
                db.execute(sql_education,
                           (insert_data[9], insert_data[10], insert_data[11], insert_data[12], insert_data[13],
                            insert_data[14], insert_data[15], insert_data[16], person_id[0]))

                sql_skill = 'insert into skill (skill_title,time_skill,skill_unit,skill_number,person_id) values (?,?,?,?,?)'
                db.execute(sql_skill,
                           (insert_data[17], insert_data[18], insert_data[19], insert_data[20], person_id[0]))

                sql_workinfo = 'insert into workinfo (time_school,work_kind,job_post,time_retire,person_id) values (?,?,?,?,?)'
                db.execute(sql_workinfo,
                           (insert_data[21], insert_data[22],
                            insert_data[23], insert_data[24], person_id[0]))
                db.commit()

            os.remove(upload_path)

            return redirect(url_for('lijing.basicInfo'))
        else:
            error = '请导入xlsx格式的文件'
            flash(error)
            return redirect(url_for('lijing.basicInfo'))


@bp.route('/add_person', methods=('GET', 'POST'))
def add_person():
    insert_data = [0 for i in range(25)]
    item = ['person_name', "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
            "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
            "skill_title", "time_skill", "skill_unit", "skill_number",
            "time_school", "work_kind", "job_post", "time_retire"]

    for i in range(0, len(item)):
        insert_data[i] = request.args.get(item[i], '暂无', type=str)
        if insert_data[i] == '':
            insert_data[i] = '暂无'

    db = get_lijing_db()
    sql_person = 'insert into person (person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume) values (?,?,?,?,?,?,?,?,?)'
    db.execute(sql_person,
               (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4],
                insert_data[5], insert_data[6], insert_data[7], insert_data[8]))
    person_id = db.execute(
        'select person_id from person where id_number=?', (insert_data[2],)).fetchone()

    sql_education = 'insert into education (edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,person_id) values (?,?,?,?,?,?,?,?,?)'
    db.execute(sql_education,
               (insert_data[9], insert_data[10], insert_data[11], insert_data[12], insert_data[13],
                insert_data[14], insert_data[15], insert_data[16], person_id[0]))

    sql_skill = 'insert into skill (skill_title,time_skill,skill_unit,skill_number,person_id) values (?,?,?,?,?)'
    db.execute(sql_skill,
               (insert_data[17], insert_data[18], insert_data[19], insert_data[20], person_id[0]))

    sql_workinfo = 'insert into workinfo (time_school,work_kind,job_post,time_retire,person_id) values (?,?,?,?,?)'
    db.execute(sql_workinfo,
               (insert_data[21], insert_data[22],
                insert_data[23], insert_data[24], person_id[0]))
    db.commit()

    msg = '成功添加教师'+ insert_data[0] +'的信息'

    # return render_template('lijing/basicInfo.html', msgs=msg)
    return {'msg': msg}
