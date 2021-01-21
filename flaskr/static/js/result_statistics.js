

window.alert("hello");
function read_file() {
    window.alert("hello");
    var formData = new FormData($('#readfile_form')[0]);

    window.alert("hello");

    $.ajax({
        url: "/result_statistics/readfile",
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

function showFilename(file) {
    $("#filename_label").html(file.name);
};