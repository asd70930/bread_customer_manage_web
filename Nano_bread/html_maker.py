import cv2
from bs4 import BeautifulSoup
from  common_fun import cv2_strbase64, generate_random_str
import json
from os import listdir
from os.path import isfile
import front_config

CUSTOMER_FILE = front_config.CUSTOMER_FILE


def html_camera_roi_inference_table_maker(data, percentage, total):
    """
    camera roi inference 回傳結果
    將每個攝影機表單依據回傳內容打印產品ID NAME 以及數量
    :param data:
    :param percentage:
    :param total: type bool , is total table or not
    :return: html 交給JS渲染網頁
    """
    keys = data.keys()

    body = BeautifulSoup()
    for key in keys:
        url = "templates/cameraROIInferenceTable.html"
        soup_table = BeautifulSoup(open(url), 'html.parser')
        if total:
            dom_body = soup_table.find("div", class_="ans")
            dom_body["data-camkey"] = "total"
        else:
            dom_body = soup_table.find("div", class_="ans")
            dom_body["data-camkey"] = key

        dom_body = soup_table.find("p", class_="product_id")
        dom_body.string = "料號："+key
        dom_body = soup_table.find("p", class_="product_name")
        dom_body.string = data[key]["name"]
        dom_body = soup_table.find("div", class_="count")
        dom_body.string = "X"+str(data[key]["count"])
        body.append(soup_table)
    url = "templates/cameraROIPercentageTable.html"
    percentage_table = BeautifulSoup(open(url), 'html.parser')
    dom_body = percentage_table.find("p")

    dom_body.string = "佔比："+str(format(percentage*100, '.0f'))+' %'
    body.append(percentage_table)
    html = body.prettify()
    return html


def html_camera_roi_table_maker(data):
    """
    由camera.data所紀錄的camera資訊
    將其自動打印多個攝影欄位並付再cameraROI.html中
    :param data: camera.data開啟後以dic帶入
    :return:
    """
    keys = data.keys()
    # 初始img 使用 static/A.png 當圖片
    img_path = 'static/A.png'
    img = cv2.imread(img_path)
    img_src = cv2_strbase64(img)
    coordinates = []
    body = BeautifulSoup()

    # 由camera.data所紀錄的camera資訊
    # 將其自動打印多個攝影欄位並付再cameraROI.html中
    for key in keys:
        if not data[key]["hasFrame"]:
            continue
        if data[key]["painted"]:
            coordinates.append({"x1": data[key]["x1"], "x2": data[key]["x2"],
                                "x3": data[key]["x3"], "x4": data[key]["x4"],
                                "y1": data[key]["y1"], "y2": data[key]["y2"],
                                "y3": data[key]["y3"], "y4": data[key]["y4"],
                                "ip": data[key]["ip"], "key": key, "painted": data[key]["painted"],
                                "hasFrame": data[key]["hasFrame"],
                                "AnchorHeight": data[key]["AnchorHeight"], "AnchorWidth": data[key]["AnchorWidth"]})

        else:
            coordinates.append({"ip": data[key]["ip"], "key": key, "painted": data[key]["painted"],
                                "hasFrame": data[key]["hasFrame"],
                                "AnchorHeight": data[key]["AnchorHeight"], "AnchorWidth": data[key]["AnchorWidth"]})
        url = "templates/cameraROITable.html"
        soup_table = BeautifulSoup(open(url), 'html.parser')
        dom_body = soup_table.find("input")
        dom_body["value"] = data[key]["ip"]
        dom_body["data-camkey"] = key
        dom_body = soup_table.find("canvas")
        dom_body["data-camkey"] = key
        dom_body = soup_table.find("img")
        dom_body["src"] = img_src
        dom_body["data-camkey"] = key
        dom_body = soup_table.find("div", class_="roi_table")
        dom_body["data-camkey"] = key
        body.append(soup_table)
    html = body.prettify()
    return {"html": html, "data": coordinates}


