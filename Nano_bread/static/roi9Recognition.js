var classDict = {}; // key is string as "1", "2"

$(document).ready(function() {
    $.ajax({
    url:"/recognitionPage/roi9Recognition/makeTable",
    method: "post",
    contentType: "application/json;charset=UTF-8",
    dataType:"html",
    beforeSend: function (xhr) {
        var value = 'Bearer '+localStorage.getItem("myJWT")
        xhr.setRequestHeader('Authorization', value);
    },
    data:{},
    success: function (html) {
        $("#table").html(html);
        init();

    },
    error: function (xhr,status,error) {
            errorBackToLogIn(xhr);
    },
    });
});

function mouseXY(obj,e){
    var id = getNum(obj.id)
    var canvas = classDict[id]
    x = e.offsetX;
    y = e.offsetY;
    canvas.set_mouseX(x)
    canvas.set_mouseY(y)


}

function cleanBTCanvas(obj){
    var id = getNum(obj.id)
    var oriId = "#canva"+id
    var canvas = classDict[id]
    canvas.set_isPainted(false);
    canvas.xyListClean();
    canvas.cleanClickFlag();
    canva = $(oriId)[0] ;
    canva.width = canva.width;
}

function drawCanvas(obj){
    var oriId = "#"+obj.id
    // id is the number of canvas
    var id = getNum(obj.id)
    var canvas = classDict[id]

    if (canvas.get_isPainted()){
        return;
    }

    x = canvas.get_mouseX(x)
    y = canvas.get_mouseY(y)
    canvas.addClickFlag()  // flag += 1

    canvas.xyListAppend([x,y])
    flag = canvas.get_clickFlag()


    canva = $(oriId)[0] // get canvas DOM , only use in once time
    ctx = canva.getContext('2d');

    if (flag ==4){
        ctx.strokeStyle = "rgb(255,0,0)"; // Red line
        clean(ctx,canvas);
        drawLine(ctx,canvas);
        canvas.xyListClean();
        canvas.set_isPainted(true);
    }
    else{
        ctx.fillRect(x, y, 1, 1);
    }
}

function drawLine(ctx,canvas){
    thisflag = 0;
    dataList = canvas.get_xyList();
    for (data of dataList){
        x = data[0];
        y = data[1];
        if (thisflag ==0){
            thisflag+=1;
            ctx.moveTo(x,y);
        }
        else{
             ctx.lineTo(x,y);
        }
    }
    ctx.lineTo(dataList[0][0],dataList[0][1]);
    ctx.closePath();
    ctx.stroke();
}

function clean(ctx,canvas){
    canvas.cleanClickFlag()
    dataList = canvas.get_xyList();
    for (data of dataList){
        x = data[0];
        y = data[1];
        ctx.clearRect(x, y, 1, 1);
    }
}



function getAllCameraAjax(dictLength){
    var deferreds = [];

    for (i=1;i<=dictLength;i++){
        let dictId = i.toString();
        let canvas = classDict[dictId]
        let img = $("#blsh"+dictId)
        ip = $("#ipInput"+dictId).val();
        var pay_load = {
            "ip": ip
        };

        deferreds.push(
        $.ajax({
            url:"/show_ipc",
            method: "post",
            contentType: "application/json;charset=UTF-8",
            dataType:"json",
            data:JSON.stringify(pay_load),
//            complete:function(){
//            },
//            success: function (data) {
//                var ret = data["ret"]
//                getCamera = ret
//                var base = data["base"]
////                $('#show_camera1').attr('disabled', false);
//                if (ret){
//                    img.attr('src', base);
//                }
//                else{
//                    let parentDiv = $('#cleanBT'+dictId).closest("div");
//                    failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                    parentDiv.append(failHtml);
//                }
//            },
//            error: function (xhr,status,error) {
//                let parentDiv = $('#cleanBT'+dictId).closest("div");
//                failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                parentDiv.append(failHtml);
//            },
        }));


    }
    return deferreds

//    for (i=1;i<=dictLength;i++){
//        let dictId = i.toString();
//        let canvas = classDict[dictId]
//        let img = $("#blsh"+dictId)
//        ip = $("#ipInput"+dictId).val();
//        var pay_load = {
//            "ip": ip
//        };
//        $.ajax({
//            url:"/show_ipc",
//            method: "post",
////            async:false,
//            contentType: "application/json;charset=UTF-8",
//            dataType:"json",
//            data:JSON.stringify(pay_load),
//            complete:function(){
//            },
//            success: function (data) {
//                var ret = data["ret"]
//                getCamera = ret
//                var base = data["base"]
////                $('#show_camera1').attr('disabled', false);
//                if (ret){
//                    img.attr('src', base);
//                }
//                else{
//                    let parentDiv = $('#cleanBT'+dictId).closest("div");
//                    failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                    parentDiv.append(failHtml);
//                }
//            },
//            error: function (xhr,status,error) {
//                let parentDiv = $('#cleanBT'+dictId).closest("div");
//                failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                parentDiv.append(failHtml);
//            },
//        });
//    }
}


