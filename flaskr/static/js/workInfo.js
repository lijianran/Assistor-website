
var update_person_id = 0;
var update_rank_number = 0;
var flag_search = false;

function init() {
    var select_search = document.getElementById("search_select");
    var item = {
        '姓名': 'person_name', '所在分校': 'school_name', '行政职务': 'job_name', '总课时数': 'lesson_number',
        '年度考核': 'year_result', '班主任': 'class_master', '任教班级': 'class_name', '任教学科': 'subject'
    };

    for (var i in item)
        select_search.options.add(new Option(i, item[i]));

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
        document.getElementById("detail_modal_title").innerHTML = row.name + "--业务档案";

        $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/search', { id: row.id }, function (datas) {
            var item = ['person_name', 'school_name', 'job_name', 'lesson_number', 'year_result', 'class_master'];
            for (var i = 0; i < item.length; i++) {
                document.getElementById(item[i]).value = datas[item[i]];
            }

            var rank_item = ['subject', 'class_id', 'rank_up_school', 'rank_up_country', 'rank_down_school', 'rank_down_country']
            var title_item = ['任教班级', '任教科目', '上学期全校排名', '上学期全县排名', '下学期全校排名', '下学期全县排名']
            var rank = datas['rank'];
            var rank_form = document.getElementById('rank_form');
            rank_form.innerHTML = '';

            for (var i = 0; i < rank.length; i++) {
                var row = document.createElement("div");
                row.className = "form-row";

                //var a = document.createElement("a");
                //a.className = "remove";
                //a.href = "javascript:void(0)";
                //a.title = "Remove";
                //var ilabel = document.createElement("i");
                //ilabel.className = "fa fa-trash";
                //a.appendChild(ilabel);
                //row.appendChild(a);

                for (var j = 0; j < rank_item.length; j++) {
                    var d = document.createElement("div");
                    d.className = "form-group col-md-2";
                    var label = document.createElement("label");
                    label.setAttribute("for", rank_item[j] + i);
                    label.innerHTML = title_item[j];
                    var input = document.createElement("input");
                    input.className = "form-control";
                    input.readOnly = true;
                    input.value = rank[i][j];
                    input.id = rank_item[j] + i;
                    d.appendChild(label);
                    d.appendChild(input);
                    row.appendChild(d);
                }
                var divider = document.createElement("div");
                divider.className = 'dropdown-divider';
                rank_form.appendChild(divider);
                rank_form.appendChild(row);
            }
        });
        $("#detailModal input").attr("readOnly", true);
        document.getElementById("update_data").style.display = "none";
        $('#detailModal').modal('show');

    },
    'click .update': function (e, value, row, index) {
        document.getElementById("detail_modal_title").innerHTML = '修改教师“' + row.name + '”的基本信息';
        update_person_id = row.id;

        $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/search', { id: row.id }, function (datas) {
            var item = ['person_name', 'school_name', 'job_name', 'lesson_number', 'year_result', 'class_master'];
            for (var i = 0; i < item.length; i++) {
                document.getElementById(item[i]).value = datas[item[i]];
            }

            var rank_item = ['class_id', 'subject', 'rank_up_school', 'rank_up_country', 'rank_down_school', 'rank_down_country']
            var title_item = ['任教班级', '任教科目', '上学期全校排名', '上学期全县排名', '下学期全校排名', '下学期全县排名']
            var rank = datas['rank'];
            rank_form = document.getElementById('rank_form');
            rank_form.innerHTML = '';

            update_rank_number = rank.length;
            var i = 0;
            for (i = 0; i < rank.length; i++) {
                var row = document.createElement("div");
                row.className = "form-row";
                for (var j = 0; j < rank_item.length; j++) {
                    var d = document.createElement("div");
                    d.className = "form-group col-md-2";
                    var label = document.createElement("label");
                    label.setAttribute("for", rank_item[j] + i);
                    label.innerHTML = title_item[j];
                    if (rank_item[j] == 'class_id') {
                        label.innerHTML = title_item[j]
                            + '&nbsp;&nbsp;<a class="remove" href="javascript:delete_data(' + i + ')" title="Remove">'
                            + '<i class="fa fa-trash"></i>'
                            + '</a>';
                    }
                    var input = document.createElement("input");
                    input.className = "form-control";
                    input.readOnly = false;
                    if (rank_item[j] == 'subject' || rank_item[j] == 'class_id') {
                        input.readOnly = true;
                    }
                    input.value = rank[i][j];
                    input.id = rank_item[j] + i;
                    d.appendChild(label);
                    d.appendChild(input);
                    row.appendChild(d);
                }
                var divider = document.createElement("div");
                divider.className = 'dropdown-divider';
                rank_form.appendChild(divider);
                rank_form.appendChild(row);
            }

            // 新增
            var row = document.createElement("div");
            row.className = "form-row";
            for (var j = 0; j < rank_item.length; j++) {
                var d = document.createElement("div");
                d.className = "form-group col-md-2";
                var label = document.createElement("label");
                label.setAttribute("for", rank_item[j] + i);
                label.innerText = title_item[j];
                var input = document.createElement("input");
                input.className = "form-control";
                input.readOnly = false;
                if (rank_item[j] == 'subject' || rank_item[j] == 'class_id') {
                    input.placeholder = '新增';
                }
                input.id = rank_item[j] + i;
                d.appendChild(label);
                d.appendChild(input);
                row.appendChild(d);
            }
            var divider = document.createElement("div");
            divider.className = 'dropdown-divider';
            rank_form.appendChild(divider);
            rank_form.appendChild(row);
        });

        $("#detailModal input").attr("readOnly", false);
        $("#person_name").attr("readOnly", true);
        $("#class_master").attr("readOnly", true);
        document.getElementById("update_data").style.display = "block";
        $("#detailModal").modal("show");

    },
    'click .remove': function (e, value, row, index) {
        window.alert("待开发");
        //$table.bootstrapTable('remove', {field: 'id',values: [row.id]})
    }
};

