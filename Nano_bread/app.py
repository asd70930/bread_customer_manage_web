from flask import Flask, request, render_template, request, jsonify, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# import yolov4_app_1_4
import json
from os import listdir, getcwd, chdir, rename, makedirs, remove
from os.path import isdir, isfile
import cv2
import threading
import front_config
import requests
from  shutil import rmtree
import copy
from common_fun import rewrite_title_image, init_image_json_data , get_json_data, init_json_file, overwrite_json_data,\
rewrite_json_data, rewrite_json_image_count, imgSrc2_cv2img, base64toimg, cv2_strbase64 , get_ipc, generate_random_str,\
create_lock_file, delete_lock_file, lockfile_sleep, save_customer_product_profile, random_product_id, check_root_file,\
get_json_image_count

from html_maker import html_add_customer_product_maker, html_editcustomer_productMaker,\
html_customer_product_image_viewMaker, html_customer_productMaker, html_camera_maker, html_camera_create_maker,\
html_camera_roi_table_maker, html_camera_roi_inference_table_maker

PREBASE64 = front_config.PREBASE64
TESTING_NOT_CONNET_JETSON_NANO =front_config.TESTING_NOT_CONNET_JETSON_NANO
CUSTOMER_FILE = front_config.CUSTOMER_FILE
USERFILE = front_config.USERFILE
TEST_JETSONNANO_IP = "http://192.168.101.201:5000"
JETSONNANO_API_BASIC = '/bread/query/basic/v2'
JETSONNANO_API_NINE = "/bread/query/nine/v2"

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
check_root_file()




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



@app.route('/customer/cameraSetting')
def cameraSetting():
    """
    進入客戶攝影機設定的頁面
    :return:
    """
    return render_template('setCamera.html')


@app.route('/recognitionPage', methods=['GET'])
def recognition_page():
    """
    回傳辨識HTML
    :return:
    """
    imga = cv2.imread('static/A.png')
    basea = cv2_strbase64(imga)
    return render_template('recognition.html', basea=basea)


@app.route('/recognitionPage/pageChangeCameraROI', methods=['GET'])
def page_change_camera_roi():
    """
    回傳辨識Camera HTML
    :return:
    """

    return render_template('cameraROI.html')


@app.route('/customer/products', methods=['GET'])
def customer_products():
    """
    進入客戶產品清單的頁面
    :return:
    """

    return render_template('customerProductList.html')


