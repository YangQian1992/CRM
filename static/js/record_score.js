$(".score").change(function () {
    let score = $(this).val();
    let sid = $(this).attr("sid");
    $.ajax({
        url: "",
        type: "post",
        data: {
            val: score,
            action: "score",
            sid: sid,
        },
        success: function (res) {
            console.log(res);
        }
    })
});
$(".homework_note").blur(function () {
    let homework_note = $(this).val();
    let sid = $(this).attr("sid");
    $.ajax({
        url: "",
        type: "post",
        data: {
            val: homework_note,
            action: "homework_note",
            sid: sid,
        },
        success: function (res) {
            console.log(res);
        }
    })
});