function init_table() {
    //window.alert("hello")
    $('#table').bootstrapTable({
        url: '/lijing_workinfo/jsondata',  // 请求数据源的路由
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
                field: 'id',
                title: '编号',
                align: 'center',  //对齐方式，居中 
            }, {
                field: 'name',
                title: '姓名',
                align: 'center'
            }, {
                field: 'school',
                title: '分校',
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

function show_school_class() {
    $('#school_classModal').modal('show');
};

function show_import_modal() {
    document.getElementById("input_file").disabled = false;
    document.getElementById("button_readfile").disabled = false;
    document.getElementById("select_card").style.display = "none";
    $('#importModal').modal('show');
};

function show_export_modal() {
    if (confirm('是否导出当前表格中的数据？') == true) {

        $('#exportModal').modal('show');

        var id_list = []
        var table_data = $('#table').bootstrapTable('getData');
        for (var i = 0; i < table_data.length; i++) {
            id_list.push(table_data[i].id);
        }

        var datas = {};
        datas['flag_search'] = flag_search;
        datas["id_list"] = id_list;

        $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/exportData', datas, function (return_data) {
            $("#exportModal").modal("hide");

            document.getElementById("export_string").innerHTML = return_data.msg;
            //document.getElementById("success_info").style.display = "block";
            //document.getElementById("success_msg").innerHTML = return_data.msg;
            //window.alert('/lijing/download_excel_file/' + return_data.filename)
            window.location.href = '/lijing/download_excel_file/' + return_data.filename;

        });

    }

};

function showFilename(file) {
    $("#filename_label").html(file.name);
};

function read_file() {
    var formData = new FormData($('#readfile_form')[0]);

    $.ajax({
        url: "/lijing_workinfo/readfile",
        type: "POST",
        data: formData,
        async: true,
        cashe: false,
        contentType: false,
        processData: false,
        success: function (returndata) {
            if (returndata.msg != '成功') {
                document.getElementById("select_card").style.display = "none";
                window.alert(returndata.msg);
            }
            else {

                document.getElementById("card_text").innerHTML = '表格中共包含 ' + returndata.table_title.length + ' 列数据'
                item = {
                    '姓名*': 'person_name', '分校': 'school', '职务': 'job_name',
                    '总课时数': 'lesson_number', '年度考核': 'year_result', '任教班级': 'class_id', '任教学科': 'subject',
                    '上学期末排名': 'rank_up_school', '上学期全县排名': 'rank_up_country', '下学期末排名': 'rank_down_school', '下学期全县排名': 'rank_down_country'
                }

                var card = document.getElementById("title_select_card");
                card.innerHTML = "";
                for (var i in item) {
                    select_id = 'select_' + item[i];
                    var d1 = document.createElement("div");
                    d1.className = "input-group mb-3";
                    var d2 = document.createElement("div");
                    d2.className = "input-group-prepend";
                    var s = document.createElement("select");
                    s.className = "custom-select";
                    s.id = select_id;
                    s.options.add(new Option('待选择', 0));
                    for (var j = 0; j < returndata.table_title.length; j++) {
                        option_string = '第' + (j + 1) + '列：' + returndata.table_title[j];
                        s.options.add(new Option(option_string, j + 1));
                    }
                    var l = document.createElement("label");
                    l.className = "input-group-text";
                    l.setAttribute("for", select_id);
                    l.innerHTML = i;
                    if (i == '上学期末排名') {
                        var d = document.createElement("div");
                        d.className = "alert alert-info";
                        d.setAttribute("role", "alert");
                        d.innerText = "导入排名时，需要同时有班级和学科。";
                        card.appendChild(d);
                    }
                    if (i == '任教班级') {
                        var d = document.createElement("div");
                        d.className = "alert alert-info";
                        d.setAttribute("role", "alert");
                        d.innerText = "任教班级和任教学科必须同时导入。";
                        card.appendChild(d);
                    }

                    d2.appendChild(l);
                    d1.appendChild(d2);
                    d1.appendChild(s);
                    card.appendChild(d1);
                }
                document.getElementById("select_card").style.display = "block";
                document.getElementById("input_file").disabled = true;
                document.getElementById("button_readfile").disabled = true;
            }

        },
        error: function (xhr, textStatus, errorThrown) {
            window.alert("上传失败！")
            alert("进入error---");
            alert("状态码：" + xhr.status);
            alert("状态:" + xhr.readyState); //当前状态,0-未初始化，1-正在载入，2-已经载入，3-数据进行交互，4-完成。
            alert("错误信息:" + xhr.statusText);
            alert("返回响应信息：" + xhr.responseText);//这里是详细的信息
            alert("请求状态：" + textStatus);
            alert(errorThrown);
            alert("请求失败");
        }
    });
}

function import_data() {
    document.getElementById("input_file").disabled = false;
    var formData = new FormData($('#readfile_form')[0]);

    var index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    formData.append("year", year);

    item_select = ['person_name', 'school', 'job_name', 'lesson_number', 'year_result',
        'class_id', 'subject', 'rank_up_school', 'rank_up_country', 'rank_down_school', 'rank_down_country']
    item_id_list = []
    var len = item_select.length;
    for (var i = 0; i < len; i++) {
        var select_id = document.getElementById('select_' + item_select[i]).selectedIndex;
        item_id_list.push(select_id);
    }

    if (item_id_list[0] == 0) {
        window.alert('姓名为必须导入的数据列。')
        return;
    }
    if (item_id_list[5] != 0) {
        if (item_id_list[1] == 0) {
            window.alert('导入任教班级时，分校需要导入。')
            return;
        }
        if (item_id_list[6] == 0) {
            window.alert('要导入任教班级，任教学科必须同时导入。')
            return;
        }
    }
    if (item_id_list[6] != 0) {
        if (item_id_list[5] == 0) {
            window.alert('要导入任教学科，任教班级必须同时导入。')
            return;
        }
    }
    if (item_id_list[7] + item_id_list[8] + item_id_list[9] + item_id_list[10] != 0) {
        if (item_id_list[5] == 0) {
            window.alert('要导入排名，任教班级和任教学科必须同时导入。')
            return;
        }
    }

    formData.append("item_id_list", item_id_list);
    $.ajax({
        url: "/lijing_workinfo/importData",
        type: "POST",
        data: formData,
        async: true,
        cashe: false,
        contentType: false,
        processData: false,
        success: function (returndata) {
            window.alert(returndata.msg);
            $("#table").bootstrapTable('refresh');
        },
        error: function (returndata) {
            window.alert("上传失败！")
        }
    });


    //item = {
    //    '姓名*': 'person_name', '分校': 'school', '职务': 'job_name',
    //    '总课时数': 'lesson_number', '年度考核': 'year_result', '任教班级': 'class_id', '任教学科': 'subject',
    //    '上学期末排名': 'rank_up_school', '上学期全县排名': 'rank_up_country', '下学期末排名': 'rank_down_school', '下学期全县排名': 'rank_down_country'
    //}

}

function add_school() {

    var school_string = document.getElementById("school_string").value;
    if (school_string == '') {
        window.alert('请输入分校名称');
        return;
    }
    datas = {}
    datas['school'] = school_string;
    var index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    datas['year'] = year;
    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/add_school', datas, function (return_data) {
        if (return_data.msg == 'error') {
            window.alert(return_data.error);
            document.getElementById("school_string").value = "";
            return;
        }
        else {
            document.getElementById("school_select").options.add(new Option(school_string));
            document.getElementById("school_select_del").options.add(new Option(school_string));
            //window.alert(return_data.msg);
        }
        var card = document.getElementById("school_card");
        card.innerHTML = ''

        for (var i = 0; i < return_data.school_list.length; i++) {
            var d1 = document.createElement("div");
            d1.className = "card mb-3 text-center";

            var d2 = document.createElement("div");
            d2.className = "card-header";
            d2.setAttribute("data-toggle", "collapse");
            d2.setAttribute("data-target", "#class_list_" + i);
            d2.innerHTML = return_data.school_list[i];

            var sp = document.createElement("span");
            sp.className = "badge badge-primary badge-pill";
            sp.innerHTML = return_data.class_list[return_data.school_list[i]].length;

            var ul = document.createElement("ul");
            ul.className = "list-group list-group-flush collapse";
            ul.id = 'class_list_' + i;

            if (return_data.class_list[return_data.school_list[i]].length == 0) {
                var li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = "暂无班级信息";
                ul.appendChild(li);
            }
            else {
                for (var j = 0; j < return_data.class_list[return_data.school_list[i]].length; j++) {
                    var li = document.createElement("li");
                    li.className = "list-group-item";
                    li.innerHTML = return_data.class_list[return_data.school_list[i]][j];
                    ul.appendChild(li);
                }
            }

            d2.appendChild(sp);
            //ul.appendChild(li);
            d1.appendChild(d2);
            d1.appendChild(ul);
            card.appendChild(d1);
        }
    });
}

