from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    session,
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

from flaskr.lijing.lijing_index import float_int_string, list_to_path, current_time

from operator import itemgetter
from itertools import groupby

import os
import xlrd
import xlsxwriter
import json
from pypinyin import lazy_pinyin

bp = Blueprint("result_statistics", __name__, url_prefix="/result_statistics")


@bp.route("/hello")
@login_required
def hello():

    return render_template("lijing/result_statistics.html")


@bp.route("/readfile", methods=("GET", "POST"))
def readfile():
    if request.method == "POST":
        msg = "成功"

        f = request.files["file"]
        filename = current_time() + secure_filename("".join(lazy_pinyin(f.filename)))

        if not filename.endswith(".xlsx"):
            msg = "请导入xlsx格式的文件"
            return jsonify({"msg": msg})

        # 保存文件
        upload_path = list_to_path(["flaskr", "static", "uploads", filename])
        f.save(upload_path)

        # 打开文件
        data = xlrd.open_workbook(upload_path)
        table = data.sheet_by_index(0)

        # 获取合并单元格（起始行，结束行，起始列，结束列）
        merged_cells = table.merged_cells
        # 获取数据行索引
        row_data = 1
        for cell in merged_cells:
            if cell[1] > row_data:
                row_data = cell[1]
            pass

        table_col = []
        items = {
            "姓名": -1,
            "考号": -1,
            "班级": -1,
            "总分": -1,
            "语文": -1,
            "数学": -1,
            "英语": -1,
            "物理": -1,
            "化学": -1,
            "道法": -1,
            "历史": -1,
            "地理": -1,
            "生物": -1,
        }
        # items = ['总分', '语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '道法']
        for row_title in range(0, row_data):
            title = table.row_values(row_title)
            for i in range(0, len(title)):
                # 返回每列的标题数据
                if row_title == 0:
                    table_col.append("第" + str(i + 1) + "列：[ " + title[i] + " ]  ")
                else:
                    table_col[i] = table_col[i] + "[ " + title[i] + " ]  "

                # 获取分数列索引
                if title[i] in items:
                    items[title[i]] = i
                pass
            pass

        # 分数列索引
        col_index = []
        for item in items:
            col_index.append(items[item])

        # 前9行数据
        table_row = []
        for i in range(0, 9):
            data_row = str(table.row_values(i))
            table_row.append("第" + str(i + 1) + "行：" + data_row)
            pass

        os.remove(upload_path)
        pass

    return jsonify(
        {
            "msg": msg,
            "table_col": table_col,
            "col_index": col_index,
            "table_row": table_row,
            "row_data": row_data,
        }
    )


