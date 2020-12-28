from flask import Flask, request, render_template, request, jsonify, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# import yolov4_app_1_4
import json
from os import listdir, getcwd, chdir, rename, makedirs
from os.path import isdir, isfile
import cv2
import threading
import front_config
import requests
from common_fun import rewrite_title_image, init_image_json_data , get_json_data, init_json_file, overwrite_json_data,\
rewrite_json_data, rewrite_json_image_count, imgSrc2_cv2img, base64toimg, cv2_strbase64 , get_ipc, generate_random_str,\
create_lock_file, delete_lock_file, lockfile_sleep, save_customer_product_profile, random_product_id

from html_maker import html_add_customer_product_maker, html_editcustomer_productMaker,\
html_customer_product_image_viewMaker, html_customer_productMaker, html_camera_maker, html_camera_create_maker

TESTING_NOT_CONNET_JETSON_NANO =front_config.TESTING_NOT_CONNET_JETSON_NANO
CUSTOMER_FILE = front_config.CUSTOMER_FILE
USERFILE = front_config.USERFILE
TEST_JETSONNANO_IP = "127.0.0.1:5000/"
JETSONNANO_API_BASIC = '/bread/query/basic/v2'


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


@app.route('/show_ipc', methods=['POST'])
def showIpc():
    """
    前端發送AJAX請求秀出IPCAMERA的影像
    詳細察看 get_ipc()
    :return:成功回傳JSON "ret":True , "base": 影像的base64
            失敗回傳JSON "ret":False
    """
    if request.method == "POST":
        data = request.get_json()
        ans  = get_ipc(data)
        return ans
    return {"base": "error"}


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