function add_class() {

    var index = document.getElementById("school_select").selectedIndex;
    var school_string = document.getElementById("school_select").options[index].value;
    if (school_string == '暂无分校') {
        window.alert('请先添加分校');
        return;
    }
    var class_string = document.getElementById("class_string").value;
    if (class_string == '') {
        window.alert('请输入班级名称');
        return;
    }
    var person_string = document.getElementById("person_string").value;
    if (person_string == '') {
        window.alert('请输入班主任名称');
        return;
    }

    datas = {}
    datas['class'] = class_string;
    datas['person'] = person_string;
    datas['school'] = school_string;
    index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    datas['year'] = year;
    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/add_class', datas, function (return_data) {
        if (return_data.msg == 'error') {
            window.alert(return_data.error);
            document.getElementById("class_string").value = "";
            document.getElementById("person_string").value = "";
            return;
        }
        else {
            //window.alert(return_data.msg);
            document.getElementById("person_string").value = "";
            document.getElementById("class_string").value = '' + (parseInt(class_string) + 1);
        }

        var card = document.getElementById("school_card");
        card.innerHTML = ''
        for (var i = 0; i < return_data.school_list.length; i++) {
            var d1 = document.createElement("div");
            d1.className = "card mb-3 text-center";

            var d2 = document.createElement("div");
            d2.className = "card-header";
            d2.setAttribute("data-toggle", "collapse");
            d2.setAttribute("data-target", "#class_list_" + i);
            d2.innerHTML = return_data.school_list[i];

            var sp = document.createElement("span");
            sp.className = "badge badge-primary badge-pill";
            sp.innerHTML = return_data.class_list[return_data.school_list[i]].length;

            var ul = document.createElement("ul");
            ul.className = "list-group list-group-flush collapse";
            ul.id = 'class_list_' + i;

            if (return_data.class_list[return_data.school_list[i]].length == 0) {
                var li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = "暂无班级信息";
                ul.appendChild(li);
            }
            else {
                for (var j = 0; j < return_data.class_list[return_data.school_list[i]].length; j++) {
                    var li = document.createElement("li");
                    li.className = "list-group-item";
                    li.innerHTML = return_data.class_list[return_data.school_list[i]][j];
                    ul.appendChild(li);
                }
            }

            d2.appendChild(sp);
            d1.appendChild(d2);
            d1.appendChild(ul);
            card.appendChild(d1);
        }
    });
}

