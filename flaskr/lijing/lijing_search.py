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

from flaskr.db import get_db, get_lijing_db, select_table

from flaskr.lijing.lijing_index import list_to_path, current_time

import xlsxwriter


bp = Blueprint("lijing_search", __name__, url_prefix="/lijing_search")


@bp.route("/hello")
@login_required
def hello():

    year_list = []
    year_data = get_lijing_db().execute("select year from year_list").fetchall()
    if len(year_data) == 0:
        year_list = ["暂无数据"]
        session["year_current"] = year_list[0]
        return render_template("lijing/search.html", year_list=year_list)
    else:
        for year in year_data:
            year_list.insert(0, year["year"])

    session["year_current"] = year_list[0]

    school_list = []
    school_id = []
    school_data = select_table(
        "school",
        session["year_current"],
        {"school_id": "school", "school_name": "school"},
    )
    if type(school_data) == dict:
        school_list.append(school_data["school_name"])
        school_id.append(school_data["school_id"])
    else:
        for i in school_data:
            school_list.append(i["school_name"])
            school_id.append(i["school_id"])

    if len(school_list) != 1:
        school_list = school_list[1:]

    return render_template(
        "lijing/search.html", year_list=year_list, school_list=school_list
    )


@bp.route("/search_data", methods=("GET", "POST"))
def search_data():
    # 获取要查询的表
    table_list = request.args.getlist("select_table_list[]")

    # 获取要查询的年份和分校
    year = request.args.get("year", type=str)
    school = request.args.get("school", type=str)

    # 获取要查询的项
    select_item = {}
    select_item_list = request.args.getlist("select_item_list[]")
    for item in select_item_list:
        select_item[item] = request.args.get(item, type=str)
        table_list.append(select_item[item])

    # 获取要查询的表
    table_list = list(set(table_list))
    print(table_list)

    # 获得要查询的字段和值
    search_item_list = request.args.getlist("condition_item_list[]")
    search_string_list = request.args.getlist("search_string_list[]")

    # 拼接condition_dict字典
    condition_dict = {}
    for i in range(0, len(search_item_list)):
        condition_dict[search_item_list[i]] = " LIKE '%" + search_string_list[i] + "%'"

    # 查询结果
    data = []
    if school == "全部数据":
        # 查所有分校
        data = select_table(table_list, year, select_item, condition_dict)
    else:
        # 查特定分校
        person_id_data = select_table(
            ["school", "job"],
            year,
            {"person_id": "job"},
            {"school_" + year + ".school_name": " = '" + school + "'"},
        )
        select_item["person_id"] = "person"
        search_data = select_table(table_list, year, select_item, condition_dict)

        person_id_list = []
        for i in person_id_data:
            person_id_list.append(i["person_id"])
        for i in search_data:
            if i["person_id"] in person_id_list:
                del i["person_id"]
                data.append(i)

    # 未查询到结果
    if len(data) == 0:
        total = 0
        msg = "没有查询到相关信息"
        return jsonify({"msg": msg, "total": total})

    # 写入表格数据
    item_name_dict = {
        "person_id": "编号",
        "person_name": "姓名",
        "gender": "性别",
        "id_number": "身份证号",
        "phone": "联系电话",
        "political_status": "政治面貌",
        "time_Party": "入党时间",
        "time_work": "参加工作时间",
        "address": "家庭住址",
        "resume": "个人简历",
        "edu_start": "第一学历",
        "time_edu_start": "第一学历毕业时间",
        "school_edu_start": "第一学历毕业学校",
        "major_edu_start": "第一学历专业",
        "edu_end": "最高学历",
        "time_edu_end": "最高学历毕业时间",
        "school_edu_end": "最高学历毕业学校",
        "major_edu_end": "最高学历专业",
        "skill_title": "专业技术职称",
        "time_skill": "职称取得时间",
        "skill_unit": "职称发证单位",
        "skill_number": "发证文件批号",
        "time_school": "调入大集中学时间",
        "work_kind": "用工性质",
        "job_post": "工作岗位",
        "time_retire": "退休时间",
        "job_name": "行政职务",
        "class_name": "班级名称",
        "lesson_number": "总课时数",
        "year_result": "年度考核",
        "school_name": "所在分校",
        "honor_time": "发证时间",
        "honor_unit": "发证单位",
        "honor_name": "获奖名称",
        "honor_grade": "证书级别",
        "honor_number": "证书编号",
        "honor_remark": "备注",
        "get_time": "获得时间",
    }

    out_file_name = "exportData(%s).xlsx" % current_time()
    save_path = list_to_path(["flaskr", "static", "downloads", out_file_name])
    workbook = xlsxwriter.Workbook(save_path)
    worksheet = workbook.add_worksheet("Sheet1")
    # 写标题
    col = 0
    for i in data[0]:
        worksheet.write(0, col, item_name_dict[i])
        col = col + 1
    # 写数据
    for i in range(len(data)):
        col = 0
        row = data[i]
        for j in row:
            worksheet.write(i + 1, col, row[j])
            col = col + 1
    workbook.close()

    total = len(data)
    msg = "查询到" + str(len(data)) + "条信息"
    return jsonify({"msg": msg, "total": total, "filename": out_file_name})
