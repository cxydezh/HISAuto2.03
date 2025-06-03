import tkinter as tk
from tkinter import ttk
from gui.tabs.base_tab import BaseTab
import psutil
import time

class CloudControlTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "云控制")
        
        # 创建界面
        self._create_widgets()
        
        # 启动系统监控
        self._start_monitoring()
        
    def _create_widgets(self):
        """创建云控制标签页的控件"""
        # 创建两列布局
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧状态面板
        left_panel = ttk.LabelFrame(self.frame, text="云服务状态")
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建右侧控制面板
        right_panel = ttk.LabelFrame(self.frame, text="云服务控制")
        right_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建各个面板内容
        self._create_status_panel(left_panel)
        self._create_control_panel(right_panel)
        
    def _create_status_panel(self, parent):
        """创建状态显示面板"""
        # 创建状态显示区域
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 系统状态标题
        title_label = ttk.Label(status_frame, text="系统监控", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # CPU使用率
        self.cpu_label = ttk.Label(status_frame, text="CPU使用率: 加载中...")
        self.cpu_label.pack(pady=5, anchor=tk.W)
        
        # 内存使用率
        self.memory_label = ttk.Label(status_frame, text="内存使用率: 加载中...")
        self.memory_label.pack(pady=5, anchor=tk.W)
        
        # 磁盘使用率
        self.disk_label = ttk.Label(status_frame, text="磁盘使用率: 加载中...")
        self.disk_label.pack(pady=5, anchor=tk.W)
        
        # 网络状态
        self.network_label = ttk.Label(status_frame, text="网络状态: 加载中...")
        self.network_label.pack(pady=5, anchor=tk.W)
        
        # 服务状态
        service_frame = ttk.LabelFrame(status_frame, text="服务状态")
        service_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 创建服务状态列表
        self.service_tree = ttk.Treeview(service_frame, columns=("service", "status"), show="headings", height=6)
        self.service_tree.heading("service", text="服务名称")
        self.service_tree.heading("status", text="状态")
        self.service_tree.column("service", width=150)
        self.service_tree.column("status", width=100)
        
        service_scroll = ttk.Scrollbar(service_frame, orient="vertical", command=self.service_tree.yview)
        self.service_tree.configure(yscrollcommand=service_scroll.set)
        
        self.service_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        service_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # 添加示例服务状态
        self.service_tree.insert("", "end", values=("数据库服务", "运行中"))
        self.service_tree.insert("", "end", values=("Web服务", "运行中"))
        self.service_tree.insert("", "end", values=("文件服务", "已停止"))
        self.service_tree.insert("", "end", values=("任务调度服务", "运行中"))
        
    def _create_control_panel(self, parent):
        """创建控制面板"""
        # 创建控制区域
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 控制面板标题
        title_label = ttk.Label(control_frame, text="系统控制", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 服务控制按钮
        service_control_frame = ttk.LabelFrame(control_frame, text="服务控制")
        service_control_frame.pack(fill=tk.X, pady=(0, 20))
        
        btn_frame1 = ttk.Frame(service_control_frame)
        btn_frame1.pack(pady=10)
        
        ttk.Button(btn_frame1, text="启动所有服务", command=self._start_all_services).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame1, text="停止所有服务", command=self._stop_all_services).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame1, text="重启服务", command=self._restart_services).pack(side=tk.LEFT, padx=5)
        
        # 系统控制按钮
        system_control_frame = ttk.LabelFrame(control_frame, text="系统控制")
        system_control_frame.pack(fill=tk.X, pady=(0, 20))
        
        btn_frame2 = ttk.Frame(system_control_frame)
        btn_frame2.pack(pady=10)
        
        ttk.Button(btn_frame2, text="系统备份", command=self._system_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="清理缓存", command=self._clear_cache).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="系统重启", command=self._system_restart).pack(side=tk.LEFT, padx=5)
        
        # 监控控制
        monitor_frame = ttk.LabelFrame(control_frame, text="监控控制")
        monitor_frame.pack(fill=tk.X)
        
        btn_frame3 = ttk.Frame(monitor_frame)
        btn_frame3.pack(pady=10)
        
        self.monitoring_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_frame3, text="启用实时监控", variable=self.monitoring_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame3, text="刷新状态", command=self._refresh_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame3, text="导出报告", command=self._export_report).pack(side=tk.LEFT, padx=5)
        
    def _start_monitoring(self):
        """启动系统监控"""
        self._update_system_status()
        
    def _update_system_status(self):
        """更新系统状态"""
        if self.monitoring_enabled.get():
            try:
                # 获取CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_label.config(text=f"CPU使用率: {cpu_percent:.1f}%")
                
                # 获取内存使用率
                memory = psutil.virtual_memory()
                self.memory_label.config(text=f"内存使用率: {memory.percent:.1f}%")
                
                # 获取磁盘使用率
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.disk_label.config(text=f"磁盘使用率: {disk_percent:.1f}%")
                
                # 获取网络状态
                network = psutil.net_io_counters()
                self.network_label.config(text=f"网络状态: 发送 {network.bytes_sent // 1024 // 1024}MB, 接收 {network.bytes_recv // 1024 // 1024}MB")
                
            except Exception as e:
                print(f"更新系统状态失败: {e}")
                self.cpu_label.config(text="CPU使用率: 获取失败")
                self.memory_label.config(text="内存使用率: 获取失败")
                self.disk_label.config(text="磁盘使用率: 获取失败")
                self.network_label.config(text="网络状态: 获取失败")
        
        # 每5秒更新一次
        self.main_window.window.after(5000, self._update_system_status)
        
    def _start_all_services(self):
        """启动所有服务"""
        self.show_message("提示", "正在启动所有服务...")
        # TODO: 实际的服务启动逻辑
        
    def _stop_all_services(self):
        """停止所有服务"""
        if self.show_question("确认", "确定要停止所有服务吗？"):
            self.show_message("提示", "正在停止所有服务...")
            # TODO: 实际的服务停止逻辑
        
    def _restart_services(self):
        """重启服务"""
        if self.show_question("确认", "确定要重启服务吗？"):
            self.show_message("提示", "正在重启服务...")
            # TODO: 实际的服务重启逻辑
        
    def _system_backup(self):
        """系统备份"""
        self.show_message("提示", "系统备份功能开发中...")
        
    def _clear_cache(self):
        """清理缓存"""
        if self.show_question("确认", "确定要清理系统缓存吗？"):
            self.show_message("提示", "正在清理缓存...")
            # TODO: 实际的缓存清理逻辑
        
    def _system_restart(self):
        """系统重启"""
        if self.show_question("警告", "确定要重启系统吗？这将关闭所有正在运行的程序。"):
            self.show_message("警告", "系统重启功能已禁用（安全考虑）", "warning")
        
    def _refresh_status(self):
        """刷新状态"""
        self._update_system_status()
        self.show_message("提示", "系统状态已刷新")
        
    def _export_report(self):
        """导出报告"""
        self.show_message("提示", "导出报告功能开发中...") 