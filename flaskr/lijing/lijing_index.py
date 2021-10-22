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
    send_file,
    send_from_directory,
)

from flaskr.auth import login_required

import os
import time

from flaskr.db import get_db, get_lijing_db, create_table, insert_table, select_table

bp = Blueprint("lijing", __name__, url_prefix="/lijing")


def float_int_string(float_num:float) -> str:
    """格式数据

    float - int - string

    主要处理班级和学号

    Args:
        float_num (浮点数): 小数

    Returns:
        str: 字符串
    """
    if type(float_num) != str:
        float_num = str(int(float_num))
    return float_num


def list_to_path(path_list: list) -> str:
    """路径拼接

    Args:
        path_list (list): 字符串列表

    Returns:
        str: 路径
    """
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "..", "..")
    for i in path_list:
        path = os.path.join(path, i)
        pass
    return path


def current_time(format:str="%Y%m%d%H%M%S")->str:
    """当前时间

    Args:
        format (str, optional): 格式. Defaults to "%Y%m%d%H%M%S".

    Returns:
        str: 时间字符串
    """
    return time.strftime(format, time.localtime())


@bp.route("/")
def index():
    # create_table(['person','education','workinfo','skill'], '2020')
    # insert_table('person', '2020', {'person_name': 'lijianran', 'gender': '22', 'id_number': '421223', 'phone': '156',
    #                                 'political_status': '群众', 'time_Party': '暂无', 'time_work': '2020', 'address': '暂无', 'resume': '暂无'})
    # select_table('person', '2020', {'person_id': 'person'}, {'gender': '=\'男\''})
    # select_table(['person','education','class'], '2023', {'person_id': 'person'}, {'gender': '男'})
    return render_template("lijing/login.html")


@bp.route("/board")
@login_required
def board():
    return render_template("lijing/board.html")
    # return render_template("test.html")



# @bp.route('/index')
# def index():
#     return render_template('lijing/hello.html')


@bp.route("/download_excel_file/<string:excel_filename>")
def download_excel_file(excel_filename):
    """
    下载src_file目录下面的文件
    eg：下载当前目录下面的123.tar 文件，eg:http://localhost:5000/download?fileId=123.tar
    :return:
    """
    # file_name = request.args.get('fileId')
    file_path = list_to_path(["flaskr", "static", "downloads", excel_filename])
    # file_path = os.path.join(
    #     os.path.dirname(__file__), "..\\static", "downloads", excel_filename
    # )
    print(file_path)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "The downloaded file does not exist"


@bp.route("/set_year")
def set_year():
    year = request.args.get("year")
    session["year_current"] = year
    return jsonify({"msg": "success"})