function del_school() {
    var school_string = document.getElementById("school_string_del").value;
    if (school_string == '') {
        window.alert('请输入要删除的分校名称');
        return;
    }
    if (confirm('是否删除？') == false) {
        return;
    }
    datas = {}
    datas['school'] = school_string;
    var index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    datas['year'] = year;
    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/del_school', datas, function (return_data) {
        if (return_data.msg == 'error') {
            window.alert(return_data.error);
            document.getElementById("school_string").value = "";
            return;
        }
        else {
            var mySelect = document.getElementById("school_select");
            for (var i = 0; i < mySelect.length; i++) {
                if (mySelect.options[i].text == school_string) {
                    mySelect.options.remove(i);
                    document.getElementById("school_select_del").options.remove(i);
                    break;
                }
            }
            //document.getElementById("school_select").options.remove(index);
            //$("#school_classModal").modal("hide");
        }

        var card = document.getElementById("school_card");
        card.innerHTML = ''
        for (var i = 0; i < return_data.school_list.length; i++) {
            var d1 = document.createElement("div");
            d1.className = "card mb-3 text-center";

            var d2 = document.createElement("div");
            d2.className = "card-header";
            d2.setAttribute("data-toggle", "collapse");
            d2.setAttribute("data-target", "#class_list_" + i);
            d2.innerHTML = return_data.school_list[i];

            var sp = document.createElement("span");
            sp.className = "badge badge-primary badge-pill";
            sp.innerHTML = return_data.class_list[return_data.school_list[i]].length;

            var ul = document.createElement("ul");
            ul.className = "list-group list-group-flush collapse";
            ul.id = 'class_list_' + i;

            if (return_data.class_list[return_data.school_list[i]].length == 0) {
                var li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = "暂无班级信息";
                ul.appendChild(li);
            }
            else {
                for (var j = 0; j < return_data.class_list[return_data.school_list[i]].length; j++) {
                    var li = document.createElement("li");
                    li.className = "list-group-item";
                    li.innerHTML = return_data.class_list[return_data.school_list[i]][j];
                    ul.appendChild(li);
                }
            }

            d2.appendChild(sp);
            d1.appendChild(d2);
            d1.appendChild(ul);
            card.appendChild(d1);
        }
    });
}

