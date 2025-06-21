#!/usr/bin/env python3
"""
测试图像采集修复
"""

import tkinter as tk
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_image_capture_fix():
    """测试图像采集修复"""
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("图像采集修复测试")
        root.geometry("500x400")
        
        # 创建测试按钮
        def test_capture():
            try:
                from core.pic_capture import PicCapture
                from config.config_manager import ConfigManager
                
                config = ConfigManager()
                save_path = config.get_value('PicCapture', 'savepath')
                
                if not save_path:
                    print("错误: 图像保存路径未配置")
                    return
                
                # 创建测试目录
                test_save_path = os.path.join(save_path, "test_capture")
                os.makedirs(test_save_path, exist_ok=True)
                
                print(f"保存路径: {test_save_path}")
                
                # 创建图像采集实例
                pic_capture = PicCapture(save_path=test_save_path, master=root)
                
                # 执行图像采集
                print("开始图像采集...")
                pic_capture.capture_screen()
                
                # 检查是否成功选择了区域
                coordinates = pic_capture.get_image_coordinates()
                print(f"选择的坐标: {coordinates}")
                
                if coordinates[0] is not None and coordinates[1] is not None:
                    # 保存测试图像
                    if pic_capture.save_image("test_fix"):
                        print("图像采集修复测试成功!")
                        result_label.config(text="测试成功! 图像已保存", fg="green")
                    else:
                        print("图像保存失败")
                        result_label.config(text="图像保存失败", fg="red")
                else:
                    print("未选择图像区域")
                    result_label.config(text="未选择图像区域", fg="orange")
                    
            except Exception as e:
                print(f"图像采集测试失败: {e}")
                print(traceback.format_exc())
                result_label.config(text=f"测试失败: {str(e)}", fg="red")
        
        # 创建说明标签
        info_label = tk.Label(root, text="图像采集修复测试", font=("Arial", 14, "bold"))
        info_label.pack(pady=10)
        
        instruction_label = tk.Label(root, text="点击'测试图像采集'按钮开始测试\n在截图界面中，点击并拖动鼠标选择区域\n然后释放鼠标完成采集\n按ESC键可以取消采集", 
                                   font=("Arial", 10), justify=tk.LEFT)
        instruction_label.pack(pady=10)
        
        # 创建按钮
        test_btn = tk.Button(root, text="测试图像采集", command=test_capture, 
                           font=("Arial", 12), bg="lightblue", padx=20, pady=10)
        test_btn.pack(pady=20)
        
        # 创建结果显示标签
        result_label = tk.Label(root, text="等待测试...", font=("Arial", 12))
        result_label.pack(pady=10)
        
        # 创建退出按钮
        exit_btn = tk.Button(root, text="退出", command=root.quit, 
                           font=("Arial", 10), bg="lightcoral", padx=15, pady=5)
        exit_btn.pack(pady=10)
        
        print("图像采集修复测试程序已启动")
        print("点击'测试图像采集'按钮开始测试")
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试程序启动失败: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_image_capture_fix() 