var update_person_id = 0;
var flag_search = false;

function init() {
    var select_search = document.getElementById("search_select");
    var item = {
        "姓名": "person_name", "性别": "gender", "身份证号": "id_number", "联系电话": "phone", "政治面貌": "political_status", "入党时间": "time_Party", "参加工作时间": "time_work", "家庭住址": "address", "个人简历": "resume",
        "第一学历": "edu_start", "第一学历毕业时间": "time_edu_start", "第一学历毕业学校": "school_edu_start", "第一学历专业": "major_edu_start", "最高学历": "edu_end", "最高学历毕业时间": "time_edu_end", "最高学历毕业学校": "school_edu_end", "最高学历专业": "major_edu_end",
        "专业技术职称": "skill_title", "职称取得时间": "time_skill", "职称发证单位": "skill_unit", "发证文件批号": "skill_number",
        "调入大集中学时间": "time_school", "用工性质": "work_kind", "工作岗位": "job_post", "退休时间": "time_retire"
    };

    for (var i in item)
        select_search.options.add(new Option(i, item[i]));


    for (var i in item) {
        var board = document.getElementById("radios");
        var radio_id = "radio_" + item[i];

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
        l.innerHTML = i;

        d.appendChild(e);
        d.appendChild(l);
        board.appendChild(d);
    }
    document.getElementById("radio_person_name").checked = true;
    document.getElementById("radio_gender").checked = true;
    document.getElementById("radio_time_work").checked = true;
    document.getElementById("radio_skill_title").checked = true;
    document.getElementById("radio_person_name").disabled = true;

}
init();

function operateFormatter(value, row, index) {
    return [
        '<a class="detail" href="javascript:void(0)" title="Detail">',
        '<i class="fa fa-bars"></i>',
        '</a>&nbsp;&nbsp;&nbsp;',
        '<a class="update" href="javascript:void(0)" title="Update">',
        '<i class="fa fa-edit"></i>',
        '</a>&nbsp;&nbsp;',
        '<a class="remove" href="javascript:void(0)" title="Remove">',
        '<i class="fa fa-trash"></i>',
        '</a>'
    ].join('')
}

window.operateEvents = {
    'click .detail': function (e, value, row, index) {
        document.getElementById("detail_modal_title").innerHTML = row.person_name + "--基本信息";

        $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/search', { id: row.person_id }, function (data) {
            var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
                "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
                "skill_title", "time_skill", "skill_unit", "skill_number",
                "time_school", "work_kind", "job_post", "time_retire"];

            for (i = 0; i < item.length; i++) {
                document.getElementById(item[i]).value = data[item[i]];
            }

        });
        $("#detailModal input").attr("readOnly", true);
        $("#resume").attr("readOnly", true);
        document.getElementById("button_add").style.display = "none";
        document.getElementById("button_update").style.display = "none";
        $('#detailModal').modal('show');

    },
    'click .update': function (e, value, row, index) {
        update_person_id = row.person_id;

        $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/search', { id: row.person_id }, function (data) {
            var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
                "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
                "skill_title", "time_skill", "skill_unit", "skill_number",
                "time_school", "work_kind", "job_post", "time_retire"];
            for (i = 0; i < item.length; i++) {
                document.getElementById(item[i]).value = data[item[i]];
            }
        });

        document.getElementById("button_update").style.display = "block";
        document.getElementById("button_add").style.display = "none";
        document.getElementById("detail_modal_title").innerHTML = '修改教师"' + row.person_name + '"的基本信息';
        $("#detailModal input").attr("readOnly", false);
        $("#resume").attr("readOnly", false);
        $("#detailModal").modal("show");

        //window.alert('You click like action, row: ' + JSON.stringify(row))
    },
    'click .remove': function (e, value, row, index) {
        window.alert("待开发");
        //$table.bootstrapTable('remove', {field: 'id',values: [row.person_id]})
    }
}

