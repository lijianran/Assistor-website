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

bp = Blueprint('lijing', __name__, url_prefix='/lijing')

item_name_dict = {
    'person_name': '姓名', "gender": '性别', "id_number": '身份证号', "phone": '联系电话', "political_status": '政治面貌', "time_Party": '入党时间', "time_work": '参加工作时间', "address": '家庭住址', "resume": '个人简历',
    "edu_start": '第一学历', "time_edu_start": '第一学历毕业时间', "school_edu_start": '第一学历毕业学校', "major_edu_start": '第一学历专业', "edu_end": '最高学历', "time_edu_end": '最高学历毕业时间', "school_edu_end": '最高学历毕业学校', "major_edu_end": '最高学历专业',
    "skill_title": '专业技术职称', "time_skill": '职称取得时间', "skill_unit": '职称发证单位', "skill_number": '发证文件批号',
    "time_school": '调入大集中学时间', "work_kind": '用工性质', "job_post": '工作岗位', "time_retire": '退休时间'
}


@bp.route('/hello')
def hello():
    return render_template('lijing/hello.html')


@bp.route('/basicInfo')
def basicInfo():
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
        # if 'year_current' not in session:
        session['year_current'] = year_list[0]
    return render_template('lijing/basicInfo.html', year_list=year_list, year_new=year_new)


@bp.route('/set_year')
def set_year():
    year = request.args.get('year')
    session['year_current'] = year
    msg = 'success'
    return {'msg': msg}


@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    db = get_lijing_db()

    data = []

    try:
        result = db.execute('select person_id, person_name, gender from person_' +
                            session['year_current']).fetchall()
        for row in result:
            d = {}
            d['id'] = row['person_id']
            d['name'] = row['person_name']
            d['gender'] = row['gender']
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


@bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id', 0, type=int)
    db = get_lijing_db()

    data = {}
    year = session['year_current']
    person = 'person_'+year
    education = 'education_'+year
    skill = 'skill_'+year
    workinfo = 'workinfo_'+year
    result = db.execute('select person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume,\
        edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,\
        skill_title,time_skill,skill_unit,skill_number,\
        time_school,work_kind,job_post,time_retire \
        from '+person+' join '+education+', '+skill+', '+workinfo+' \
        on '+person+'.person_id = '+education+'.person_id and '+person+'.person_id = '+skill+'.person_id and '+person+'.person_id = '+workinfo+'.person_id \
        where '+person+'.person_id = ?', (person_id,)).fetchall()

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
        db = get_lijing_db()

        year_select = request.form.get('year_select')

        sql_data = {}
        with open('flaskr\sql_lijing.json', 'r') as f:
            sql_data = json.load(f)

        sql_create = ['', '', '', '']
        sql_create[0] = 'CREATE TABLE person_' + \
            year_select+sql_data['person']
        sql_create[1] = 'CREATE TABLE education_' + \
            year_select+sql_data['education']
        sql_create[2] = 'CREATE TABLE skill_' + \
            year_select+sql_data['skill']
        sql_create[3] = 'CREATE TABLE workinfo_' + \
            year_select+sql_data['workinfo']

        year_data = db.execute('select year from year_list').fetchall()
        year_list = []
        year_new = datetime.datetime.now().year
        for year in year_data:
            year_list.insert(0, year['year'])

        if year_select not in year_list:
            db.execute('insert into year_list (year, basicinfo, workinfo) values (?,?,?)',
                       (year_select,0,0,))
            for sql in sql_create:
                db.execute(sql)
            db.commit()

        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        if filename.endswith('.xlsx'):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, '..\\static\\uploads', filename)
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

                sql_person = 'insert into person_'+year_select + \
                    ' (person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume) values (?,?,?,?,?,?,?,?,?)'
                db.execute(sql_person,
                           (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4],
                            insert_data[5], insert_data[6], insert_data[7], insert_data[8]))
                person_id = db.execute(
                    'select person_id from person_'+year_select+' where id_number=?', (insert_data[2],)).fetchone()

                sql_education = 'insert into education_'+year_select + \
                    ' (edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,person_id) values (?,?,?,?,?,?,?,?,?)'
                db.execute(sql_education,
                           (insert_data[9], insert_data[10], insert_data[11], insert_data[12], insert_data[13],
                            insert_data[14], insert_data[15], insert_data[16], person_id[0]))

                sql_skill = 'insert into skill_'+year_select + \
                    ' (skill_title,time_skill,skill_unit,skill_number,person_id) values (?,?,?,?,?)'
                db.execute(sql_skill,
                           (insert_data[17], insert_data[18], insert_data[19], insert_data[20], person_id[0]))

                sql_workinfo = 'insert into workinfo_'+year_select + \
                    ' (time_school,work_kind,job_post,time_retire,person_id) values (?,?,?,?,?)'
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