def html_add_customer_product_maker():
    """
    產生客戶新增產品profile的html
    :return:
    """
    url = "templates/editProductProfile.html"
    soup_table = BeautifulSoup(open(url), 'html.parser')
    img_path = 'static/A.png'
    img = cv2.imread(img_path)
    img_src = cv2_strbase64(img)
    dom_body = soup_table.find(id="blsh1")
    dom_body["src"] = img_src

    output = soup_table.prettify()
    return output


def html_editcustomer_productMaker(customername, productId):
    """
    產生客戶編輯產品profile的html
    :param customername:
    :param productId:
    :return:
    """
    url = "templates/editProductProfile.html"
    soup_table = BeautifulSoup(open(url), 'html.parser')
    with open('customer/' + customername + '/' + productId + '/data.data') as json_file:
        data = json.load(json_file)
        img_path = 'customer/' + customername + '/' + productId + '/title.jpg'
        img = cv2.imread(img_path)
        img_src = cv2_strbase64(img)
        dom_body = soup_table.find(id="blsh1")
        dom_body["src"] = img_src
        dom_body = soup_table.find(id="pre_barcode_error")
        dom_body["value"] = data["product_id"]
        dom_body = soup_table.find(id="barcode_error")
        dom_body["value"] = data["product_id"]
        dom_body = soup_table.find(id="product_name_error")
        dom_body["value"] = data["product_name"]
        dom_body = soup_table.find(id="remarks_error")
        dom_body["value"] = data["memo"]

    output = soup_table.prettify()
    return output


def html_customer_product_image_viewMaker(customername, productId):
    """
    動態產生客戶商品的所有商品圖片HTML交由JS渲染頁面
    :param customername: 此專案都預設為ROOT 沒有其他使用者
    :param productId: 產品的ID
    :return: html: 動態產生的HTML
    """
    images = []
    alllist = listdir(CUSTOMER_FILE + str(customername)+'/'+str(productId))
    for file in alllist:
        data_type = file.split(".")[-1]
        if data_type == "jpg":
            file_name = file.split(".")[0]
            if file_name != 'title':
                images.append(file)
    images_length = len(images)
    data_url = CUSTOMER_FILE + str(customername)+'/'+str(productId) + '/data.data'
    # 開始動態產生HTML
    with open(data_url) as json_file:
        data = json.load(json_file)
        product_name = data["product_name"]
    url = "templates/customerProductImages.html"
    soup_table = BeautifulSoup(open(url), 'html.parser')
    body = soup_table.findAll("button")[2]
    body["data-productID"] = productId
    body = soup_table.find("button", attrs={"data-toggle": "modal"})
    body["data-productID"] = productId
    body["data-imageCount"] = images_length
    body = soup_table.find("h4")
    body["data-id"] = productId
    body.string = "商品名稱: %s , 總圖資數: %s" % (str(product_name), str(images_length))
    img_ul = soup_table.find(class_="images-list")
    for image_path in images:
        id = image_path.split(".")[0].split("_")[-1]
        img = cv2.imread("customer/"+customername+"/"+productId+"/"+image_path)
        img_src = cv2_strbase64(img)
        url = "templates/customerProductImagetable.html"
        soup_body = BeautifulSoup(open(url), 'html.parser')
        table_body = soup_body.find("input")
        table_body["data-art5"] = "input"
        table_body["data-path"] = image_path
        table_body = soup_body.find("img")
        table_body["src"] = img_src
        table_body["onclick"] = "checkedInputBox(this)"
        table_body["data-path"] = image_path
        table_body["data-id"] = id
        table_body = soup_body.find("input")
        table_body["for"] = "inputSelect%s" + id
        table_body["data-id"] = id
        img_ul.append(soup_body)
    html = soup_table.prettify()
    return html