@bp.route("/exportData", methods=("GET", "POST"))
def exportData():
    if request.method == "POST":
        msg = "成功"

        f = request.files["file"]
        filename = current_time() + secure_filename("".join(lazy_pinyin(f.filename)))

        # 保存文件
        upload_path = list_to_path(["flaskr", "static", "uploads", filename])
        f.save(upload_path)

        # 打开文件
        data = xlrd.open_workbook(upload_path)
        table = data.sheet_by_index(0)

        # 获取要导出的列
        items = {
            "姓名": -1,
            "考号": -1,
            "班级": -1,
            "总分": -1,
            "语文": -1,
            "数学": -1,
            "英语": -1,
            "物理": -1,
            "化学": -1,
            "道法": -1,
            "历史": -1,
            "地理": -1,
            "生物": -1,
        }
        item_title = [
            "考号",
            "班级",
            "姓名",
            "语文",
            "数学",
            "英语",
            "物理",
            "化学",
            "生物",
            "历史",
            "地理",
            "道法",
            "总分",
        ]

        item_id_list = request.form.get("item_id_list").split(",")
        it = 0
        for item in items:
            items[item] = int(item_id_list[it]) - 1
            it = it + 1
            if items[item] == -1:
                item_title.remove(item)
            pass

        # 获取数据
        data_table = []
        index_data = int(request.form.get("index_data")) - 1
        for i in range(index_data, table.nrows):
            row_value = table.row_values(i)

            data_row = []
            for item in item_title:
                if row_value[items[item]] == "":
                    data_row.append(0.0)
                else:
                    data_row.append(row_value[items[item]])
                pass

            data_table.append(data_row)
            pass

        os.remove(upload_path)

        # 计算排名
        # 找到总分
        index_total = -1
        for i in range(len(item_title)):
            if "总分" == item_title[i]:
                index_total = i
            pass

        item_title.append("学校排名")
        # 按总分排序
        data_table.sort(key=itemgetter(index_total), reverse=True)
        # data_table = sorted(data_table, key=(
        #     lambda x: x[index_total]), reverse=True)
        for i in range(len(data_table)):
            if i == 0:
                data_table[i].append(i + 1)
            else:
                if data_table[i][index_total] == data_table[i - 1][index_total]:
                    data_table[i].append(data_table[i - 1][-1])
                else:
                    data_table[i].append(i + 1)
                pass
            pass

        # 找到班级
        index_class = -1
        for i in range(len(item_title)):
            if "班级" == item_title[i]:
                index_class = i
            pass

        item_title.append("班级排名")

        # 按班级排序
        data_table.sort(key=itemgetter(index_class))
        for elt, items in groupby(data_table, itemgetter(index_class)):
            it = 1
            totol_old = 0
            for i in items:
                if it == 1:
                    i.append(it)
                    totol_old = i[index_total]
                else:
                    if totol_old == i[index_total]:
                        i.append(i[-1])
                    else:
                        i.append(it)
                    pass

                it = it + 1
                pass
            pass

        # 导出数据
        out_file_name = "exportData(%s).xlsx" % current_time()
        save_path = list_to_path(["flaskr", "static", "downloads", out_file_name])
        workbook = xlsxwriter.Workbook(save_path)
        worksheet = workbook.add_worksheet("Sheet1")

        it = 0
        for it in range(len(item_title)):
            worksheet.write(0, it, item_title[it])

        for i in range(len(data_table)):
            data_row = data_table[i]
            for j in range(len(data_row)):
                worksheet.write(i + 1, j, data_row[j])
            pass

        workbook.close()

    return jsonify({"msg": msg, "filename": out_file_name})


