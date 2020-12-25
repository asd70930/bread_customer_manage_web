var flag = 0;
var dataList = [];
var dataSendList = [];
var dataPreSendList = [];
var mouseX = 0;
var mouseY = 0;
var first = true;
var fileSizeLimit = 6 * 1024 * 1024
var widthAnchor = 0;
var heightAnchor = 0;


$(document).ready(function() {
//  draw()
});



$("#upLoadImageBT").change(function () {
readURL(this);
});

$("#btCleanAll").click(function(){
    canva = $("#canva")[0]
    ctx = canva.getContext('2d');
    canva.width = canva.width
    dataList = []
    dataSendList = []
    $("#xyTable").html("")
    flag = 0
    $("#pointCount").text("pointCount 0");
    $('#bt1').removeAttr("disabled");
    $('#upLoadImageBT').removeAttr("disabled");
    $('#btSend').removeAttr("disabled");

});

$("#btSend").click(function(){

    var aimgsrc = $("#blsh1").attr("src");
    var pay_load = {
        "b64string": aimgsrc,
        "roi": dataSendList
    };
    $.ajax({
        url:"/roiIfrence",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(pay_load),
        success: function (data) {
            console.log("good")
        },
        error: function (xhr,status,error) {
            alert("server error");
        },
    });
});

function readURL(input) {
    clean();
    if (input.files && input.files[0]) {
        if (fileSizeLimit <= input.files[0].size) {
            alert("圖片檔案無法上傳大於2MB");
        }
        else{
            var inputt = input
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#blsh1').attr('src', e.target.result);

            }
            var filename = input.files[0].name.split(".",1)[0]
            reader.readAsDataURL(input.files[0]); // convert to base64 string
        }
    }
}

function changeWeight(){
    widthAnchor = 0;
    heightAnchor = 0;
    var image = new Image();
    image.src = $("#blsh1").attr("src");
    var displayHeight = $("#blsh1")[0].clientHeight;
    var displayWidth  = $("#blsh1")[0].clientWidth;
    image.onload = function() {
        var oriHeight = image.height;
        var oriWidth  = image.width;
        dataSendList = dataPreSendList.slice(0);
        if (oriHeight > displayHeight){
            heightAnchor = oriHeight-displayHeight;
        }
        if (oriWidth > displayWidth){
            widthAnchor = oriWidth-displayWidth;
        }
        if(widthAnchor > 0 || heightAnchor > 0){
            for (datas of dataSendList){
                for (data of datas){
                    data[0] += widthAnchor;
                    data[1] += heightAnchor;
                }
            }
        }
    }
    var xxx = 1;
}

function pointD(e){
    first = false;
    x = mouseX
    y = mouseY
    flag+=1;
    console.log("x"+flag+" :"+x)
    console.log("y"+flag+" :"+y)
    const point = document.getElementById('pointCount')
    point.textContent = "pointCount " + flag

    canva = $("#canva")[0]
    ctx = canva.getContext('2d');

    dataList.push([x,y]);
    if (flag ==4){
        dataPreSendList.push(dataList)
        makeTable()
        ctx.strokeStyle = "rgb(255,0,0)"; // Red line
        clean(ctx);
        drawLine(ctx)
        dataList = [];
        $('#bt1').removeAttr("disabled");
        $('#upLoadImageBT').removeAttr("disabled");
        $('#btSend').removeAttr("disabled");
    }
    else{
        ctx.fillRect(x, y, 1, 1);
        $('#bt1').attr('disabled','disabled');
        $('#upLoadImageBT').attr('disabled','disabled');
        $('#btSend').attr('disabled','disabled');

    }
}

function makeTable(){
    layoutHtml = '<div class="flex-row tableBorder m-2">'+
                 '<p>x1:'+dataList[0][0]+', y1:'+dataList[0][1]+'</p>'+
                 '<p>x2:'+dataList[1][0]+', y2:'+dataList[1][1]+'</p>'+
                 '<p>x3:'+dataList[2][0]+', y3:'+dataList[2][1]+'</p>'+
                 '<p>x4:'+dataList[3][0]+', y4:'+dataList[3][1]+'</p>'+
                 '</div>'
    $("#xyTable").append(layoutHtml);
    changeWeight();
}

function drawLine(c){
    thisflag = 0
    for (data of dataList){
        x = data[0];
        y = data[1];
        if (thisflag ==0){
            thisflag+=1;
            c.moveTo(x,y);
        }
        else{
             c.lineTo(x,y);
        }
    }
    c.lineTo(dataList[0][0],dataList[0][1]);
    c.closePath();
    c.stroke();
}

function clean(c){
//    for
    flag = 0;
    for (data of dataList){
        x = data[0]
        y = data[1]
        c.clearRect(x, y, 1, 1)
    }
}



function reportCurrentPoint(e) {
  //	選取 HTML 各元素
  const info = document.getElementById('info')
  const offset = document.getElementById('offset')
  const client = document.getElementById('client')

  //	取得 viewport 座標系統中的 offset 和 client 座標值，並顯示於視窗上
  offset.textContent = `offset (${e.offsetX}, ${e.offsetY})`
  client.textContent = `client (${e.clientX}, ${e.clientY})`
  mouseX = e.offsetX;
  mouseY = e.offsetY;

} //	結束：取得游標座標資訊

