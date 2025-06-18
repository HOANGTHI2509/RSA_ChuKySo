# 🔐 File Transfer RSA - Ứng dụng truyền file với chữ ký số

Ứng dụng web cho phép truyền file an toàn với chữ ký số RSA, đảm bảo tính toàn vẹn và xác thực nguồn gốc file.

## ✨ Tính năng chính

- 🔑 **Chữ ký số RSA 2048-bit**: Mỗi file được ký bằng private key của người gửi
- 🌐 **Real-time với Socket.IO**: Thông báo trực tiếp khi có file mới
- 👥 **Quản lý người dùng**: Đăng ký/đăng nhập, hiển thị người online
- 📋 **Lịch sử chi tiết**: Theo dõi file đã gửi/nhận, admin xem tất cả
- 🔐 **Xác thực khóa**: Người gửi và nhận đều phải xác thực bằng khóa cá nhân
- 📱 **Giao diện responsive**: Thiết kế đẹp mắt, tương thích mobile
- 🛡️ **Bảo mật cao**: Không sử dụng database, chỉ lưu trữ JSON local

## 🔒 Nguyên lý hoạt động RSA

### Quy trình chữ ký số:
1. **Tạo khóa**: Mỗi user có cặp khóa RSA (private + public)
2. **Ký file**: Người gửi dùng **private key** của mình để ký file
3. **Xác minh**: Người nhận dùng **public key của người gửi** để xác minh chữ ký
4. **Đảm bảo**: Chỉ người có private key mới tạo được chữ ký hợp lệ

\`\`\`
Người gửi: File + Private Key → Chữ ký số
Người nhận: File + Chữ ký + Public Key người gửi → Xác minh
\`\`\`

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- pip

### Bước 1: Clone repository
\`\`\`bash
git clone https://github.com/yourusername/file-transfer-rsa.git
cd file-transfer-rsa
\`\`\`

### Bước 2: Cài đặt dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Bước 3: Chạy ứng dụng
\`\`\`bash
python app.py
\`\`\`

### Bước 4: Truy cập ứng dụng
Mở trình duyệt và truy cập: `http://localhost:5000`

## 📖 Hướng dẫn sử dụng

### 1. Đăng ký tài khoản
- Truy cập `/register`
- Nhập tên đăng nhập, mật khẩu và **khóa cá nhân**
- Khóa cá nhân sẽ không thể thay đổi sau khi tạo
- Hệ thống tự động tạo cặp khóa RSA cho bạn

### 2. Đăng nhập
- Sử dụng tên đăng nhập và mật khẩu đã tạo
- Sau khi đăng nhập, bạn sẽ xuất hiện trong danh sách "online"

### 3. Gửi file
- Vào trang "Gửi file"
- Chọn file cần gửi
- Chọn người nhận (không cần người đó online)
- Nhập **khóa cá nhân** để xác thực
- File sẽ được ký bằng private key của bạn

### 4. Nhận file
- Khi có file mới, bạn sẽ nhận thông báo real-time
- Vào Dashboard để xem file đã nhận
- Click "Xác minh" và nhập **khóa cá nhân** của bạn
- Hệ thống sử dụng **public key của người gửi** để xác minh chữ ký
- Nếu hợp lệ, bạn có thể tải file về

### 5. Xem lịch sử
- User thường: Xem file đã gửi/nhận của mình
- Admin: Xem tất cả file trong hệ thống

## 👨‍💼 Tài khoản Admin

Tài khoản đầu tiên có username `admin` sẽ tự động có quyền quản trị:
- Xem tất cả file trong hệ thống
- Truy cập bảng điều khiển admin
- Tải xuống bất kỳ file nào

## 🏗️ Cấu trúc dự án

\`\`\`
DuAn7/
├── app.py                 # Server chính Flask + SocketIO
├── requirements.txt       # Dependencies Python
├── README.md             # Tài liệu hướng dẫn
├── static/
│   ├── css/
│   │   └── style.css     # CSS responsive, đẹp mắt
│   ├── js/
│   │   └── main.js       # JavaScript tương tác
│   └── uploads/          # Thư mục lưu file upload
├── templates/
│   ├── index.html        # Trang đăng nhập
│   ├── register.html     # Trang đăng ký
│   ├── dashboard.html    # Dashboard chính
│   ├── admin.html        # Bảng điều khiển admin
│   ├── history.html      # Lịch sử truyền file
│   └── upload.html       # Trang gửi file
└── data/
    ├── users.json        # Thông tin người dùng
    ├── files.json        # Thông tin file
    └── keys/             # Thư mục lưu khóa RSA
\`\`\`

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - Đăng ký tài khoản mới
- `POST /api/login` - Đăng nhập
- `GET /logout` - Đăng xuất

### File Operations
- `POST /api/upload` - Upload và ký file
- `POST /api/verify` - Xác minh chữ ký file
- `GET /api/download/<file_id>` - Tải file về

### Pages
- `GET /` - Trang đăng nhập
- `GET /register` - Trang đăng ký
- `GET /dashboard` - Dashboard chính
- `GET /upload` - Trang gửi file
- `GET /history` - Lịch sử file
- `GET /admin` - Bảng điều khiển admin (chỉ admin)

## 🔐 Bảo mật

### Mã hóa và chữ ký
- **RSA 2048-bit**: Độ bảo mật cao
- **SHA-256**: Hash algorithm an toàn
- **PSS Padding**: Padding scheme bảo mật

### Xác thực
- **Session-based**: Quản lý phiên đăng nhập
- **Password hashing**: SHA-256 cho mật khẩu
- **Key verification**: Xác thực khóa cá nhân

### Lưu trữ
- **No SQL Database**: Chỉ sử dụng JSON files
- **Local storage**: Dữ liệu lưu trên server
- **File isolation**: Mỗi file có ID riêng

## 🌐 Socket.IO Events

### Client → Server
- `connect` - Kết nối WebSocket
- `disconnect` - Ngắt kết nối

### Server → Client
- `user_online` - Thông báo user online
- `user_offline` - Thông báo user offline
- `online_users` - Danh sách user online
- `new_file` - Thông báo file mới

## 🎨 Giao diện

### Thiết kế
- **Modern UI**: Gradient backgrounds, rounded corners
- **Responsive**: Tương thích desktop, tablet, mobile
- **Animations**: Smooth transitions và hover effects
- **Dark/Light**: Tối ưu cho cả hai chế độ

### Thành phần chính
- **Dashboard**: Tổng quan hệ thống
- **File Cards**: Hiển thị file đẹp mắt
- **Modal**: Popup xác minh file
- **Notifications**: Thông báo real-time
- **Tables**: Bảng lịch sử responsive

## 🚀 Deployment

### Local Development
\`\`\`bash
python app.py
# Truy cập: http://localhost:5000
\`\`\`

### Production (với Gunicorn)
\`\`\`bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 app:app
\`\`\`

### Docker (tùy chọn)
\`\`\`dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
\`\`\`

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Liên hệ

- **Author**: Your Name
- **Email**: your.email@example.com
- **Project Link**: [https://github.com/yourusername/file-transfer-rsa](https://github.com/yourusername/file-transfer-rsa)

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication
- [Cryptography](https://cryptography.io/) - RSA implementation
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon inspiration

---

**⚠️ Lưu ý bảo mật**: Đây là ứng dụng demo. Trong môi trường production, cần thêm các biện pháp bảo mật như HTTPS, rate limiting, input validation, và secure session management.
