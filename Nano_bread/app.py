from flask import Flask, request
import yolov4_app_1_4
import json
import numpy as np

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
