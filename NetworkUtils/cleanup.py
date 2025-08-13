#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HISAuto_web 端口清理脚本
用于清理占用端口5001的进程
"""

import subprocess
import socket
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
        print(f"正在查找占用端口{port}的进程...")
        
        # 查找占用端口的进程
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        found_processes = []
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    found_processes.append(pid)
        
        if not found_processes:
            print(f"未找到占用端口{port}的进程")
            return True
        
        print(f"找到 {len(found_processes)} 个占用端口{port}的进程:")
        
        for pid in found_processes:
            try:
                # 获取进程信息
                process_info = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                           capture_output=True, text=True)
                lines = process_info.stdout.split('\n')
                process_name = lines[3] if len(lines) > 3 else 'Unknown'
                print(f"  PID {pid}: {process_name}")
                
                # 终止进程
                subprocess.run(['taskkill', '/PID', pid, '/F'], 
                             capture_output=True, check=True)
                print(f"  ✓ 已终止进程 {pid}")
                
            except subprocess.CalledProcessError as e:
                print(f"  ✗ 终止进程 {pid} 失败: {e}")
        
        time.sleep(2)  # 等待进程完全终止
        
        # 再次检查端口
        if not check_port(port):
            print(f"✓ 端口{port}已成功释放")
            return True
        else:
            print(f"✗ 端口{port}仍被占用")
            return False
            
    except Exception as e:
        print(f"清理过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("HISAuto_web 端口清理工具")
    print("=" * 50)
    
    port = 5001
    
    if not check_port(port):
        print(f"端口{port}未被占用，无需清理")
        return
    
    print(f"检测到端口{port}被占用，开始清理...")
    
    if kill_process_on_port(port):
        print("\n清理完成！现在可以重新启动应用了。")
    else:
        print("\n清理失败，请手动检查并关闭占用端口的应用。")
        print("可以尝试以下命令:")
        print(f"  netstat -ano | findstr :{port}")
        print("  taskkill /PID <进程ID> /F")

if __name__ == '__main__':
    main() 