@app.route('/infrence', methods=['POST'])
def Recognition_bread():
    """
    發送Post Request至Jetson nano上,API格式查詢gitlab 機器設備issues
    發送的url:http://192.168.101.201:5000/bread/query/position/v1
    data : JSON "b64string": 圖片的base64
    :return:
    """
    if request.method == "POST":
        username = USERFILE
        data = request.get_json()
        # for testing image shape
        # img = imgSrc2_cv2img(data["b64string"])
        # print(img.shape)
        send_data = [{"function": "basic",
                     "values": {
                        "id":0,
                        "b64string": data["b64string"]
                    }
        }]
        try:
            # for testing , fake API response
            # response_data = [{"rtn":200,
            #         "b64string":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gNzAK/9sAQwAKBwcIBwYKCAgICwoKCw4YEA4NDQ4dFRYRGCMfJSQiHyIhJis3LyYpNCkhIjBBMTQ5Oz4+PiUuRElDPEg3PT47/9sAQwEKCwsODQ4cEBAcOygiKDs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7/8AAEQgCWAMgAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A9looooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBaSiigAooooAKKKKACiiigAooooAWkoooAKKKKACiiigAooooAKKKKAFpKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACijNJmgBaKTNJuoAdRTd1JuoAfRTN1G6gB9FM3UbqAH0U3dRuoAdRSZozQAtFGaKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooozQAUUmaTdQA7NGaZuqN7iKP78qL/ALzAUATZo3VmT67p0Gd1yrEdlOazpvGFog/dxlvqwFK6Hys6PdSbq4m68aSuCsOyL6cn9aypfE91KGEl/MfZcD+VLmK5GekNKifedV+pxVSbWLCEHfdIcdlO7+VeZTa1HwZJ3JP949f1qtJqMUo4lI+j0uZj5D0eXxZYR/dWV/cLVKfxooOIbXPuzV5810OQJevqcVC13ITjk+4oux8qO5k8b3P3RHEp9lJ/rVV/Gt+GxvUf8ArjXmMgIY4HrmoDdCJsGTgDu1Go7I7b/hNr8nAlT8hUi+NL9cFnT8UFcE93A4VS2W69alW5WFP9ZjH8JNILI79PG90Rkxxkf7p/xq3D43XH722B9SjY/nXmY1JfvK3zehbFSJqULHBlIbvzRdhyo9Xg8XabKQHZ4if7w/wrWgvre5UGGZHz6GvGUv2OGjkU4OMMM1YGrzRSgiQwledwp8zE4LoeyhqcGrzfTfHFxAwSdhOnqx5/Ouu0zxFY6kAI5Qkn9xj1+nrTUkyHFo2807NQB6eGqiSXNFMBpwNAC0UZooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiijNABRSZozQAtGabuqOSeOIZkkVB/tHFAEuaTNY9z4l063yBIZSOyCse68a7c+RFGo9WbJpXRSizry1VJ9UsrbiW5jB9Acn8hXnt94qurjIeckegOBWRNq5P8AHj2zS5ilA9In8WadEDtZ3PsMVk3XjOVsi3VEHqeTXBSaipBMj4HtwaqyasgbbHuYnoSeKV2Vyo6668SXsp2tcStn+4Dis+a7lcHdIfU7ga5iXV5Ovm7T2G41BJqEx481/wA8Uh2OieQs+FuEHsQR/OopJXXH79M/7+B/Ouc855GK7jk92c4ppGxiyhWz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gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAWkNFFADCKYy5qUimkUAV3SoHjq6VqNkoAz3iqB4fatJo6iaL2oGZjQ+1RmH2rTaGmGH2pAZhh9qaYfatIw+1NMPtQBneT7Unk+1aPke1J5HtQBn+T7UeT7VoeR7Uvke1AGf5PtThD7Ve8j2p3k+1AFAQ+1OEHtV4Q04Q+1AFEQe1OEHtV4Q+1KIaAKQg9qeIPargi9qcIvamBTEPtTxD7VbEXtTxFQBUEPtTxDVoR04R+1AisIvaniL2qwI6UJQBAIqcI6n2Uu2gCER08JUm2nbaAIglOC0/FLigBm2nbadiigBMUYpaKADFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABSYpaKAGkU0ipKTFAERSmFKnIpNtAFcx0wx1aK0m2gCoYqTyvareyk2UAVPK9qPK9qteXR5dAFXyvajyqtbKPLoAreV7UeVVrZRsoArCKneXVjZRsoAgEdL5ftU+2l20AQiP2pRHU22jbQBEEpwSpNtLigCMLS7afilxQAzbS7adRQAmKMUtFABiiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoxRRQAYpMUtFACbaTbTqKAG7aNtOooAbto206igBu2l20tFACbaMUtFACYpcUUUAGKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBaSiigAooooAKKKKACiiigAooooAWkoooAKKKKACiiigAooooAKKKKAFpKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigApaSigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/2Q==",
            #         "rtn_values":[
            #             [[0, 0, 200, 200], "4", "Taro"],
            #             [[200, 200, 200, 200], "4", "Taro"],
            #             [[500, 500, 50, 60], "5", "Bun"],
            #             [[400, 400, 100, 100], "5", "Bun"],
            #         ]
            #         }]
            response_data = {
                    "rtn": 200,
                    "items": [{"id": 0,
                               "item": {
                                        "num":0,
                                        "position": [200, 200, 200, 200],
                                        "confidence":0.8,
                                        "real_id": 1,
                                        "name": "Taro"
                                      }
                              }
                              ]
            }

            if not TESTING_NOT_CONNET_JETSON_NANO:
                ans = requests.post(TEST_JETSONNANO_IP+JETSONNANO_API_BASIC, json=send_data)
                response_data = ans.json()

            recognition_json_path = CUSTOMER_FILE + username + '/recognition.data'
            data_lock = CUSTOMER_FILE + username + '/recognition_datalock'

            # if data lock exited , sleep a little time
            while isfile(data_lock):
                lockfile_sleep(data_lock)

            # create data lock file
            create_lock_file(data_lock)

            recognition_dict = get_json_data(recognition_json_path)
            # delete data lock file
            delete_lock_file(data_lock)

            prepare_data = []
            for index, data_item in enumerate(response_data["items"]):
                # model_id is response yolo model output
                model_id = data_item["item"]["real_id"] #########
                max_id = ''
                if model_id in recognition_dict:
                    max_count = 0
                    for key in recognition_dict[model_id].keys():
                        if recognition_dict[model_id][key] > max_count:
                            max_count = recognition_dict[model_id][key]
                            max_id = key
                if max_id == '':
                    max_id = random_product_id(username)

                data_lock = CUSTOMER_FILE+username+'/'+max_id+'/datalock'
                # create data lock file
                create_lock_file(data_lock)
                data_json = get_json_data(CUSTOMER_FILE+username+'/'+max_id+'/data.data')
                # delete data lock file
                delete_lock_file(data_lock)
                data_name = data_json["product_name"]
                prepare_data.append([max_id, data_name])

            for i, datas in enumerate(prepare_data):
                response_data["items"][i]["item"]["real_id"] = datas[0]
                response_data["items"][i]["item"]["name"] = datas[1]

            return response_data
        except Exception as e:
            print(e)
            return {"rtn": 400}
    else:
        return {"rtn": 400, "message": "Error, pls using post"}


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