def html_customer_productMaker(customername, this_list):
    """
    取得客戶所有商品明細並動態產生html回傳至前端顯示
    :param customername: 此專案都預設為ROOT 沒有其他使用者
    :param this_list: 將/customer/root/搜索有多少資料夾，表示有多少商品 , type = list
    :return: html (type = str), html 交給JS渲染網頁
    """
    url = "templates/customerProductTable.html"
    soup_table = BeautifulSoup(open(url), 'html.parser')
    soup = BeautifulSoup()

    for i, name in enumerate(this_list):
        if isfile("customer/"+customername+"/"+name):
            continue
        data_url = "customer/"+customername+"/"+name+"/data.data"
        url = "templates/tr_tlp.html"
        soup_body = BeautifulSoup(open(url), 'html.parser')

        # 開始動態產生HTML
        with open(data_url) as json_file:
            # 依照開會內容將商品清單的順序改為
            # 品名> 料號 > 商品圖片
            flag = i + 1
            img_url = "customer/"+customername+"/"+name+"/title.jpg"
            img = cv2.imread(img_url)
            img_base64 = cv2_strbase64(img)
            data = json.load(json_file)
            bodys = soup_body.find_all('th')
            newtag = soup.new_tag(name="input", type="checkbox", id="checkbox_" + str(flag))
            newtag["data-pdkey"] = data["product_id"]
            bodys[0].append(newtag)
            # 料號
            bodys[2].string = data["product_id"]
            bodys[2]["id"]  = "pdid_"+str(flag)
            # 商品圖片
            newtag = soup.new_tag(name="img", src=img_base64, height="70")
            bodys[3].append(newtag)
            # 品名
            bodys[1].string = data["product_name"]
            bodys[4].string = data["memo"]
            bodys[5].string = data["image_count"]
            new_button = soup.new_tag(name="button",
                                      attrs={"class": "btn btn-success customize-btn f-20 mx-3",
                                             "onclick": "showCustomerEditProduct(this)",
                                             "data-productID": data["product_id"],
                                             "type": "button"
                                             })

            new_svg = soup.new_tag(name="svg",
                                   attrs={"xmlns": "http://www.w3.org/2000/svg",
                                          "fill": "currentColor",
                                          "class": "svg-size bi bi-files",
                                          "viewBox": "0 0 16 16"
                                          })
            new_path = soup.new_tag(name="path",
                                    attrs={"d": "M3 4.5a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5zM11.5 4a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1zm0 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1zm0 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1zm0 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1zm0 2a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1z"})
            new_path2 = soup.new_tag(name="path",
                                    attrs={"d": "M2.354.646a.5.5 0 0 0-.801.13l-.5 1A.5.5 0 0 0 1 2v13H.5a.5.5 0 0 0 0 1h15a.5.5 0 0 0 0-1H15V2a.5.5 0 0 0-.053-.224l-.5-1a.5.5 0 0 0-.8-.13L13 1.293l-.646-.647a.5.5 0 0 0-.708 0L11 1.293l-.646-.647a.5.5 0 0 0-.708 0L9 1.293 8.354.646a.5.5 0 0 0-.708 0L7 1.293 6.354.646a.5.5 0 0 0-.708 0L5 1.293 4.354.646a.5.5 0 0 0-.708 0L3 1.293 2.354.646zm-.217 1.198l.51.51a.5.5 0 0 0 .707 0L4 1.707l.646.647a.5.5 0 0 0 .708 0L6 1.707l.646.647a.5.5 0 0 0 .708 0L8 1.707l.646.647a.5.5 0 0 0 .708 0L10 1.707l.646.647a.5.5 0 0 0 .708 0L12 1.707l.646.647a.5.5 0 0 0 .708 0l.509-.51.137.274V15H2V2.118l.137-.274z"})
            new_span = soup.new_tag(name="sapn",
                                    attrs={"class": "block-bottom"})
            new_span.string = "編輯"
            new_svg.append(new_path)
            new_svg.append(new_path2)
            new_button.append(new_svg)
            new_button.append(new_span)
            bodys[6].append(new_button)
            new_button = soup.new_tag(name="button",
                                      attrs={"class": "btn btn-success customize-btn f-20 mx-3",
                                             "onclick": "showCustomerProductsImage(this)",
                                             "data-productID": data["product_id"],
                                             "type": "button"
                                             })
            new_svg = soup.new_tag(name="svg",
                                   attrs={"xmlns": "http://www.w3.org/2000/svg",
                                          "fill": "currentColor",
                                          "class": "svg-size bi bi-files",
                                          "viewBox": "0 0 16 16"
                                          })
            new_path = soup.new_tag(name="path",
                                    attrs={
                                        "d": "M13 0H6a2 2 0 0 0-2 2 2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2 2 2 0 0 0 2-2V2a2 2 0 0 0-2-2zm0 13V4a2 2 0 0 0-2-2H5a1 1 0 0 1 1-1h7a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1zM3 4a1 1 0 0 1 1-1h7a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4z"})
            new_span = soup.new_tag(name="sapn",
                                    attrs={"class": "block-bottom"})
            new_span.string = "圖資"
            new_svg.append(new_path)
            new_button.append(new_svg)
            new_button.append(new_span)
            bodys[6].append(new_button)
            soup_table.tbody.append(soup_body)
    html = soup_table.prettify()
    return html


