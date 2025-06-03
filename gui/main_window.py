import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
from datetime import datetime
from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager
import globalvariable

# 导入各个Tab类
from gui.tabs.home_tab import HomeTab
from gui.tabs.debug_tab import DebugTab
from gui.tabs.conduction_manager_tab import ConductionManagerTab
from gui.tabs.workspace_tab import WorkspaceTab
from gui.tabs.aiset_tab import AISetTab
from gui.tabs.task_control_tab import TaskControlTab
from gui.tabs.cloud_control_tab import CloudControlTab
from gui.tabs.setting_tab import SettingTab

class MainWindow:
    def show_time_picker(self, root, entry_widget):
        """显示时间选择器"""
        def confirm_time():
            selected_time = f"{hour.get()}:{minute.get()}"
            print("Selected Time:", selected_time)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_time)            
            time_picker.destroy()
            
        # 获取 Entry 控件在屏幕上的位置
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        time_picker = tk.Toplevel(root)
        time_picker.title("选择时间")
        time_picker.geometry(f"+{x}+{y}")
        time_picker.transient(root)
        time_picker.grab_set()
        time_picker.focus_set()
    
        # 小时选择
        hour_label = ttk.Label(time_picker, text="小时:")
        hour_label.grid(row=0, column=0, padx=5, pady=5)
        hour = ttk.Spinbox(time_picker, from_=0, to=23, width=3)
        hour.grid(row=0, column=1, padx=5, pady=5)
    
        # 分钟选择
        minute_label = ttk.Label(time_picker, text="分钟:")
        minute_label.grid(row=1, column=0, padx=5, pady=5)
        minute = ttk.Spinbox(time_picker, from_=0, to=59, width=3)
        minute.grid(row=1, column=1, padx=5, pady=5)
    
        # 确认按钮
        confirm_btn = ttk.Button(time_picker, text="确定", command=confirm_time)
        confirm_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
    def show_mode_picker(self, root):
        """显示模式选择器"""
        def confirm_module():
            self.module_select_node = local_mode_var.get()
            select_mode.destroy()
            
        select_mode = tk.Toplevel(root)
        select_mode.title("选择模式")
        select_mode.geometry("400x200")
        select_mode.transient(root)
        select_mode.grab_set()
        select_mode.focus_set()

        local_mode_frame = ttk.Frame(select_mode)
        local_mode_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        local_mode_var = tk.IntVar()
        
        label_local = ttk.Label(local_mode_frame, text='选择插入位置:', font=("Arial", 12))
        label_local.pack(pady=10)
        
        # 根据当前选中的节点类型显示不同的选项
        if hasattr(self, 'home_tab') and hasattr(self.home_tab, 'action_tree'):
            selected = self.home_tab.action_tree.selection()
            if not selected:
                messagebox.showwarning("警告", "请选择节点")
                local_mode_var.set(5)
                select_mode.destroy()
                return
            elif selected[0].startswith("group_"):
                ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
                ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
            elif selected[0].startswith("A"):
                ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
                ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
                ttk.Radiobutton(local_mode_frame, text ='插入子项', variable=local_mode_var, value=3).pack(pady=5)
            else:
                messagebox.showwarning("警告", "节点的内容出现错误，请修复")
                local_mode_var.set(5)
                select_mode.destroy()
                return
        else:
            # 默认选项
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
            
        confirm_btn = ttk.Button(local_mode_frame, text="确定", command=confirm_module)
        confirm_btn.pack(pady=10)

    def __init__(self, username: str, is_super_admin: bool = False, engine=None):
        """
        初始化主窗口
        
        Args:
            username: 当前登录的用户名
            is_super_admin: 是否为超级管理员
            engine: 数据库引擎（可选）
        """
        self.window = tk.Tk()
        self.window.title(f"智能自动化办公系统 - {username}")
        self.window.state('zoomed')  # 最大化窗口
        
        # 设置窗口最小尺寸
        self.window.minsize(1024, 768)
        
        # 用户信息
        self.username = username
        self.is_super_admin = is_super_admin
        
        # 初始化数据库会话
        self.session = None
        self._initialize_database()
        
        # 设置全局变量（用于子Tab访问）
        self.module_select_node = None
        
        # 创建主界面
        self._create_widgets()
        
    def _initialize_database(self):
        """初始化数据库连接"""
        try:
            config_manager = ConfigManager()
            db_path = config_manager.get_value('System', 'DataSource')
            encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
            
            if db_path and encryption_key:
                db_manager = DatabaseManager(
                    db_path=db_path,
                    encryption_key=encryption_key
                )
                db_manager.initialize()
                self.session = db_manager.get_session()
                print("数据库初始化成功")
            else:
                print("数据库配置不完整")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
        
    def _create_widgets(self):
        """创建主界面的控件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Notebook控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页
        self._create_tabs()
        
    def _create_tabs(self):
        """创建所有标签页"""
        try:
            # 创建首页标签页
            self.home_tab = HomeTab(self.notebook, self)
            
            # 创建调试标签页
            self.debug_tab = DebugTab(self.notebook, self)
            
            # 创建流程管理器标签页
            self.conduction_manager_tab = ConductionManagerTab(self.notebook, self)
            
            # 创建工作区标签页
            self.workspace_tab = WorkspaceTab(self.notebook, self)
            
            # 创建AI设置标签页
            self.aiset_tab = AISetTab(self.notebook, self)
            
            # 只有超级管理员才能看到任务控制界面
            if self.is_super_admin:
                self.task_control_tab = TaskControlTab(self.notebook, self)
                
            # 创建云控制标签页
            self.cloud_control_tab = CloudControlTab(self.notebook, self)
            
            # 创建设置标签页
            self.setting_tab = SettingTab(self.notebook, self)
            
            print("所有标签页创建完成")
            
        except Exception as e:
            print(f"创建标签页失败: {str(e)}")
            messagebox.showerror("错误", f"创建界面失败: {str(e)}")
        
    def show(self):
        """显示主窗口"""
        try:
            self.window.mainloop()
        except Exception as e:
            print(f"运行主窗口失败: {str(e)}")
            messagebox.showerror("错误", f"运行程序失败: {str(e)}")
        
    def hide(self):
        """隐藏主窗口"""
        self.window.withdraw()
        
    def destroy(self):
        """销毁主窗口"""
        try:
            # 关闭数据库连接
            if self.session:
                self.session.close()
            self.window.destroy()
        except Exception as e:
            print(f"关闭程序失败: {str(e)}")
            
    def get_session(self):
        """获取数据库会话"""
        return self.session