function del_class() {

    var index = document.getElementById("school_select_del").selectedIndex;
    var school_string = document.getElementById("school_select_del").options[index].value;
    if (school_string == '暂无分校') {
        window.alert('请先添加分校');
        return;
    }
    var class_string = document.getElementById("class_string_del").value;
    if (class_string == '') {
        window.alert('请输入要删除的班级名称');
        return;
    }
    if (confirm('是否删除？') == false) {
        return;
    }

    datas = {}
    datas['class'] = class_string;
    datas['school'] = school_string;
    index = document.getElementById("select_year").selectedIndex;
    var year = document.getElementById("select_year").options[index].value;
    datas['year'] = year;
    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/del_class', datas, function (return_data) {
        if (return_data.msg == 'error') {
            window.alert(return_data.error);
            document.getElementById("school_string").value = "";
            return;
        }
        var card = document.getElementById("school_card");
        card.innerHTML = ''
        for (var i = 0; i < return_data.school_list.length; i++) {
            var d1 = document.createElement("div");
            d1.className = "card mb-3 text-center";

            var d2 = document.createElement("div");
            d2.className = "card-header";
            d2.setAttribute("data-toggle", "collapse");
            d2.setAttribute("data-target", "#class_list_" + i);
            d2.innerHTML = return_data.school_list[i];

            var sp = document.createElement("span");
            sp.className = "badge badge-primary badge-pill";
            sp.innerHTML = return_data.class_list[return_data.school_list[i]].length;

            var ul = document.createElement("ul");
            ul.className = "list-group list-group-flush collapse";
            ul.id = 'class_list_' + i;

            if (return_data.class_list[return_data.school_list[i]].length == 0) {
                var li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = "暂无班级信息";
                ul.appendChild(li);
            }
            else {
                for (var j = 0; j < return_data.class_list[return_data.school_list[i]].length; j++) {
                    var li = document.createElement("li");
                    li.className = "list-group-item";
                    li.innerHTML = return_data.class_list[return_data.school_list[i]][j];
                    ul.appendChild(li);
                }
            }

            d2.appendChild(sp);
            d1.appendChild(d2);
            d1.appendChild(ul);
            card.appendChild(d1);
        }

    });

}

