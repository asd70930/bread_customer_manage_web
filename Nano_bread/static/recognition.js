var filesizeLimit = 6 * 1024 * 1024
var imageZoneHeight = $(".img-zone")[0].clientHeight
var imageZoneWidth  = $(".img-zone")[0].clientWidth
var imageHeight = 0;
var imageWidth = 0;
var moreHeight = false;
var moreWidth = false;
var heightAnchor = 0;
var widthAnchor = 0;
var weightsHeight = 0;
var weightsWidth = 0;

function changeWeight(){
    var image = new Image();
    image.src = $("#blsh1").attr("src");

    displayHeight = $("#blsh1")[0].clientHeight;
    displayWidth  = $("#blsh1")[0].clientWidth;
    image.onload = function() {
        oriHeight = image.height;
        oriWidth  = image.width;

        console.log("imageZoneHeight:"+imageZoneHeight);
        console.log("imageZoneWidth:"+imageZoneWidth);
        console.log("oriHeight:"+oriHeight);
        console.log("oriWidth:"+oriWidth);

        if (imageZoneHeight>=displayHeight){
            // 顯示圖片Height 比img-zone 的Height小，需要補anchor
            heightAnchor = (imageZoneHeight - displayHeight) / 2;
        }
        else{
            // 顯示圖片Height 比img-zone 的Height大，不需要補anchor
            heightAnchor = 0;
        }
        if (imageZoneWidth>=displayWidth){
            // 顯示圖片Width 比img-zone 的Width小，需要補anchor
            widthAnchor = (imageZoneWidth - displayWidth) / 2;
        }
        else{
            // 顯示圖片Width 比img-zone 的Width大，不需要補anchor
            widthAnchor = 0;
        }
        if (oriHeight>=displayHeight){
            // 原始圖片Height 比顯示圖片 Height大 , 需要縮小 Height間距
            weightsHeight = displayHeight / oriHeight;
        }
        else{
            // 原始圖片Height 比顯示圖片 Height小 , 不需要縮小 Height間距
            weightsHeight = 1;
        }
        if (oriWidth>=displayWidth){
            // 原始圖片Width 比顯示圖片 Width大 , 需要縮小 Width間距
            weightsWidth = displayWidth / oriWidth;
        }
        else{
            // 原始圖片Width 比顯示圖片 Width小 , 不需要縮小 Width間距
            weightsWidth = 1;
        }
    };
}


$("#testingBt").click(function(){
    console.log("imageZoneWidth:"+imageZoneWidth)
    console.log("imageZoneHeight:"+imageZoneHeight)
    console.log("moreHeight:"+moreHeight)
    console.log("moreWidth:"+moreWidth)
    console.log("heightAnchor:"+heightAnchor)
    console.log("widthAnchor:"+widthAnchor)
    console.log("weightsHeight:"+weightsHeight)
    console.log("weightsWidth:"+weightsWidth)
});

function readURL(input) {
    clean();
    if (input.files && input.files[0]) {
        if (filesizeLimit <= input.files[0].size) {
            alert("圖片檔案無法上傳大於2MB");
        }
        else{
            var inputt = input
            var reader = new FileReader();

            reader.onload = function (e) {
                $('#blsh1').attr('src', e.target.result);
            }
            var filename = input.files[0].name.split(".",1)[0]
            var base64X = reader.readAsDataURL(input.files[0]); // convert to base64 string
            var xxx =1;
        }
    }
}

$("#uploadimg1").change(function () {
readURL(this);
});

$("#show_camera1").click(function () {
    clean();
    $('#show_camera1').attr('disabled', "disabled");
    ip = $("#textarea_getipc1").val();
    var pay_load = {
        "ip": ip
    };
    var getCamera = false;
    $.ajax({
        url:"show_ipc",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(pay_load),
        complete:function(){
        },
        success: function (data) {
            var ret = data["ret"]
            getCamera = ret
            var base = data["base"]
            $('#show_camera1').attr('disabled', false);
            if (ret){
                $('#blsh1').attr('src', base);

            }
            else{alert("無法取得攝影機影像！");}
        }
    });

    var imgObject = $("#blsh1")[0]
    var width = imgObject.clientWidth;
    var height = imgObject.clientHeight;
});

function infrernce() {
    changeWeight()
    var aimgsrc = $("#blsh1").attr("src")
    var pay_load = {
        "b64string": aimgsrc
    };
    var value = 'Bearer '+localStorage.getItem("myJWT");
    $("#bt2").attr("disabled","")
    $.ajax({
        url:"infrence",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(pay_load),
        beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization', value);
        },
        complete:function(){
            $("#bt2").removeAttr("disabled");
        },
        success: function (data) {
            var status = data["rtn"]
            if (status == 400){
                alert("server error, try it later");
            }
            else{
                var datalist = data["rtn_values"]
                var datadic = {}
                for (data of datalist){
                    dataKey = data[1];
                    dataLeft = data[0][0]
                    dataTop = data[0][1]
                    dataWidth = data[0][2]
                    dataHeight = data[0][3]

                    var htmlBox = '<div class="rect rect-'+dataKey+' unselected" onclick="addSelectedList(this)" data-key="'+dataKey +'" style="left:'
                    htmlBox += (dataLeft * weightsWidth  + widthAnchor) +  'px;top:'+ (dataTop * weightsHeight + heightAnchor) + 'px;width:'
                    htmlBox += (dataWidth * weightsWidth) + 'px;height:' + (dataHeight * weightsHeight) + 'px;"></div>';

                    $(".img-zone").append(htmlBox);
                    if (dataKey in datadic){
                        datadic[dataKey][0]+=1;
                    }
                    else{datadic[dataKey] = [1, data[2]];}
                }
                var flag = 0;
                for (key in datadic){
                    datanum  = datadic[key][0];
                    dataname = datadic[key][1];
                    if (flag==0){
                        flag+=1;
                        layoutHtml = '<div class="li-layout list-'+key+' selected" data-key="'+key+'" onclick="addSelectedList(this)">' +
                                     '<div class="layout-8 fl-col" >' +
                                     '<span>'+key+'</span>'+
                                     '<span>'+dataname+'</span>'+
                                     '</div>'+
                                     '<div class="layout-2 ta-r num">X'+datanum+'</div>'+
                                     '</div>'
                        $("#layout").append(layoutHtml);
                        $('.rect-'+key).removeClass('unselected');
                        $('.rect-'+key).addClass('selected')
                    }
                    else{
                        layoutHtml = '<div class="li-layout list-'+key+' div-unselected" data-key="'+key+'" onclick="addSelectedList(this)">' +
                                     '<div class="layout-8 fl-col" >' +
                                     '<span>'+key+'</span>'+
                                     '<span>'+dataname+'</span>'+
                                     '</div>'+
                                     '<div class="layout-2 ta-r num">X'+datanum+'</div>'+
                                     '</div>'
                        $("#layout").append(layoutHtml);
                    }
                }
                if (flag==0){alert("無法辨識,請嘗試其他圖片")}
            }
        },
        error: function (xhr,status,error) {
            alert("server error");
        },
    });

}

function clean(){
    $('.li-layout').remove();
    $('.rect').remove();
}

function addSelectedList(even){
  var dataKey = $(even).attr('data-key');
  $('.li-layout').removeClass('selected');
  $('.rect').removeClass('selected');
  $('.rect').addClass('unselected');
  $('.rect-'+dataKey).removeClass('unselected');
  $('.rect-'+dataKey).addClass('selected');
  $('.li-layout').addClass('div-unselected');
  $('.list-'+dataKey).removeClass('div-unselected');
  $('.list-'+dataKey).addClass('selected');
};