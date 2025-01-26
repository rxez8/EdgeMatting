import json
import time
import datetime
import requests
import os
import sys
from pathlib import Path
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

current_dir = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(current_dir)[0]
sys.path.append(rootPath)


# 生成密钥
def generate_key():
    return b'\x11\xd7\x90h_G\x8d\xb7X-H\xc5\xb9\x8a\xbc\xd4'  # 生成16字节的密钥


# 获取目录中时间最新的一个文件
def get_latest_file():
    directory = Path(rootPath) / "photos"
    # 获取目录中所有文件的列表（不包括子目录中的文件）
    files = [f for f in directory.iterdir() if f.is_file()]

    # 获取文件修改时间并找到最新的文件
    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    return latest_file


# 解密图像
def decrypt_image(input_image_path, output_image_path, key):
    with open(input_image_path, 'rb') as input_file:
        iv = input_file.read(16)  # 读取初始化向量
        width = int.from_bytes(input_file.read(4), 'big')  # 读取宽度
        height = int.from_bytes(input_file.read(4), 'big')  # 读取高度
        ciphertext = input_file.read()

        # 创建解密器
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)

    # 创建图像并保存
    image = Image.frombytes('RGB', (width, height), decrypted_bytes)
    image.save(output_image_path)


def formatTime():
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()
    add_zero_if_less_than_10 = lambda x: f'0{x}' if x < 10 else str(x)
    # 分别获取当前年、月、日、时、分、秒
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_hour = current_datetime.hour
    current_minute = current_datetime.minute
    current_second = current_datetime.second
    return str(current_year) + '-' + add_zero_if_less_than_10(current_month) + '-' + add_zero_if_less_than_10(
        current_day) + ' ' + add_zero_if_less_than_10(current_hour) + ':' + add_zero_if_less_than_10(
        current_minute) + ':' + add_zero_if_less_than_10(current_second)


def edgeMatting():
    image_dir = os.path.join(rootPath, "photos")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    while True:
        entries = os.listdir(image_dir)
        if len(entries) > 0:
            file = get_latest_file()
            response = requests.get("http://192.168.1.16:8080")
            rData = json.loads(response.text)

            if rData['ip'] is not None:
                with open(file, 'rb') as f:
                    resp = requests.post("http://" + rData['ip'] + ":8000", files={'file': f})
                    respData = json.loads(resp.text)
                    f.close()
                    if respData['success']:
                        print(formatTime() + ' ' + file.name + ' Send To:', json.dumps(rData))
                        os.remove(file)
            time.sleep(1)
        else:
            print(formatTime() + ' finish')
            break


def cloudMatting():
    image_dir = os.path.join(rootPath, "photos")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    while True:
        entries = os.listdir(image_dir)
        if len(entries) > 0:
            file = get_latest_file()
            with open(file, 'rb') as f:
                # change 'https://cloud.saveimage.url' to your url
                resp = requests.post("https://cloud.saveimage.url", files={'file': f})
                respData = json.loads(resp.text)
                f.close()
                if respData['success']:
                    print(formatTime() + ' ' + file.name + ' Upload To CloudServer')
                    os.remove(file)
            time.sleep(1)
        else:
            print(formatTime() + ' finish')
            break


if __name__ == '__main__':
    cloudMatting()
    # edgeMatting()