@app.route('/customer_saveProductData', methods=['POST'])
def customer_saveProductData():
    username = USERFILE
    data = request.get_json()
    path = "customer/"+USERFILE+"/"
    save_customer_product_profile(data, path)
    alllist = listdir(CUSTOMER_FILE+str(username))
    html = html_customer_productMaker(username, alllist)
    return html


@app.route('/customer_add_product', methods=['GET'])
def customer_add_product():
    html = html_add_customer_product_maker()
    return html


@app.route('/reveal_customer_productdataimg', methods=['POST'])
def reveal_customer_productdataimg():
    if request.method == "POST":
        username = USERFILE
        data = request.get_json()
        product_id = data["product_id"]

        html = html_customer_product_image_viewMaker(username, product_id)
        return html

    else:
        return {"message": "post only"}


@app.route('/save_product_image', methods=['POST'])
def save_product_image():
    """

    """

    if request.method == "POST":
        username = USERFILE
        data = request.get_json()
        # print("got data")
        img_src = data["base64"]
        flag = data["flag"]
        product_id = str(data["product_id"])
        data_lock = CUSTOMER_FILE+username+'/'+product_id+'/datalock'
        # if data lock exited , sleep a little time
        while isfile(data_lock):
            lockfile_sleep(data_lock)

        # create data lock file
        with open(data_lock, 'w') as lock:
            pass

        # save image
        path = CUSTOMER_FILE+username+'/'+product_id
        files = listdir(path)
        # final_number = '1'
        image_count = 0

        # check out file image number to decide savefile name
        for i, file in enumerate(files):
            data_type = file.split(".")[-1]
            if data_type == "jpg" and file.split(".")[0].split("_")[-1] != 'title':
                image_count += 1
                # final_number = str(int(file.split(".")[0].split("_")[-1])+1)
        save_data_name = generate_random_str(25)+'.jpg'
        try:
            img = imgSrc2_cv2img(img_src)
            cv2.imwrite(path+'/'+save_data_name, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        except Exception as e:
            delete_lock_file(data_lock)
            return {"message": "image save error"}

        # overwrite data.data
        json_file_path = path+'/'+'data.data'
        image_count += 1
        rewrite_json_image_count(json_file_path, str(image_count))
        delete_lock_file(data_lock)

        ###
        # save json data to debug
        # debug_file_path = generate_random_str(10)+'.txt'
        # overwrite_json_data(debug_file_path, data)
        ###

        # send request to jetson nano
        if flag == 0:
            t = threading.Thread(target=jetson_nano_request,
                                 args=(product_id, username, save_data_name,
                                       img_src, TEST_JETSONNANO_IP, JETSONNANO_API_BASIC))
            t.start()

        return {"message": "done"}

    return {"message": "error"}


@app.route('/camera_set', methods=['GET'])
def camera_set():
    """

    """

    if request.method == "GET":
        data_path = 'customer/root/camera.data'
        if not isfile(data_path):
            init_json_file(data_path)
        dic_data = get_json_data(data_path)

        ans = html_camera_maker(dic_data)
        return ans
    return {"message": "error"}


@app.route('/camera_create', methods=['GET'])
def camera_create():
    """

    """
    if request.method == "GET":

        data_path = 'customer/root/camera.data'
        dic_data = get_json_data(data_path)
        ans = html_camera_create_maker(dic_data)
        return ans

    return {"status": 0}


@app.route('/camera_save', methods=['POST'])
def camera_save():
    """

    """
    if request.method == "POST":
        data = request.get_json()
        data_path = 'customer/root/camera.data'
        overwrite_json_data(data_path, data)

        return {"status": 1}

    return {"status": 0}



def jetson_nano_request(product_id, username, image_name, image_src, ip, function):
    send_data = {"companyName": "Ezchain",
                 "function": "position",
                 "values": {
                     "b64string": image_src
                 }}
    try:
        # for testing , fake API response
        ans = {"rtn":200,
                "b64string":"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gNzAK/9sAQwAKBwcIBwYKCAgICwoKCw4YEA4NDQ4dFRYRGCMfJSQiHyIhJis3LyYpNCkhIjBBMTQ5Oz4+PiUuRElDPEg3PT47/9sAQwEKCwsODQ4cEBAcOygiKDs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7/8AAEQgCWAMgAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A9looooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBaSiigAooooAKKKKACiiigAooooAWkoooAKKKKACiiigAooooAKKKKAFpKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACijNJmgBaKTNJuoAdRTd1JuoAfRTN1G6gB9FM3UbqAH0U3dRuoAdRSZozQAtFGaKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooozQAUUmaTdQA7NGaZuqN7iKP78qL/ALzAUATZo3VmT67p0Gd1yrEdlOazpvGFog/dxlvqwFK6Hys6PdSbq4m68aSuCsOyL6cn9aypfE91KGEl/MfZcD+VLmK5GekNKifedV+pxVSbWLCEHfdIcdlO7+VeZTa1HwZJ3JP949f1qtJqMUo4lI+j0uZj5D0eXxZYR/dWV/cLVKfxooOIbXPuzV5810OQJevqcVC13ITjk+4oux8qO5k8b3P3RHEp9lJ/rVV/Gt+GxvUf8ArjXmMgIY4HrmoDdCJsGTgDu1Go7I7b/hNr8nAlT8hUi+NL9cFnT8UFcE93A4VS2W69alW5WFP9ZjH8JNILI79PG90Rkxxkf7p/xq3D43XH722B9SjY/nXmY1JfvK3zehbFSJqULHBlIbvzRdhyo9Xg8XabKQHZ4if7w/wrWgvre5UGGZHz6GvGUv2OGjkU4OMMM1YGrzRSgiQwledwp8zE4LoeyhqcGrzfTfHFxAwSdhOnqx5/Ouu0zxFY6kAI5Qkn9xj1+nrTUkyHFo2807NQB6eGqiSXNFMBpwNAC0UZooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiijNABRSZozQAtGabuqOSeOIZkkVB/tHFAEuaTNY9z4l063yBIZSOyCse68a7c+RFGo9WbJpXRSizry1VJ9UsrbiW5jB9Acn8hXnt94qurjIeckegOBWRNq5P8AHj2zS5ilA9In8WadEDtZ3PsMVk3XjOVsi3VEHqeTXBSaipBMj4HtwaqyasgbbHuYnoSeKV2Vyo6668SXsp2tcStn+4Dis+a7lcHdIfU7ga5iXV5Ovm7T2G41BJqEx481/wA8Uh2OieQs+FuEHsQR/OopJXXH79M/7+B/Ouc855GK7jk92c4ppGxiyhWz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gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAWkNFFADCKYy5qUimkUAV3SoHjq6VqNkoAz3iqB4fatJo6iaL2oGZjQ+1RmH2rTaGmGH2pAZhh9qaYfatIw+1NMPtQBneT7Unk+1aPke1J5HtQBn+T7UeT7VoeR7Uvke1AGf5PtThD7Ve8j2p3k+1AFAQ+1OEHtV4Q04Q+1AFEQe1OEHtV4Q+1KIaAKQg9qeIPargi9qcIvamBTEPtTxD7VbEXtTxFQBUEPtTxDVoR04R+1AisIvaniL2qwI6UJQBAIqcI6n2Uu2gCER08JUm2nbaAIglOC0/FLigBm2nbadiigBMUYpaKADFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABSYpaKAGkU0ipKTFAERSmFKnIpNtAFcx0wx1aK0m2gCoYqTyvareyk2UAVPK9qPK9qteXR5dAFXyvajyqtbKPLoAreV7UeVVrZRsoArCKneXVjZRsoAgEdL5ftU+2l20AQiP2pRHU22jbQBEEpwSpNtLigCMLS7afilxQAzbS7adRQAmKMUtFABiiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoxRRQAYpMUtFACbaTbTqKAG7aNtOooAbto206igBu2l20tFACbaMUtFACYpcUUUAGKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBaSiigAooooAKKKKACiiigAooooAWkoooAKKKKACiiigAooooAKKKKAFpKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigApaSigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/2Q==",
                "rtn_values":[
                    [[0, 0, 200, 200], "1", "Taro"],
                    [[200, 200, 200, 200], "1", "Taro"],
                    [[500, 500, 50, 60], "0", "Bun"],
                    [[400, 400, 100, 100], "0", "Bun"],
                ]
                }

        if not TESTING_NOT_CONNET_JETSON_NANO:
            # ans = requests.post(ip + function, json=send_data).json()
            pass
        # return ans

    except Exception as e:
        # request fail
        print("%s  %s location recognition request fail" % (product_id, image_name))
        return ""

    if ans['rtn'] == 400:
        print("%s  %s location recognition request fail x" % (product_id, image_name))
        return ""
    # Parsing data to dict
    convert_dict = {}
    for data in ans["rtn_values"]:
        id = data[1]
        if id not in convert_dict:
            convert_dict[id] = {product_id: 1}
        else:
            if product_id in convert_dict[id]:
                convert_dict[id][product_id] += 1
            else:
                convert_dict[id][product_id] = 1

    ################ update convert_recognition.data################

    convert_json_path = CUSTOMER_FILE + username + '/convert_recognition.data'
    data_lock = CUSTOMER_FILE + username + '/convert_datalock'
    # if data lock exited , sleep a little time
    while isfile(data_lock):
        lockfile_sleep(data_lock)

    # create data lock file
    create_lock_file(data_lock)

    # if convert_recognition.data not exited , create it
    if not isfile(convert_json_path):
        init_json_file(convert_json_path)

    convert_recognition_dict = get_json_data(convert_json_path)
    convert_recognition_dict[product_id + '/' + image_name] = convert_dict
    overwrite_json_data(convert_json_path, convert_recognition_dict)


    # delete data lock file
    delete_lock_file(data_lock)

    ####################################################################
    ################ update recognition.data################
    recognition_json_path = CUSTOMER_FILE + username + '/recognition.data'
    data_lock = CUSTOMER_FILE + username + '/recognition_datalock'

    # if data lock exited , sleep a little time
    while isfile(data_lock):
        lockfile_sleep(data_lock)

    # create data lock file
    create_lock_file(data_lock)

    # if recognition.data not exited , create it
    if not isfile(recognition_json_path):
        init_json_file(recognition_json_path)

    recognition_dict = get_json_data(recognition_json_path)
    keys = convert_dict.keys()
    for key in keys:
        if key in recognition_dict:
            if product_id in recognition_dict[key]:
                recognition_dict[key][product_id] += convert_dict[key][product_id]
            else:
                recognition_dict[key][product_id] = convert_dict[key][product_id]
        else:
            recognition_dict[key] = convert_dict[key]

    overwrite_json_data(recognition_json_path, recognition_dict)
    # delete data lock file
    delete_lock_file(data_lock)
    print("jetson_nano response and process data all done!")




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
