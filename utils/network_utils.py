import os
import sys
import webbrowser
import time
import threading
from NetworkUtils.app import app

class NetworkUtils:
    """网络通信工具类"""
    
    def __init__(self):
        self.flask_thread = None
        self.flask_app = None
        self.is_running = False
        self._stop_event = threading.Event()
    
    def start_network_utils(self):
        """启动网络服务（非阻塞）"""
        if self.is_running:
            print("服务已在运行中...")
            return
        
        # 确保之前的服务完全停止
        self._ensure_service_stopped()
        
        # 等待端口完全释放
        max_wait = 5
        wait_count = 0
        while self._check_port(5001) and wait_count < max_wait:
            print(f"等待端口5001释放... ({wait_count + 1}/{max_wait})")
            time.sleep(1)
            wait_count += 1
        
        # 重置状态
        self.is_running = False
        self.flask_thread = None
        self.flask_app = None
        self._stop_event.clear()
        
        # 在新线程中启动Flask应用
        self.flask_thread = threading.Thread(target=self._run_flask_app, daemon=True)
        self.flask_thread.start()
        
        # 等待服务启动
        time.sleep(2)
        if self.is_running:
            print("应用启动成功!")
            print("访问地址: http://localhost:5001")
            # 自动打开浏览器
            webbrowser.open('http://localhost:5001')
        else:
            print("应用启动失败，请检查日志")
    
    def stop_network_utils(self):
        """停止网络服务"""
        if not self.is_running:
            print("服务未在运行...")
            return
            
        try:
            print("正在停止网络服务...")
            
            # 设置停止标志
            self._stop_event.set()
            self.is_running = False
            
            # 等待线程自然结束
            if self.flask_thread and self.flask_thread.is_alive():
                print("等待网络服务自然停止...")
                # 给线程一些时间来自然结束
                self.flask_thread.join(timeout=3)
                
                # 如果线程还在运行，等待更长时间
                if self.flask_thread.is_alive():
                    print("等待服务完全停止...")
                    self.flask_thread.join(timeout=2)
            
            # 清理资源
            self.flask_thread = None
            self.flask_app = None
            
            print("网络服务已停止")
                
        except Exception as e:
            print(f"停止服务时出错: {e}")
            # 即使出错也要清理资源
            self.is_running = False
            self.flask_thread = None
            self.flask_app = None
    
    def _ensure_service_stopped(self):
        """确保服务完全停止"""
        if self.is_running:
            print("检测到服务仍在运行，正在停止...")
            self.stop_network_utils()
            time.sleep(1)  # 等待完全停止
    
    def _run_flask_app(self):
        """在独立线程中运行Flask应用"""
        try:
            self.is_running = True
            
            # 创建新的Flask应用实例
            from NetworkUtils.app import app
            self.flask_app = app
            
            print("Flask应用正在启动...")
            
            # 使用更温和的启动方式
            app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False, threaded=True)
            
        except Exception as e:
            print(f"Flask应用运行出错: {e}")
            self.is_running = False
        finally:
            # 确保状态正确
            if not self.is_running:
                print("Flask应用已停止")
    
    def _check_port(self, port):
        """检查端口是否被占用"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def is_service_running(self):
        """检查服务是否正在运行"""
        return self.is_running
    
    def get_service_status(self):
        """获取详细的服务状态信息"""
        status = {
            'is_running': self.is_running,
            'thread_alive': self.flask_thread.is_alive() if self.flask_thread else False,
            'port_occupied': self._check_port(5001),
            'thread_info': str(self.flask_thread) if self.flask_thread else 'None'
        }
        return status

# 创建全局实例
network_utils_instance = NetworkUtils()