function init_table() {
    $('#table').bootstrapTable({
        url: '/lijing_basicinfo/jsondata',  // 请求数据源的路由
        method: 'get',
        dataType: "json",
        theadClasses: "thead-light",//标题样式
        pagination: true, //前端处理分页
        singleSelect: false,//是否只能单选
        search: false, //显示搜索框，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
        toolbar: '#toolbar', //工具按钮用哪个容器
        cache: false, //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
        pagination: true,
        pageNumber: 1, //初始化加载第10页，默认第一页
        pageSize: 20, //每页的记录行数（*）
        pageList: [10, 20, 50, 100], //可供选择的每页的行数（*）
        smartDisplay: false,
        strictSearch: true,//设置为 true启用 全匹配搜索，false为模糊搜索
        showColumns: true, //显示内容列下拉框
        showRefresh: true, //显示刷新按钮
        minimumCountColumns: 2, //当列数小于此值时，将隐藏内容列下拉框
        clickToSelect: true, //设置true， 将在点击某行时，自动勾选rediobox 和 checkbox
        uniqueId: "id", //每一行的唯一标识，一般为主键列
        showToggle: true, //是否显示详细视图和列表视图的切换按钮
        cardView: false, //是否显示详细视图
        detailView: false,                   //是否显示父子表
        sidePagination: "server", //分页方式：client客户端分页，server服务端分页（*）
        columns: [
            //{
            //    checkbox: false  //第一列显示复选框
            //},
            {  //定义表头,这个表头必须定义,下边field后边跟的字段名字必须与后端传递的字段名字相同.如:id、name、price跟后端的字段名id  name price是完全一样的.
                field: 'person_id',
                title: '编号',
                align: 'center',  //对齐方式，居中 
            }, {
                field: 'person_name',
                title: '姓名',
                align: 'center'
            }, {
                field: 'gender',
                title: '性别',
                align: 'center',

            }, {
                field: 'operations',
                title: '操作',
                align: 'center',
                clickToSelect: false,
                events: window.operateEvents,
                formatter: operateFormatter
            }
        ],
        //onDblClickRow: function (row, $element, field) {},
    });

}
init_table();

function show_import_modal() {
    $('#importModal').modal('show');
};

function show_add_modal() {
    var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
        "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
        "skill_title", "time_skill", "skill_unit", "skill_number",
        "time_school", "work_kind", "job_post", "time_retire"];
    for (i = 0; i < item.length; i++) {
        document.getElementById(item[i]).value = "";
    }

    document.getElementById("button_add").style.display = "block";
    document.getElementById("button_update").style.display = "none";
    document.getElementById("detail_modal_title").innerHTML = "新增教师基本信息";
    $("#detailModal input").attr("readOnly", false);
    $("#resume").attr("readOnly", false);
    $("#detailModal").modal("show");

};

function add_data() {
    if (test_data("add") != 0) {
        window.alert("姓名和身份证为必填项！");
        return;
    }
    var datas = {};
    var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
        "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
        "skill_title", "time_skill", "skill_unit", "skill_number",
        "time_school", "work_kind", "job_post", "time_retire"];

    for (var i = 0; i < item.length; i++) {
        datas[item[i]] = document.getElementById(item[i]).value;
    }

    $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/add_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;
        $("#detailModal").modal("hide");
    });

};

function update_data() {
    var datas = {};
    var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
        "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
        "skill_title", "time_skill", "skill_unit", "skill_number",
        "time_school", "work_kind", "job_post", "time_retire"];

    datas["person_id"] = update_person_id;
    for (var i = 0; i < item.length; i++) {
        datas[item[i]] = document.getElementById(item[i]).value;
    }

    $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/update_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;
        $("#detailModal").modal("hide");
        $("#table").bootstrapTable('refresh');
    });
};

function search_data() {
    if (test_data("search") != 0) {
        window.alert("请填入要搜索内容");
        return;
    }

    var index = document.getElementById("search_select").selectedIndex;
    var search_item = document.getElementById("search_select").options[index].value;

    var search_string = document.getElementById("search_string").value;

    datas = {};
    datas["search_item"] = search_item;
    datas["search_string"] = search_string;

    $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/search_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;

        flag_search = true;
        document.getElementById("select_year").disabled = true;
        document.getElementById("origin_button").style.display = "block";
        //$('#export_button').removeClass('disabled');
        $("#table").bootstrapTable("destroy");
        $('#table').bootstrapTable({
            //url: '/lijing_basicinfo/jsondata',  // 请求数据源的路由
            data: return_data.rows,
            //method: 'get',
            dataType: "json",
            theadClasses: "thead-dark",//标题样式
            pagination: true, //前端处理分页
            singleSelect: false,//是否只能单选
            search: false, //显示搜索框，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            toolbar: '#toolbar', //工具按钮用哪个容器
            cache: false, //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: false,
            pageNumber: 1, //初始化加载第10页，默认第一页
            pageSize: 20, //每页的记录行数（*）
            pageList: [10, 20, 50, 100], //可供选择的每页的行数（*）
            smartDisplay: false,
            strictSearch: true,//设置为 true启用 全匹配搜索，false为模糊搜索
            showColumns: true, //显示内容列下拉框
            showRefresh: true, //显示刷新按钮
            minimumCountColumns: 2, //当列数小于此值时，将隐藏内容列下拉框
            clickToSelect: true, //设置true， 将在点击某行时，自动勾选rediobox 和 checkbox
            uniqueId: "id", //每一行的唯一标识，一般为主键列
            showToggle: true, //是否显示详细视图和列表视图的切换按钮
            cardView: false, //是否显示详细视图
            detailView: false,                   //是否显示父子表
            sidePagination: "server", //分页方式：client客户端分页，server服务端分页（*）
            columns: [
                //{
                //    checkbox: false  //第一列显示复选框
                //},
                {  //定义表头,这个表头必须定义,下边field后边跟的字段名字必须与后端传递的字段名字相同.如:id、name、price跟后端的字段名id  name price是完全一样的.
                    field: 'person_id',
                    title: '编号',
                    align: 'center',  //对齐方式，居中 
                }, {
                    field: 'person_name',
                    title: '姓名',
                    align: 'center'
                }, {
                    field: 'gender',
                    title: '性别',
                    align: 'center',

                }, {
                    field: 'operations',
                    title: '操作',
                    align: 'center',
                    clickToSelect: false,
                    events: window.operateEvents,
                    formatter: operateFormatter
                }
            ],
            //onDblClickRow: function (row, $element, field) {},
        });

    });
}

