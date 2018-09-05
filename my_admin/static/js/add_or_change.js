var pop_back_id = "";
function pop(url,id) {
    pop_back_id = id;
    window.open(url+'?pop=1',url+'?pop=1','width=800,height=500,top=100,left=100')
}

function pop_back_func(form_data,pk) {
   console.log(form_data,pk);
    var $option = $("<option>");  // 生成一个<option></option>标签
    $option.html(form_data);
    $option.attr("value",pk);
    $option.attr("selected","selected");

    $("#"+pop_back_id).append($option);
}