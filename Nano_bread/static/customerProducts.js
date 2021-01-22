$(document).ready(function() {
    showTable(2);
    showCustomerProductList();
});

function showTable(tableId){
    var a = $("[id^='table-']")
    for (i=0;i<a.length;i++){
        if (a[i].id.split("-")[a[i].id.split("-").length-1]==tableId){
            a[i].style.display="block"
        }
        else{
            a[i].style.display="none"
        }
    }
}

function showCustomerProductList(){
    $.ajax({
        url:"/customer_productData",
        method: "get",
        contentType: "application/json;charset=UTF-8",
        dataType:"html",
        success: function (data) {
            $("#table1").html(data)
        },
        error: function (xhr,status,error) {
            errorBackToLogIn(xhr)
        },
    });
}