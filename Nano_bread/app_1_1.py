from flask import Flask, request
import yolov4_app_1_1
import json
import logging

app = Flask(__name__)


@app.route('/bread/query/category/v1', methods=['POST'])
def category():
    if request.method == 'POST':
        data = request.json
        b64 = data['values']['b64string']
        name = data['values']['name']
        if data['function'] == 'category':
            image = yolov4_app_1_1.isimage(b64)
            if image:
                result = yolov4_app_1_1.inference(b64, 1)
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
            image = yolov4_app_1_1.isimage(b64)
            if image:
                result = yolov4_app_1_1.inference(b64, 1)
                rtn_data = {
                    "rtn": 200,
                    "rtn_values": result['data']
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
            image = yolov4_app_1_1.isimage(b64)
            if image:
                result = yolov4_app_1_1.inference(b64, 3)
                rtn_data = {
                    "rtn": 200,
                    "b64string": result['b64string'],
                    "rtn_values": result['data']
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
            image = yolov4_app_1_1.isimage(b64)
            if image:
                result = yolov4_app_1_1.inference(b64, 4)
                rtn_data = {
                    "rtn": 200,
                    "b64string": result['b64string'],
                    "rtn_values": result['data']
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


@app.route('/bread/query/area/v1', methods=['POST'])
def area():
    if request.method == 'POST':
        data = request.json
        # app.logger.debug('input data: %s' % (data))
        if data['function'] == 'area':
            b64 = data['values']['b64string']
            try:
                roi = data['values']['roi']
            except:
                rtn_data = {
                    "rtn": 500,
                    "message": 'roi type error'
                }
                return json.dumps(rtn_data)
            image = yolov4_app_1_1.isimage(b64)
            if image:
                if roi == []:
                    # full image
                    points = yolov4_app_1_1.getsize(b64)
                elif isinstance(roi, list) and len(roi) > 2:
                    points = roi
                else:
                    rtn_data = {
                        "rtn": 500,
                        "message": 'roi type error'
                    }
                    return json.dumps(rtn_data)
                # print('points ',points)
                # !!!!!! if roi is not rectangle !!!!!!
                result = yolov4_app_1_1.inference_area(b64, points)
                rtn_data = {
                    "rtn": 200,
                    "b64string": result['b64string'],
                    "roi": points,
                    "percentage": result['percentage'],
                    "items": result['data'],
                }
                # print(rtn_data)
                # print(type(rtn_data))
                return json.dumps(rtn_data)
            else:
                rtn_data = {
                    "rtn": 500,
                    "message": 'b64string type error'
                }
                return rtn_data
    else:
        rtn_data = {
            "rtn": 404
        }
        return rtn_data


if __name__ == '__main__':
    # app.debug = True
    # handler = logging.FileHandler('log/flask.log', encoding='UTF-8')
    # handler.setLevel(logging.DEBUG)
    # logging_format = logging.Formatter("%(asctime)s flask %(levelname)s %(message)s")
    # handler.setFormatter(logging_format)
    # app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True)