$("#select_year").change(function () {
    //要触发的事件

    document.getElementById('jumbotron_string').innerHTML = this.value + '年-教师业务档案';
    datas = {};
    datas['year'] = this.value;
    $.getJSON($SCRIPT_ROOT + '/lijing/set_year', datas, function (return_data) {

        $("#table").bootstrapTable('refresh');
    });

});

function update_data() {
    var datas = {}
    var item = ['person_name', 'school_name', 'job_name', 'lesson_number', 'year_result', 'class_master'];
    var rank_item = ['class_id', 'subject', 'rank_up_school', 'rank_up_country', 'rank_down_school', 'rank_down_country']

    datas['person_id'] = update_person_id;
    for (var i = 0; i < item.length; i++) {
        datas[item[i]] = document.getElementById(item[i]).value;
    }

    if (document.getElementById('class_id' + update_rank_number).value != '') {
        update_rank_number++;
    }
    datas['rank_number'] = update_rank_number;
    for (var i = 0; i < update_rank_number; i++) {
        for (var j = 0; j < rank_item.length; j++) {
            datas[rank_item[j] + i] = document.getElementById(rank_item[j] + i).value;
        }
    }

    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/update_data', datas, function (return_data) {
        if (return_data.msg == 'error') {
            window.alert(return_data.error);
            return;
        }
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;
        $("#detailModal").modal("hide");
        $("#table").bootstrapTable('refresh');
    });
}

function delete_data(id) {

    if (confirm('是否删除？') == true) {
        var datas = {}
        datas['person_id'] = update_person_id;
        datas['class_name'] = document.getElementById("class_id" + id).value;
        datas['subject'] = document.getElementById("subject" + id).value;

        $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/delete_data', datas, function (return_data) {
            if (return_data.msg == 'error') {
                window.alert(return_data.error);
                return;
            }
            document.getElementById("success_info").style.display = "block";
            document.getElementById("success_msg").innerHTML = return_data.msg;
            $("#detailModal").modal("hide");
            $("#table").bootstrapTable('refresh');
        });
    }

}

function search_data() {
    var search_string = document.getElementById("search_string").value;
    if (search_string == "") {
        window.alert("请填入要搜索内容");
        return;
    }

    document.getElementById("select_year").disabled = true;
    var index = document.getElementById("search_select").selectedIndex;
    var item = document.getElementById("search_select").options[index].value;
    index = document.getElementById("search_school_select").selectedIndex;
    var school = document.getElementById("search_school_select").options[index].value;
    if (index == 0) { school = '#' + school; }

    datas = {};
    datas["school_select"] = school;
    datas["search_item"] = item;
    datas["search_string"] = search_string;

    $.getJSON($SCRIPT_ROOT + '/lijing_workinfo/search_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;

        flag_search = true;
        document.getElementById("origin_button").style.display = "block";
        //$('#export_button').removeClass('disabled');
        $("#table").bootstrapTable("destroy");
        $('#table').bootstrapTable({
            //url: '/lijing/jsondata',  // 请求数据源的路由
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
                    field: 'id',
                    title: '编号',
                    align: 'center',  //对齐方式，居中 
                }, {
                    field: 'name',
                    title: '姓名',
                    align: 'center'
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
}
