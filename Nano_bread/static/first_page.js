let uploadImageBase64List = [];
var filesizeLimit = 6 * 1024 * 1024;

$("#syBt_3").click(function(){
    showTable(1);
});
$("#tb1_bt1").click(function(){
    // 呈現客戶所有產品清單頁面
    showTable(2);
    showCustomerProductList();
});
$("#customerUploadImg").change(function(){
    $("#uploadLayout").empty();
    readUrlMultiple(this);
});


function imageAjax(srcs){
    let flag = 0;
    [].forEach.call(srcs,src =>{
        $.ajax({
            url:"/save_product_image",
            async:false,
            method: "post",
            contentType: "application/json;charset=UTF-8",
            dataType:"json",
            data:JSON.stringify({"base64":src,"product_id":productIdSend(),"flag":flag}),
        }).done(function(data){
        });
        flag +=1;
    });


}


function imageAllAjax(srcs){
    $.ajax({
            url:"/save_product_image",
            async:false,
            method: "post",
            contentType: "application/json;charset=UTF-8",
            dataType:"json",
            data:JSON.stringify({"base64":srcs,"product_id":productIdSend()})
        }).done(function(data){
        });
}



async function productImageSave(obj){
    var srcArray = [];
    let imgArray = $("#uploadLayout > li > div > div > img");
    [].forEach.call(imgArray, imgObj =>{
        srcArray.push(imgObj.getAttribute('src'))
    });
    if (srcArray.length ===0){alert("沒有上傳照片！");return ""}
//    await imageAjax(srcArray);
    imageAllAjax(srcArray);
    // close modal and return to product_id images page

    alert("上傳成功！");

    $("#uploadLayout").empty();
    showCustomerProductsImage(obj);
    $("#modal1").modal('hide');

}

function closeModal(){
    $("#uploadLayout").empty();
    $("p[class='f-l ml-3']").text("選擇圖片0張");
}

function removeUploadImage(obj){
    var id = 0;
    id = parseInt(obj.getAttribute("data-key"));
    $("#uploadLayout > li[data-key='"+id.toString()+"']").remove();
    let imageCount = getNum($("p[class='f-l ml-3']").text());
    $("p[class='f-l ml-3']").text("選擇圖片"+(imageCount-1).toString()+"張")
}

function readUrlMultiple(input) {
    $("p[class='f-l ml-3']").text("選擇圖片0張");
    var inputt = input;
    var srcList = [];
    uploadImageBase64List.length = 0;
    let files = input.files;
    let imgCount = 0;
    function readAndPreview(file) {
        var reader = new FileReader();
        reader.addEventListener("load", function () {
        // convert image file to base64 string
        // preview.src = reader.result;

            function imageHtmlMaker(number,obj){
                src  = obj.result;
                uploadImageBase64List.push(src);
                liHtml = '<li class="layout-3-3 my-3 px-3" data-key="'+number.toString()+'">'+
                       '<div class="select-img-wrapper is-valid">'+
                       '<div>'+
                       '<span class="bt-X" data-key="'+number.toString()+ '" onClick="removeUploadImage(this)"></span>'+
                       '<img data-key="'+number.toString()+ '" height="150" width="100%" src="'+src+'">'+
                       '</div>'+
                       '</div>'+
                       '</li>'
                $("#uploadLayout").append(liHtml);
            }

            imageHtmlMaker(imgCount,this);
            imgCount += 1;
            $("p[class='f-l ml-3']").text("選擇圖片"+imgCount.toString()+"張")

        }, false);
        reader.readAsDataURL(file);
    }

    if (files) {
        [].forEach.call(files, readAndPreview);
    }
}

function goRecognitionPage(){
    window.location.href='recognitionPage';
}

function backToCustomerProductList(){
    // 返回客戶所有產品清單頁面
    showTable(2)
    showCustomerProductList()
}

async function deleteCustomerProduct(obj){
    var deleteArray = [];
    var productId = obj.getAttribute("data-productid");
    var inputs = $("input[data-art5='input']");
    [].forEach.call(inputs, input =>{
        if (input.checked == true){
            deleteArray.push(input.getAttribute("data-path"))
        }
    });
    function ajax_(dataArray,id){
        [].forEach.call(dataArray,fileName =>{
            var payload = {"file_path":fileName,
                           "product_id":id};
            $.ajax({
            url:"/delete_product_image",
            method: "post",
            contentType: "application/json;charset=UTF-8",
            dataType:"json",
            data:JSON.stringify(payload),
            }).done(function(data){
            });

        });
    }

    await ajax_(deleteArray,productId);

    alert("照片刪除成功！");
    showCustomerProductsImage(obj);
}

