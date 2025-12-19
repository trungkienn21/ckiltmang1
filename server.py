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
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        self.server_socket = None
        self.is_running = False
        self.save_directory = "received_files"
        self.chat_clients = []  # Danh sách client chat
        
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        
        self.files_received = 0
        self.total_size = 0
        
        self.setup_gui()
    
    def setup_gui(self):
        # Container chính - chia 2 cột
        main_container = Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cột trái - Server Control
        left_frame = Frame(main_container, width=450)
        left_frame.pack(side=LEFT, fill="both", expand=True, padx=(0, 5))
        
        # Cột phải - Chat
        right_frame = Frame(main_container, width=440)
        right_frame.pack(side=RIGHT, fill="both", expand=True, padx=(5, 0))
        
        # === CỘT TRÁI - SERVER CONTROL ===
        # Frame cấu hình
        config_frame = LabelFrame(left_frame, text="⚙️ Cấu hình Server", padx=10, pady=10)
        config_frame.pack(padx=5, pady=5, fill="x")
        
        Label(config_frame, text="Host:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = Entry(config_frame, width=20)
        self.host_entry.insert(0, "0.0.0.0")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = Entry(config_frame, width=20)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Nút điều khiển
        btn_frame = Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_btn = Button(btn_frame, text="▶️ Khởi động", 
                                command=self.start_server, bg="#4CAF50", fg="white",
                                font=("Arial", 9, "bold"), width=12)
        self.start_btn.pack(side=LEFT, padx=5)
        
        self.stop_btn = Button(btn_frame, text="⏹️ Dừng", 
                               command=self.stop_server, bg="#f44336", fg="white",
                               font=("Arial", 9, "bold"), width=12, state=DISABLED)
        self.stop_btn.pack(side=LEFT, padx=5)
        
        # Trạng thái
        status_frame = LabelFrame(left_frame, text="📊 Trạng thái", padx=10, pady=10)
        status_frame.pack(padx=5, pady=5, fill="x")
        
        self.status_label = Label(status_frame, text="⚫ Server chưa khởi động", 
                                  font=("Arial", 10, "bold"), fg="red")
        self.status_label.pack()
        
        # Thống kê
        stats_frame = LabelFrame(left_frame, text="📈 Thống kê", padx=10, pady=5)
        stats_frame.pack(padx=5, pady=5, fill="x")
        
        stats_inner = Frame(stats_frame)
        stats_inner.pack()
        
        self.files_received_label = Label(stats_inner, text="File đã nhận: 0", 
                                          font=("Arial", 9))
        self.files_received_label.grid(row=0, column=0, padx=10)
        
        self.total_size_label = Label(stats_inner, text="Tổng dung lượng: 0 MB", 
                                      font=("Arial", 9))
        self.total_size_label.grid(row=0, column=1, padx=10)
        
        self.clients_label = Label(stats_inner, text="Client chat: 0", 
                                   font=("Arial", 9))
        self.clients_label.grid(row=0, column=2, padx=10)
        
        # Nhật ký hoạt động
        log_frame = LabelFrame(left_frame, text="📝 Nhật ký hoạt động", padx=10, pady=10)
        log_frame.pack(padx=5, pady=5, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                   font=("Courier", 8), state=DISABLED)
        self.log_text.pack(fill="both", expand=True)
        
        # === CỘT PHẢI - CHAT ===
        chat_main_frame = LabelFrame(right_frame, text="💬 Chat với Client", padx=10, pady=10)
        chat_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Khung hiển thị tin nhắn
        self.chat_display = scrolledtext.ScrolledText(chat_main_frame, height=25, 
                                                       font=("Arial", 9), state=DISABLED,
                                                       wrap=WORD)
        self.chat_display.pack(fill="both", expand=True, pady=(0, 10))
        
        # Cấu hình tag cho tin nhắn
        self.chat_display.tag_config("me", foreground="#4CAF50", font=("Arial", 9, "bold"))
        self.chat_display.tag_config("client", foreground="#2196F3", font=("Arial", 9, "bold"))
        self.chat_display.tag_config("system", foreground="#FF9800", font=("Arial", 9, "italic"))
        
        # Khung nhập tin nhắn
        input_frame = Frame(chat_main_frame)
        input_frame.pack(fill="x")
        
        self.chat_entry = Entry(input_frame, font=("Arial", 10))
        self.chat_entry.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))
        self.chat_entry.bind("<Return>", lambda e: self.send_message())
        self.chat_entry.config(state=DISABLED)
        
        self.send_msg_btn = Button(input_frame, text="Gửi", command=self.send_message,
                                   bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
                                   width=8, state=DISABLED)
        self.send_msg_btn.pack(side=RIGHT)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.root.after(0, self._update_log, log_entry)
    
    def _update_log(self, log_entry):
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, log_entry)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def add_chat_message(self, message, sender="system"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.config(state=NORMAL)
        
        if sender == "me":
            self.chat_display.insert(END, f"[{timestamp}] Bạn: ", "me")
            self.chat_display.insert(END, f"{message}\n")
        elif sender == "client":
            self.chat_display.insert(END, f"[{timestamp}] Client: ", "client")
            self.chat_display.insert(END, f"{message}\n")
        else:
            self.chat_display.insert(END, f"[{timestamp}] ", "system")
            self.chat_display.insert(END, f"{message}\n", "system")
        
        self.chat_display.see(END)
        self.chat_display.config(state=DISABLED)
    
    def send_message(self):
        message = self.chat_entry.get().strip()
        if not message or not self.chat_clients:
            return
        
        # Gửi tin nhắn đến tất cả client
        disconnected = []
        for client in self.chat_clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                disconnected.append(client)
        
        # Xóa các client đã ngắt kết nối
        for client in disconnected:
            self.chat_clients.remove(client)
            self.update_client_count()
        
        self.add_chat_message(message, "me")
        self.chat_entry.delete(0, END)
    
    def update_stats(self, file_size):
        self.files_received += 1
        self.total_size += file_size
        self.root.after(0, self._update_stats_ui)
    
    def _update_stats_ui(self):
        self.files_received_label.config(text=f"File đã nhận: {self.files_received}")
        self.total_size_label.config(text=f"Tổng dung lượng: {self.total_size / (1024*1024):.2f} MB")
    
    def update_client_count(self):
        self.root.after(0, lambda: self.clients_label.config(text=f"Client chat: {len(self.chat_clients)}"))
    
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
            self.chat_entry.config(state=NORMAL)
            self.send_msg_btn.config(state=NORMAL)
            
            # Bắt đầu luồng lắng nghe kết nối
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể khởi động server: {str(e)}")
            self.log_message(f"❌ Lỗi khởi động: {str(e)}")
    
    def stop_server(self):
        self.is_running = False
        
        # Đóng tất cả chat clients
        for client in self.chat_clients:
            try:
                client.close()
            except:
                pass
        self.chat_clients.clear()
        
        if self.server_socket:
            self.server_socket.close()
        
        self.status_label.config(text="⚫ Server đã dừng", fg="red")
        self.log_message("🛑 Server đã dừng hoạt động")
        
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.host_entry.config(state=NORMAL)
        self.port_entry.config(state=NORMAL)
        self.chat_entry.config(state=DISABLED)
        self.send_msg_btn.config(state=DISABLED)
        self.update_client_count()
    
    def accept_connections(self):
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                self.log_message(f"🔗 Kết nối mới từ {address[0]}:{address[1]}")
                
                # Nhận identifier để biết là chat hay file transfer
                identifier = client_socket.recv(1024).decode('utf-8')
                
                if identifier == "CHAT_MODE":
                    # Xử lý chat client
                    self.chat_clients.append(client_socket)
                    self.update_client_count()
                    self.root.after(0, self.add_chat_message, f"Client {address[0]} đã kết nối")
                    
                    chat_thread = threading.Thread(target=self.handle_chat_client, 
                                                   args=(client_socket, address), daemon=True)
                    chat_thread.start()
                    
                elif identifier == "FILE_MODE":
                    # Xác nhận và xử lý file transfer
                    client_socket.send(b"OK")
                    file_thread = threading.Thread(target=self.handle_file_client, 
                                                   args=(client_socket, address), daemon=True)
                    file_thread.start()
                
            except Exception as e:
                if self.is_running:
                    self.log_message(f"❌ Lỗi kết nối: {str(e)}")
                break
    
    def handle_chat_client(self, client_socket, address):
        while self.is_running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    self.root.after(0, self.add_chat_message, message, "client")
                else:
                    break
            except:
                break
        
        # Xóa client khi ngắt kết nối
        if client_socket in self.chat_clients:
            self.chat_clients.remove(client_socket)
            self.update_client_count()
            self.root.after(0, self.add_chat_message, f"Client {address[0]} đã ngắt kết nối")
        
        try:
            client_socket.close()
        except:
            pass
    
    def get_unique_filepath(self, filename):
        filepath = os.path.join(self.save_directory, filename)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(self.save_directory, f"{name}_{counter}{ext}")
                counter += 1
        return filepath
    
    def handle_file_client(self, client_socket, address):
        filepath = None
        try:
            client_socket.settimeout(300)
            
            # Nhận tên file
            filename = client_socket.recv(1024).decode('utf-8', errors='ignore')
            client_socket.send(b"OK")
            
            # Nhận kích thước file
            filesize = int(client_socket.recv(1024).decode('utf-8'))
            client_socket.send(b"OK")
            
            self.log_message(f"📥 Đang nhận file: {filename} ({filesize / (1024*1024):.2f} MB)")
            
            filepath = self.get_unique_filepath(filename)
            received = 0
            last_logged_progress = -1
            
            with open(filepath, 'wb') as f:
                while received < filesize:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    
                    progress = int((received / filesize) * 100)
                    
                    if progress % 10 == 0 and progress != last_logged_progress and progress > 0:
                        self.log_message(f"   ⏳ Tiến trình: {progress}%")
                        last_logged_progress = progress
            
            if received == filesize:
                client_socket.send(b"SUCCESS")
                self.log_message(f"✅ Nhận file thành công: {os.path.basename(filepath)}")
                self.update_stats(filesize)
            else:
                if os.path.exists(filepath):
                    os.remove(filepath)
                client_socket.send(b"FAILED")
                self.log_message(f"❌ Nhận file thất bại: {filename}")
            
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