@app.route('/recognitionPage/pageChangeCameraROI/roiInference', methods=['POST'])
def roiInference():
    if request.method == "POST":
        username = USERFILE
        request_data = request.get_json()
        datas = request_data["data"]
        print('get input datas:', datas)
        # keep_data = [[key,AnchorWidth, AnchorHeight],[key,AnchorWidth, AnchorHeight],....]
        keep_data = []
        datas_jetson  = []

        for i, re_data in enumerate(datas):
            keep_data.append([re_data["key"], re_data["AnchorWidth"], re_data["AnchorHeight"]])
            ip = re_data["ip"]
            painted = re_data["painted"]
            coordinates = []
            if painted:
                x = int(re_data["coordinate"][0][0] * re_data["AnchorWidth"])
                y = int(re_data["coordinate"][0][1] * re_data["AnchorHeight"])
                coordinates.append([x, y])
                x = int(re_data["coordinate"][1][0] * re_data["AnchorWidth"])
                y = int(re_data["coordinate"][1][1] * re_data["AnchorHeight"])
                coordinates.append([x, y])
                x = int(re_data["coordinate"][2][0] * re_data["AnchorWidth"])
                y = int(re_data["coordinate"][2][1] * re_data["AnchorHeight"])
                coordinates.append([x, y])
                x = int(re_data["coordinate"][3][0] * re_data["AnchorWidth"])
                y = int(re_data["coordinate"][3][1] * re_data["AnchorHeight"])
                coordinates.append([x, y])
            datas_jetson.append({"id": i, "cam_type": "ip_cam", "cam_addr": ip, "roi": coordinates})

        send_data = {
            "function": "nine",
            "values": datas_jetson
                    }
        print()
        # try:
        if not TESTING_NOT_CONNET_JETSON_NANO:
            ans = requests.post(TEST_JETSONNANO_IP+JETSONNANO_API_NINE, json=send_data)
            response_data = ans.json()
            print()
        else:
            base64_test = "" # test image base64
            response_data = {
                "rtn": 200,
                "items": [
                    {
                        "id": 0,
                        "b64string": base64_test,
                        "roi": datas_jetson[0]["roi"],
                        "percentage":0.5,
                        "item":[{
                                    "num": 0,
                                    "position": [[-8, -4], [261, -4], [261, 454], [-8, 454]],
                                    "confidence": 0.8,
                                    "real_id": 2,
                                    "name": "BA"
                        }]
                    }, {
                        "id": 1,
                        "b64string": base64_test,
                        "roi": datas_jetson[1]["roi"],
                        "percentage":0.7,
                        "item":[{
                                    "num": 0,
                                    "position": [[30, 170], [1025, 400], [50, 150], [30, 70]],
                                    "confidence":0.8,
                                    "real_id":1,
                                    "name":"Taro"
                        }]
                    }
                ]
            }
        if response_data["rtn"] != 200:
            return response_data


        ################################
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

        # name_dict : use product_id to get product_name
        name_dict = {}
        path =  CUSTOMER_FILE+USERFILE
        files = listdir(path)
        for file in files:
            if isdir(path+'/'+file):
                data_data = get_json_data(path+'/'+file+'/data.data')
                product_name = data_data["product_name"]
                product_id = data_data["product_id"]
                name_dict[product_id] = product_name
        #####################################

        total_percentage = 0
        image_count = len(response_data["items"])
        items_datas = {}
        htmls = []
        for i in range(image_count):
            item_datas = {}

            # set original data-key, anchorWidth and anchorHeight  to response
            response_data["items"][i]["id"] = keep_data[i][0]
            response_data["items"][i]["AnchorWidth"] = keep_data[i][1]
            response_data["items"][i]["AnchorHeight"] = keep_data[i][2]
            response_data["items"][i]["b64string"] = PREBASE64+response_data["items"][i]["b64string"]

            iamge_items_count = len(response_data["items"][i]["item"])
            percentage_response = response_data["items"][i]["percentage"]
            total_percentage += percentage_response
            # turn model id and name to customer product id and name.
            for l in range(iamge_items_count):
                model_id = str(response_data["items"][i]["item"][l]["real_id"])
                max_id = ''
                if model_id in recognition_dict:
                    max_count = 0
                    for key in recognition_dict[model_id].keys():
                        if recognition_dict[model_id][key] > max_count:
                            max_count = recognition_dict[model_id][key]
                            max_id = key
                if max_id == '':
                    max_id = random_product_id(username)

                response_data["items"][i]["item"][l]["real_id"] = max_id

                max_name = name_dict[max_id]
                if max_id in item_datas:
                    item_datas[max_id]["count"] += 1
                else:
                    item_datas[max_id] = {"count": 1, "name": max_name}
                if max_id in items_datas:
                    items_datas[max_id]["count"] += 1
                else:
                    items_datas[max_id] = {"count": 1, "name": max_name}

            # item_datas is one image all product id and name and count
            html = html_camera_roi_inference_table_maker(item_datas, percentage_response, False)

            htmls.append({"key": keep_data[i][0], "html": html})

        total_percentage = total_percentage/image_count
        html = html_camera_roi_inference_table_maker(items_datas, total_percentage, True)
        htmls.append({"key": "total", "html": html})
        response_data["html"] = htmls

        return response_data


        # except Exception as e:
        #     print(e)
        #     return {"rtn": 400}


@app.route('/infrence', methods=['POST'])
def Recognition_bread():
    """
    發送Post Request至Jetson nano上,API格式查詢gitlab 機器設備issues
    data : JSON "b64string": 圖片的base64
    :return:
    """
    if request.method == "POST":
        username = USERFILE
        data = request.get_json()
        # for testing image shape
        # img = imgSrc2_cv2img(data["b64string"])
        # print(img.shape)
        send_data = {"function": "basic",
                     "values": [{
                        "id": 0,
                        "b64string": data["b64string"]
                    }]
        }
        try:
            # for testing , fake API response
            response_data = {
                    "rtn": 200,
                    "items": [{"id": 0,
                               "item": [{
                                        "num": 0,
                                        "position": [200, 200, 200, 200],
                                        "confidence":0.8,
                                        "real_id": 1,
                                        "name": "Taro"
                                      }]
                              }
                              ]
            }

            if not TESTING_NOT_CONNET_JETSON_NANO:
                ans = requests.post(TEST_JETSONNANO_IP+JETSONNANO_API_BASIC, json=send_data)
                response_data = ans.json()
            print("response_data", response_data)
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
            for index, data_item in enumerate(response_data["items"][0]["item"]):
                # model_id is response yolo model output
                model_id = str(data_item["real_id"]) #########
                print("model_id", model_id)
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
                response_data["items"][0]["item"][i]["real_id"] = datas[0]
                response_data["items"][0]["item"][i]["name"] = datas[1]

            return response_data
        except Exception as e:
            print(e)
            return {"rtn": 400}
    else:
        return {"rtn": 400, "message": "Error, pls using post"}


