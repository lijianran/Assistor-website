
import os
import time
import json
from copy import deepcopy
from itertools import groupby
from operator import itemgetter

import xlsxwriter
import pandas as pd

from pywebio import *
from pywebio.input import *
from pywebio.output import *


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

name_dict = {
    "姓名": "name",
    "考号": "id",
    "班级": "class",
    "总分": "total",
    "语文": "chinese",
    "数学": "math",
    "英语": "english",
    "物理": "wuli",
    "化学": "huaxue",
    "道法": "daofa",
    "历史": "lishi",
    "地理": "dili",
    "生物": "shengwu",
}


def check_required(data):
    item_required = {"name": "姓名", "id": "考号", "class": "班级", "total": "总分"}
    for item in item_required:
        if data[item] == -1:
            toast(
                item_required[item] + "必须选择",
                position="right",
                color="#2188ff",
                duration=0,
            )
            return (item, "必须选择")


def check_class_num(data):
    if data["class1"] < 0:
        return ("class1", "不能为负数")
    if data["class2"] < 0:
        return ("class2", "不能为负数")


def result_statistics():

    put_markdown("# 成绩统计")

    # 上传成绩表
    upload_file = file_upload(
        "选择成绩表", placeholder="选择成绩表", accept=".xlsx", required=True
    )
    if not upload_file:
        print("终止操作")
        exit()

    file_path = os.path.join("temp", upload_file["filename"])
    open(file_path, "wb").write(upload_file["content"])

    # 打开文件
    data = pd.read_excel(file_path)
    head = list(data)

    put_markdown("## 成绩表")
    put_table(data.values.tolist()[:100], header=head)

    table_col = []

    # 读取每列的位置
    options = []
    for i in range(len(head)):
        table_col.append("第%d列: [ %s ]" % (i + 1, head[i]))
        options.append({"label": "第%2d 列: [ %s ]" % (i + 1, head[i]), "value": i})

        if head[i] in items:
            items[head[i]] = i

    options.append({"label": "无", "value": -1})

    # 前几行数据
    table_row = []
    for i in range(9):
        data_row = data.loc[i + 1].tolist()
        table_row.append({"label": "第%2d 行: %s" % (i + 1, str(data_row)), "value": i})
        pass

    # 选择框
    select_group = []
    for item in items:
        col_index = items[item]
        options_item = deepcopy(options)
        options_item[col_index]["selected"] = True

        select_group.append(
            select(
                item,
                name=name_dict[item],
                options=options_item,
            )
        )

        pass

    select_group.append(select("数据", name="data", options=table_row))

    # 选择数据
    select_result = input_group("解析数据", select_group, validate=check_required)

    os.remove(file_path)

    upload_teacher_file = file_upload(
        "选择教师表", placeholder="选择教师表", accept=".xlsx", required=True
    )
    if not upload_teacher_file:
        print("终止操作")
        exit()

    # 一类尖子生个数
    class1_input = input(
        "一类尖子生个数",
        name="class1",
        type=NUMBER,
        required=True,
        value=330,
    )
    # 二类尖子生个数
    class2_input = input(
        "二类尖子生个数",
        name="class2",
        type=NUMBER,
        required=True,
        value=660,
    )
    class_result = input_group(
        "尖子生", [class1_input, class2_input], validate=check_class_num
    )
    class1 = class_result["class1"]
    class2 = class_result["class2"]

    # 不计入成绩统计的学生（选填）
    delete_id_textarea = textarea("不计入成绩统计的学生（选填）")
    delete_id_list = delete_id_textarea.split("\n")
    # 需要调整班级的学生（选填）
    change_examid_textarea = textarea("需调整的考号（选填）：", name="change_examid")
    change_class_textarea = textarea("对应的班级（选填）：", name="change_class")
    change_result = input_group(
        "需要调整班级的学生（选填）", [change_examid_textarea, change_class_textarea]
    )

    change_examid_list = change_result["change_examid"].split("\n")
    change_class_list = change_result["change_class"].split("\n")
    if len(change_examid_list) != len(change_class_list):
        print("调整班级数据有错误")
        exit()

    file_path = os.path.join("temp", upload_teacher_file["filename"])
    open(file_path, "wb").write(upload_teacher_file["content"])

    # 打开文件
    teacher_data = pd.read_excel(file_path)
    head = list(teacher_data)

    put_markdown("## 教师表")
    put_row(put_table(teacher_data.values.tolist(), header=head))

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

    for item in name_dict:
        key = name_dict[item]
        if select_result[key] == -1:
            item_title.remove(item)

    # # 获取各科老师、人数表格索引
    items_table2 = item_title[2:]
    items_table2[-1] = "人数"
    data_title_teacher = head

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
                print("教师、有效人数表格：缺少班级")
            elif item == "人数":
                print("教师、有效人数表格：缺少班级有效人数")
            else:
                print("教师、有效人数表格：缺少" + item + "教师姓名")

            exit()
        pass

    # 获取老师、有效人数数据
    data_table2 = []
    for i in range(len(teacher_data)):
        row = []
        data_row = teacher_data.loc[i]
        for teacher_id in item_table2_id_list:
            row.append(data_row[teacher_id])
        data_table2.append(row)

    os.remove(file_path)

    # 获取成绩数据、班级数据
    data_table = []
    class_list = []
    index_data = select_result["data"]

    for i in range(index_data, len(data)):
        row_value = data.loc[i]
        class_name = row_value[items["班级"]]
        if class_name not in class_list:
            class_list.append(class_name)

        data_row = []
        for item in item_title:
            if row_value[items[item]] == "":
                data_row.append(0.0)
            else:
                if item == "班级":
                    data_row.append(int(row_value[items[item]]))
                elif item == "考号":
                    data_row.append(row_value[items[item]])
                else:
                    data_row.append(row_value[items[item]])
                pass
            pass

        data_table.append(data_row)
        pass

    ####################################### 处理数据
    # 调整部分学生的班级
    for i in range(len(change_examid_list)):
        change_exam_id = change_examid_list[i]
        if change_exam_id == "":
            continue

        flag = False
        for j in range(len(data_table)):
            if change_exam_id == data_table[j][1]:
                flag = True
                data_table[j][2] = int(change_class_list[i])
                pass
            pass
        if not flag:
            print("要调整班级的学生学号找不到：" + change_exam_id)
            exit()
        pass

    # 判断调整的班级是否存在
    for class_name in change_class_list:
        if class_name not in class_list:
            if not class_name:
                continue
            else:
                print("要调整班级的班级不存在：" + class_name)
                exit()
            pass
        pass

    # 通过学号删除不计入统计的学生
    index_delele = []
    delete_id_dict = {}
    for id in delete_id_list:
        if not id:
            continue
        id = id.replace("\r", "")
        delete_id_dict[id] = True
        pass

    for i in range(len(data_table)):
        exam_id = data_table[i][1]
        if exam_id in delete_id_dict:
            delete_id_dict[exam_id] = False
            index_delele.append(i)
        pass

    for id in delete_id_dict:
        if delete_id_dict[id]:
            print("要删除的学生学号找不到：" + id)
            exit()
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
            if class_name == data_table2[i][0]:
                index_teacher_number = i
                break

        if index_teacher_number == -1:
            print("教师、有效人数表格：找不到班级 %s" % str(class_name))
            exit()

        # 有效人数
        average_num = int(data_table2[index_teacher_number][-1])

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
                data_class.append(data_table2[index_teacher_number][index_teacher_name])

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
            pass
        pass

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
        pass

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
    out_file_name = "exportData(%s).xlsx" % time.time()
    save_path = os.path.join("temp", out_file_name)
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

    put_file(
        name=out_file_name, label="成绩统计结果.xlsx", content=open(save_path, "rb").read()
    )


if __name__ == "__main__":
    # start_server(result_statistics, port=8080, debug=True, remote_access=True)
    result_statistics()
