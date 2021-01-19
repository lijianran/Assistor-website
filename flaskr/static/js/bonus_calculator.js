

var item_subject = ['chinese', 'math', 'english', 'wl', 'hx', 'zz', 'ls', 'dl', 'sw'];
var item = ['chinese', 'math', 'english', 'wl', 'hx', 'zz', 'ls', 'dl', 'sw',
    'class1', 'class2', 'bonus1', 'bonus2', 'ebonus1', 'ebonus2', 'bonus_average', 'bonus3'];

function add_total(id, value) {
    if (value < 0) {
        document.getElementById(id).value = 0;
    }
    var total = 0.0;

    for (var i = 0; i < item_subject.length; i++) {
        total += Number(document.getElementById(item_subject[i]).value);
    }
    document.getElementById("total").value = total.toFixed(2);
}


function init() {
    document.getElementById("chinese").value = '1';
    document.getElementById("math").value = '1';
    document.getElementById("english").value = '0.8';
    document.getElementById("wl").value = '0.55';
    document.getElementById("hx").value = '0.5';
    document.getElementById("zz").value = '0.15';
    document.getElementById("ls").value = '0.15';
    document.getElementById("dl").value = '0.15';
    document.getElementById("sw").value = '0.15';

    document.getElementById("class1").value = '10';
    document.getElementById("class2").value = '20';

    document.getElementById("bonus1").value = '500';
    document.getElementById("bonus2").value = '300';

    document.getElementById("ebonus1").value = '60';
    document.getElementById("ebonus2").value = '40';

    document.getElementById("bonus_average").value = '100';
    document.getElementById("bonus3").value = '8';


    add_total();
}
init();

function showFilename(file) {
    $("#filename_label").html(file.name);
};

function read_file() {
    if (document.getElementById("input_file").value == 0) {
        window.alert('请选择文件');
        return;
    }

    var formData = new FormData($('#readfile_form')[0]);

    item_value = []
    for (var i = 0; i < item.length; i++) {
        item_value.push(document.getElementById(item[i]).value);

    }
    formData.append("item_value", item_value);


    $.ajax({
        url: "/bonus_calculator/calculator_bonus",
        type: "POST",
        data: formData,
        async: true,
        cashe: false,
        contentType: false,
        processData: false,
        success: function (returndata) {
            if (returndata.msg != '成功') {
                document.getElementById("log").append(returndata.msg);
            }
            else {
                document.getElementById("log").innerText = '';
                document.getElementById("button_readfile").disabled = true;
                document.getElementById("button_readfile").innerText = '统计已完成';
                document.getElementById("input_file").disabled = true;
                log = returndata['log'];

                class_list = returndata['class_list'];
                teacher_list = returndata['teacher_list'];
                document.getElementById("log").append('共有' + class_list.length + '个班级，' + teacher_list.length + '位教师\n');


                for (var i in log) {
                    document.getElementById("log").append(log[i]);
                }

                window.location.href = '/lijing/download_excel_file/' + returndata.filename;
            }

        },
        error: function (xhr, textStatus, errorThrown) {
            window.alert("上传失败！")
            //alert("进入error---");
            //alert("状态码：" + xhr.status);
            //alert("状态:" + xhr.readyState); //当前状态,0-未初始化，1-正在载入，2-已经载入，3-数据进行交互，4-完成。
            //alert("错误信息:" + xhr.statusText);
            //alert("返回响应信息：" + xhr.responseText);//这里是详细的信息
            //alert("请求状态：" + textStatus);
            //alert(errorThrown);
            //alert("请求失败");
        }
    });
}

