import cv2
import numpy as np
import datetime
import darknet
import base64
from PIL import Image
import io
import json


class Timer:
    def __init__(self):
        self.clock = {}

    def start(self, key="default"):
        self.clock[key] = datetime.datetime.now()

    def end(self, key="default"):
        if key not in self.clock:
            raise Exception(f"{key} is not in the clock.")
        interval = datetime.datetime.now() - self.clock[key]
        del self.clock[key]
        return interval.total_seconds()


timer = Timer()


def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


configPath = "../../darknet-master/backup/bread10_0916/bread10_0916_yolov4.cfg"
weightPath = "../../darknet-master/backup/bread10_0916/model/bread10_0916_yolov4_last.weights"
metaPath = "../../darknet-master/backup/bread10_0916/bread10_0916.data"
classPath = "../../darknet-master/backup/bread10_0916/classes.txt"

netMain = darknet.load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, 1)
metaMain = darknet.load_meta(metaPath.encode("ascii"))


def get_id(name):
    with open(classPath, 'r') as f:
        num = 0
        for line in f:
            new_str = line.replace("\n", '')
            if new_str == name:
                return num
            else:
                num = num + 1


def YOLO_detection(image, darknet_image):
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    timer.start()
    darknet.copy_image_from_bytes(darknet_image, frame_rgb.tobytes())
    detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
    z_box_list = []
    object_type_list = []
    labels = 0
    for i, detection in enumerate(detections):
        object_type = detection[0].decode()
        confidence = detection[1]
        labels += 1
        x, y, w, h = detection[2][0], \
                     detection[2][1], \
                     detection[2][2], \
                     detection[2][3]
        left, top, rights, bottom = convertBack(float(x), float(y), float(w), float(h))
        box = np.array([top, left, bottom, rights])
        z_box_list.append(box)
        type_and_confidence = [object_type, confidence]
        object_type_list.append(type_and_confidence)
    interval = timer.end()
    print('image1 Time: {:.6f}s, Detect Objects: {:d}.'.format(interval, labels))
    return z_box_list, labels, object_type_list


def stringToRGB(base64_string):
    b64_str = base64_string.split(',')[1]
    extension = base64_string.split(',')[0].split('/')[1].split(';')[0]
    imgdata = base64.b64decode(str(b64_str))
    image = Image.open(io.BytesIO(imgdata))
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB), extension


def inference(base64_data, num):
    image, extension = stringToRGB(base64_data)
    (h, w, _) = np.shape(image)
    darknet_image = darknet.make_image(w, h, 3)
    bboxes, labels, classes_and_confidence = YOLO_detection(image, darknet_image)
    datas = []
    points = []
    if str(num) == '1':
        for boxes, obj_classes in zip(bboxes, classes_and_confidence):
            id = get_id(obj_classes[0])
            data = [obj_classes[0], str(id)]
            datas.append(data)
        return {"data": datas}
    elif str(num) == '3':
        for boxes, obj_classes in zip(bboxes, classes_and_confidence):
            dots = [(boxes[1], boxes[0]), (boxes[3], boxes[0]), (boxes[3], boxes[2]), (boxes[1], boxes[2])]
            points.append(dots)
            id = get_id(obj_classes[0])
            position = [boxes[1], boxes[0], (boxes[3] - boxes[1]), (boxes[2] - boxes[0])]
            position = json.dumps(position, cls=NpEncoder)
            position = eval(position)
            data = [position, str(id), obj_classes[0]]
            datas.append(data)
        rtn_data = draw_image(base64_data, points)
        return {"b64string": rtn_data, "data": datas}
    elif str(num) == '4':
        for boxes, obj_classes in zip(bboxes, classes_and_confidence):
            dots = [(boxes[1], boxes[0]), (boxes[3], boxes[0]), (boxes[3], boxes[2]), (boxes[1], boxes[2])]
            points.append(dots)
            id = get_id(obj_classes[0])
            position = [boxes[1], boxes[0], (boxes[3] - boxes[1]), (boxes[2] - boxes[0])]
            position = json.dumps(position, cls=NpEncoder)
            position = eval(position)
            data = [position, ('%.2f' % (obj_classes[1])), str(id), obj_classes[0]]
            datas.append(data)
        rtn_data = draw_image(base64_data, points)
        return {"b64string": rtn_data, "data": datas}
    else:
        return '???'


def draw_image(b64string, points):
    info, data = b64string.split(',')
    img_data = data.encode(encoding='utf-8')
    with open("before.jpg", "wb") as fh:
        fh.write(base64.decodebytes(img_data))
    image = cv2.imread('before.jpg')
    # print('points ', points)
    for i in range(len(points)):
        for point in points:
            for x in range(4):
                cv2.line(image, point[x - 1], point[x], (0, 0, 255), 2)
    cv2.imwrite('after.jpg', image)
    with open("after.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    after_str = info + ',' + encoded_string
    return after_str


def isimage(b64string):
    try:
        image, extension = stringToRGB(b64string)
        return True
    except:
        return False


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
