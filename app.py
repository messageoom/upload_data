from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
import uuid

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    # 图片格式
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico',
    # 文档格式
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    # 数据格式
    'csv', 'json', 'xml',
    # 压缩文件
    'zip', 'rar', '7z',
    # 其他常见格式
    'mp3', 'mp4', 'avi', 'mov', 'wmv'
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key-here'  # 在生产环境中应该使用更安全的密钥

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查是否有文件被提交
        if 'file' not in request.files:
            flash('没有选择文件')
            return redirect(request.url)
        
        file = request.files['file']
        
        # 如果用户没有选择文件，浏览器也会提交空部分
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)
        
        # 如果文件存在且符合要求
        if file and allowed_file(file.filename):
            # 使用安全的文件名
            filename = secure_filename(file.filename)
            
            # 生成唯一文件名以避免冲突
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = str(uuid.uuid4()) + '.' + file_extension
            
            # 保存文件
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            flash('文件上传成功', 'success')
            return redirect(url_for('upload_file'))
        else:
            flash('不支持的文件类型')
    
    # 获取已上传的文件列表
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # 按文件类型分类
    file_categories = {
        'images': [],
        'documents': [],
        'data': [],
        'archives': [],
        'media': [],
        'others': []
    }
    
    # 定义文件类型分类
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'}
    document_extensions = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
    data_extensions = {'csv', 'json', 'xml'}
    archive_extensions = {'zip', 'rar', '7z'}
    media_extensions = {'mp3', 'mp4', 'avi', 'mov', 'wmv'}
    
    for file in uploaded_files:
        if '.' in file:
            extension = file.rsplit('.', 1)[1].lower()
            if extension in image_extensions:
                file_categories['images'].append(file)
            elif extension in document_extensions:
                file_categories['documents'].append(file)
            elif extension in data_extensions:
                file_categories['data'].append(file)
            elif extension in archive_extensions:
                file_categories['archives'].append(file)
            elif extension in media_extensions:
                file_categories['media'].append(file)
            else:
                file_categories['others'].append(file)
        else:
            file_categories['others'].append(file)
    
    return render_template('index.html', file_categories=file_categories)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # 获取本机IP地址
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"服务器将在以下地址运行: http://{local_ip}:5000")
    print("按 Ctrl+C 停止服务器")
    
    # 在局域网内运行，host设置为'0.0.0.0'
    app.run(host='0.0.0.0', port=5000, debug=True)
