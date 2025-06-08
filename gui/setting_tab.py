import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config.config_manager import ConfigManager
# 其他必要import

class SettingTab(ttk.Frame):
    def __init__(self, master, main_window, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.main_window = main_window  # 可用于与主窗口交互
        self._create_widgets()
        self._load_settings()
        # 其他初始化

    def _create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 系统设置区域
        system_frame = ttk.LabelFrame(main_frame, text="系统设置")
        system_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 数据库路径设置
        ttk.Label(system_frame, text="数据库路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.db_path_var = tk.StringVar()
        self.db_path_entry = ttk.Entry(system_frame, textvariable=self.db_path_var, width=50)
        self.db_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(system_frame, text="浏览", command=self._browse_db_path).grid(row=0, column=2, padx=5, pady=5)
        
        # 日志级别设置
        ttk.Label(system_frame, text="日志级别:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_level_var = tk.StringVar()
        log_level_combo = ttk.Combobox(system_frame, textvariable=self.log_level_var, 
                                     values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_level_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 自动保存间隔
        ttk.Label(system_frame, text="自动保存间隔(秒):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.auto_save_var = tk.StringVar()
        self.auto_save_entry = ttk.Entry(system_frame, textvariable=self.auto_save_var, width=20)
        self.auto_save_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        system_frame.grid_columnconfigure(1, weight=1)
        
        # 界面设置区域
        ui_frame = ttk.LabelFrame(main_frame, text="界面设置")
        ui_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 主题设置
        ttk.Label(ui_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var, 
                                 values=["default", "dark", "light"], state="readonly")
        theme_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 字体大小设置
        ttk.Label(ui_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.font_size_var = tk.StringVar()
        font_size_spin = ttk.Spinbox(ui_frame, textvariable=self.font_size_var, from_=8, to=24, width=10)
        font_size_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ui_frame.grid_columnconfigure(1, weight=1)
        
        # 高级设置区域
        advanced_frame = ttk.LabelFrame(main_frame, text="高级设置")
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 调试模式
        self.debug_mode_var = tk.BooleanVar()
        debug_check = ttk.Checkbutton(advanced_frame, text="启用调试模式", variable=self.debug_mode_var)
        debug_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 自动更新
        self.auto_update_var = tk.BooleanVar()
        auto_update_check = ttk.Checkbutton(advanced_frame, text="自动检查更新", variable=self.auto_update_var)
        auto_update_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="保存设置", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置默认", command=self._reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出配置", command=self._export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导入配置", command=self._import_config).pack(side=tk.LEFT, padx=5)

    def _load_settings(self):
        """加载当前设置"""
        try:
            config = ConfigManager()
            # 加载系统设置
            self.db_path_var.set(config.get_value('System', 'DataSource', ''))
            self.log_level_var.set(config.get_value('System', 'LogLevel', 'INFO'))
            self.auto_save_var.set(config.get_value('System', 'AutoSaveInterval', '300'))
            
            # 加载界面设置  
            self.theme_var.set(config.get_value('UI', 'Theme', 'default'))
            self.font_size_var.set(config.get_value('UI', 'FontSize', '12'))
            
            # 加载高级设置
            self.debug_mode_var.set(config.get_value('Advanced', 'DebugMode', 'False') == 'True')
            self.auto_update_var.set(config.get_value('Advanced', 'AutoUpdate', 'True') == 'True')
        except Exception as e:
            messagebox.showerror("错误", f"加载设置失败: {str(e)}")

    def _save_settings(self):
        """保存设置"""
        try:
            config = ConfigManager()
            # 保存系统设置
            config.set_value('System', 'DataSource', self.db_path_var.get())
            config.set_value('System', 'LogLevel', self.log_level_var.get())
            config.set_value('System', 'AutoSaveInterval', self.auto_save_var.get())
            
            # 保存界面设置
            config.set_value('UI', 'Theme', self.theme_var.get())
            config.set_value('UI', 'FontSize', self.font_size_var.get())
            
            # 保存高级设置
            config.set_value('Advanced', 'DebugMode', str(self.debug_mode_var.get()))
            config.set_value('Advanced', 'AutoUpdate', str(self.auto_update_var.get()))
            
            messagebox.showinfo("成功", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def _reset_defaults(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认", "确定要重置为默认设置吗？"):
            self.db_path_var.set("data/his_auto.db")
            self.log_level_var.set("INFO")
            self.auto_save_var.set("300")
            self.theme_var.set("default")
            self.font_size_var.set("12")
            self.debug_mode_var.set(False)
            self.auto_update_var.set(True)

    def _browse_db_path(self):
        """浏览数据库文件路径"""
        filename = filedialog.asksaveasfilename(
            title="选择数据库文件",
            defaultextension=".db",
            filetypes=[("SQLite database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)

    def _export_config(self):
        """导出配置"""
        filename = filedialog.asksaveasfilename(
            title="导出配置文件",
            defaultextension=".ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        if filename:
            try:
                config = ConfigManager()
                # TODO: 实现配置导出功能
                messagebox.showinfo("提示", "配置导出功能待实现")
            except Exception as e:
                messagebox.showerror("错误", f"导出配置失败: {str(e)}")

    def _import_config(self):
        """导入配置"""
        filename = filedialog.askopenfilename(
            title="导入配置文件",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")]
        )
        if filename:
            try:
                # TODO: 实现配置导入功能
                messagebox.showinfo("提示", "配置导入功能待实现")
                self._load_settings()  # 重新加载设置
            except Exception as e:
                messagebox.showerror("错误", f"导入配置失败: {str(e)}")

    # 其他SettingTab专属方法 

    # 其它设置相关方法全部迁移到这里 