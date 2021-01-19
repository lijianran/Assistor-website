

// 加载feather图标
feather.replace()


$("#ul_header").find("li").each(function () {
    var a = $(this).find("a:first")[0];
    // window.alert(a);

    if ($(a).attr("href") === location.pathname) {
        $(a).addClass("active");

        var demo = document.getElementById("demo");
        if ($.contains(demo, this)) {
            demo.classList.add("show");
        } else {
            demo.classList.remove("show");
        }
    } else {
        // $(this).removeClass("active");
    }
});