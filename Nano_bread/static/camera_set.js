var classDict = {}; // key is string as "1", "2"

$(document).ready(function() {
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
});


function testing(){
    var xxx = 1111;
}

function mouseXY(obj,e){
    var id = obj.getAttribute("data-camkey")
    var canvas = classDict[id]
    x = e.offsetX;
    y = e.offsetY;
    canvas.set_mouseX(x)
    canvas.set_mouseY(y)
}

function cleanBTCanvas(obj){
    var id = obj.getAttribute("data-camkey")
    var canvas = classDict[id]
    canvas.set_isPainted(false);
    canvas.xyListClean();
    canvas.cleanClickFlag();
    canva = $("canvas[data-camkey='"+id+"']")[0] ;
    canva.width = canva.width;
}

function drawCanvas(obj){
    // id is the number of canvas
    var id = obj.getAttribute("data-camkey")
    var canvas = classDict[id]
    if (canvas.get_isPainted()){
        return;
    }

    x = canvas.get_mouseX(x)
    y = canvas.get_mouseY(y)
    canvas.addClickFlag()  // flag += 1

    canvas.xyListAppend([x,y])
    flag = canvas.get_clickFlag()


    canva = $("canvas[data-camkey='"+id+"']")[0] ; // get canvas DOM , only use in once time
    ctx = canva.getContext('2d');

    if (flag ==4){
        ctx.strokeStyle = "rgb(255,0,0)"; // Red line
        clean(ctx,canvas);
        drawLine(ctx,canvas);
//        canvas.xyListClean();
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
    canvas.cleanClickFlag();
    dataList = canvas.get_xyList();
    for (data of dataList){
        x = data[0];
        y = data[1];
        ctx.clearRect(x, y, 1, 1);
    }
}

function getNum(text){
    // only get number
	var value = text.replace(/[^0-9]/ig,"");
	return value;
}

function saveCamera(){
    payload = {};
    for (key in classDict){
        sendData = {};
        ip = $("input[data-camkey='"+key+"']").val();
        sendData["ip"] = ip;
        painted = classDict[key].get_isPainted();
        hasFrame = classDict[key].get_hasFrame();
        if (painted){
            corList = classDict[key].get_xyList();
            sendData["painted"] = true;
            sendData["x1"] = corList[0][0];
            sendData["x2"] = corList[1][0];
            sendData["x3"] = corList[2][0];
            sendData["x4"] = corList[3][0];
            sendData["y1"] = corList[0][1];
            sendData["y2"] = corList[1][1];
            sendData["y3"] = corList[2][1];
            sendData["y4"] = corList[3][1];
        }
        else{
            sendData["painted"] = false;
        }

        if(hasFrame){
            AnchorHeight = classDict[key].get_AnchorHeight();
            AnchorWidth  = classDict[key].get_AnchorWidth();
            sendData["hasFrame"] = hasFrame;
            sendData["AnchorHeight"] = AnchorHeight;
            sendData["AnchorWidth"] = AnchorWidth;
        }
        else{
            sendData["hasFrame"] = hasFrame;
        }


        payload[key] = sendData;
    }

    $.ajax({
        url:"/camera_save",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(payload),
        success: function (data) {
            status = data["status"];
            if (status == 1 ){
                alert("儲存成功");
            }
            else{
                alert('try it later');
            }
        },
        error: function (xhr,status,error) {
            alert('try it later');
        },
    });

}

function getCameraFrame(obj){
    var id = obj.getAttribute("data-camkey");
    var ip = $("input[data-camkey='"+id+"']").val();
    var payload = {"ip":ip};
    $.ajax({
        url:"/show_ipc",
        method: "post",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        data:JSON.stringify(payload),
        success: function (data) {
            if(data["ret"]){
                $("img[data-camkey='"+id+"']").attr("src",data["base"]);
                classDict[id].set_hasFrame(true);

                var image = new Image();
                image.src = data["base"];
                image.onload = function() {
                    oriHeight = image.height;
                    oriWidth  = image.width;
                    var imageZoneHeight = $("img[data-camkey='"+id+"']")[0].clientHeight;
                    var imageZoneWidth  = $("img[data-camkey='"+id+"']")[0].clientWidth;
                    var AnchorWidth  = oriWidth/imageZoneWidth;
                    var AnchorHeight = oriHeight/imageZoneHeight;
                    classDict[id].set_AnchorHeight(AnchorHeight);
                    classDict[id].set_AnchorWidth(AnchorWidth);
                };
            }
            else{
                alert('try it later');
            }
        },
        error: function (xhr,status,error) {
                alert('try it later');
        },
    });

}

function deleteCameraTable(obj){
    var id = obj.getAttribute("data-camkey");
    delete classDict[id];
    $("div[data-camkey='"+id+"']").remove();
    $("hr[data-camkey='"+id+"']").remove();
}

function createNewCamera(){
    $.ajax({
        url:"/camera_create",
        method: "get",
        contentType: "application/json;charset=UTF-8",
        dataType:"json",
        success: function (data) {
            if (data["status"]==1){
                $("#table").append(data["html"]);
                number = data["id"];
                canvas = new myCanvas(number);
                classDict[number] = canvas;
            }
        },
        error: function (xhr,status,error) {
                alert('try it later');
        },
    });
}

function initCamera(data){
    classDict={};
    var dataLen = data.length;
    for (i=0;i<dataLen;i++){
        number = data[i][0];
        canvas = new myCanvas(number);

        var hasFrame = data[i][1]["hasFrame"];
        canvas.set_hasFrame(hasFrame);
        if (hasFrame){
            var AnchorHeight = data[i][1]["AnchorHeight"];
            var AnchorWidth  = data[i][1]["AnchorWidth"];
            canvas.set_AnchorHeight = AnchorHeight;
            canvas.set_AnchorWidth  = AnchorWidth;
        }

        var painted = data[i][1]["painted"];
        if (painted){
            canvas.initSetXYList(data[i][1]);
            canvas.set_isPainted(painted);
            canva = $("canvas[data-camkey='"+number+"']")[0] ; // get canvas DOM , only use in once time
            ctx = canva.getContext('2d');
            ctx.strokeStyle = "rgb(255,0,0)"; // Red line
            clean(ctx,canvas);
            drawLine(ctx,canvas);
        }
        classDict[number] = canvas;
    }
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
        this.hasFrame = false;
    }

    initSetXYList(data){
        this.xyList.length = 0;
        this.xyList.push([data["x1"],data["y1"]]);
        this.xyList.push([data["x2"],data["y2"]]);
        this.xyList.push([data["x3"],data["y3"]]);
        this.xyList.push([data["x4"],data["y4"]]);
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
        this.xyList.length = 0;
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

    get_hasFrame(){
        return this.hasFrame;
    }

    set_hasFrame(bool){
        this.hasFrame = bool;
    }

}



