from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

# from flaskr.db import (
#     get_item_list, get_lijing_db, create_table, insert_table, select_table, update_table
# )

from flaskr.lijing.lijing_index import float_int_string

import os
import xlrd
import xlsxwriter
# import datetime
from pypinyin import lazy_pinyin


bp = Blueprint('bonus_calculator', __name__, url_prefix='/bonus_calculator')


@bp.route('/hello')
@login_required
def hello():

    return render_template('lijing/bonus_calculator.html')


@bp.route('/calculator_bonus', methods=('GET', 'POST'))
def calculator_bonus():
    if request.method == "POST":
        msg = '成功'

        # 接收文件
        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        # 接收参数
        item_value = request.form.get('item_value').split(',')
        item_subject = ['chinese', 'math', 'english',
                        'wl', 'hx', 'zz', 'ls', 'dl', 'sw']
        item = ['chinese', 'math', 'english', 'wl', 'hx', 'zz', 'ls', 'dl', 'sw', 'class1',
                'class2', 'bonus1', 'bonus2', 'ebonus1', 'ebonus2', 'bonus_average', 'bonus3']

        # 参数字典
        value_dict = {}
        for i in range(len(item)):
            value_dict[item[i]] = float(item_value[i])

        # 科目系数
        item_coefficient = []
        for i in item_subject:
            item_coefficient.append(value_dict[i])

        # 判断文件格式
        if filename.endswith('.xlsx'):
            # 保存文件
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(
                basepath, '..\\static\\uploads', filename)
            f.save(upload_path)

            # 打开文件
            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)

            # 标题栏
            table_title = table.row_values(0)

            item_average = ['语文人平', '数学人平', '英语人平', '物理人平',
                            '化学人平', '政治人平', '历史人平', '地理人平', '生物人平']
            item_teacher = ['语文教师', '数学教师', '英语教师', '物理教师',
                            '化学人平', '政治教师', '历史教师', '地理教师', '生物教师']

            # 日志数据
            log = {}
            # 奖金数据
            bonus_dict = {}

            # 标题序号
            id_dict = {}
            for i in range(len(table_title)):
                if table_title[i] == '班级':
                    id_dict['班级'] = i

                if table_title[i] in item_average:
                    id_dict[table_title[i]] = i

                if table_title[i] in item_teacher:
                    id_dict[table_title[i]] = i

                if '一类' in table_title[i]:
                    id_dict['一类'] = i
                if '二类' in table_title[i]:
                    id_dict['二类'] = i

            # 检查是否有班级数据
            if '班级' not in id_dict:
                msg = '找不到班级数据，读取失败\n'
                return jsonify({'msg': msg})

            # 获取班级数据
            class_list = []
            for i in range(1, table.nrows):
                table_row = table.row_values(i)
                class_list.append(float_int_string(table_row[id_dict['班级']]))
            class_list.remove('全校人平')

            # 获取老师列表
            teacher_list = []
            for item in item_teacher:
                for i in range(1, table.nrows):
                    table_row = table.row_values(i)
                    if item in id_dict:
                        if table_row[id_dict[item]] != '':
                            teacher_list.append(table_row[id_dict[item]])
            teacher_list = list(set(teacher_list))
            teacher_list = sorted(teacher_list)

            # 平均分奖金计算
            # 按九个科目依次计算
            for i in range(9):
                # 没有某科目老师
                if item_teacher[i] in id_dict:
                    teacher_id = id_dict[item_teacher[i]]
                else:
                    continue

                # 没有某科目平均分
                if item_average[i] in id_dict:
                    average_id = id_dict[item_average[i]]
                else:
                    continue

                # 拿到某科目全校平均分
                average_total = table.row_values(table.nrows - 1)[average_id]

                # 计算每行数据
                for row in range(1, table.nrows - 1):
                    table_row = table.row_values(row)

                    class_name = table_row[id_dict['班级']]
                    teacher = table_row[teacher_id]
                    average = table_row[average_id]
                    diff = round((average - average_total), 1)

                    # 日志
                    log_string = []
                    log_string.append(float_int_string(class_name)+'班')
                    log_string.append(item_average[i])
                    log_string.append(str(average))
                    log_string.append(str(average_total))
                    log_string.append('%.2f-%.2f=%.2f' %
                                      (average, average_total, diff))

                    # 判断是否有老师奖金的信息
                    if teacher in bonus_dict:
                        sum = bonus_dict[teacher]
                    else:
                        # 没有某老师信息则初始化
                        log[teacher] = teacher + '\n'
                        sum = 0

                    # 计算基本奖金：100*系数
                    basic = value_dict['bonus_average'] * item_coefficient[i]
                    log_string.append('%.2f*%.2f=%.2f' %
                                      (value_dict['bonus_average'], item_coefficient[i], basic))

                    # 计算额外奖金：多一分8元
                    addition = value_dict['bonus3'] * diff
                    log_string.append('%.2f*%.2f=%.2f' %
                                      (value_dict['bonus3'], diff, addition))

                    # 奖金相加
                    bonus_dict[teacher] = sum + basic + addition
                    log_string.append(
                        '%.2f+%.2f=%.2f' % (sum, basic + addition, bonus_dict[teacher]))

                    # 保存日志
                    log[teacher] = log[teacher] + '\t'.join(log_string) + '\n'

            # 计算系数和
            total_coefficient = 0
            for i in range(len(item_teacher)):
                if item_teacher[i] in id_dict:
                    total_coefficient = total_coefficient + item_coefficient[i]
            total_coefficient = round(total_coefficient, 2)

            # 计算尖子生奖金
            # 按每行一个班级计算
            for i in range(1, table.nrows - 1):
                # 日志
                log_string = []

                table_row = table.row_values(i)
                class_name = float_int_string(table_row[id_dict['班级']]) + '班'
                log_string.append(class_name)

                # 尖子生个数
                class1 = table_row[id_dict['一类']]
                class2 = table_row[id_dict['二类']]
                log_string.append('一类：%d个，二类：%d个' % (class1, class2))

                # 尖子生差距
                diff1 = class1 - value_dict['class1']
                diff2 = class2 - value_dict['class2']

                # 尖子生奖金
                bonus1 = value_dict['bonus1'] + value_dict['ebonus1'] * diff1
                bonus2 = value_dict['bonus2'] + value_dict['ebonus2'] * diff2
                log_string.append('一类奖金：%d，二类奖金：%d' % (bonus1, bonus2))

                # 总奖金
                bonus_total = bonus1 + bonus2
                log_string.append('总奖金：%d' % (bonus_total))

                # 计算某个班级的老师奖金
                for j in range(len(item_teacher)):
                    # 没有某科目老师
                    if item_teacher[j] not in id_dict:
                        continue

                    # 老师名称
                    teacher_id = id_dict[item_teacher[j]]
                    teacher = table_row[teacher_id]
                    log_string.append('\n\t%s：%s' % (item_teacher[j], teacher))

                    # 奖金比例
                    ratio = item_coefficient[j]/total_coefficient
                    log_string.append(
                        '%.2f/%.2f=%.2f' % (item_coefficient[j], total_coefficient, ratio))

                    # 尖子生奖金
                    bonus_class = bonus_total*ratio
                    log_string.append('%.2f*%.2f=%.2f' %
                                      (bonus_total, ratio, bonus_class))

                    # 汇入奖金数据
                    origin = bonus_dict[teacher]
                    bonus_dict[teacher] = origin + bonus_class
                    log[teacher] = log[teacher] + '%s %.2f+%.2f=%.2f\n' % (
                        class_name, origin, bonus_class, bonus_dict[teacher])

                # 日志保存
                log[class_name] = '\t'.join(log_string) + '\n'

            # 输出数据到表格
            workbook = xlsxwriter.Workbook(
                'flaskr\\static\\downloads\\exportData.xlsx')
            worksheet = workbook.add_worksheet('Sheet1')
            worksheet.write(0, 0, '教师')
            worksheet.write(0, 1, '奖金')

            for i in range(len(teacher_list)):
                teacher = teacher_list[i]
                worksheet.write(i+1, 0, teacher)
                # 四舍五入
                bonus_dict[teacher] = int(bonus_dict[teacher] + 0.5)
                worksheet.write(i+1, 1, bonus_dict[teacher])

            workbook.close()

            os.remove(upload_path)
        else:
            msg = '请导入xlsx格式的文件\n'
            return jsonify({'msg': msg})

    return jsonify({'msg': msg, 'class_list': class_list, 'teacher_list': teacher_list, 'log': log, 'filename': 'exportData.xlsx'})
