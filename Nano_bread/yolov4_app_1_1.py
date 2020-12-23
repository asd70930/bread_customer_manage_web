import cv2
import numpy as np
import datetime
import darknet
import base64
from PIL import Image
import io
import json
from geometry_area_cv import Fill_geometry
from shapely.geometry import Polygon


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


# configPath = "../../darknet-master/backup/bread10_0916/bread10_0916_yolov4.cfg"
# weightPath = "../../darknet-master/backup/bread10_0916/model/bread10_0916_yolov4_last.weights"
# metaPath = "../../darknet-master/backup/bread10_0916/bread10_0916.data"
# classPath = "../../darknet-master/backup/bread10_0916/classes.txt"

configPath = "../../darknet-master/backup/starbuck12/starbuck12_yolov4.cfg"
weightPath = "../../darknet-master/backup/starbuck12/model/starbuck12_yolov4_final.weights"
metaPath = "../../darknet-master/backup/starbuck12/starbuck12.data"
classPath = "../../darknet-master/backup/starbuck12/classes.txt"

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
    detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.8)
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


def inference_area(base64_data, ROI_points):
    image, extension = stringToRGB(base64_data)
    (h, w, _) = np.shape(image)
    darknet_image = darknet.make_image(w, h, 3)
    bboxes, labels, classes_and_confidence = YOLO_detection(image, darknet_image)
    datas = []
    dot = []
    num = 0

    # for rectangle roi
    # cv2.rectangle(image, (ROI_points[0][0], ROI_points[0][1]), (ROI_points[2][0], ROI_points[2][1]), (0, 0, 255), 2)

    # for all kind of roi in four points
    # dot = [(ROI_points[0][0], ROI_points[0][1]), (ROI_points[1][0], ROI_points[1][1]),
    #        (ROI_points[2][0], ROI_points[2][1]), (ROI_points[3][0], ROI_points[3][1]), ]
    # for i in range(len(dot)):
    #     cv2.line(image, dot[i - 1], dot[i], (0, 0, 255), 2)

    # for any points
    for i in range(len(ROI_points)):
        dot.append((ROI_points[i][0], ROI_points[i][1]))
    for i in range(len(dot)):
        cv2.line(image, dot[i - 1], dot[i], (0, 0, 255), 2)

    area = Fill_geometry(h, w, ROI_points)

    for boxes, obj_classes in zip(bboxes, classes_and_confidence):
        result = {}
        # boxes = [y0,x0,y1,x1]
        # Clockwise A B C D from the upper left
        A, B, C, D = [boxes[1], boxes[0]], [boxes[3], boxes[0]], [boxes[3], boxes[2]], [boxes[1], boxes[2]]
        anchors = [A, B, C, D]
        # print('origin anchors: ', anchors)
        id = get_id(obj_classes[0])
        text = obj_classes[0] + " " + str(int(obj_classes[1] * 100)) + "%"
        # text = str(int(obj_classes[1] * 100)) + "%"
        # print(text)

        # if ROI_points[0][0] == ROI_points[3][0] and ROI_points[0][1] == ROI_points[1][1] and ROI_points[1][0] == \
        #         ROI_points[2][0] and ROI_points[3][1] == ROI_points[2][1]:
        #     # print('rectangle')
        #     # for only rectangle
        #
        #     print('origin rectangle ', boxes[0], boxes[1], boxes[2], boxes[3])
        #     if boxes[0] < ROI_points[0][1]:
        #         boxes[0] = ROI_points[0][1]
        #     if boxes[1] < ROI_points[0][0]:
        #         boxes[1] = ROI_points[0][0]
        #     if boxes[2] > ROI_points[2][1]:
        #         boxes[2] = ROI_points[2][1]
        #     if boxes[3] > ROI_points[2][0]:
        #         boxes[3] = ROI_points[2][0]
        #
        #     print('new rectangle ', boxes[0], boxes[1], boxes[2], boxes[3])
        #
        #     cv2.rectangle(image, (boxes[1], boxes[0]), (boxes[3], boxes[2]), (0, 255, 0), 2)
        #
        # else:
            # for not rectangle

        roi_point = Polygon(dot)
        box = anchors
        box_point = Polygon(box)
        real_point = []
        if roi_point.intersects(box_point):
            x = roi_point.intersection(box_point)
            for a, b in x.exterior.coords:
                real_point.append((int(a), int(b)))
            del real_point[0]
            real_point = real_point[::-1]
            for i in range(len(real_point)):
                cv2.line(image, real_point[i - 1], real_point[i], (255, 0, 0), 2)

        # cv2.rectangle(image, (boxes[1], boxes[0]), (boxes[3], boxes[2]), (0, 255, 0), 2)
        # print('after anchors: ', anchors)
        cv2.putText(image, text, (boxes[1], boxes[0] - 5), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
        area.obj_points_to_fill(anchors)
        position = [boxes[1], boxes[0]], [boxes[3], boxes[0]], [boxes[3], boxes[2]], [boxes[1], boxes[2]]
        position = json.dumps(position, cls=NpEncoder)

        result['id'] = str(num)
        result['position'] = position
        result['confidence'] = ('%.2f' % (obj_classes[1]))
        result['real_id'] = str(id)
        result['name'] = obj_classes[0]
        # print('result ', result)
        result_copy = result.copy()
        datas.append(result_copy)
        num = num + 1

    area_result = area.area_ratio()
    print("area ratio : {}%".format(int(area_result)))
    area.clear_mask()

    cv2.imwrite('area.jpg', image)
    with open("area.jpg", "rb") as img_file:
        rtn_data = base64.b64encode(img_file.read())
    rtn_data = rtn_data.decode('utf-8')
    # datas needs to be dict
    return {"b64string": rtn_data, "percentage": str(int(area_result)), "data": datas}


def draw_image(b64string, points):
    info, data = b64string.split(',')
    img_data = data.encode(encoding='utf-8')
    with open("before.jpg", "wb") as f:
        f.write(base64.decodebytes(img_data))
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


def getsize(b64string):
    info, data = b64string.split(',')
    img_data = data.encode(encoding='utf-8')
    with open("size.jpg", "wb") as f:
        f.write(base64.decodebytes(img_data))
    img = cv2.imread('size.jpg')
    h, w, c = img.shape
    l = [(0, 0), (w, 0), (w, h), (0, h)]
    return l
