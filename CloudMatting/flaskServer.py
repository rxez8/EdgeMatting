import json

from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['TEMP_FOLDER'] = 'temp/'
app.config['MATTING_FOLDER'] = 'matting/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = 'supersecretkey'  # 用于闪现消息（flash messages）

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['MATTING_FOLDER']):
    os.makedirs(app.config['MATTING_FOLDER'])
if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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


@app.route('/imagematting', methods=['POST'])
def matting_upload_file():
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
        filename = str(uuid.uuid4())
        file.save(os.path.join(app.config['TEMP_FOLDER'], filename + ext))
        file.close()
        os.rename(os.path.join(app.config['TEMP_FOLDER'], filename + ext),
                  os.path.join(app.config['UPLOAD_FOLDER'], filename + ext))
        return jsonify({
            'success': True
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Please select a file.'
        })


@app.route('/save', methods=['POST'])
def save_upload_file():
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
        filename = file.filename
        file.save(os.path.join(app.config['MATTING_FOLDER'], filename))
        file.close()
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
    app.run()