@bp.route("/resultStatistics", methods=("GET", "POST"))
def resultStatistics():
    if request.method == "POST":

        msg = "成功"

        f = request.files["file"]
        f2 = request.files["file2"]
        filename = secure_filename("".join(lazy_pinyin(f.filename)))
        filename2 = secure_filename("".join(lazy_pinyin(f2.filename)))

        if not filename2.endswith(".xlsx"):
            msg = "请导入xlsx格式的文件"
            return jsonify({"msg": msg})

        # 防止文件重名
        if filename == filename2:
            filename2 = "1" + filename2

        # 获取request数据
        class1 = int(request.form.get("class1"))
        class2 = int(request.form.get("class2"))
        delete_id_list = request.form.get("delete_id").split("\n")
        change_examid_list = request.form.get("change_examid").split("\n")
        change_class_list = request.form.get("change_class").split("\n")

        if len(change_examid_list) != len(change_class_list):
            msg = "调整班级数据有错误"
            return jsonify({"msg": msg})

        # 保存文件
        upload_path = list_to_path(["flaskr", "static", "uploads", filename])
        f.save(upload_path)
        upload_path2 = list_to_path(["flaskr", "static", "uploads", filename2])
        f2.save(upload_path2)

        # 打开文件
        data = xlrd.open_workbook(upload_path)
        table = data.sheet_by_index(0)

        data2 = xlrd.open_workbook(upload_path2)
        table2 = data2.sheet_by_index(0)

        # 获取成绩表格列索引
        items = {
            "姓名": -1,
            "考号": -1,
            "班级": -1,
            "总分": -1,
            "语文": -1,
            "数学": -1,
            "英语": -1,
            "物理": -1,
            "化学": -1,
            "道法": -1,
            "历史": -1,
            "地理": -1,
            "生物": -1,
        }
        item_title = [
            "姓名",
            "考号",
            "班级",
            "语文",
            "数学",
            "英语",
            "物理",
            "化学",
            "生物",
            "历史",
            "地理",
            "道法",
            "总分",
        ]
        item_id_list = request.form.get("item_id_list").split(",")
        it = 0
        for item in items:
            items[item] = int(item_id_list[it]) - 1
            it = it + 1
            if items[item] == -1:
                item_title.remove(item)
            pass

        # 获取各科老师、人数表格索引
        items_table2 = item_title[2:]
        items_table2[-1] = "人数"
        data_title_teacher = table2.row_values(0)
        item_table2_id_list = []

        for item in items_table2:
            flag = False
            for i in range(len(data_title_teacher)):
                if item in data_title_teacher[i]:
                    flag = True
                    item_table2_id_list.append(i)
                    pass
                pass

            if not flag:
                if item == "班级":
                    msg = "教师、有效人数表格：缺少班级"
                elif item == "人数":
                    msg = "教师、有效人数表格：缺少班级有效人数"
                else:
                    msg = "教师、有效人数表格：缺少" + item + "教师姓名"
                return jsonify({"msg": msg})
            pass

        # 获取成绩数据、班级数据
        data_table = []
        class_list = []
        index_data = int(request.form.get("index_data")) - 1
        for i in range(index_data, table.nrows):
            row_value = table.row_values(i)
            class_name = float_int_string(row_value[items["班级"]])
            if class_name not in class_list:
                class_list.append(class_name)

            data_row = []
            for item in item_title:
                if row_value[items[item]] == "":
                    data_row.append(0.0)
                else:
                    if item == "班级":
                        data_row.append(int(float_int_string(row_value[items[item]])))
                    elif item == "考号":
                        data_row.append(float_int_string(row_value[items[item]]))
                    else:
                        data_row.append(row_value[items[item]])
                    pass
                pass

            data_table.append(data_row)
            pass

        # 获取老师、有效人数数据
        data_table2 = []
        for i in range(1, table2.nrows):
            row = []
            data_row = table2.row_values(i)
            for teacher_id in item_table2_id_list:
                row.append(float_int_string(data_row[teacher_id]))
            data_table2.append(row)

        os.remove(upload_path)
        os.remove(upload_path2)

        # 处理数据
        # 调整部分学生的班级
        for i in range(len(change_examid_list)):
            change_exam_id = change_examid_list[i]
            flag = False
            for j in range(len(data_table)):
                if change_exam_id == data_table[j][1]:
                    flag = True
                    data_table[j][2] = int(change_class_list[i])
                    pass
                pass
            if not flag:
                if change_exam_id == "":
                    pass
                else:
                    msg = "要调整班级的学生学号找不到：" + change_exam_id
                    return jsonify({"msg": msg})
                pass
            pass

        # 判断调整的班级是否存在
        for class_name in change_class_list:
            if class_name not in class_list:
                if class_name == "":
                    pass
                else:
                    msg = "要调整班级的班级不存在：" + class_name
                    return jsonify({"msg": msg})
                pass
            pass

        # 通过学号删除不计入统计的学生
        index_delele = []
        delete_id_dict = {}
        for i in delete_id_list:
            if i == "":
                continue
            i = i.replace("\r", "")
            delete_id_dict[i] = True
            pass

        for i in range(len(data_table)):
            exam_id = data_table[i][1]
            if exam_id in delete_id_dict:
                delete_id_dict[exam_id] = False
                index_delele.append(i)
            pass

        for i in delete_id_dict:
            if delete_id_dict[i]:
                msg = "要删除的学生学号找不到：" + i
                return jsonify({"msg": msg})
            pass

        index_delele = sorted(index_delele, reverse=True)
        for i in index_delele:
            del data_table[i]

        #############################################################

        export_title = []
        export_data = []
        item_subject = item_title[3:]

        # 找到总分索引
        index_total = -1
        for i in range(len(item_title)):
            if "总分" == item_title[i]:
                index_total = i
                break
            pass

        # 按总分排序
        data_table.sort(key=itemgetter(index_total), reverse=True)

        # 找到尖子生边界分数
        class1_total_result = data_table[class1 - 1][-1]
        class2_total_result = data_table[class1 + class2 - 1][-1]

        # 找到班级索引
        index_class = -1
        for i in range(len(item_title)):
            if "班级" == item_title[i]:
                index_class = i
                break
            pass

        # 按班级排序、按班级分组
        data_table.sort(key=itemgetter(index_class))
        for class_name, class_students in groupby(data_table, itemgetter(index_class)):

            # 一个班的所有学生数据
            class_students_result = []
            for student in class_students:
                class_students_result.append(student)

            # 判断教师、有效人数表格中是否有对应的班级
            index_teacher_number = -1
            for i in range(len(data_table2)):
                if str(class_name) == data_table2[i][0]:
                    index_teacher_number = i
                    break

            if index_teacher_number == -1:
                msg = "教师、有效人数表格：找不到班级 %s" % str(class_name)
                return jsonify({"msg": msg})

            # # 有效人数
            average_num = int(data_table2[index_teacher_number][-1])
            # if average_num > len(class_students_result):
            #     msg = "教师、有效人数表格：%s班有效人数错误" % str(class_name)
            #     return jsonify({"msg": msg})

            # 每个班级的数据
            data_class = []
            data_class.append(class_name)

            # 分科目计算平均分
            for item in item_subject:

                # 科目老师的名字
                index_teacher_name = -1
                for i in range(len(items_table2)):
                    if item == items_table2[i]:
                        index_teacher_name = i
                        break
                if index_teacher_name != -1:
                    data_class.append(
                        data_table2[index_teacher_number][index_teacher_name]
                    )

                # 找到分数索引
                index_item = -1
                for i in range(len(item_title)):
                    if item == item_title[i]:
                        index_item = i
                        break

                # 计算平均分
                sum_result = 0
                if average_num <= len(class_students_result):
                    for i in range(0, average_num):
                        sum_result = sum_result + class_students_result[i][index_item]
                    pass
                else:
                    for i in range(0, len(class_students_result)):
                        sum_result = sum_result + class_students_result[i][index_item]
                    pass

                average_result = sum_result / average_num
                data_class.append(average_result)

                # 预留排名
                data_class.append(0)

            # 统计尖子生个数
            number_class1 = 0
            number_class2 = 0
            for student in class_students_result:
                if student[-1] >= class1_total_result:
                    number_class1 = number_class1 + 1
                elif student[-1] >= class2_total_result:
                    number_class2 = number_class2 + 1
                else:
                    pass

            data_class.append(number_class1)
            data_class.append(0)
            data_class.append(number_class2)
            data_class.append(0)

            export_data.append(data_class)

        # 标题
        export_title.append("班级")
        it = 0
        sort_id_list = []
        for item in item_subject:
            if item != "总分":
                export_title.append(item + "教师")
                it = it + 1
            export_title.append(item + "人平")
            export_title.append(item + "排名")
            it = it + 2
            sort_id_list.append(it)
            pass

        export_title.append("一类人数")
        export_title.append("排名")
        it = it + 2
        sort_id_list.append(it)
        export_title.append("二类人数")
        export_title.append("排名")
        it = it + 2
        sort_id_list.append(it)

        # 统计排名
        for i in sort_id_list:
            export_data.sort(key=itemgetter(i - 1), reverse=True)
            it = 1
            old_result = export_data[0][i - 1]
            old_paiming = 1
            for row in export_data:
                if old_result == row[i - 1]:
                    row[i] = old_paiming
                else:
                    row[i] = it
                    old_result = row[i - 1]
                    old_paiming = row[i]
                it = it + 1
                pass
            pass

        # 按班级排序
        export_data.sort(key=itemgetter(0))

        # 统计全校人平
        total_school_row = []
        for i in range(len(export_title)):
            if i == 0:
                total_school_row.append("全校人平")
            else:
                total_school_row.append("")
            pass

        for i in sort_id_list:
            sum_result = 0
            for row in export_data:
                sum_result = sum_result + row[i - 1]
            total_school_row[i - 1] = sum_result / len(class_list)
            pass

        total_school_row[-2] = total_school_row[-2] * len(class_list)
        total_school_row[-4] = total_school_row[-4] * len(class_list)
        export_data.append(total_school_row)

        ##############################################################
        # 导出数据
        out_file_name = "exportData(%s).xlsx" % current_time()
        save_path = list_to_path(["flaskr", "static", "downloads", out_file_name])
        workbook = xlsxwriter.Workbook(save_path)
        worksheet = workbook.add_worksheet("Sheet1")

        for it in range(len(export_title)):
            worksheet.write(0, it, export_title[it])

        for i in range(len(export_data)):
            data_row = export_data[i]
            for j in range(len(data_row)):
                worksheet.write(i + 1, j, data_row[j])
            pass

        workbook.close()

    return jsonify({"msg": msg, "filename": out_file_name})
