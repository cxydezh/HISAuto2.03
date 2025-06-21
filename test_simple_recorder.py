"""
简化的ActionRecorder测试
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SimpleActionRecorder:
    """简化的行为录制管理器"""
    
    def __init__(self, home_tab):
        """初始化录制管理器"""
        self.home_tab = home_tab
        self.recording = False
        self.record_window = None
        self.record_mode = "全部"
        
    def show_record_options(self):
        """显示录制选项窗口"""
        print("开始显示录制选项窗口...")
        
        if not self.home_tab.action_group_id:
            messagebox.showwarning("警告", "请先选择行为组")
            return False
            
        print("创建录制选项窗口...")
        
        # 创建录制选项窗口
        self.record_window = tk.Toplevel(self.home_tab.my_window)
        self.record_window.title("录制选项")
        self.record_window.geometry("400x450")
        self.record_window.resizable(False, False)
        self.record_window.transient(self.home_tab.my_window)
        self.record_window.grab_set()
        
        print("窗口创建完成，开始添加控件...")
        
        # 创建主框架
        main_frame = ttk.Frame(self.record_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="选择录制内容", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 说明文本
        info_label = ttk.Label(main_frame, text="请选择要录制的鼠标事件类型：", font=("Arial", 10))
        info_label.pack(pady=(0, 15))
        
        # 录制模式选择
        mode_var = tk.StringVar(value="全部")
        
        # 单选按钮框架
        radio_frame = ttk.Frame(main_frame)
        radio_frame.pack(pady=10)
        
        ttk.Radiobutton(radio_frame, text="单击", variable=mode_var, value="单击").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(radio_frame, text="按下弹起", variable=mode_var, value="按下弹起").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(radio_frame, text="全部", variable=mode_var, value="全部").pack(anchor=tk.W, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def start_recording():
            """开始录制"""
            print("开始录制...")
            self.record_mode = mode_var.get()
            self.record_window.destroy()
            self.record_window = None
            print("录制窗口已关闭")
            
        def cancel_recording():
            """取消录制"""
            print("取消录制...")
            self.record_window.destroy()
            self.record_window = None
            
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="确认", command=start_recording)
        ok_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=cancel_recording)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键和ESC键
        self.record_window.bind('<Return>', lambda e: start_recording())
        self.record_window.bind('<Escape>', lambda e: cancel_recording())
        
        # 设置焦点
        ok_button.focus_set()
        
        print("控件添加完成，开始显示窗口...")
        
        # 强制更新窗口布局
        self.record_window.update_idletasks()
        self.record_window.update()
        
        # 确保窗口可见
        self.record_window.lift()
        self.record_window.focus_force()
        
        print("窗口准备就绪，开始事件循环...")
        
        # 使用独立的事件循环
        self.record_window.mainloop()
        
        print("事件循环结束")
        return True

class MockHomeTab:
    """模拟HomeTab类"""
    
    def __init__(self):
        print("创建MockHomeTab...")
        self.my_window = tk.Tk()
        self.my_window.title("测试主窗口")
        self.my_window.geometry("600x400")
        self.action_group_id = 1  # 模拟选中的行为组ID
        
        # 创建测试界面
        self._create_test_ui()
        print("MockHomeTab创建完成")
        
    def _create_test_ui(self):
        """创建测试界面"""
        # 主框架
        main_frame = ttk.Frame(self.my_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="简化录制窗口测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 说明
        info_label = ttk.Label(main_frame, text="点击下方按钮测试简化录制窗口", font=("Arial", 12))
        info_label.pack(pady=(0, 20))
        
        # 测试按钮
        test_button = ttk.Button(main_frame, text="测试简化录制窗口", command=self._test_recording_window)
        test_button.pack(pady=10)
        
        # 状态显示
        self.status_label = ttk.Label(main_frame, text="状态: 等待测试", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
    def _test_recording_window(self):
        """测试录制窗口"""
        try:
            print("=== 开始测试简化录制窗口 ===")
            self.status_label.config(text="状态: 正在创建录制窗口...")
            self.my_window.update()
            
            # 创建录制管理器
            print("创建SimpleActionRecorder...")
            recorder = SimpleActionRecorder(self)
            print("SimpleActionRecorder创建完成")
            
            # 显示录制选项
            print("调用show_record_options...")
            result = recorder.show_record_options()
            print(f"show_record_options返回: {result}")
            
            if result:
                self.status_label.config(text="状态: 录制窗口显示成功")
                print("录制窗口显示成功")
            else:
                self.status_label.config(text="状态: 录制窗口显示失败")
                print("录制窗口显示失败")
                
        except Exception as e:
            error_msg = f"测试录制窗口失败: {str(e)}"
            self.status_label.config(text=f"状态: {error_msg}")
            print(f"错误详情: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", error_msg)
    
    def run(self):
        """运行测试"""
        print("开始测试简化录制窗口...")
        self.my_window.mainloop()

def main():
    """主函数"""
    print("开始测试简化录制窗口...")
    
    # 创建测试窗口
    home_tab = MockHomeTab()
    
    # 运行测试
    home_tab.run()

if __name__ == "__main__":
    main() 