function saveEditCustomerProfile(){
    var preProductId = $("#pre_barcode_error").val();
    var productId = $("#barcode_error").val();
    var productName = $("#product_name_error").val();
    var memo = $("#remarks_error").val();
    var imgscr = $("#blsh1").attr("src")
    inputdata = {"product_id":productId,
                 "pre_product_id":preProductId,
                 "product_name":productName,
                 "memo":memo,
                 "img":imgscr
    }
    $.ajax({
        url:"customer_saveProductData",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"html",
        data:JSON.stringify(inputdata),
        success: function (data) {
            showTable(2);
            showCustomerProductList();
        },
        error: function (xhr,status,error) {
            errorBackToLogIn(xhr);
        },
    });
}

function checkedInputBox(obj){
    var dataId = obj.getAttribute("data-id");
    var input = $("input[data-id='"+dataId+"']")[0].checked;
    if (input){
        $("input[data-id='"+dataId+"']").removeAttr('checked');
    }
    else{
        $("input[data-id='"+dataId+"']").attr('checked','checked');
    }

}

function readURL(input) {
    if (input.files && input.files[0]) {
        if (filesizeLimit <= input.files[0].size) {
            alert("圖片檔案無法上傳大於2MB");
        }
        else{
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#blsh1').attr('src', e.target.result);
            }
            var filename = input.files[0].name.split(".",1)[0]
            reader.readAsDataURL(input.files[0]); // convert to base64 string
        }
    }
}

function deleteProduct(){
    var inputs = $("#table1").find('input');
    var selectedInput = [];
    for (inputt of inputs){
        if (inputt.checked ==true){
            selectedInput.push(inputt.getAttribute("data-pdkey"));
        }
    }
    if (selectedInput.length ==0){
        alert("請選取要刪除的商品！");
        return "";
    }
    var inputdata = {"product_id":selectedInput};

    $.ajax({
        url:"customer_delete_product_data",
        method: "del",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(inputdata),
        success: function (data) {
            var status = data["status"];
            if (status == "01"){
                showTable(2);
                showCustomerProductList();
                alert("刪除成功");

            }
            else{
                alert("刪除失敗");
            }
        },
        error: function (xhr,status,error) {

        },
    });
}

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
        url:"customer_productData",
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

function productIdSend(){
    id = $("h4[class='float-r m-t-5']").attr("data-id");
    return id
}

function showCustomerEditProduct(obj){
//    var id = obj.id.split("_")[1];
    var value = 'Bearer '+localStorage.getItem("myJWT");
    var productId = obj.getAttribute("data-productID");
    inputdata = {"product_id":productId}
    $.ajax({
        url:"/customer_editProductData",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"html",
        data:JSON.stringify(inputdata),
        beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization', value);
        },
        success: function (data) {
            showTable(5);
            $("#table-5").html(data);
        },
        error: function (xhr,status,error) {
                errorBackToLogIn(xhr);
        },
    });
}

function passProductId(obj){
    var productId = obj.getAttribute("data-productID");
    $("#imageCount").text(obj.getAttribute("data-imageCount"));
    $("#bt_saveImage").attr("data-productID", productId);
}

function addCustomerProduct(){
    $.ajax({
        url:"/customer_add_product",
        method: "get",
        contentType: "application/json;charset=UTF-8",
        dataType:"html",
        success: function (data) {
            showTable(5);
            $("#table-5").html(data);
        },
    });
}


function showCustomerProductsImage(obj){
//    var id = obj.id.split("_")[1];
    var productId = obj.getAttribute("data-productid");
    inputdata = {"product_id":productId}
    $.ajax({
        url:"/reveal_customer_productdataimg",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"html",
        data:JSON.stringify(inputdata),
        success: function (data) {
            showTable(6)
            $("#table-6").html(data)
        },
        error: function (xhr,status,error) {
                errorBackToLogIn(xhr)
        },
    });

}


function errorBackToLogIn(xhr){
    if (xhr["status"]=="422" || xhr["status"]=="401" ){
            alert("Your Authorization is expired or invalid, please sign in again!");
            localStorage.clear();
            window.location.href='/';
       }
}

function getNum(text){
    // only get number and English letter
	var value = text.replace(/[^0-9a-zA-Z]/ig,"");
	return value;
}

function setCameraPage(){
    $.ajax({
        url:"/camera_set",
        method: "get",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        success: function (data) {
            showTable(7);

            if (data["status"]==1){
                $("#table").html(data["html"]);
                initCamera(data["camData"]);
            }
        },
        error: function (xhr,status,error) {
                alert('try it later')
        },
    });

}

