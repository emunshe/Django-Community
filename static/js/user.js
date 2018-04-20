$(function () {
    $('.changed').change(function () {
        $(this).css("background-color","white");
    });

    $(".list li").click(function(){
        $(".list li").eq($(this).index()).addClass("liCls").siblings().removeClass("liCls");
    });
    $("#zidongclick").click();


});