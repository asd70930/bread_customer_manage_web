var classDict={};

$(document).ready(function() {
    classDict={};
    $.ajax({
    url:"/recognitionPage/pageChangeCameraROI/roiTable",
    method: "get",
    contentType: "application/json;charset=UTF-8",
    dataType:"json",
    success: function (data) {
        $("#table").append(data["html"]);
        cameraDatas = data["data"];
        for (cameraData of cameraDatas){
            initCamera(cameraData);
        }
    },
    error: function (xhr,status,error) {
            errorBackToLogIn(xhr);
    },
    });
});

function clean(){
    $(".ans").remove();
}

function cleanCanvas(id){
    canva = $("canvas[data-camkey='"+id+"']")[0];
    canva.width = canva.width;
}

function drawCanvas(roiList, color, id,AnchorWidth,AnchorHeight){
    var canva = $("canvas[data-camkey='"+id+"']")[0] ; // get canvas DOM , only use in once time
    var ctx = canva.getContext('2d');

    ctx.strokeStyle = color; // Red line
    drawLine(ctx, roiList,AnchorWidth,AnchorHeight);
}

function drawLine(ctx, roiList,AnchorWidth,AnchorHeight){
    thisflag = 0;
    dataList = roiList;
    if (!dataList){return "";}
    ctx.beginPath();
    for (data of dataList){
        var x = data[0]/AnchorWidth;
        var y = data[1]/AnchorHeight;
        if (x<0){x=1;}
        if (x>400){x=399;}
        if (y<0){y=1;}
        if (y>400){y=399;}

        if (thisflag ==0){
            thisflag+=1;
            ctx.moveTo(x,y);
        }
        else{
             ctx.lineTo(x,y);
        }
    }
    ctx.lineTo(dataList[0][0]/AnchorWidth,dataList[0][1]/AnchorHeight);
    ctx.closePath();
    ctx.stroke();
}


function get_rand_color(){
    var color = Math.floor(Math.random() * 16777216).toString(16);
    return '#000000'.slice(0, -color.length) + color;
}

function roiInference(){
    clean();
    var send_data = [];
    for(key in classDict){
        var ip = classDict[key].get_ip();
        var isPainted = classDict[key].get_isPainted();
        var AnchorWidth = classDict[key].get_AnchorWidth();
        var AnchorHeight = classDict[key].get_AnchorHeight();
        var dic_data = {"ip": ip, "painted":isPainted,"AnchorWidth":AnchorWidth,"AnchorHeight":AnchorHeight,
                        "key":key
                        }
        if (isPainted){
            var coordinate = classDict[key].get_xyList();
            dic_data["coordinate"] = coordinate;
        }
        send_data.push(dic_data)
    }

    $.ajax({
    url:"/recognitionPage/pageChangeCameraROI/roiInference",
    method: "post",
    data:JSON.stringify({"data":send_data}),
    contentType: "application/json;charset=UTF-8",
    dataType:"json",
    success: function (data) {
        // 將結果打印再對應的table上
        for (htmlDic of data["html"]){
            var key = htmlDic["key"];
            var html = htmlDic["html"];
            if (key != "total"){
                $("div[data-camkey='"+key+"']").append(html);
            }
            else{
                $("#total-table").append(html);
            }
        }

        //將畫面打印再對應的IMG, 把ROI一併畫上
        for (itemDic of data["items"]){
            var roi = itemDic["roi"];
            // id is camera id
            var id  = itemDic["id"];
            var imgBase64 = itemDic["b64string"];
            var AnchorHeight = itemDic["AnchorHeight"];
            var AnchorWidth = itemDic["AnchorWidth"];
            cleanCanvas(id);
            $("img[data-camkey='"+id+"']").attr("src",imgBase64);
            drawCanvas(roi,"rgb(255,0,0)", id,AnchorWidth,AnchorHeight);


            if(itemDic["item"].length>0){
                for (itemsDic of itemDic["item"])
                    var itemRoi = itemsDic["position"];
                    var color = get_rand_color();
                    // realId is object detection model id transfer to customer product id
                    var realId = itemsDic["real_id"];
                    drawCanvas(itemRoi, color, id,AnchorWidth,AnchorHeight);
    //                $("div[data-camkey='"+realId+"']").attr("style","border-style:solid;border-color:"+color+";");
                    $(".ans[data-camkey='"+realId+"']").attr("style","border-style:solid;border-color:"+color+";");
            }

        }

        $("div[data-camkey='total']").attr("style","border-style:solid;border-color:black;");
        var xx = 123;
    },
    error: function (xhr,status,error) {
            alert('try it later');
    },
    });
}

function initCamera(data){
    var number = data["key"];
    var ip = data["ip"];
    var isPainted = data["painted"];
    var hasFrame  = data["hasFrame"];
    var AnchorHeight = data["AnchorHeight"];
    var AnchorWidth  = data["AnchorWidth"];
    canvas = new myCanvas(number,ip);
    canvas.set_AnchorWidth(AnchorWidth);
    canvas.set_AnchorHeight(AnchorHeight);
    canvas.set_isPainted(isPainted);
    if(isPainted){canvas.initSetXYList(data);}
    classDict[number] = canvas;
}

function test(){
    var x = 1;
    var color = get_rand_color();
}


class myCanvas{
    constructor(id,ip){
        this.ip = ip;
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
        this.AnchorXYList = [];
    }

    initSetXYList(data){
        this.xyList.length = 0;
        this.xyList.push([data["x1"],data["y1"]]);
        this.xyList.push([data["x2"],data["y2"]]);
        this.xyList.push([data["x3"],data["y3"]]);
        this.xyList.push([data["x4"],data["y4"]]);
    }

    get_ip(){
        return this.ip;
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
        return this.xyList.slice(0);
    }

    get_AnchorXYList(){
        this.AnchorXYList = this.xyList.slice(0);
        this.AnchorXYList[0][0] = this.AnchorXYList[0][0]*this.AnchorWidth;
        this.AnchorXYList[1][0] = this.AnchorXYList[1][0]*this.AnchorWidth;
        this.AnchorXYList[2][0] = this.AnchorXYList[2][0]*this.AnchorWidth;
        this.AnchorXYList[3][0] = this.AnchorXYList[3][0]*this.AnchorWidth;
        this.AnchorXYList[0][1] = this.AnchorXYList[0][1]*this.AnchorHeight;
        this.AnchorXYList[1][1] = this.AnchorXYList[1][1]*this.AnchorHeight;
        this.AnchorXYList[2][1] = this.AnchorXYList[2][1]*this.AnchorHeight;
        this.AnchorXYList[3][1] = this.AnchorXYList[3][1]*this.AnchorHeight;
        return this.AnchorXYList;
    }

    sh_xyList(){
        var x = this.xyList.slice(0);
        return x;
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

}