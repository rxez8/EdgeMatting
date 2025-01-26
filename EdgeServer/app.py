from flask import Flask, jsonify
import json
import redis
import random
# 创建连接池并连接到redis，并设置最大连接数量;
conn_pool = redis.ConnectionPool(host='192.168.1.14', port=6379, password='redis', max_connections=10, db=1)
__conn = redis.Redis(connection_pool=conn_pool)


app = Flask(__name__)

deviceList = [{
    'deviceId': '0001',
    'ip': '192.168.1.11',
    'task': 0
},{
    'deviceId': '0002',
    'ip': '192.168.1.15',
    'task': 0
}]



@app.route('/')
def checktask():  # put application's code here
    if __conn.llen('taskList') == 0:
        # 如果所有设备均没有任务，则随机选择一个
        random_number = random.randint(1, len(deviceList))
        print(random_number)
        return jsonify(deviceList[random_number-1])
    else:
        items = __conn.lrange('taskList', 0, -1)
        for index, item in enumerate(items):
            decoded_data = json.loads(item)
            for device in deviceList:
                if device['deviceId'] == decoded_data['deviceId']:
                    device['task'] = decoded_data['task']
        # 获取当前图像任务数最小的设备
        min_object = min(deviceList, key=lambda x: x['task'])
        return jsonify(min_object)

if __name__ == '__main__':
    app.run()
