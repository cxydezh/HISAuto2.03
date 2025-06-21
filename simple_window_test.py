"""
最简单的窗口测试
"""

import tkinter as tk
from tkinter import ttk

def test_simple_window():
    """测试简单的Toplevel窗口"""
    print("创建主窗口...")
    root = tk.Tk()
    root.title("主窗口")
    root.geometry("400x300")
    
    # 创建按钮
    def show_child():
        print("创建子窗口...")
        child = tk.Toplevel(root)
        child.title("子窗口")
        child.geometry("300x200")
        child.transient(root)
        child.grab_set()
        
        # 添加一些内容
        label = ttk.Label(child, text="这是子窗口")
        label.pack(pady=20)
        
        button = ttk.Button(child, text="关闭", command=child.destroy)
        button.pack(pady=10)
        
        print("子窗口创建完成")
        
    button = ttk.Button(root, text="显示子窗口", command=show_child)
    button.pack(pady=20)
    
    print("主窗口创建完成，开始mainloop...")
    root.mainloop()

if __name__ == "__main__":
    test_simple_window() 