import socket
import os
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class FileTransferClient:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Client 💻")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        self.selected_file = None
        self.is_connected = False
        
        self.setup_gui()
    
    def setup_gui(self):
        # Frame kết nối
        connection_frame = LabelFrame(self.root, text="🔗 Kết nối Server", padx=10, pady=10)
        connection_frame.pack(padx=10, pady=10, fill="x")
        
        Label(connection_frame, text="Server IP:").grid(row=0, column=0, sticky="w", pady=5)
        self.host_entry = Entry(connection_frame, width=30)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(connection_frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.port_entry = Entry(connection_frame, width=30)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.connect_btn = Button(connection_frame, text="🔌 Kết nối", 
                                  command=self.toggle_connection, bg="#2196F3", fg="white",
                                  font=("Arial", 10, "bold"), width=15)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Trạng thái kết nối
        self.connection_status = Label(connection_frame, text="⚫ Chưa kết nối", 
                                       font=("Arial", 10, "bold"), fg="red")
        self.connection_status.grid(row=3, column=0, columnspan=2)
        
        # Frame chọn file
        file_frame = LabelFrame(self.root, text="📁 Chọn File", padx=10, pady=10)
        file_frame.pack(padx=10, pady=10, fill="x")
        
        self.file_path_entry = Entry(file_frame, width=45, state="readonly")
        self.file_path_entry.pack(side=LEFT, padx=5)
        
        Button(file_frame, text="📂 Chọn File", command=self.select_file,
               bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side=LEFT, padx=5)
        
        # Thông tin file
        info_frame = LabelFrame(self.root, text="ℹ️ Thông tin File", padx=10, pady=10)
        info_frame.pack(padx=10, pady=5, fill="x")
        
        self.file_name_label = Label(info_frame, text="Tên file: Chưa chọn", 
                                     font=("Arial", 9), anchor="w")
        self.file_name_label.pack(fill="x", pady=2)
        
        self.file_size_label = Label(info_frame, text="Kích thước: 0 MB", 
                                     font=("Arial", 9), anchor="w")
        self.file_size_label.pack(fill="x", pady=2)
        
        # Nút gửi file
        send_frame = Frame(self.root)
        send_frame.pack(padx=10, pady=10)
        
        self.send_btn = Button(send_frame, text="📤 Gửi File", command=self.send_file,
                              bg="#FF9800", fg="white", font=("Arial", 11, "bold"),
                              width=20, height=2, state=DISABLED)
        self.send_btn.pack()
        
        # Progress bar
        progress_frame = LabelFrame(self.root, text="⏳ Tiến trình", padx=10, pady=10)
        progress_frame.pack(padx=10, pady=5, fill="x")
        
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=550)
        self.progress_bar.pack(pady=5)
        
        self.progress_label = Label(progress_frame, text="0%", font=("Arial", 10, "bold"))
        self.progress_label.pack()
        
        # Log
        log_frame = LabelFrame(self.root, text="📋 Trạng thái", padx=10, pady=10)
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_text = Text(log_frame, height=8, font=("Courier", 9), state=DISABLED)
        self.log_text.pack(fill="both", expand=True)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, log_entry)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def toggle_connection(self):
        if not self.is_connected:
            self.test_connection()
        else:
            self.disconnect()
    
    def test_connection(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(3)
            test_socket.connect((host, port))
            test_socket.close()
            
            self.is_connected = True
            self.connection_status.config(text="🟢 Đã kết nối", fg="green")
            self.connect_btn.config(text="🔌 Ngắt kết nối", bg="#f44336")
            self.send_btn.config(state=NORMAL if self.selected_file else DISABLED)
            self.log_message(f"✅ Kết nối thành công đến {host}:{port}")
            
            self.host_entry.config(state=DISABLED)
            self.port_entry.config(state=DISABLED)
            
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến server:\n{str(e)}")
            self.log_message(f"❌ Kết nối thất bại: {str(e)}")
    
    def disconnect(self):
        self.is_connected = False
        self.connection_status.config(text="⚫ Chưa kết nối", fg="red")
        self.connect_btn.config(text="🔌 Kết nối", bg="#2196F3")
        self.send_btn.config(state=DISABLED)
        self.log_message("🔌 Đã ngắt kết nối")
        
        self.host_entry.config(state=NORMAL)
        self.port_entry.config(state=NORMAL)
    
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
        
        # Vô hiệu hóa nút gửi trong quá trình truyền
        self.send_btn.config(state=DISABLED)
        
        # Chạy truyền file trong luồng riêng
        send_thread = threading.Thread(target=self.send_file_thread, daemon=True)
        send_thread.start()
    
    def send_file_thread(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        try:
            # Kết nối đến server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            
            filename = os.path.basename(self.selected_file)
            filesize = os.path.getsize(self.selected_file)
            
            self.log_message(f"📤 Bắt đầu gửi file: {filename}")
            
            # Gửi tên file
            client_socket.send(filename.encode('utf-8'))
            client_socket.recv(1024)  # Chờ xác nhận
            
            # Gửi kích thước file
            client_socket.send(str(filesize).encode('utf-8'))
            client_socket.recv(1024)  # Chờ xác nhận
            
            # Gửi dữ liệu file
            sent = 0
            with open(self.selected_file, 'rb') as f:
                while sent < filesize:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    sent += len(chunk)
                    
                    # Cập nhật progress bar
                    progress = (sent / filesize) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"{progress:.1f}%")
                    self.root.update_idletasks()
            
            # Nhận kết quả
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
            # Reset progress và kích hoạt lại nút gửi
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            if self.is_connected:
                self.send_btn.config(state=NORMAL)

if __name__ == "__main__":
    root = Tk()
    app = FileTransferClient(root)
    root.mainloop()