from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# Tạo thư mục cần thiết
os.makedirs('data', exist_ok=True)
os.makedirs('data/keys', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Khởi tạo file JSON nếu chưa tồn tại
def init_json_files():
    if not os.path.exists('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists('data/files.json'):
        with open('data/files.json', 'w') as f:
            json.dump({}, f)

init_json_files()

# Lưu trữ người dùng online
online_users = {}

def load_users():
    with open('data/users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=2)

def load_files():
    with open('data/files.json', 'r') as f:
        return json.load(f)

def save_files(files):
    with open('data/files.json', 'w') as f:
        json.dump(files, f, indent=2)

def generate_rsa_keys():
    """Tạo cặp khóa RSA"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Serialize keys
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode(), public_pem.decode()

def sign_file(file_path, private_key_pem):
    """Ký file bằng private key"""
    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        signature = private_key.sign(
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    except Exception as e:
        print(f"Error signing file: {e}")
        return None

def verify_signature(file_path, signature_b64, public_key_pem):
    """
    Xác minh chữ ký file bằng PUBLIC KEY của người gửi
    - File được ký bằng PRIVATE KEY của người gửi
    - Xác minh bằng PUBLIC KEY của người gửi
    - Đây là nguyên lý cơ bản của chữ ký số RSA
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        signature = base64.b64decode(signature_b64)
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Sử dụng PUBLIC KEY của người gửi để xác minh chữ ký
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    users = load_users()
    files = load_files()
    
    # Lấy file được gửi cho user hiện tại
    received_files = []
    for file_id, file_info in files.items():
        if file_info['receiver'] == session['username']:
            received_files.append(file_info)
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         is_admin=users[session['username']]['is_admin'],
                         online_users=list(online_users.keys()),
                         all_users=list(users.keys()),
                         received_files=received_files)

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    users = load_users()
    if not users[session['username']]['is_admin']:
        return redirect(url_for('dashboard'))
    
    files = load_files()
    return render_template('admin.html', files=files, online_users=list(online_users.keys()))

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    users = load_users()
    files = load_files()
    
    if users[session['username']]['is_admin']:
        # Admin xem tất cả lịch sử
        user_files = list(files.values())
    else:
        # User chỉ xem lịch sử của mình
        user_files = []
        for file_info in files.values():
            if file_info['sender'] == session['username'] or file_info['receiver'] == session['username']:
                user_files.append(file_info)
    
    return render_template('history.html', files=user_files, is_admin=users[session['username']]['is_admin'])

@app.route('/upload')
def upload():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    users = load_users()
    return render_template('upload.html', 
                         all_users=list(users.keys()),
                         current_user=session['username'],
                         is_admin=users[session['username']]['is_admin'])

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_key = data.get('user_key')
    
    if not username or not password or not user_key:
        return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'})
    
    users = load_users()
    
    if username in users:
        return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại'})
    
    # Tạo cặp khóa RSA
    private_key, public_key = generate_rsa_keys()
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Lưu thông tin user
    users[username] = {
        'password': password_hash,
        'user_key': user_key,
        'private_key': private_key,
        'public_key': public_key,
        'is_admin': username == 'admin',
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    
    return jsonify({'success': True, 'message': 'Đăng ký thành công'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'})
    
    users = load_users()
    
    if username not in users:
        return jsonify({'success': False, 'message': 'Tên đăng nhập không tồn tại'})
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if users[username]['password'] != password_hash:
        return jsonify({'success': False, 'message': 'Mật khẩu không đúng'})
    
    session['username'] = username
    return jsonify({'success': True, 'message': 'Đăng nhập thành công'})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file được chọn'})
    
    file = request.files['file']
    receiver = request.form.get('receiver')
    user_key = request.form.get('user_key')
    
    if not receiver or not user_key:
        return jsonify({'success': False, 'message': 'Vui lòng chọn người nhận và nhập khóa'})
    
    users = load_users()
    
    # Kiểm tra khóa người gửi
    if users[session['username']]['user_key'] != user_key:
        return jsonify({'success': False, 'message': 'Khóa người gửi không đúng'})
    
    if receiver not in users:
        return jsonify({'success': False, 'message': 'Người nhận không tồn tại'})
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Không có file được chọn'})
    
    try:
        # Lưu file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(file_path)
        
        # Ký file
        private_key = users[session['username']]['private_key']
        signature = sign_file(file_path, private_key)
        
        if not signature:
            os.remove(file_path)
            return jsonify({'success': False, 'message': 'Lỗi khi ký file'})
        
        # Lưu thông tin file
        files = load_files()
        files[file_id] = {
            'id': file_id,
            'filename': filename,
            'sender': session['username'],
            'receiver': receiver,
            'file_path': file_path,
            'signature': signature,
            'timestamp': datetime.now().isoformat(),
            'verified': False
        }
        
        save_files(files)
        
        # Thông báo cho người nhận qua socket
        socketio.emit('new_file', {
            'sender': session['username'],
            'filename': filename,
            'file_id': file_id
        }, room=receiver)
        
        return jsonify({'success': True, 'message': 'Gửi file thành công'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi khi gửi file: {str(e)}'})

@app.route('/api/verify', methods=['POST'])
def api_verify():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'})
    
    data = request.json
    file_id = data.get('file_id')
    user_key = data.get('user_key')
    
    if not file_id or not user_key:
        return jsonify({'success': False, 'message': 'Thiếu thông tin'})
    
    users = load_users()
    files = load_files()
    
    if file_id not in files:
        return jsonify({'success': False, 'message': 'File không tồn tại'})
    
    file_info = files[file_id]
    
    # Kiểm tra quyền truy cập
    if file_info['receiver'] != session['username']:
        return jsonify({'success': False, 'message': 'Không có quyền truy cập file này'})
    
    # Kiểm tra khóa người nhận
    if users[session['username']]['user_key'] != user_key:
        return jsonify({'success': False, 'message': 'Khóa người nhận không đúng'})
    
    # Lấy PUBLIC KEY của người gửi để xác minh chữ ký
    # (File được ký bằng PRIVATE KEY của người gửi)
    sender_public_key = users[file_info['sender']]['public_key']
    is_valid = verify_signature(file_info['file_path'], file_info['signature'], sender_public_key)
    
    # Cập nhật trạng thái xác minh
    files[file_id]['verified'] = is_valid
    files[file_id]['verified_at'] = datetime.now().isoformat()
    save_files(files)
    
    if is_valid:
        return jsonify({'success': True, 'message': 'Xác minh chữ ký thành công', 'download_url': f'/api/download/{file_id}'})
    else:
        return jsonify({'success': False, 'message': 'Chữ ký không hợp lệ'})

@app.route('/api/download/<file_id>')
def api_download(file_id):
    if 'username' not in session:
        return redirect(url_for('index'))
    
    files = load_files()
    
    if file_id not in files:
        return "File không tồn tại", 404
    
    file_info = files[file_id]
    
    # Kiểm tra quyền truy cập
    if file_info['receiver'] != session['username'] and not load_users()[session['username']]['is_admin']:
        return "Không có quyền truy cập", 403
    
    return send_file(file_info['file_path'], as_attachment=True, download_name=file_info['filename'])

@app.route('/logout')
def logout():
    username = session.get('username')
    if username and username in online_users:
        del online_users[username]
        socketio.emit('user_offline', {'username': username}, broadcast=True)
    
    session.clear()
    return redirect(url_for('index'))

@socketio.on('connect')
def on_connect():
    if 'username' in session:
        username = session['username']
        online_users[username] = request.sid
        join_room(username)
        emit('user_online', {'username': username}, broadcast=True)
        emit('online_users', {'users': list(online_users.keys())}, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    if 'username' in session:
        username = session['username']
        if username in online_users:
            del online_users[username]
            leave_room(username)
            emit('user_offline', {'username': username}, broadcast=True)
            emit('online_users', {'users': list(online_users.keys())}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
