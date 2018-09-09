$(".record").change(function () {
    let pk = $(this).attr("pk");
    let record = $(this).val();
    $.ajax({
        url: '/my_admin/old_boy_crm/studentstudyrecord/' + pk + '/change_record/',
        type: "post",
        data: {
            record: record,
        },
        success: function (res) {
            console.log(res);
        },
    })
});