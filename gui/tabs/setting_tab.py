import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab

class SettingTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "设置")
        
        # 初始化配置管理器和设置条目
        self.config_manager = self.get_config()
        self.setting_entries = {}  # {(section, key): entry}
        
        # 创建界面
        self._create_widgets()
        
    def _create_widgets(self):
        """创建设置标签页的控件"""
        # 创建主框架和滚动区域
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和Scrollbar实现滚动
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 创建设置内容
        self._create_settings_content()
        
    def _create_settings_content(self):
        """创建设置内容"""
        # 标题
        title_label = ttk.Label(self.scrollable_frame, text="系统设置", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky=tk.W)
        
        row = 1
        
        try:
            # 遍历配置文件的所有section
            for section in self.config_manager.config.sections():
                # 创建section标题框架
                section_frame = ttk.LabelFrame(self.scrollable_frame, text=section)
                section_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5, ipadx=5, ipady=5)
                section_frame.grid_columnconfigure(1, weight=1)
                
                inner_row = 0
                # 遍历section中的所有配置项
                for key, value in self.config_manager.config[section].items():
                    # 创建标签
                    ttk.Label(section_frame, text=f"{key}:").grid(row=inner_row, column=0, sticky=tk.W, padx=5, pady=2)
                    
                    # 创建输入框
                    entry = ttk.Entry(section_frame, width=50)
                    entry.insert(0, value)
                    entry.grid(row=inner_row, column=1, sticky=tk.EW, padx=5, pady=2)
                    
                    # 保存entry引用
                    self.setting_entries[(section, key)] = entry
                    inner_row += 1
                
                row += 1
                
        except Exception as e:
            # 如果配置文件不存在或有问题，创建默认设置
            self._create_default_settings()
        
        # 创建按钮区域
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存所有设置", command=self._save_all_settings)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        reset_btn = ttk.Button(button_frame, text="重置默认值", command=self._reset_settings)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 导入导出按钮
        import_btn = ttk.Button(button_frame, text="导入配置", command=self._import_settings)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="导出配置", command=self._export_settings)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
    def _create_default_settings(self):
        """创建默认设置界面"""
        # 系统设置
        system_frame = ttk.LabelFrame(self.scrollable_frame, text="系统设置")
        system_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5, ipadx=5, ipady=5)
        system_frame.grid_columnconfigure(1, weight=1)
        
        # 数据库路径
        ttk.Label(system_frame, text="数据库路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        db_entry = ttk.Entry(system_frame, width=50)
        db_entry.insert(0, "data/database.db")
        db_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.setting_entries[("System", "DataSource")] = db_entry
        
        # 日志级别
        ttk.Label(system_frame, text="日志级别:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        log_entry = ttk.Entry(system_frame, width=50)
        log_entry.insert(0, "INFO")
        log_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.setting_entries[("System", "LogLevel")] = log_entry
        
        # 界面设置
        ui_frame = ttk.LabelFrame(self.scrollable_frame, text="界面设置")
        ui_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5, ipadx=5, ipady=5)
        ui_frame.grid_columnconfigure(1, weight=1)
        
        # 主题
        ttk.Label(ui_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        theme_entry = ttk.Entry(ui_frame, width=50)
        theme_entry.insert(0, "default")
        theme_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.setting_entries[("UI", "Theme")] = theme_entry
        
        # 字体大小
        ttk.Label(ui_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        font_entry = ttk.Entry(ui_frame, width=50)
        font_entry.insert(0, "12")
        font_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.setting_entries[("UI", "FontSize")] = font_entry
        
    def _save_all_settings(self):
        """保存所有设置到配置文件"""
        try:
            for (section, key), entry in self.setting_entries.items():
                value = entry.get()
                self.config_manager.set_value(section, key, value)
            
            self.show_message("成功", "所有设置已保存！")
            
        except Exception as e:
            self.show_message("错误", f"保存设置失败: {str(e)}", "error")
            
    def _reset_settings(self):
        """重置为默认设置"""
        if self.show_question("确认", "确定要重置所有设置为默认值吗？这将清除当前的所有自定义设置。"):
            try:
                # 清空所有输入框并设置默认值
                default_values = {
                    ("System", "DataSource"): "data/database.db",
                    ("System", "LogLevel"): "INFO",
                    ("UI", "Theme"): "default",
                    ("UI", "FontSize"): "12",
                }
                
                for (section, key), entry in self.setting_entries.items():
                    if (section, key) in default_values:
                        entry.delete(0, tk.END)
                        entry.insert(0, default_values[(section, key)])
                
                self.show_message("成功", "设置已重置为默认值")
                
            except Exception as e:
                self.show_message("错误", f"重置设置失败: {str(e)}", "error")
                
    def _import_settings(self):
        """导入配置文件"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("配置文件", "*.ini *.cfg"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # TODO: 实现配置文件导入逻辑
                self.show_message("提示", "配置导入功能开发中...")
            except Exception as e:
                self.show_message("错误", f"导入配置失败: {str(e)}", "error")
                
    def _export_settings(self):
        """导出配置文件"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".ini",
            filetypes=[("配置文件", "*.ini"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # TODO: 实现配置文件导出逻辑
                self.show_message("提示", "配置导出功能开发中...")
            except Exception as e:
                self.show_message("错误", f"导出配置失败: {str(e)}", "error") 