function show_origin_table() {
    flag_search = false;

    $('#table').bootstrapTable("destroy");
    init_table();
    document.getElementById("select_year").disabled = false;
    document.getElementById("search_string").value = "";
    document.getElementById("success_info").style.display = "none";
    document.getElementById("origin_button").style.display = "none";
    //$('#export_button').addClass('disabled');
};

function show_export_modal() {
    $('#exportModal').modal('show');
};

function export_table() {
    var id_list = []
    var table_data = $('#table').bootstrapTable('getData');

    for (var i = 0; i < table_data.length; i++) {
        id_list.push(table_data[i].person_id);
    }

    var datas = {};
    datas['flag_search'] = flag_search;
    var item = ["person_name", "gender", "id_number", "phone", "political_status", "time_Party", "time_work", "address", "resume",
        "edu_start", "time_edu_start", "school_edu_start", "major_edu_start", "edu_end", "time_edu_end", "school_edu_end", "major_edu_end",
        "skill_title", "time_skill", "skill_unit", "skill_number",
        "time_school", "work_kind", "job_post", "time_retire"];

    for (i = 0; i < item.length; i++) {
        var id = "radio_" + item[i];
        //window.alert(document.getElementById(id).checked)
        if (document.getElementById(id).checked == true) {
            datas[item[i]] = true;
        }
        else {
            datas[item[i]] = false;
        }
    }
    datas["id_list"] = id_list;

    $.getJSON($SCRIPT_ROOT + '/lijing_basicinfo/exportData', datas, function (return_data) {
        $("#exportModal").modal("hide");
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;
        //window.alert('/lijing/download_excel_file/' + return_data.filename)
        window.location.href = '/lijing/download_excel_file/' + return_data.filename;
        //$("#detailModal").modal("hide");
        //$("#table").bootstrapTable('refresh');
    });
}

function export_all() {
    var item = {
        "姓名": "person_name", "性别": "gender", "身份证号": "id_number", "联系电话": "phone", "政治面貌": "political_status", "入党时间": "time_Party", "参加工作时间": "time_work", "家庭住址": "address", "个人简历": "resume",
        "第一学历": "edu_start", "第一学历毕业时间": "time_edu_start", "第一学历毕业学校": "school_edu_start", "第一学历专业": "major_edu_start", "最高学历": "edu_end", "最高学历毕业时间": "time_edu_end", "最高学历毕业学校": "school_edu_end", "最高学历专业": "major_edu_end",
        "专业技术职称": "skill_title", "职称取得时间": "time_skill", "职称发证单位": "skill_unit", "发证文件批号": "skill_number",
        "调入大集中学时间": "time_school", "用工性质": "work_kind", "工作岗位": "job_post", "退休时间": "time_retire"
    };

    for (var i in item) {
        var radio_id = "radio_" + item[i];
        document.getElementById(radio_id).checked = true;
    }

}

function test_data(code) {
    if (code == "add") {
        if (document.getElementById("person_name").value == "") {
            return 1;
        }
        if (document.getElementById("id_number").value == "") {
            return 1;
        }
    }
    if (code == "search") {
        if (document.getElementById("search_string").value == "") {
            return 1;
        }

    }

    return 0;
};

function showFilename(file) {
    $("#filename_label").html(file.name);
};

$("#select_year").change(function () {
    //要触发的事件
    document.getElementById('jumbotron_string').innerHTML = this.value + '年-教师基本信息';

    datas = {};
    datas['year'] = this.value;
    $.getJSON($SCRIPT_ROOT + '/lijing/set_year', datas, function (return_data) {
        $("#table").bootstrapTable('refresh');
    });

});
