import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from gui.main_window import MainWindow
from utils.logger import logger

class LoginWindow:
    def __init__(self, on_login_success: Callable[[str, str], None]):
        """
        初始化登录窗口
        
        Args:
            on_login_success: 登录成功后的回调函数，接收用户名和密码作为参数
        """
        self.window = tk.Tk()
        self.window.title("智能自动化办公系统 - 登录")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # 设置窗口图标
        # self.window.iconbitmap("path/to/icon.ico")  # TODO: 添加图标
        
        # 登录失败计数器
        self.login_attempts = 0
        self.max_attempts = 5
        
        # 回调函数
        self.on_login_success = on_login_success
        
        self._create_widgets()
        self._center_window()
        
    def _create_widgets(self):
        """创建登录界面的控件"""
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="智能自动化办公系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 用户名
        ttk.Label(main_frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_var.set("admin")
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=1, column=1, pady=5)
        self.username_var.set('admin2')
        # 密码
        ttk.Label(main_frame, text="密码:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_var.set("admin")
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
         # 添加诊断信息
        print("登录窗体诊断信息:")
        print(f"1. StringVar 值: {self.username_var.get()}")
        print(f"2. Entry 控件值: {self.username_entry.get()}")
        print(f"3. Entry 状态: {self.username_entry.cget('state')}")
        print(f"4. StringVar ID: {id(self.username_var)}")
        print(f"5. Entry 的 textvariable ID: {id(self.username_entry.cget('textvariable'))}")

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 登录按钮
        login_button = ttk.Button(button_frame, text="登录", command=self._handle_login)
        login_button.grid(row=0, column=0, padx=5)
        
        # 注册按钮
        register_button = ttk.Button(button_frame, text="注册", command=self._handle_register)
        register_button.grid(row=0, column=1, padx=5)
        
        # 绑定回车键
        self.window.bind('<Return>', lambda e: self._handle_login())
        
    def _center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def _handle_login(self):
        """处理登录事件"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空！")
            return
            
        try:
            # 调用登录成功回调函数
            success_login,is_super_user = self.on_login_success(username, password)
            if success_login:
                self.login_attempts = 0  # 重置登录尝试次数
                main_window = MainWindow(username=username, is_super_admin=is_super_user)
                self.destroy()
                main_window.show()
                
            else:
                self.login_attempts += 1
                if self.login_attempts >= self.max_attempts:
                    messagebox.showerror("登录失败", "登录失败次数过多，系统将强制关闭！")
                    self.window.quit()
                else:
                    # 如果登录失败，显示错误信息
                    remaining = self.max_attempts - self.login_attempts
                    messagebox.showerror("登录失败", f"登录失败！还剩 {remaining} 次尝试机会。")
        except Exception as e:
            logger.info(f"登录失败: {str(e)}")
            
                
    def _handle_register(self):
        """处理注册事件"""
        # TODO: 实现注册功能
        messagebox.showinfo("提示", "注册功能开发中...")
        
    def show(self):
        """显示登录窗口"""
        self.window.mainloop()
        
    def hide(self):
        """隐藏登录窗口"""
        self.window.withdraw()
        
    def destroy(self):
        """销毁登录窗口"""
        self.window.destroy() 