@bp.route('/exportData3244', methods=('GET', 'POST'))
def exportData():
    export_data = [0 for i in range(25)]
    item = ['person_name', "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
            "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
            "skill_title", "time_skill", "skill_unit", "skill_number",
            "time_school", "work_kind", "job_post", "time_retire"]

    for i in range(0, len(item)):
        export_data[i] = request.args.get(item[i])

    id_list = request.args.getlist("id_list[]")

    export_item = []
    for i in range(0, len(item)):
        if export_data[i] == 'true':
            export_item.append(item[i])

    sql_search = 'select '
    for item in export_item:
        sql_search = sql_search + item + ','
    sql_search = sql_search[:len(sql_search)-1]

    year = session['year_current']
    person = 'person_'+year
    education = 'education_'+year
    skill = 'skill_'+year
    workinfo = 'workinfo_'+year
    sql_search = sql_search + ' from '+person+' join '+education+', '+skill+', '+workinfo+' on '+person+'.person_id = ' + \
        education+'.person_id and '+person+'.person_id = '+skill + '.person_id and '+person+'.person_id = '+workinfo+'.person_id \
        where '+person+'.person_id = ?'

    table_data = []
    db = get_lijing_db()
    for id in id_list:
        result = db.execute(sql_search, (int(id),)).fetchall()
        row = []
        for item in export_item:
            row.append(result[0][item])
        table_data.append(row)

    workbook = xlsxwriter.Workbook(
        'flaskr\\static\\downloads\\exportData.xlsx')
    worksheet = workbook.add_worksheet('Sheet1')
    for i in range(len(export_item)):
        worksheet.write(0, i, item_name_dict[export_item[i]])
    for i in range(len(id_list)):
        for j in range(len(export_item)):
            worksheet.write(i+1, j, table_data[i][j])

    workbook.close()
    # print(os.path.join(os.path.dirname(
    #     __file__), 'static', 'downloads', 'exportData.xlsx'))
    msg = '成功导出'+str(len(id_list))+'条信息'

    return {'msg': msg, 'filename': 'exportData.xlsx'}


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
    sql_person = 'insert into person_' + \
        session['year_current'] + \
        ' (person_name,gender,id_number,phone,political_status,time_Party,time_work,address,resume) values (?,?,?,?,?,?,?,?,?)'
    db.execute(sql_person,
               (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4],
                insert_data[5], insert_data[6], insert_data[7], insert_data[8]))
    person_id = db.execute(
        'select person_id from person_'+session['year_current']+' where id_number=?', (insert_data[2],)).fetchone()

    sql_education = 'insert into education_' + \
        session['year_current'] + \
        ' (edu_start,time_edu_start,school_edu_start,major_edu_start,edu_end,time_edu_end,school_edu_end,major_edu_end,person_id) values (?,?,?,?,?,?,?,?,?)'
    db.execute(sql_education,
               (insert_data[9], insert_data[10], insert_data[11], insert_data[12], insert_data[13],
                insert_data[14], insert_data[15], insert_data[16], person_id[0]))

    sql_skill = 'insert into skill_' + \
        session['year_current'] + \
        ' (skill_title,time_skill,skill_unit,skill_number,person_id) values (?,?,?,?,?)'
    db.execute(sql_skill,
               (insert_data[17], insert_data[18], insert_data[19], insert_data[20], person_id[0]))

    sql_workinfo = 'insert into workinfo_' + \
        session['year_current'] + \
        ' (time_school,work_kind,job_post,time_retire,person_id) values (?,?,?,?,?)'
    db.execute(sql_workinfo,
               (insert_data[21], insert_data[22],
                insert_data[23], insert_data[24], person_id[0]))
    db.commit()

    msg = '成功添加教师' + insert_data[0] + '的信息'

    # return redirect(url_for('lijing.basicInfo'))
    # return render_template('lijing/basicInfo.html')
    return {'msg': msg}


