from flask import Flask, request, render_template, request, jsonify, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# import yolov4_app_1_4
import json
import numpy as np
from os import listdir, getcwd, chdir, rename, remove
from os.path import isdir, isfile, getctime
import cv2
import base64
import random
import string
from bs4 import BeautifulSoup

PREBASE64 = "data:image/jpeg;base64,"
USERFILE  = 'root'
CUSTOMER_FILE = "customer/"




app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)



@app.route('/bread/query/category/v1', methods=['POST'])
def category():
    if request.method == 'POST':
        data = request.json
        b64 = data['values']['b64string']
        name = data['values']['name']
        if data['function'] == 'category':
            image = yolov4_app_1_4.isimage(b64)
            if image:
                result = yolov4_app_1_4.inference(b64, 1)
                result_data = result['data']
                if len(result_data) != 1:
                    rtn_data = {
                        "rtn": 405,
                    }
                else:
                    rtn_data = {
                        "rtn": 200,
                        "name": result_data[0],
                        "id": result_data[1]
                    }
                return rtn_data
            else:
                rtn_data = {
                    "rtn": 500,
                }
                return rtn_data
    else:
        rtn_data = {
            "rtn": 404
        }
        return rtn_data


@app.route('/bread/query/quantity/v1', methods=['POST'])
def quantity():
    if request.method == 'POST':
        data = request.json
        b64 = data['values']['b64string']
        if data['function'] == 'quantity':
            image = yolov4_app_1_4.isimage(b64)
            if image:
                result = yolov4_app_1_4.inference(b64, 1)
                result_data = result['data']
                rtn_data = {
                    "rtn": 200,
                    "rtn_values": result_data
                }
                return rtn_data
            else:
                rtn_data = {
                    "rtn": 500,
                }
                return rtn_data
    else:
        rtn_data = {
            "rtn": 404
        }
        return rtn_data


@app.route('/bread/query/position/v1', methods=['POST'])
def position():
    if request.method == 'POST':
        data = request.json
        if data['function'] == 'position':
            b64 = data['values']['b64string']
            image = yolov4_app_1_4.isimage(b64)
            if image:
                result = yolov4_app_1_4.inference(b64, 3)
                result_data = result['data']
                rtn_data = {
                    "rtn": 200,
                    "b64string": result['b64string'],
                    "rtn_values": result_data
                }
                return json.dumps(rtn_data)
            else:
                rtn_data = {
                    "rtn": 500,
                }
                return rtn_data
    else:
        rtn_data = {
            "rtn": 404
        }
        return rtn_data


@app.route('/bread/query/confidence/v1', methods=['POST'])
def confidence():
    if request.method == 'POST':
        data = request.json
        if data['function'] == 'confidence':
            b64 = data['values']['b64string']
            image = yolov4_app_1_4.isimage(b64)
            if image:
                result = yolov4_app_1_4.inference(b64, 4)
                result_data = result['data']
                rtn_data = {
                    "rtn": 200,
                    "b64string": result['b64string'],
                    "rtn_values": result_data
                }
                return rtn_data
            else:
                rtn_data = {
                    "rtn": 500,
                }
                return rtn_data
    else:
        rtn_data = {
            "rtn": 404
        }
        return rtn_data



@app.route('/')
def first_page():
    """
    頁面最初的頁面
    :return:
    """
    return render_template('first_page.html')

@app.route('/recognitionPage', methods=['GET'])
def recognitionpage():
    """
    回傳辨識HTML
    :return:
    """
    imga = cv2.imread('static/A.png')
    basea = cv2_strbase64(imga)
    return render_template('recognition.html', basea=basea)


@app.route('/customer_productData')
def customer_productData():
    username = USERFILE
    alllist = listdir(CUSTOMER_FILE+str(username))
    html = html_customer_productMaker(username, alllist)
    return html

@app.route('/customer_editProductData', methods=['POST'])
def customer_editProductData():
    username = USERFILE
    data = request.get_json()
    product_id = data["product_id"]
    # print("os path :", getcwd())
    html = html_editcustomer_productMaker(username, product_id)
    return html

@app.route('/customer_add_product')
def customer_add_product():
    username = USERFILE
    html = html_add_customer_product_maker(username)
    return html

def html_add_customer_product_maker(customername):
    """
    產生客戶新增產品profile的html
    :param customername:
    :param productId:
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




def imgSrc2_cv2img(src):
    """
    去除圖片base64多餘前綴詞並轉化成OPENCV的IMG型態
    :param src:
    :return:
    """
    src = src.split(",")[1]
    img = base64toimg(src)
    return img


def base64toimg(string):
    """
    base64 to np type image

    :param string: base64 string
    :return: numpy image
    """
    erro  = True
    lens = len(string)
    lenx = lens - (lens % 4 if lens % 4 else 0)
    result = string[:lenx]
    try:
        base64encode = bytes(result, encoding="utf8")
        base64decode = base64.b64decode(base64encode)
        img_array = np.fromstring(base64decode, np.uint8)
        img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
        if img is None:
            return None
        else:
            return img
    except Exception as e:
        return None


def cv2_strbase64(image):
    base64_str = cv2.imencode('.jpg', image)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    output = PREBASE64+str(base64_str).split("'")[1]
    return output


def get_ipc(data):
    """
    透過opencv取得RTSP串流攝影機當下影像
    :param data: JSON格式 "ip": RTSP的IP
    :return:成功回傳JSON "ret":True , "base": 影像的base64
            失敗回傳JSON "ret":False
    """
    ip = data["ip"]
    try:
        cap = cv2.VideoCapture(ip)
        ret, image = cap.read()
        if ret:
            out_base = cv2_strbase64(image)
            # print("backend spend %f" % (end - start))
            return {"ret": ret, "base": out_base}
        # print("backend spend %f" % (end - start))
        return {"ret": ret}
    except Exception as e:
        return {"ret": False}

def generate_random_str(randomlength):
    '''
    string.digits = 0123456789
    string.ascii_letters = 26个小写,26个大写
    '''
    str_list = random.sample(string.digits + string.ascii_letters, randomlength)
    random_str = ''.join(str_list)
    return random_str

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