@app.route('/recognitionPage/pageChangeCameraROI/roiTable', methods=['GET'])
def camera_roi_table():
    camera_data_path = "customer/root/camera.data"
    camera_data = get_json_data(camera_data_path)
    response_data = html_camera_roi_table_maker(camera_data)
    return response_data


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

@app.route('/customer_delete_product_data', methods=['DEL'])
def customer_delete_product_data():
    if request.method == "DEL":
        username = 'root'
        data = request.get_json()
        # get product id as list
        product_ids = data["product_id"]

        # get json data from convert_recognition.data
        recognition_json_path = CUSTOMER_FILE + username + '/recognition.data'
        convert_json_path = CUSTOMER_FILE + username + '/convert_recognition.data'
        data_lock = CUSTOMER_FILE + username + '/convert_datalock'

        if not isfile(convert_json_path) or not isfile(recognition_json_path):
            return {"message": "not image data", "status": "02"}
        # if data lock exited , sleep a little time
        while isfile(data_lock):
            lockfile_sleep(data_lock)

        # create data lock file
        create_lock_file(data_lock)
        convert_recognition_dict = get_json_data(convert_json_path)

        convert_recognition_dict_keys = convert_recognition_dict.keys()
        delete_covert_keys = []
        for key in convert_recognition_dict_keys:
            pro_key = key.split('/')[0]
            if pro_key in product_ids:
                delete_covert_keys.append(key)
        for key in delete_covert_keys:
            del convert_recognition_dict[key]

        # convert_recognition data done
        # make recognition

        overwrite_recognition_dict = {}
        convert_keys = convert_recognition_dict.keys()
        for convert_key in convert_keys:
            recognition_keys = convert_recognition_dict[convert_key].keys()
            for recognition_key in recognition_keys:
                if recognition_key not in overwrite_recognition_dict:
                    overwrite_recognition_dict[recognition_key] = \
                        convert_recognition_dict[convert_key][recognition_key]
                else:
                    product_keys = convert_recognition_dict[convert_key][recognition_key].keys()
                    for product_key in product_keys:
                        if product_key not in overwrite_recognition_dict[recognition_key]:
                            overwrite_recognition_dict[recognition_key][product_key] = \
                                convert_recognition_dict[convert_key][recognition_key][product_key]
                        else:
                            overwrite_recognition_dict[recognition_key][product_key] += \
                                convert_recognition_dict[convert_key][recognition_key][product_key]

        overwrite_json_data(convert_json_path, convert_recognition_dict)

        # delete data lock file
        delete_lock_file(data_lock)


        data_lock = CUSTOMER_FILE + username + '/recognition_datalock'



        while isfile(data_lock):
            lockfile_sleep(data_lock)

        # create data lock file
        create_lock_file(data_lock)

        # overwirte recognition.data
        overwrite_json_data(recognition_json_path, overwrite_recognition_dict)

        # delete data lock file
        delete_lock_file(data_lock)


        # delete file
        for product_id in product_ids:
            file_path = CUSTOMER_FILE + username + '/' + product_id
            try:
                rmtree(file_path)
            except Exception as e:
                print(e)
        return {"message": "done", "status": "01"}
    return {"message":"del only", "status": "02"}


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
        img_srcs = data["base64"]
        product_id = str(data["product_id"])
        first_image_name = []
        flag = 0
        for i, img_src in enumerate(img_srcs):
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
            if flag == 0:
                flag += 1
                first_image_name.append(save_data_name)

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

        t = threading.Thread(target=jetson_nano_request,
                             args=(product_id, username, first_image_name[0],
                                   img_srcs[0], TEST_JETSONNANO_IP, JETSONNANO_API_BASIC))
        t.start()

        return {"message": "done"}

    return {"message": "error"}



