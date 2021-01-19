
var search_number = 1;
var serach_id_list = [0];

item_list_dict = {
    'person': ['person_name', 'gender', 'id_number', 'phone', 'political_status', 'time_Party', 'time_work', 'address', 'resume'],
    'education': ['edu_start', 'time_edu_start', 'school_edu_start', 'major_edu_start', 'edu_end', 'time_edu_end', 'school_edu_end', 'major_edu_end'],
    'skill': ['skill_title', 'time_skill', 'skill_unit', 'skill_number'],
    'workinfo': ['time_school', 'work_kind', 'job_post', 'time_retire'],
    'job': ['job_name'],
    'class': ['class_name'],
    'workload': ['lesson_number', 'year_result'],
    'honor': ['school_name', 'honor_time', 'get_time', 'honor_unit', 'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
}

item_name_dict = {
    'person_name': '姓名', "gender": '性别', "id_number": '身份证号', "phone": '联系电话', "political_status": '政治面貌', "time_Party": '入党时间', "time_work": '参加工作时间', "address": '家庭住址', "resume": '个人简历',
    "edu_start": '第一学历', "time_edu_start": '第一学历毕业时间', "school_edu_start": '第一学历毕业学校', "major_edu_start": '第一学历专业', "edu_end": '最高学历', "time_edu_end": '最高学历毕业时间', "school_edu_end": '最高学历毕业学校', "major_edu_end": '最高学历专业',
    "skill_title": '专业技术职称', "time_skill": '职称取得时间', "skill_unit": '职称发证单位', "skill_number": '发证文件批号',
    "time_school": '调入大集中学时间', "work_kind": '用工性质', "job_post": '工作岗位', "time_retire": '退休时间',
    'job_name': '行政职务', 'class_name': '班级名称',
    'lesson_number': '总课时数', 'year_result': '年度考核',
    'school_name': '所在分校', 'honor_time': '发证时间', 'honor_unit': '发证单位', 'honor_name': '获奖名称', 'honor_grade': '证书级别', 'honor_number': '证书编号', 'honor_remark': '备注', 'get_time': '获得时间'
}

function init() {
    add_table_select(0);

    // 添加查询项复选框
    for (var i in item_list_dict) {
        var board = document.getElementById("select_item_" + i);
        var item_list = item_list_dict[i];

        for (var j = 0; j < item_list.length; j++) {
            var radio_id = "radio_" + item_list[j];

            var d = document.createElement("div");
            d.className = "custom-control custom-checkbox custom-control-inline col-md-3";
            var e = document.createElement("input");
            e.type = "checkbox";
            e.className = "custom-control-input";
            e.id = radio_id;
            e.name = "radio";
            var l = document.createElement("label");
            l.className = "custom-control-label";
            l.setAttribute("for", radio_id);
            l.innerHTML = item_name_dict[item_list[j]];

            d.appendChild(e);
            d.appendChild(l);
            board.appendChild(d);

        }
    }
    document.getElementById("radio_person_name").checked = true;
    document.getElementById("radio_gender").checked = true;
    document.getElementById("radio_time_work").checked = true;
    document.getElementById("radio_skill_title").checked = true;
    document.getElementById("radio_person_name").disabled = true;

}
init();

// 改变选项
function change_item(id) {
    var i = id[id.length - 1];

    var select_item_id = "item_select_" + i;
    var select_item = document.getElementById(select_item_id);

    var index = document.getElementById(id).selectedIndex;
    var table = document.getElementById(id).options[index].value;

    if (table == "None") {
        $("#" + select_item_id).empty();
        select_item.options.add(new Option("待选择", "None"));
        document.getElementById("search_string_" + i).placeholder = "**请选择要查询的项**";
        document.getElementById("search_string_" + i).readOnly = true;
        return;
    }

    $("#" + select_item_id).empty();
    select_item.options.add(new Option("待选择", "None"));
    item_list = item_list_dict[table];
    for (var j = 0; j < item_list.length; j++) {
        select_item.options.add(new Option(item_name_dict[item_list[j]], item_list[j]));
    }
}

// 添加选项
function add_table_select(id) {
    var select_search = document.getElementById("table_select_" + id);
    var item = {
        '个人信息': 'person', '学历信息': 'education', '职称信息': 'skill', '工作信息': 'workinfo',
        '职务': 'job', '班级': 'class', '任课信息': 'workload', '荣誉信息': 'honor'
    };

    for (var i in item)
        select_search.options.add(new Option(i, item[i]));

}

// 使能输入
function enable_input(id) {
    // 获取输入框
    var i = id[id.length - 1];
    var select_string = document.getElementById("search_string_" + i);

    // 判断选择项
    var index = document.getElementById(id).selectedIndex;
    var item = document.getElementById(id).options[index].value;
    if (item != "None") {
        select_string.readOnly = false;
        select_string.placeholder = "请输入查询内容";
    }
    else {
        select_string.readOnly = true;
        select_string.placeholder = "**请选择要查询的项**";
    }
}

// 添加查询项
function add_search() {
    if (document.getElementById("search_string_" + (search_number - 1)).value == "") {
        window.alert("请输入查询内容");
        return;
    }

    // 新增查询条件
    var d1 = document.createElement("div");
    d1.className = "row mb-3";
    var d2 = document.createElement("div");
    d2.className = "input-group mb-3 col-md-10";
    var d3 = document.createElement("div");
    d3.className = "input-group-prepend";
    var select1 = document.createElement("select");
    select1.className = "custom-select";
    select1.id = "table_select_" + search_number;
    select1.options.add(new Option("待添加", "None"));
    select1.setAttribute("onchange", "change_item(this.id)");
    var d4 = document.createElement("div");
    d4.className = "input-group-prepend";
    var select2 = document.createElement("select");
    select2.className = "custom-select";
    select2.id = "item_select_" + search_number;
    select2.options.add(new Option("待添加", "None"));
    select2.setAttribute("onchange", "enable_input(this.id)");
    var input = document.createElement("input");
    input.type = "text";
    input.className = "form-control";
    input.setAttribute("aria-label", "Text input with dropdown button");
    input.id = "search_string_" + search_number;
    input.placeholder="**请选择要查询的项**"
    input.readOnly = true;
    var d5 = document.createElement("div");
    d5.className = "col-md-2";
    var button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-success";
    button.setAttribute("onclick", "add_search()");
    button.id = "button_add_" + search_number;
    button.innerHTML = "新增";

    d1.appendChild(d2);
    d2.appendChild(d3);
    d3.appendChild(select1);
    d2.appendChild(d4);
    d4.appendChild(select2);
    d2.appendChild(input);
    d1.appendChild(d5);
    d5.appendChild(button);

    var select_block = document.getElementById("select_block");
    select_block.appendChild(d1);


    // 修改增加->删除
    var button_add = document.getElementById("button_add_" + (search_number - 1));
    button_add.className = "btn btn-danger";
    button_add.setAttribute("onclick", "del_search(this.id)");
    button_add.innerHTML = "删除";

    // 添加选项
    serach_id_list.push(search_number);
    add_table_select(search_number);

    search_number++;
}

// 删除查询项
function del_search(id) {
    if (confirm('是否要删除该查询项？') == true) {
        var i = id[id.length - 1];
        var box = document.getElementById(id);
        box.parentNode.parentNode.remove();

        // 删除选项
        for (var j = 0; j < serach_id_list.length; j++) {
            if (serach_id_list[j] == i) {
                remove_id = j;
            }
        }
        serach_id_list.splice(remove_id, 1);
    }

}

// 查询数据
function search_data() {

    var i;
    var j;
    var index;
    var item;

    // 获取要查询的年份和分校
    index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    index = document.getElementById("search_school_select").selectedIndex;
    var school = document.getElementById("search_school_select").options[index].value;

    // 获取要查询的项
    select_item = {};
    select_item_list = []
    for (i in item_list_dict) {
        var item_list = item_list_dict[i];

        for (j = 0; j < item_list.length; j++) {
            var radio_id = "radio_" + item_list[j];

            if (document.getElementById(radio_id).checked == true) {
                select_item_list.push(item_list[j]);
                select_item[item_list[j]] = i;
            }
        }
    }

    // 获取查询的表名和条件字段
    select_table_list = [];
    condition_item_list = [];
    for (i = 0; i < search_number; i++) {
        if (serach_id_list.includes(i)) {
            index = document.getElementById("table_select_" + i).selectedIndex;
            item = document.getElementById("table_select_" + i).options[index].value;
            if (item == "None") {
                window.alert("请选择要查询的数据项");
                return;
            }
            select_table_list.push(item);

            index = document.getElementById("item_select_" + i).selectedIndex;
            item = document.getElementById("item_select_" + i).options[index].value;
            if (item == "None") {
                window.alert("请选择要查询的数据项");
                return;
            }
            condition_item_list.push(item);
        }

    }

    // 判断是否有重复查询字段
    for (i = 0; i < condition_item_list.length; i++) {
        item = condition_item_list[i];
        for (j = i + 1; j < condition_item_list.length; j++) {
            if (item == condition_item_list[j]) {
                window.alert("失败，重复查询：" + item_name_dict[item]);
                return;
            }
        }
    }

    // 获取要查询的值
    var string;
    var search_string_list = [];
    for (i = 0; i < search_number; i++) {
        if (serach_id_list.includes(i)) {
            string = document.getElementById("search_string_" + i).value;
            if (string == "") {
                window.alert("请输入查询内容");
                return;
            }
            search_string_list.push(string);
        }
    }

    // 访问后台
    datas = {};
    datas = select_item;
    datas["year"] = year;
    datas["school"] = school;
    datas["select_table_list"] = select_table_list;
    datas["select_item_list"] = select_item_list;
    datas["condition_item_list"] = condition_item_list;
    datas["search_string_list"] = search_string_list;
    $.getJSON($SCRIPT_ROOT + '/lijing_search/search_data', datas, function (return_data) {
        // 判断是否查询到数据
        if (return_data['total'] == 0) {
            window.alert(return_data['msg']);
            return;
        }
        if (confirm(return_data['msg'] + '，是否要下载？') == true) {
            window.location.href = '/lijing/download_excel_file/' + return_data.filename;
        }
    });

}