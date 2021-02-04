import cv2
import json
import base64
import random
import string
import time
import numpy as np
import front_config
from os import remove, makedirs, getcwd, chdir, rename, listdir, makedirs
from os.path import getctime, isdir,exists


CUSTOMER_FILE = front_config.CUSTOMER_FILE
ORIGIN_PATH = front_config.ORIGIN_PATH
PREBASE64 = front_config.PREBASE64
LOCKFILEEXITEDTIME = front_config.LOCKFILEEXITEDTIME
SLEEPLITTLETIME = front_config.SLEEPLITTLETIME

def get_json_image_count(path):
    """
    :param path: type: String , json file path
    :return: String , value of productID has how many image
    """
    dic = get_json_data(path)
    return dic["image_count"]


def check_root_file():
    """
    check root file path exited or not ,
    if not exited, create it.
    :return:
    """
    path = "customer/root"
    folder = exists(path)
    if not folder:
        makedirs(path)


def random_product_id(customer):
    """
    當找不到合適的產品ID隨機挑選現有的產品ID回傳
    :return: 隨機產品ID
    """
    dir_list = []
    path = CUSTOMER_FILE + customer+'/'
    files = listdir(path)

    for file in files:
        if isdir(path+file):
            dir_list.append(file)
    random.shuffle(dir_list)
    return dir_list[0]


def save_customer_product_profile(data, path):
    """
    依照前端給予的資料修改客戶某個產品的資料
    依照網頁點選可以是新增產品資料或是修改產品資料
    :param data: 前端給予的產品資料
    :param path: customer/root/
    :return:
    """
    # path = customer/root/
    imagebase = data["img"]
    product_id = data["product_id"]
    pre_product_id = data["pre_product_id"]

    if pre_product_id == "":
        data_path = path + product_id + '/data.data'
        dir_path = path + product_id + "/"
        # pre_product_id 為空的話為新增商品品項
        product_name = data["product_name"]
        product_memo = data["memo"]

        # add new file
        makedirs(path+product_id)

        # add title image
        rewrite_title_image(dir_path, imagebase)
        save_data = {
            "image_count": "0",
            "product_id": product_id,
            "product_name": product_name,
            "memo": product_memo,
            "ON": "1"
        }

        # add data.data
        init_image_json_data(data_path, save_data)
    else:
        # 反之為修改商品品項
        data_path = path + pre_product_id + '/data.data'
        dir_path = path + pre_product_id + "/"
        rewrite_json_data(data_path, data)
        rewrite_title_image(dir_path, imagebase)

        if pre_product_id != product_id:
            # 如果使用者需要修改產品ID
            chdir(path)
            rename(pre_product_id, product_id)
            chdir(ORIGIN_PATH)


def rewrite_title_image(path, imabase64):
    """
    rewrite title image
    :param path: title image file path
    :param imabase64: new image base64 string
    """
    img = imgSrc2_cv2img(imabase64)
    imag_path = path+'title.jpg'
    cv2.imwrite(imag_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])


def init_image_json_data(path, data):
    """
    Create image json data.
    :param path: file path
    :param data: a data type as dict.
    """
    init_json_file(path)
    overwrite_json_data(path, data)


def get_json_data(path):
    """
    get a json file data as dict where at path.
    :param path: file path
    :return: json data
    """
    with open(path) as json_file:
        data = json.load(json_file)
        dic = data
    return dic


def init_json_file(path):
    """
    create a json data where at path.
    :param path: file path
    """
    with open(path, 'w') as outfile:
        json.dump({}, outfile)


def overwrite_json_data(path, dic):
    """
    use dic to overwrite json data where at path.
    :param path: file path
    :param dic: a data type as dict.
    """
    with open(path, 'w') as outfile:
        json.dump(dic, outfile)


def rewrite_json_data(path, data):
    """
    use data which key in data to update json file
    :param path:
    :param data:
    :return:
    """
    dic = get_json_data(path)
    allkeys = data.keys()
    for key in allkeys:
        if key in dic:
            dic[key] = data[key]
    with open(path, 'w') as outfile:
        json.dump(dic, outfile)


def rewrite_json_image_count(path, count):
    """
    rewrite json data image count .
    :param path: type: String , json file path
    :param count: type: String , value of productID has how many image
    :return: not return
    """
    dic = get_json_data(path)
    dic["image_count"] = count
    with open(path, 'w') as outfile:
        json.dump(dic, outfile)


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
    """
    image to base64,and plus "data:image/jpeg;base64,"
    :param image: cv2.imread image
    :return: image to base64
    """
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
        print(e)
        return {"ret": False}


def generate_random_str(randomlength):
    '''
    string.digits = 0123456789
    string.ascii_letters = 26个小写,26个大写
    '''
    str_list = random.sample(string.digits + string.ascii_letters, randomlength)
    random_str = ''.join(str_list)
    return random_str


def create_lock_file(lock_path):
    """
    create a lockfile
    """
    with open(lock_path, 'w') as lock:
        pass


def delete_lock_file(lock_path):
    """
    delete a lockfile
    """
    remove(lock_path)


def lockfile_sleep(data_lock):
    """
    check data lock file exited time is larger then a time or not,
    if larger , delete data lock file ensure file save.
    if not , sleep a little time
    :param data_lock: data lock file path
    """
    acess_time = getctime(data_lock)
    if time.time() - acess_time >= LOCKFILEEXITEDTIME:
        delete_lock_file(data_lock)
    else:
        time.sleep(SLEEPLITTLETIME)