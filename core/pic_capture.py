"""
图像采集模块的主要实现类
"""

import os
import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime

class PicCapture:
    def __init__(self, save_path: str):
        """
        初始化图像采集类
        
        Args:
            save_path (str): 图像保存的根目录路径
        """
        self.save_path = save_path
        self.screenshot = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.photo = None
        self.window = None
        self.canvas = None
        
    def capture_screen(self):
        """
        捕获全屏截图并显示在窗口中
        """
        # 隐藏主窗口
        if self.window:
            self.window.withdraw()
            
        # 捕获全屏
        self.screenshot = pyautogui.screenshot()
        
        # 创建全屏窗口
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # 创建画布
        self.canvas = tk.Canvas(self.window, width=self.screenshot.width, height=self.screenshot.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 显示截图
        self.photo = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # 显示窗口
        self.window.deiconify()
        
    def on_click(self, event):
        """
        鼠标点击事件处理
        """
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """
        鼠标拖动事件处理
        """
        if self.start_x is not None and self.start_y is not None:
            # 清除之前的矩形
            self.canvas.delete("rectangle")
            # 绘制新的矩形
            self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, tags="rectangle"
            )
            
    def on_release(self, event):
        """
        鼠标释放事件处理
        """
        self.end_x = event.x
        self.end_y = event.y
        
        # 确保坐标正确
        if self.start_x > self.end_x:
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.start_y > self.end_y:
            self.start_y, self.end_y = self.end_y, self.start_y
            
        # 关闭窗口
        self.window.destroy()
        
    def get_cropped_image(self) -> Image.Image:
        """
        获取裁剪后的图像
        
        Returns:
            Image.Image: 裁剪后的图像
        """
        if self.screenshot and self.start_x is not None and self.start_y is not None:
            return self.screenshot.crop((self.start_x, self.start_y, self.end_x, self.end_y))
        return None
        
    def save_image(self, image_name: str) -> bool:
        """
        保存图像到指定位置
        
        Args:
            image_name (str): 图像名称
            
        Returns:
            bool: 是否保存成功
        """
        if not image_name:
            return False
            
        # 检查文件名是否已存在
        save_path = os.path.join(self.save_path, f"{image_name}.png")
        if os.path.exists(save_path):
            return False
            
        # 获取裁剪后的图像
        cropped_image = self.get_cropped_image()
        if cropped_image:
            # 保存图像
            cropped_image.save(save_path)
            return True
        return False
        
    def get_image_coordinates(self) -> tuple:
        """
        获取图像坐标
        
        Returns:
            tuple: (start_x, start_y, end_x, end_y)
        """
        return (self.start_x, self.start_y, self.end_x, self.end_y) 