import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import socket
import os
import sys
import json
import argparse
from app import app

class FileUploadGUI:
    def __init__(self, root, port=5000):
        self.root = root
        self.root.title("文件上传服务")
        self.root.geometry("600x400")
        self.root.minsize(500, 300)
        
        # 设置窗口图标（如果有的话）
        try:
            # 尝试设置窗口图标
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 获取本机IP地址
        hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(hostname)
        self.port = port
        self.service_address = f"http://{self.local_ip}:{self.port}"
        
        # 获取文件存储地址
        self.load_settings()
        
        # 创建UI
        self.create_widgets()
        
        # 在后台线程启动Flask服务器
        self.start_flask_server()
        
    def load_settings(self):
        """加载用户设置"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是python脚本
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        self.settings_file = os.path.join(application_path, "settings.json")
        
        # 默认存储路径
        self.storage_path = os.path.join(application_path, "uploads")
        
        # 确保默认的uploads目录存在
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
            except Exception as e:
                print(f"创建默认上传目录时出错: {e}")
        
        # 如果设置文件存在，加载设置
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'storage_path' in settings:
                        self.storage_path = settings['storage_path']
                        # 确保用户设置的存储路径存在
                        if not os.path.exists(self.storage_path):
                            try:
                                os.makedirs(self.storage_path)
                            except Exception as e:
                                print(f"创建用户设置的上传目录时出错: {e}")
                                # 如果创建失败，回退到默认路径
                                self.storage_path = os.path.join(application_path, "uploads")
            except:
                pass
        
        # 更新Flask应用的上传目录
        app.config['UPLOAD_FOLDER'] = self.storage_path
        
    def create_widgets(self):
        # 设置样式
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#2c3e50")
        style.configure("Section.TLabel", font=("Arial", 10, "bold"), foreground="#34495e")
        style.configure("Status.TLabel", font=("Arial", 10))
        style.configure("Action.TButton", font=("Arial", 10, "bold"))
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重，使窗口可调整大小
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="文件上传服务", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky=tk.W)
        
        # 服务地址框架
        service_frame = ttk.LabelFrame(main_frame, text="服务信息", padding="10")
        service_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        service_frame.columnconfigure(1, weight=1)
        
        # 服务地址
        service_label = ttk.Label(service_frame, text="上传地址:", style="Section.TLabel")
        service_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.service_address_var = tk.StringVar(value=self.service_address)
        service_entry = ttk.Entry(service_frame, textvariable=self.service_address_var, state="readonly", font=("Consolas", 10))
        service_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件存储地址框架
        storage_frame = ttk.LabelFrame(main_frame, text="存储设置", padding="10")
        storage_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        storage_frame.columnconfigure(1, weight=1)
        
        # 文件存储地址
        storage_label = ttk.Label(storage_frame, text="存储路径:", style="Section.TLabel")
        storage_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.storage_path_var = tk.StringVar(value=self.storage_path)
        storage_entry = ttk.Entry(storage_frame, textvariable=self.storage_path_var, state="readonly", font=("Consolas", 10))
        storage_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 更改路径按钮
        change_path_button = ttk.Button(storage_frame, text="更改存储路径", command=self.change_storage_path, style="Action.TButton")
        change_path_button.grid(row=2, column=0, pady=(0, 5), sticky=tk.W)
        
        # 状态框架
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, text="服务运行中...", foreground="green", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, pady=(5, 5), sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭服务", command=self.close_service, style="Action.TButton")
        close_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 打开存储文件夹按钮
        open_folder_button = ttk.Button(button_frame, text="打开存储文件夹", command=self.open_storage_folder, style="Action.TButton")
        open_folder_button.pack(side=tk.RIGHT)
        
        # 添加一些间距
        main_frame.rowconfigure(5, weight=1)
        
        # 底部信息
        info_label = ttk.Label(main_frame, text="文件上传服务 v1.0", font=("Arial", 8), foreground="#7f8c8d")
        info_label.grid(row=6, column=0, columnspan=3, pady=(0, 10), sticky=tk.S)
        
    def start_flask_server(self):
        """在后台线程启动Flask服务器"""
        def run_flask():
            app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
    def save_settings(self):
        """保存用户设置"""
        settings = {
            'storage_path': self.storage_path
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def change_storage_path(self):
        """更改文件存储路径"""
        new_path = filedialog.askdirectory(
            title="选择文件存储路径",
            initialdir=self.storage_path
        )
        
        if new_path:
            # 检查路径是否有效
            if os.path.exists(new_path) or messagebox.askyesno("创建目录", f"目录 {new_path} 不存在，是否创建？"):
                try:
                    # 如果目录不存在则创建
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    
                    # 更新存储路径
                    self.storage_path = new_path
                    self.storage_path_var.set(new_path)
                    
                    # 保存设置
                    self.save_settings()
                    
                    # 更新Flask应用的上传目录
                    app.config['UPLOAD_FOLDER'] = new_path
                    
                    messagebox.showinfo("成功", "存储路径已更新！")
                except Exception as e:
                    messagebox.showerror("错误", f"无法设置存储路径: {e}")
    
    def open_storage_folder(self):
        """打开存储文件夹"""
        try:
            if os.path.exists(self.storage_path):
                os.startfile(self.storage_path)
            else:
                # 如果目录不存在则创建
                os.makedirs(self.storage_path)
                os.startfile(self.storage_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def close_service(self):
        """关闭服务"""
        self.status_label.config(text="服务已停止", foreground="red")
        # 这里可以添加更多清理代码
        self.root.after(1000, self.root.destroy)  # 1秒后关闭窗口

def main(port=5000):
    root = tk.Tk()
    app = FileUploadGUI(root, port)
    root.mainloop()

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='文件上传服务 GUI')
    parser.add_argument('--port', type=int, default=5000, help='指定服务器端口 (默认: 5000)')
    args = parser.parse_args()
    
    main(args.port)
