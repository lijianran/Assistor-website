
var update_person_id = 0;
var update_honor_number = 0;
var flag_search = false;

function init() {

    var select_search = document.getElementById("search_select");

    var item = {
        '姓名': 'person_name', '获奖名称': 'honor_name', '证书级别': 'honor_grade', '发证时间': 'honor_time',
        '证书编号': 'honor_number', '发证单位': 'honor_unit', '获奖时间': 'get_time', '所在分校': 'school_name', '备注': 'honor_remark',
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
};

window.operateEvents = {
    'click .detail': function (e, value, row, index) {
        document.getElementById("detail_modal_title").innerHTML = row.name + "--荣誉档案";

        $.getJSON($SCRIPT_ROOT + '/lijing_honorinfo/search', { id: row.id }, function (data) {
            var item = ['school_name', 'honor_time', 'get_time', 'honor_unit', 'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
            var honor_data = data['data_list'];
            if (honor_data.length == 0) {
                var honor_list = document.getElementById('honor_list');
                honor_list.innerHTML = '<h4>暂无</h4>';
                return;
            }

            var honor_item = ['honor_name', 'honor_grade', 'honor_time', 'honor_number', 'honor_unit', 'get_time', 'school_name', 'honor_remark']
            var title_item = ['获奖名称', '证书级别', '发证时间', '证书编号', '发证单位', '获奖时间', '获奖时所在分校', '备注']
            var md = [5, 2, 2, 3, 5, 2, 2, 3];

            var honor_list = document.getElementById('honor_list');
            honor_list.innerHTML = '';

            for (var i = 0; i < honor_data.length; i++) {
                var honor = honor_data[i];

                var card = document.createElement("div");
                card.className = "card";
                var header = document.createElement("div");
                header.className = "card-header";
                header.innerHTML = '荣誉' + (i + 1);
                var body = document.createElement("div");
                body.className = "card-body";
                card.appendChild(header);
                card.appendChild(body);

                var row1 = document.createElement("div");
                row1.className = "form-row";
                var row2 = document.createElement("div");
                row2.className = "form-row";
                for (var j = 0; j < 8; j++) {
                    var div = document.createElement("div");
                    div.className = "form-group col-md-" + md[j];
                    var label = document.createElement("label");
                    label.setAttribute("for", honor_item[j] + i);
                    label.innerText = title_item[j];
                    var input = document.createElement("input");
                    input.className = "form-control";
                    input.readOnly = true;
                    input.value = honor[honor_item[j]];
                    input.id = honor_item[j] + i;
                    div.appendChild(label);
                    div.appendChild(input);
                    if (j < 4) { row1.appendChild(div); }
                    else { row2.appendChild(div); }
                }
                body.appendChild(row1);
                body.appendChild(row2);

                honor_list.appendChild(card);

                var divider = document.createElement("div");
                divider.className = 'dropdown-divider';
                honor_list.appendChild(divider);
                //honor_list.appendChild(divider);
            }

        });
        $("#honor_list input").attr("readOnly", true);
        document.getElementById("button_update").style.display = "none";
        document.getElementById("honor_add").style.display = "none";
        $('#detailModal').modal('show');

    },
    'click .update': function (e, value, row, index) {
        update_person_id = row.id;

        $.getJSON($SCRIPT_ROOT + '/lijing_honorinfo/search', { id: row.id }, function (data) {
            var item = ['school_name', 'honor_time', 'get_time', 'honor_unit', 'honor_name', 'honor_grade', 'honor_number', 'honor_remark']
            var honor_data = data['data_list'];
            if (honor_data.length == 0) {
                update_honor_number = 0;
                var honor_list = document.getElementById('honor_list');
                honor_list.innerHTML = '<h4>暂无，请先添加</h4>';

                $("#honor_list input").attr("readOnly", false);
                document.getElementById("button_update").style.display = "none";
                document.getElementById("honor_add").style.display = "none";
                document.getElementById("detail_modal_title").innerHTML = '修改教师“' + row.name + '”的荣誉档案';
                $('#detailModal').modal('show');
                return;
            }

            var honor_item = ['honor_name', 'honor_grade', 'honor_time', 'honor_number', 'honor_unit', 'get_time', 'school_name', 'honor_remark']
            var title_item = ['获奖名称', '证书级别', '发证时间', '证书编号', '发证单位', '获奖时间', '获奖时所在分校', '备注']
            var md = [3, 2, 2, 5, 3, 2, 2, 5];

            var honor_list = document.getElementById('honor_list');
            honor_list.innerHTML = '';

            update_honor_number = honor_data.length;
            for (var i = 0; i < honor_data.length; i++) {
                var honor = honor_data[i];

                var card = document.createElement("div");
                card.className = "card";
                var header = document.createElement("div");
                header.className = "card-header";
                header.innerHTML = '荣誉' + (i + 1);
                var body = document.createElement("div");
                body.className = "card-body";
                card.appendChild(header);
                card.appendChild(body);

                var row1 = document.createElement("div");
                row1.className = "form-row";
                var row2 = document.createElement("div");
                row2.className = "form-row";
                for (var j = 0; j < 8; j++) {
                    var div = document.createElement("div");
                    div.className = "form-group col-md-" + md[j];
                    var label = document.createElement("label");
                    label.setAttribute("for", honor_item[j] + i);
                    label.innerText = title_item[j];
                    var input = document.createElement("input");
                    input.className = "form-control";
                    input.readOnly = false;
                    input.value = honor[honor_item[j]];
                    input.id = honor_item[j] + i;
                    div.appendChild(label);
                    div.appendChild(input);
                    if (j < 4) { row1.appendChild(div); }
                    else { row2.appendChild(div); }
                }
                body.appendChild(row1);
                body.appendChild(row2);

                honor_list.appendChild(card);

                var divider = document.createElement("div");
                divider.className = 'dropdown-divider';
                honor_list.appendChild(divider);
            }


            $("#honor_list input").attr("readOnly", false);
            document.getElementById("button_update").style.display = "block";
            document.getElementById("honor_add").style.display = "none";
            document.getElementById("detail_modal_title").innerHTML = '修改教师“' + row.name + '”的荣誉档案';
            $('#detailModal').modal('show');

        });



    },
    'click .remove': function (e, value, row, index) {
        window.alert("待开发");
        //$table.bootstrapTable('remove', {field: 'id',values: [row.id]})
    }
};

function init_table() {
    $('#table').bootstrapTable({
        url: '/lijing_honorinfo/jsondata',  // 请求数据源的路由
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
                field: 'num',
                title: '荣誉项',
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

};
init_table();

function show_import_modal() {
    $('#importModal').modal('show');
};

function show_add_modal() {
    document.getElementById("detail_modal_title").innerHTML = "荣誉档案";
    var honor_list = document.getElementById('honor_list');
    honor_list.innerHTML = '';

    document.getElementById("honor_add").style.display = "block";
    $("#detailModal").modal("show");
};

function update_data() {
    var datas = {};
    var item = ['school_name', 'honor_time', 'get_time', 'honor_unit', 'honor_name', 'honor_grade', 'honor_number', 'honor_remark']

    datas["person_id"] = update_person_id;
    datas['update_number'] = update_honor_number;
    for (var i = 0; i < update_honor_number; i++) {
        for (var j = 0; j < item.length; j++) {
            datas[item[j] + i] = document.getElementById(item[j] + i).value;
        }
    }

    $.getJSON($SCRIPT_ROOT + '/lijing_honorinfo/update_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;
        $("#detailModal").modal("hide");
        $("#table").bootstrapTable('refresh');
    });
};

function search_data() {
    var search_string = document.getElementById("search_string").value;
    if (search_string == "") {
        window.alert("请填入要搜索内容");
        return;
    }

    document.getElementById("select_year").disabled = true;
    var index = document.getElementById("search_select").selectedIndex;
    var search_item = document.getElementById("search_select").options[index].value;

    datas = {};
    datas["search_item"] = search_item;
    datas["search_string"] = search_string;

    $.getJSON($SCRIPT_ROOT + '/lijing_honorinfo/search_data', datas, function (return_data) {
        document.getElementById("success_info").style.display = "block";
        document.getElementById("success_msg").innerHTML = return_data.msg;

        flag_search = true;
        document.getElementById("origin_button").style.display = "block";

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
                    field: 'id',
                    title: '编号',
                    align: 'center',  //对齐方式，居中 
                }, {
                    field: 'name',
                    title: '姓名',
                    align: 'center'
                }, {
                    field: 'num',
                    title: '荣誉项',
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

        $.getJSON($SCRIPT_ROOT + '/lijing_honorinfo/exportData', datas, function (return_data) {
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

$("#select_year").change(function () {
    //要触发的事件
    document.getElementById('jumbotron_string').innerHTML = this.value + '年-教师基本信息';

    datas = {};
    datas['year'] = this.value;
    $.getJSON($SCRIPT_ROOT + '/lijing/set_year', datas, function (return_data) {
        $("#table").bootstrapTable('refresh');
    });

});