function getAllCamera(){
    // almost 25s to get all camera
    let dictLength = Object.keys(classDict).length;
    $(".drop").remove();

// try way2
//    defs = getAllCameraAjax(dictLength);
//    $.when.apply($, defs).then.apply($.data)
//    (data) =>{
//        var ret = data["ret"]
//        getCamera = ret
//        var base = data["base"]
//    //                $('#show_camera1').attr('disabled', false);
//        if (ret){
//            img.attr('src', base);
//        }
//        else{
//            let parentDiv = $('#cleanBT'+dictId).closest("div");
//            failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//            parentDiv.append(failHtml);
//        }
//    },
//    err =>{
//        let parentDiv = $('#cleanBT'+dictId).closest("div");
//        failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//        parentDiv.append(failHtml);
//    }
//    );


// try way1
//    for (i=1;i<=dictLength;i++){
//        let dictId = i.toString();
//        let canvas = classDict[dictId]
//        let img = $("#blsh"+dictId)
//        ip = $("#ipInput"+dictId).val();
//        var pay_load = {
//            "ip": ip
//        };
//        $.ajax({
//            url:"/show_ipc",
//            method: "post",
//            contentType: "application/json;charset=UTF-8",
//            dataType:"json",
//            data:JSON.stringify(pay_load),
//            complete:function(){
//            },
//            success: function (data) {
//                var ret = data["ret"]
//                getCamera = ret
//                var base = data["base"]
////                $('#show_camera1').attr('disabled', false);
//                if (ret){
//                    img.attr('src', base);
//                }
//                else{
//                    let parentDiv = $('#cleanBT'+dictId).closest("div");
//                    failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                    parentDiv.append(failHtml);
//                }
//            },
//            error: function (xhr,status,error) {
//                let parentDiv = $('#cleanBT'+dictId).closest("div");
//                failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
//                parentDiv.append(failHtml);
//            },
//        });
//    }


// try way3
    for (i=1;i<=dictLength;i++){
        let dictId = i.toString();
        let canvas = classDict[dictId]
        let img = $("#blsh"+dictId)
        ip = $("#ipInput"+dictId).val();
        var pay_load = {
            "ip": ip
        };
        $.ajax({
            url:"/show_ipc",
            method: "post",
            contentType: "application/json;charset=UTF-8",
            dataType:"json",
            data:JSON.stringify(pay_load),
            complete:function(){
            },
        }).done(function(data){
            var ret = data["ret"]
            getCamera = ret
            var base = data["base"]
//                $('#show_camera1').attr('disabled', false);
            if (ret){
                img.attr('src', base);
            }
            else{
                let parentDiv = $('#cleanBT'+dictId).closest("div");
                failHtml = '<span class="badge badge-danger f-mid drop">無法取得攝影機影像</span>';
                parentDiv.append(failHtml);
            }
        });

    }

}

function inferenceAllImage(){


}

function getNum(text){
    // only get number
	var value = text.replace(/[^0-9]/ig,"");
	return value;
}


function errorBackToLogIn(xhr){
    if (xhr["status"]=="422" || xhr["status"]=="401" ){
            alert("Your Authorization is expired or invalid, please sign in again!");
            localStorage.clear();
            window.location.href='/';
       }
}

function init(){
    var a = $("[id^='cleanBT']");
    for (i=1;i<=a.length;i++){
        number = i.toString();
        canvas = new myCanvas(number)
        classDict[number] = canvas;
    }
    var xxx= 111;
}

class myCanvas{
    constructor(id){
        this.number = id; //string
        this.isPainted = false;
        this.xyList = [];
        this.orgImageWidth = 0;
        this.orgImageHeight = 0;
        this.AnchorWidth = 0;
        this.AnchorHeight = 0;
        this.clickFlag = 0;
        this.mouseX = 0;
        this.mouseY = 0;
    }

    get_mouseX(){
        return this.mouseX;
    }

    set_mouseX(x){
        this.mouseX = x;
    }

    get_mouseY(){
        return this.mouseY;
    }

    set_mouseY(y){
        this.mouseY = y;
    }

    get_clickFlag(){
        return this.clickFlag;
    }

    addClickFlag(){
        this.clickFlag += 1;
    }

    cleanClickFlag(){
        this.clickFlag = 0;
    }

    get_AnchorWidth(){
        return this.AnchorWidth;
    }

    set_AnchorWidth(anchor){
        this.AnchorWidth = anchor;
    }

    get_AnchorHeight(){
        return this.AnchorHeight;
    }

    set_AnchorHeight(anchor){
        this.AnchorHeight = anchor;
    }

    get_orgImageHeight(){
        return this.orgImageHeight;
    }

    set_orgImageHeight(height){
        this.orgImageHeight = height;
    }


    get_orgImageWidth(){
        return this.orgImageWidth;
    }

    set_orgImageWidth(width){
        this.orgImageWidth = width;
    }

    get_xyList(){
        return this.xyList.slice(0)
    }

    xyListClean(){
        this.xyList = [];
    }

    xyListAppend(list){
        this.xyList.push(list);
    }

    get_isPainted(){
        return this.isPainted;
    }

    set_isPainted(bool){
        this.isPainted = bool;
    }

    get_number(){
        return this.number;
    }

    set_number(n){
        this.number = n;
    }

}



