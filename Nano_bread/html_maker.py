import cv2
from bs4 import BeautifulSoup
from  common_fun import cv2_strbase64, generate_random_str
import json
from os import listdir
from os.path import isfile
import front_config

CUSTOMER_FILE = front_config.CUSTOMER_FILE

def html_camera_roi_inference_table_maker(data, percentage):
    """
    camera roi inference 回傳結果
    將每個攝影機表單依據回傳內容打印產品ID NAME 以及數量

    :param data:
    :return:
    """
    keys = data.keys()

    body = BeautifulSoup()
    for key in keys:
        url = "templates/cameraROIInferenceTable.html"
        soup_table = BeautifulSoup(open(url), 'html.parser')
        dom_body = soup_table.find("div", class_="ans")
        dom_body["data-camkey"] = key
        dom_body = soup_table.find("p", class_="product_id")
        dom_body.string = key
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
    img_path = 'static/A.png'
    img = cv2.imread(img_path)
    img_src = cv2_strbase64(img)

    coordinates = []
    body = BeautifulSoup()
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
    images  = []
    alllist = listdir(CUSTOMER_FILE + str(customername)+'/'+str(productId))
    for file in alllist:
        data_type = file.split(".")[-1]
        if data_type == "jpg":
            file_name = file.split(".")[0]
            if file_name != 'title':
                images.append(file)
    images_length = len(images)
    data_url = CUSTOMER_FILE + str(customername)+'/'+str(productId) + '/data.data'
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
        table_body["data-path"] = image_path
        table_body["data-id"] = id
        table_body = soup_body.find("input")
        # table_body["id"] = "inputSelect%s" + id
        # table_body = soup_body.find("label")
        table_body["for"] = "inputSelect%s" + id
        table_body["data-id"] = id
        img_ul.append(soup_body)

    output = soup_table.prettify()

    return output


def html_customer_productMaker(customername, this_list):
    """
    :param customername:
    :param this_list:
    :return:
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
        with open(data_url) as json_file:
            flag = i + 1
            img_url = "customer/"+customername+"/"+name+"/title.jpg"
            img = cv2.imread(img_url)
            img_base64 = cv2_strbase64(img)
            data = json.load(json_file)
            bodys = soup_body.find_all('th')
            newtag = soup.new_tag(name="input", type="checkbox", id="checkbox_" + str(flag))
            bodys[0].append(newtag)
            bodys[1].string = data["product_id"]
            bodys[1]["id"]  = "pdid_"+str(flag)
            newtag = soup.new_tag(name="img", src=img_base64, height="70")
            bodys[2].append(newtag)
            bodys[3].string = data["product_name"]
            bodys[4].string = data["memo"]
            bodys[5].string = data["image_count"]
            if data["ON"] == "1":
                bodys[6].string = "ON"
            else:
                bodys[6].string = "OFF"
            newtag = soup.new_tag(name="button",
                                  attrs={"class": "btn btn-outline-danger",
                                         "type": "button",
                                         "data-productID": data["product_id"],
                                         "onclick": "showCustomerEditProduct(this)",
                                         "id": "button_%i_1" % flag})
            newtag.string = "編輯"
            bodys[7].append(newtag)
            newtag = soup.new_tag(name="button",
                                  attrs={"class": "btn btn-outline-danger",
                                         "type": "button",
                                         "data-productID": data["product_id"],
                                         "onclick": "showCustomerProductsImage(this)",
                                         "id": "button_%i_2" % flag})
            newtag.string = "圖資"
            bodys[7].append(newtag)
            soup_table.tbody.append(soup_body)
    output = soup_table.prettify()
    return output


def html_camera_maker(dic_data):
    keys = dic_data.keys()
    if len(keys) == 0:
        return {"html": "", "status": 0}

    coordinates = []

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
    while(True):
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
    return {"html": html, "status": 1, "id":key}