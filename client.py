import socket
import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

class FileTransferClient:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Client 💻")
        self.root.geometry("850x650")
        self.root.resizable(False, False)
        
        self.selected_file = None
        self.is_connected = False
        self.chat_socket = None
        self.username = "Client"
        
        self.setup_gui()
    
    def setup_gui(self):
        # Container chính - chia 2 cột
        main_container = Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cột trái - File Transfer
        left_frame = Frame(main_container, width=420)
        left_frame.pack(side=LEFT, fill="both", expand=True, padx=(0, 5))
        
        # Cột phải - Chat
        right_frame = Frame(main_container, width=420)
        right_frame.pack(side=RIGHT, fill="both", expand=True, padx=(5, 0))
        
        # === CỘT TRÁI - FILE TRANSFER ===
        # Frame kết nối
        connection_frame = LabelFrame(left_frame, text="🔗 Kết nối Server", padx=10, pady=10)
        connection_frame.pack(padx=5, pady=5, fill="x")
        
        Label(connection_frame, text="Server IP:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = Entry(connection_frame, width=20)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(connection_frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = Entry(connection_frame, width=20)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.connect_btn = Button(connection_frame, text="🔌 Kết nối", 
                                  command=self.toggle_connection, bg="#2196F3", fg="white",
                                  font=("Arial", 9, "bold"), width=12)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.connection_status = Label(connection_frame, text="⚫ Chưa kết nối", 
                                       font=("Arial", 9, "bold"), fg="red")
        self.connection_status.grid(row=3, column=0, columnspan=2)
        
        # Frame chọn file
        file_frame = LabelFrame(left_frame, text="📁 Chọn File", padx=10, pady=10)
        file_frame.pack(padx=5, pady=5, fill="x")
        
        self.file_path_entry = Entry(file_frame, width=30, state="readonly")
        self.file_path_entry.pack(side=LEFT, padx=5)
        
        Button(file_frame, text="📂 Chọn", command=self.select_file,
               bg="#4CAF50", fg="white", font=("Arial", 8, "bold")).pack(side=LEFT, padx=5)
        
        # Thông tin file
        info_frame = LabelFrame(left_frame, text="ℹ️ Thông tin File", padx=10, pady=10)
        info_frame.pack(padx=5, pady=5, fill="x")
        
        self.file_name_label = Label(info_frame, text="Tên file: Chưa chọn", 
                                     font=("Arial", 8), anchor="w")
        self.file_name_label.pack(fill="x", pady=2)
        
        self.file_size_label = Label(info_frame, text="Kích thước: 0 MB", 
                                     font=("Arial", 8), anchor="w")
        self.file_size_label.pack(fill="x", pady=2)
        
        # Nút gửi file
        send_frame = Frame(left_frame)
        send_frame.pack(padx=5, pady=5)
        
        self.send_btn = Button(send_frame, text="📤 Gửi File", command=self.send_file,
                              bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                              width=18, height=2, state=DISABLED)
        self.send_btn.pack()
        
        # Progress bar
        progress_frame = LabelFrame(left_frame, text="⏳ Tiến trình", padx=10, pady=10)
        progress_frame.pack(padx=5, pady=5, fill="x")
        
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=350)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = Label(progress_frame, text="0%", font=("Arial", 9, "bold"))
        self.progress_label.pack()
        
        # Log
        log_frame = LabelFrame(left_frame, text="📋 Trạng thái", padx=10, pady=10)
        log_frame.pack(padx=5, pady=5, fill="both", expand=True)
        
        self.log_text = Text(log_frame, height=6, font=("Courier", 8), state=DISABLED)
        self.log_text.pack(fill="both", expand=True)
        
        # === CỘT PHẢI - CHAT ===
        chat_main_frame = LabelFrame(right_frame, text="💬 Chat với Server", padx=10, pady=10)
        chat_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Khung hiển thị tin nhắn
        self.chat_display = scrolledtext.ScrolledText(chat_main_frame, height=25, 
                                                       font=("Arial", 9), state=DISABLED,
                                                       wrap=WORD)
        self.chat_display.pack(fill="both", expand=True, pady=(0, 10))
        
        # Cấu hình tag cho tin nhắn
        self.chat_display.tag_config("me", foreground="#2196F3", font=("Arial", 9, "bold"))
        self.chat_display.tag_config("server", foreground="#4CAF50", font=("Arial", 9, "bold"))
        self.chat_display.tag_config("system", foreground="#FF9800", font=("Arial", 9, "italic"))
        
        # Khung nhập tin nhắn
        input_frame = Frame(chat_main_frame)
        input_frame.pack(fill="x")
        
        self.chat_entry = Entry(input_frame, font=("Arial", 10))
        self.chat_entry.pack(side=LEFT, fill="x", expand=True, padx=(0, 5))
        self.chat_entry.bind("<Return>", lambda e: self.send_message())
        self.chat_entry.config(state=DISABLED)
        
        self.send_msg_btn = Button(input_frame, text="Gửi", command=self.send_message,
                                   bg="#2196F3", fg="white", font=("Arial", 9, "bold"),
                                   width=8, state=DISABLED)
        self.send_msg_btn.pack(side=RIGHT)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
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
        elif sender == "server":
            self.chat_display.insert(END, f"[{timestamp}] Server: ", "server")
            self.chat_display.insert(END, f"{message}\n")
        else:
            self.chat_display.insert(END, f"[{timestamp}] ", "system")
            self.chat_display.insert(END, f"{message}\n", "system")
        
        self.chat_display.see(END)
        self.chat_display.config(state=DISABLED)
    
    def toggle_connection(self):
        if not self.is_connected:
            self.connect_to_server()
        else:
            self.disconnect()
    
    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        try:
            # Socket cho chat
            self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_socket.settimeout(5)  # Timeout 5 giây khi kết nối
            self.chat_socket.connect((host, port))
            
            # Gửi identifier để server biết đây là chat socket
            self.chat_socket.send(b"CHAT_MODE")
            self.log_message("📡 Đã gửi CHAT_MODE identifier")
            
            # Chờ xác nhận từ server (nếu có)
            try:
                self.chat_socket.settimeout(2)
                confirm = self.chat_socket.recv(1024)
                if confirm:
                    self.log_message(f"📡 Nhận xác nhận: {confirm.decode('utf-8', errors='ignore')}")
            except socket.timeout:
                self.log_message("📡 Không nhận được xác nhận (timeout) - tiếp tục")
            except:
                pass
            
            # Đặt lại timeout thành None để không bị ngắt kết nối
            self.chat_socket.settimeout(None)
            
            self.is_connected = True
            self.connection_status.config(text="🟢 Đã kết nối", fg="green")
            self.connect_btn.config(text="🔌 Ngắt kết nối", bg="#f44336")
            self.send_btn.config(state=NORMAL if self.selected_file else DISABLED)
            self.chat_entry.config(state=NORMAL)
            self.send_msg_btn.config(state=NORMAL)
            
            self.log_message(f"✅ Kết nối thành công đến {host}:{port}")
            self.add_chat_message(f"Đã kết nối đến server {host}:{port}")
            
            self.host_entry.config(state=DISABLED)
            self.port_entry.config(state=DISABLED)
            
            # Bắt đầu nhận tin nhắn từ server
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except socket.timeout:
            error_msg = "Timeout khi kết nối đến server"
            messagebox.showerror("Lỗi kết nối", error_msg)
            self.log_message(f"❌ {error_msg}")
            if self.chat_socket:
                try:
                    self.chat_socket.close()
                except:
                    pass
                self.chat_socket = None
        except ConnectionRefusedError:
            error_msg = "Server từ chối kết nối. Hãy chắc chắn server đã khởi động!"
            messagebox.showerror("Lỗi kết nối", error_msg)
            self.log_message(f"❌ {error_msg}")
            if self.chat_socket:
                try:
                    self.chat_socket.close()
                except:
                    pass
                self.chat_socket = None
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến server:\n{str(e)}")
            self.log_message(f"❌ Kết nối thất bại: {str(e)}")
            if self.chat_socket:
                try:
                    self.chat_socket.close()
                except:
                    pass
                self.chat_socket = None
    
    def disconnect(self):
        self.is_connected = False
        
        if self.chat_socket:
            try:
                self.chat_socket.close()
            except:
                pass
            self.chat_socket = None
        
        self.connection_status.config(text="⚫ Chưa kết nối", fg="red")
        self.connect_btn.config(text="🔌 Kết nối", bg="#2196F3")
        self.send_btn.config(state=DISABLED)
        self.chat_entry.config(state=DISABLED)
        self.send_msg_btn.config(state=DISABLED)
        
        self.log_message("🔌 Đã ngắt kết nối")
        self.add_chat_message("Đã ngắt kết nối khỏi server")
        
        self.host_entry.config(state=NORMAL)
        self.port_entry.config(state=NORMAL)
    
    def send_message(self):
        message = self.chat_entry.get().strip()
        if not message or not self.is_connected:
            return
        
        try:
            self.chat_socket.send(message.encode('utf-8'))
            self.add_chat_message(message, "me")
            self.chat_entry.delete(0, END)
        except Exception as e:
            self.add_chat_message(f"❌ Lỗi gửi tin nhắn: {str(e)}")
            self.log_message(f"❌ Lỗi gửi tin nhắn: {str(e)}")
            self.disconnect()
    
    def receive_messages(self):
        self.log_message("👂 Bắt đầu lắng nghe tin nhắn từ server...")
        
        while self.is_connected:
            try:
                message = self.chat_socket.recv(1024).decode('utf-8', errors='ignore')
                if message:
                    self.log_message(f"📩 Nhận tin nhắn: {message[:50]}...")
                    self.root.after(0, self.add_chat_message, message, "server")
                else:
                    # Server đóng kết nối (recv trả về empty)
                    self.log_message("⚠️ Server đóng kết nối (recv empty)")
                    break
            except socket.timeout:
                continue  # Timeout bình thường, tiếp tục
            except Exception as e:
                if self.is_connected:
                    self.log_message(f"❌ Lỗi nhận tin nhắn: {str(e)}")
                    self.root.after(0, self.add_chat_message, f"Mất kết nối: {str(e)}")
                break
        
        self.log_message("👂 Dừng lắng nghe tin nhắn")
        
        if self.is_connected:
            self.root.after(0, self.disconnect)
    
    def select_file(self):
        filepath = filedialog.askopenfilename(title="Chọn file cần gửi")
        
        if filepath:
            self.selected_file = filepath
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            self.file_path_entry.config(state=NORMAL)
            self.file_path_entry.delete(0, END)
            self.file_path_entry.insert(0, filepath)
            self.file_path_entry.config(state="readonly")
            
            self.file_name_label.config(text=f"Tên file: {filename}")
            self.file_size_label.config(text=f"Kích thước: {filesize / (1024*1024):.2f} MB")
            
            if self.is_connected:
                self.send_btn.config(state=NORMAL)
            
            self.log_message(f"📁 Đã chọn file: {filename}")
    
    def send_file(self):
        if not self.selected_file or not self.is_connected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file và kết nối đến server!")
            return
        
        self.send_btn.config(state=DISABLED)
        
        send_thread = threading.Thread(target=self.send_file_thread, daemon=True)
        send_thread.start()
    
    def send_file_thread(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        try:
            # Socket riêng cho file transfer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            client_socket.connect((host, port))
            
            # Gửi identifier
            client_socket.send(b"FILE_MODE")
            client_socket.recv(1024)
            
            filename = os.path.basename(self.selected_file)
            filesize = os.path.getsize(self.selected_file)
            
            self.log_message(f"📤 Bắt đầu gửi file: {filename}")
            
            # Gửi tên file
            client_socket.send(filename.encode('utf-8'))
            client_socket.recv(1024)
            
            # Gửi kích thước file
            client_socket.send(str(filesize).encode('utf-8'))
            client_socket.recv(1024)
            
            # Gửi dữ liệu file
            sent = 0
            with open(self.selected_file, 'rb') as f:
                while sent < filesize:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    sent += len(chunk)
                    
                    progress = (sent / filesize) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"{progress:.1f}%")
                    self.root.update_idletasks()
            
            result = client_socket.recv(1024).decode('utf-8')
            
            if result == "SUCCESS":
                self.log_message(f"✅ Gửi file thành công: {filename}")
                messagebox.showinfo("Thành công", f"File {filename} đã được gửi thành công!")
            else:
                self.log_message(f"❌ Gửi file thất bại: {filename}")
                messagebox.showerror("Thất bại", "Gửi file không thành công!")
            
            client_socket.close()
            
        except Exception as e:
            self.log_message(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
        
        finally:
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            if self.is_connected:
                self.send_btn.config(state=NORMAL)

if __name__ == "__main__":
    root = Tk()
    app = FileTransferClient(root)
    root.mainloop()