@app.route('/delete_product_image', methods=['POST'])
def delete_product_image():
    """

    """
    if request.method == "POST":

        username = 'root'
        data = request.get_json()
        image_name = data["file_path"]
        product_id = str(data["product_id"])
        path = CUSTOMER_FILE + username + '/'
        image_path = path + product_id + '/' + image_name
        data_lock = path + '/datalock'

        #######   delete image file and rewrite json data image count
        while isfile(data_lock):
            lockfile_sleep(data_lock)
        # create data lock file
        with open(data_lock, 'w') as lock:
            pass
        try:
            remove(image_path)
        except Exception as e:
            return {"message": "image delete error"}

        json_file_path = path + product_id + '/' + 'data.data'
        rewrite_count = str(int(get_json_image_count(json_file_path)) - 1)
        rewrite_json_image_count(json_file_path, rewrite_count)
        delete_lock_file(data_lock)
        ##############################################################

        ####### rewrite recognition.data and convert_recognition.data

        convert_json_path = CUSTOMER_FILE + username + '/convert_recognition.data'
        data_lock = CUSTOMER_FILE + username + '/convert_datalock'
        convert_json_key  = product_id+'/'+image_name

        while isfile(data_lock):
            lockfile_sleep(data_lock)

        # create data lock file
        create_lock_file(data_lock)
        convert_recognition_dict = get_json_data(convert_json_path)

        # get data which key is convert_json_key and delete the key
        data_dict = convert_recognition_dict.pop(convert_json_key)
        overwrite_json_data(convert_json_path, convert_recognition_dict)

        # delete data lock file
        delete_lock_file(data_lock)

        #
        recognition_json_path = CUSTOMER_FILE + username + '/recognition.data'
        data_lock = CUSTOMER_FILE + username + '/recognition_datalock'

        while isfile(data_lock):
            lockfile_sleep(data_lock)

        # create data lock file
        create_lock_file(data_lock)
        recognition_dict = get_json_data(recognition_json_path)

        model_keys = data_dict.keys()
        for model_key in model_keys:
            product_keys = data_dict[model_key].keys()
            for product_key in product_keys:
                recognition_dict[model_key][product_key] -= data_dict[model_key][product_key]

        overwrite_json_data(recognition_json_path, recognition_dict)
        # delete data lock file
        delete_lock_file(data_lock)
        print("delete image all process done!")

        return {"message": "done"}
    return {"message": "post only"}



# for only one image in ajax
# @app.route('/save_product_image', methods=['POST'])
# def save_product_image():
#     """
#
#     """
#
#     if request.method == "POST":
#         username = USERFILE
#         data = request.get_json()
#         # print("got data")
#         img_src = data["base64"]
#         flag = data["flag"]
#         product_id = str(data["product_id"])
#         data_lock = CUSTOMER_FILE+username+'/'+product_id+'/datalock'
#         # if data lock exited , sleep a little time
#         while isfile(data_lock):
#             lockfile_sleep(data_lock)
#
#         # create data lock file
#         with open(data_lock, 'w') as lock:
#             pass
#
#         # save image
#         path = CUSTOMER_FILE+username+'/'+product_id
#         files = listdir(path)
#         # final_number = '1'
#         image_count = 0
#
#         # check out file image number to decide savefile name
#         for i, file in enumerate(files):
#             data_type = file.split(".")[-1]
#             if data_type == "jpg" and file.split(".")[0].split("_")[-1] != 'title':
#                 image_count += 1
#                 # final_number = str(int(file.split(".")[0].split("_")[-1])+1)
#         save_data_name = generate_random_str(25)+'.jpg'
#         try:
#             img = imgSrc2_cv2img(img_src)
#             cv2.imwrite(path+'/'+save_data_name, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
#         except Exception as e:
#             delete_lock_file(data_lock)
#             return {"message": "image save error"}
#
#         # overwrite data.data
#         json_file_path = path+'/'+'data.data'
#         image_count += 1
#         rewrite_json_image_count(json_file_path, str(image_count))
#         delete_lock_file(data_lock)
#
#         ###
#         # save json data to debug
#         # debug_file_path = generate_random_str(10)+'.txt'
#         # overwrite_json_data(debug_file_path, data)
#         ###
#
#         # send request to jetson nano
#         if flag == 0:
#             t = threading.Thread(target=jetson_nano_request,
#                                  args=(product_id, username, save_data_name,
#                                        img_src, TEST_JETSONNANO_IP, JETSONNANO_API_BASIC))
#             t.start()
#
#         return {"message": "done"}
#
#     return {"message": "error"}


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
    # image_src is only one image base64
    print(image_name)
    send_data = {"function": "basic",
                 "values": [{
                     "id": 0,
                     "b64string": image_src
                 }]
                 }

    try:
        # for testing , fake API response
        # for testing , fake API response


        ans = {
            "rtn": 200,
            "items": [{"id": 0,
                       "item": [{
                           "num": 0,
                           "position": [200, 200, 200, 200],
                           "confidence": 0.8,
                           "real_id": 1,
                           "name": "Taro"
                       }]
                       }
                      ]
        }

        if not TESTING_NOT_CONNET_JETSON_NANO:
            ans = requests.post(ip + function, json=send_data).json()
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
    response_data = ans["items"]
    print(response_data)

    for data in response_data:
        id = str(data["item"][0]["real_id"])
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
    recognition_dict_keys = recognition_dict.keys()
    print("recognition_dict_keys", recognition_dict_keys)
    keys = convert_dict.keys()
    print("convert_dict keys", keys)
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