@bp.route('/download_excel_file/<string:excel_filename>')
def download_excel_file(excel_filename):
    """
    下载src_file目录下面的文件
    eg：下载当前目录下面的123.tar 文件，eg:http://localhost:5000/download?fileId=123.tar
    :return:
    """
    # file_name = request.args.get('fileId')
    file_path = os.path.join(os.path.dirname(
        __file__), 'static', 'downloads', excel_filename)
    print(file_path)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "The downloaded file does not exist"


@bp.route('/update_person', methods=('GET', 'POST'))
def update_person():
    update_data = [0 for i in range(25)]
    item = ['person_name', "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
            "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
            "skill_title", "time_skill", "skill_unit", "skill_number",
            "time_school", "work_kind", "job_post", "time_retire"]

    for i in range(0, len(item)):
        update_data[i] = request.args.get(item[i], '暂无', type=str)
        if update_data[i] == '':
            update_data[i] = '暂无'

    person_id = request.args.get("person_id", '暂无', type=str)
    print(update_data)
    print(person_id)

    db = get_lijing_db()
    sql_person = 'update person_' + \
        session['year_current'] + \
        ' set person_name = ?,gender = ?,id_number = ?,phone = ?,political_status = ?,time_Party = ?,time_work = ?,address = ?,resume = ? where person_id = ?'
    db.execute(sql_person,
               (update_data[0], update_data[1], update_data[2], update_data[3], update_data[4],
                update_data[5], update_data[6], update_data[7], update_data[8], person_id))

    sql_education = 'update education_' + \
        session['year_current'] + \
        ' set edu_start = ?,time_edu_start = ?,school_edu_start = ?,major_edu_start = ?,edu_end = ?,time_edu_end = ?,school_edu_end = ?,major_edu_end = ? where person_id = ?'
    db.execute(sql_education,
               (update_data[9], update_data[10], update_data[11], update_data[12], update_data[13],
                update_data[14], update_data[15], update_data[16], person_id))

    sql_skill = 'update skill_' + \
        session['year_current'] + \
        ' set skill_title = ?,time_skill = ?,skill_unit = ?,skill_number = ? where person_id = ?'
    db.execute(sql_skill,
               (update_data[17], update_data[18], update_data[19], update_data[20], person_id))

    sql_workinfo = 'update workinfo_' + \
        session['year_current'] + \
        ' set time_school = ?,work_kind = ?,job_post = ?,time_retire = ? where person_id = ?'
    db.execute(sql_workinfo,
               (update_data[21], update_data[22],
                update_data[23], update_data[24], person_id))
    db.commit()
    msg = '成功修改教师“' + update_data[0] + '”的信息'

    return {'msg': msg}


@bp.route('/search_person', methods=('GET', 'POST'))
def seach_person():
    search_item = request.args.get('search_item', '暂无', type=str)
    search_string = request.args.get('search_string', '暂无', type=str)

    db = get_lijing_db()
    year = session['year_current']
    person = 'person_'+year
    education = 'education_'+year
    skill = 'skill_'+year
    workinfo = 'workinfo_'+year
    sql = 'select '+person+'.person_id, '+person+'.person_name, '+person+'.gender from '+person+' join '+education+', '+skill+', '+workinfo + \
        ' on '+person+'.person_id = '+education+'.person_id and '+person+'.person_id = '+skill+'.person_id and '+person+'.person_id = '+workinfo+'.person_id \
        where ' + search_item + ' like "%' + search_string + '%"'
    result = db.execute(sql).fetchall()
    db.commit()

    data = []
    for row in result:
        d = {}
        d['id'] = row['person_id']
        d['name'] = row['person_name']
        d['gender'] = row['gender']
        data.append(d)

    msg = '成功查询到'+str(len(result))+'条信息'
    limit = 10
    offset = 0
    return jsonify({'msg': msg, 'total': len(data), 'rows': data})
    # return {'msg': msg, 'data': data}
