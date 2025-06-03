import tkinter as tk
from tkinter import ttk, messagebox
from config.config_manager import ConfigManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class BaseTab:
    """所有Tab类的基类，提供通用功能"""
    
    def __init__(self, notebook, main_window, tab_name):
        self.notebook = notebook
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=tab_name)
        
    def get_session(self):
        """获取数据库会话"""
        return self.main_window.session
        
    def get_config(self):
        """获取配置管理器"""
        return ConfigManager()
        
    def show_message(self, title, message, msg_type="info"):
        """显示消息框"""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
            
    def show_question(self, title, message):
        """显示确认对话框"""
        return messagebox.askyesno(title, message)
        
    def _set_controls_state(self, controls, state):
        """批量设置控件状态"""
        for control in controls:
            if hasattr(control, 'config'):
                control.config(state=state) 