def html_camera_maker(dic_data):
    """
    根據camera.data的資料動態產生HTML頁面後回傳至前端
    :param dic_data: camera.data 讀取資料 as dict type
    :return: {
        "html": str,
        "camData": list,
        "status": int
    }
        html = 動態產生HTML頁面後回傳至前端直接貼上
        camData = 保存攝影機ROI四角座標交給前端渲染網頁
        status = 狀態碼 1表示正常 0表示客戶尚未儲存任何攝影機資料
    """
    keys = dic_data.keys()
    if len(keys) == 0:
        return {"html": "", "status": 0}
    coordinates = []
    # 開始動態產生HTML
    soup = BeautifulSoup()
    for key in keys:
        url = "templates/roiRecognitionTable.html"
        soup_table = BeautifulSoup(open(url), 'html.parser')
        table_body = soup_table.find("input")
        table_body["value"] = dic_data[key]["ip"]
        table_body["data-camkey"] = key
        buttons = soup_table.find_all("button")
        for table_body in buttons:
            table_body["data-camkey"] = key
        table_body = soup_table.find("img")
        table_body["data-camkey"] = key
        if "img_base64" in dic_data[key]:
            if dic_data[key]["img_base64"] != "":
                table_body["src"] = dic_data[key]["img_base64"]
        table_body = soup_table.find("canvas")
        table_body["data-camkey"] = key
        table_body = soup_table.find("div", class_="camera_table")
        table_body["data-camkey"] = key
        table_body = soup_table.find("hr")
        table_body["data-camkey"] = key
        soup.append(soup_table)
        coordinates.append([key, dic_data[key]])
    html = soup.prettify()
    return {"html": html, "status": 1, "camData": coordinates}


def html_camera_create_maker(dic_data):
    """
    產新新的不重複KEY並動態產生HTML頁面後回傳至前端
    :param dic_data: camera.data 讀取資料 as dict type
    :return:{
        "html": str,
        "camData": list,
        "status": int
    }
        html = 動態產生HTML頁面後回傳至前端直接貼上
        id = 不重複KEY
        status = 狀態碼 1表示正常 0表示客戶尚未儲存任何攝影機資料
    """
    while True:
        key = generate_random_str(4)
        if key not in dic_data:
            break
    url = "templates/roiRecognitionTable.html"
    soup_table = BeautifulSoup(open(url), 'html.parser')
    table_body = soup_table.find("input")
    table_body["value"] = ""
    table_body["data-camkey"] = key
    buttons = soup_table.find_all("button")
    for table_body in buttons:
        table_body["data-camkey"] = key
    table_body = soup_table.find("img")
    table_body["data-camkey"] = key
    table_body = soup_table.find("canvas")
    table_body["data-camkey"] = key
    table_body = soup_table.find("div", class_="camera_table")
    table_body["data-camkey"] = key
    table_body = soup_table.find("hr")
    table_body["data-camkey"] = key
    html = soup_table.prettify()
    return {"html": html, "status": 1, "id": key}
