from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os
import uuid
import redis
import json
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import io

# 多设备编号
deviceId = '0001'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}
# 创建连接池并连接到redis，并设置最大连接数量;
conn_pool = redis.ConnectionPool(host='192.168.1.14', port=6379, password='redis', max_connections=10, db=1)
__conn = redis.Redis(connection_pool=conn_pool)
# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 生成密钥
def generate_key():
    return b'\x11\xd7\x90h_G\x8d\xb7X-H\xc5\xb9\x8a\xbc\xd4'  # 生成16字节的密钥


# 加密图像
def encrypt_image(input_image_path, output_image_path, key):
    # 打开图像文件并获取图像的宽和高
    image = Image.open(input_image_path)
    image_bytes = image.tobytes()
    width, height = image.size

    # 创建加密器
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(image_bytes, AES.block_size))

    # 保存加密后的图像，包含IV和尺寸信息
    with open(output_image_path, 'wb') as output_file:
        output_file.write(cipher.iv)  # 写入初始化向量
        output_file.write(width.to_bytes(4, 'big'))  # 写入宽度（4字节）
        output_file.write(height.to_bytes(4, 'big'))  # 写入高度（4字节）
        output_file.write(ciphertext)  # 写入密文


def updateRedis(taskNum):
    if __conn.llen('taskList') == 0:
        data = {
            'deviceId': deviceId,
            'task': taskNum
        }
        json_str = json.dumps(data)
        __conn.rpush('taskList', json_str)
    else:
        items = __conn.lrange('taskList', 0, -1)
        for index, item in enumerate(items):
            decoded_data = json.loads(item)
            if decoded_data['deviceId'] == deviceId:
                decoded_data['task'] = taskNum
                __conn.lset('taskList', index, json.dumps(decoded_data))
                break


@app.route('/')
def upload_form():
    html = '''  
    <!doctype html>  
    <title>Upload new File</title>  
    <h1>Upload new File</h1>  
    <form method=post enctype=multipart/form-data>  
      <input type=file name=file>  
      <input type=submit value=Upload>  
    </form>  
    '''
    return render_template_string(html)


@app.route('/', methods=['POST'])
def upload_file():
    # 检查是否有文件部分在请求中
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file part.'
        })
    file = request.files['file']
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No selected file.'
        })
    if file and allowed_file(file.filename):
        root, ext = os.path.splitext(file.filename)
        filename = str(uuid.uuid4()).replace('-', '')
        entries = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], ''))
        encrypt_image(file.stream, os.path.join(app.config['UPLOAD_FOLDER'], filename + ext), generate_key())
        updateRedis(len(entries))
        return jsonify({
            'success': True
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Please select a file.'
        })


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
