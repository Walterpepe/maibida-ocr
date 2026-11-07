$(function () {
    $.ajax({
        url: "/IAjax/Ajax.ashx",
        type: "POST",
        cache: false,
        dataType: "text",
        data: { action: "Visits"},
        success: function () {          
        }
    });
});