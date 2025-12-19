# 📁 File Transfer Client–Server (Python Socket + GUI)

## 📌 Mô tả dự án
Dự án xây dựng **ứng dụng truyền file theo mô hình Client–Server** sử dụng **Python Socket TCP** kết hợp **giao diện đồ họa Tkinter**.

Hệ thống cho phép:
- Server khởi động và lắng nghe kết nối từ nhiều Client
- Client kết nối đến Server và gửi file
- Hiển thị tiến trình truyền file (progress bar)
- Server lưu file nhận được và thống kê số lượng, dung lượng file
- Giao diện trực quan, dễ sử dụng

Dự án phục vụ cho **môn Lập trình mạng**, giúp hiểu rõ cơ chế giao tiếp mạng TCP, xử lý đa luồng và truyền dữ liệu qua socket.

---

## 👥 Danh sách thành viên
- Sinh viên thực hiện: nhóm 9: Trung Kiên, Hoài Trinh, Bảo Hân, Thu Hiên, Khamchanh
- Môn học: **Lập trình mạng**
- Giảng viên hướng dẫn: TS. Nguyễn Hoàng Hải

---

## 🛠️ Công nghệ sử dụng
- **Ngôn ngữ:** Python 3
- **Lập trình mạng:** socket (TCP)
- **Giao diện:** tkinter, ttk
- **Đa luồng:** threading
- **Hệ điều hành:** Windows / Linux / macOS

> Dự án **không sử dụng thư viện bên ngoài**, chỉ dùng thư viện chuẩn của Python.

---

## 📂 Cấu trúc thư mục
```text
.
├── server.py          # Chương trình Server (GUI)
├── client.py          # Chương trình Client (GUI)
├── received_files/    # Thư mục lưu file nhận (tự tạo khi chạy server)
└── README.md          # Tài liệu mô tả dự án
```
---

## ▶️ Hướng dẫn cài đặt và chạy dự án

### Bước 1: Cài đặt Python
Dự án yêu cầu **Python 3.8 trở lên**.

Kiểm tra Python:
```bash
python --version
```
### Bước 2: Chuẩn bị mã nguồn
- Giải nén tệp, cấu trúc thư mục như sau
guifilequaGUI/
├── server.py
├── client.py
└── README.md

### Bước 3: Chạy server
python server.py
Ấn start server

### Bước 4: Chạy client
python client.py
Nhập IP và port của server
Chọn kết nối
Chọn file và gửi file

### Bước 5: Kiểm tra kết quae
Kiểm tra trong thư mục received_files

