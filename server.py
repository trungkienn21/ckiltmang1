import socket
import threading
import os
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

class FileTransferServer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Server 🖥️")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.server_socket = None
        self.is_running = False
        self.save_directory = "received_files"
        
        # Tạo thư mục lưu file nếu chưa tồn tại
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        
        self.setup_gui()
    
    def setup_gui(self):
        # Frame cấu hình
        config_frame = LabelFrame(self.root, text="⚙️ Cấu hình Server", padx=10, pady=10)
        config_frame.pack(padx=10, pady=10, fill="x")
        
        Label(config_frame, text="Host:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = Entry(config_frame, width=30)
        self.host_entry.insert(0, "0.0.0.0")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = Entry(config_frame, width=30)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Nút điều khiển
        btn_frame = Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_btn = Button(btn_frame, text="▶️ Khởi động Server", 
                                command=self.start_server, bg="#4CAF50", fg="white",
                                font=("Arial", 10, "bold"), width=15)
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = Button(btn_frame, text="⏹️ Dừng Server", 
                               command=self.stop_server, bg="#f44336", fg="white",
                               font=("Arial", 10, "bold"), width=15, state=DISABLED)
        self.stop_btn.pack(side=LEFT, padx=5)
        
        # Trạng thái
        status_frame = LabelFrame(self.root, text="📊 Trạng thái", padx=10, pady=10)
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.status_label = Label(status_frame, text="⚫ Server chưa khởi động", 
                                  font=("Arial", 11, "bold"), fg="red")
        self.status_label.pack()
        
        # Nhật ký hoạt động
        log_frame = LabelFrame(self.root, text="📝 Nhật ký hoạt động", padx=10, pady=10)
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                   font=("Courier", 9), state=DISABLED)
        self.log_text.pack(fill="both", expand=True)
        
        # Thống kê
        stats_frame = LabelFrame(self.root, text="📈 Thống kê", padx=10, pady=5)
        stats_frame.pack(padx=10, pady=5, fill="x")
        
        self.files_received_label = Label(stats_frame, text="File đã nhận: 0", 
                                          font=("Arial", 10))
        self.files_received_label.pack(side=LEFT, padx=20)
        
        self.total_size_label = Label(stats_frame, text="Tổng dung lượng: 0 MB", 
                                      font=("Arial", 10))
        self.total_size_label.pack(side=LEFT, padx=20)
        
        self.files_received = 0
        self.total_size = 0
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Sử dụng after() để update UI thread-safe
        self.root.after(0, self._update_log, log_entry)
    
    def _update_log(self, log_entry):
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, log_entry)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def update_stats(self, file_size):
        self.files_received += 1
        self.total_size += file_size
        
        # Update UI thread-safe
        self.root.after(0, self._update_stats_ui)
    
    def _update_stats_ui(self):
        self.files_received_label.config(text=f"File đã nhận: {self.files_received}")
        self.total_size_label.config(text=f"Tổng dung lượng: {self.total_size / (1024*1024):.2f} MB")
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_server(self):
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            
            self.is_running = True
            
            local_ip = self.get_local_ip()
            self.status_label.config(text=f"🟢 Server đang chạy tại {host}:{port}", fg="green")
            self.log_message(f"✅ Server khởi động thành công tại {host}:{port}")
            self.log_message(f"💡 Client cần kết nối tới: {local_ip}:{port}")
            
            self.start_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
            self.host_entry.config(state=DISABLED)
            self.port_entry.config(state=DISABLED)
            
            # Bắt đầu luồng lắng nghe kết nối
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi động server: {str(e)}")
            self.log_message(f"❌ Lỗi khởi động: {str(e)}")
    
    def stop_server(self):
        self.is_running = False
        
        if self.server_socket:
            self.server_socket.close()
        
        self.status_label.config(text="⚫ Server đã dừng", fg="red")
        self.log_message("🛑 Server đã dừng hoạt động")
        
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.host_entry.config(state=NORMAL)
        self.port_entry.config(state=NORMAL)
    
    def accept_connections(self):
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                self.log_message(f"🔗 Kết nối mới từ {address[0]}:{address[1]}")
                
                # Xử lý client trong luồng riêng
                client_thread = threading.Thread(target=self.handle_client, 
                                                args=(client_socket, address), daemon=True)
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    self.log_message(f"❌ Lỗi kết nối: {str(e)}")
                break
    
    def get_unique_filepath(self, filename):
        """Tạo tên file unique nếu file đã tồn tại"""
        filepath = os.path.join(self.save_directory, filename)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(self.save_directory, f"{name}_{counter}{ext}")
                counter += 1
        return filepath
    
    def handle_client(self, client_socket, address):
        filepath = None
        try:
            # Set timeout để tránh treo
            client_socket.settimeout(300)  # 5 phút timeout
            
            # Nhận tên file
            filename = client_socket.recv(1024).decode('utf-8', errors='ignore')
            client_socket.send(b"OK")
            
            # Nhận kích thước file
            filesize = int(client_socket.recv(1024).decode('utf-8'))
            client_socket.send(b"OK")
            
            self.log_message(f"📥 Đang nhận file: {filename} ({filesize / (1024*1024):.2f} MB)")
            
            # Tạo filepath unique
            filepath = self.get_unique_filepath(filename)
            received = 0
            last_logged_progress = -1  # ← KEY FIX: Theo dõi progress đã log
            
            with open(filepath, 'wb') as f:
                while received < filesize:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    
                    # Tính tiến trình và chỉ log khi đạt mốc 10%, 20%, 30%...
                    progress = int((received / filesize) * 100)
                    
                    # ← KEY FIX: Chỉ log khi progress chia hết cho 10 VÀ chưa log mốc này
                    if progress % 10 == 0 and progress != last_logged_progress and progress > 0:
                        self.log_message(f"   ⏳ Tiến trình: {progress}%")
                        last_logged_progress = progress
            
            if received == filesize:
                client_socket.send(b"SUCCESS")
                self.log_message(f"✅ Nhận file thành công: {os.path.basename(filepath)}")
                self.update_stats(filesize)
            else:
                # Xóa file lỗi nếu nhận không đủ
                if os.path.exists(filepath):
                    os.remove(filepath)
                client_socket.send(b"FAILED")
                self.log_message(f"❌ Nhận file thất bại: {filename} (chỉ nhận được {received}/{filesize} bytes)")
            
        except socket.timeout:
            self.log_message(f"⏱️ Timeout khi nhận file từ {address}")
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            self.log_message(f"❌ Lỗi xử lý client {address}: {str(e)}")
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        finally:
            client_socket.close()

if __name__ == "__main__":
    root = Tk()
    app = FileTransferServer(root)
    root.mainloop()