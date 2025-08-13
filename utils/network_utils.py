import os
import sys
import webbrowser
import time
from NetworkUtils.app import app

class NetworkUtils:
    """网络通信工具类"""
    @staticmethod
    def start_network_utils():
        """主函数"""
        # 检查是否是主进程启动（不是Flask的reloader进程）
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            print("=" * 50)
            print("HISAuto_web - 住院部HIS Agent应用")
            print("=" * 50)
            print("正在启动应用...")
        
        # 检查端口是否被占用
        import socket
        import subprocess
        import time
        
        def check_port(port):
            """检查端口是否被占用"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        
        def kill_process_on_port(port):
            """终止占用指定端口的进程"""
            try:
                # 查找占用端口的进程
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                # 终止进程
                                subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                            capture_output=True, check=True)
                                print(f"已终止占用端口{port}的进程 (PID: {pid})")
                                time.sleep(1)  # 等待进程完全终止
                                return True
                            except subprocess.CalledProcessError:
                                continue
                return False
            except Exception as e:
                print(f"终止进程时出错: {e}")
                return False
        
        # 检查端口占用情况（只在主进程启动时检查）
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            if check_port(5001):
                print("检测到端口5001被占用，正在尝试释放...")
                if kill_process_on_port(5001):
                    print("端口已释放，继续启动...")
                else:
                    print("无法自动释放端口，请手动关闭占用端口的应用后重试")
                    print("或者等待几秒钟后重新运行此脚本")
                    return
            
            # 再次检查端口
            if check_port(5001):
                print("错误: 端口5001仍被占用，请关闭其他应用后重试")
                return
        
        # 启动应用
        try:
            # 只在主进程启动时显示成功信息和打开浏览器
            if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
                print("应用启动成功!")
                print("访问地址: http://localhost:5001")
                print("登录信息:")
                print("  用户名: admin")
                print("  密码: admin")
                print()
                print("按 Ctrl+C 停止应用")
                print("-" * 50)
                
            # 启动Flask应用
            app.run(debug=False, host='0.0.0.0', port=5001)
            
        except KeyboardInterrupt:
            print("\n正在停止应用...")
            print("应用已停止")
        except Exception as e:
            print(f"启动失败: {e}")
            print("请检查端口是否被占用或尝试重新启动")