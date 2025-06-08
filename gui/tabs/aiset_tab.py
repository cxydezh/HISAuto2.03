import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab

class AISetTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "AI设置")
        
        # 初始化变量
        self._init_variables()
        
        # 创建界面
        self._create_widgets()
        
    def _init_variables(self):
        """初始化变量"""
        self.train_group_var = tk.StringVar()
        self.train_long_txt_var = tk.StringVar()
        self.long_txt_location_var = tk.StringVar()
        self.output_location_var = tk.StringVar()
        
    def _create_widgets(self):
        """创建AI设置标签页的控件"""
        # 创建两列布局
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=2)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧列表区域
        left_panel = ttk.Frame(self.frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建右侧详情区域
        right_panel = ttk.Frame(self.frame)
        right_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建各个面板内容
        self._create_left_panel(left_panel)
        self._create_right_panel(right_panel)
        
    def _create_left_panel(self, parent):
        """创建左侧面板 - AI操作列表"""
        # 创建AI操作列表
        list_frame = ttk.LabelFrame(parent, text="AI操作列表")
        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建列表视图和滚动条
        self.ai_list = ttk.Treeview(list_frame, columns=("id", "name"), show="headings")
        self.ai_list.heading("id", text="ID")
        self.ai_list.heading("name", text="名称")
        
        self.ai_list.column("id", width=100)
        self.ai_list.column("name", width=200)
        
        # 添加滚动条
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.ai_list.yview)
        self.ai_list.configure(yscrollcommand=list_scroll.set)
        
        # 布局
        self.ai_list.grid(row=0, column=0, sticky=tk.NSEW)
        list_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 添加示例数据
        self.ai_list.insert("", "end", values=("1", "语音识别AI"))
        self.ai_list.insert("", "end", values=("2", "图像识别AI"))
        self.ai_list.insert("", "end", values=("3", "文本分析AI"))
        
    def _create_right_panel(self, parent):
        """创建右侧面板 - AI操作详情"""
        # 创建详情显示区域
        detail_frame = ttk.LabelFrame(parent, text="AI操作详情")
        detail_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 训练组
        ttk.Label(detail_frame, text="训练组:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_group_entry = ttk.Entry(detail_frame, textvariable=self.train_group_var, width=40)
        self.train_group_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 训练长文本
        ttk.Label(detail_frame, text="训练长文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_long_txt_entry = ttk.Entry(detail_frame, textvariable=self.train_long_txt_var, width=40)
        self.train_long_txt_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 长文本位置
        ttk.Label(detail_frame, text="长文本位置:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.long_txt_location_entry = ttk.Entry(detail_frame, textvariable=self.long_txt_location_var, width=40)
        self.long_txt_location_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 输出位置
        ttk.Label(detail_frame, text="输出位置:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_location_entry = ttk.Entry(detail_frame, textvariable=self.output_location_var, width=40)
        self.output_location_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(detail_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="新建", command=self._new_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修改", command=self._modify_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self._delete_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self._save_ai_action).pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重
        detail_frame.grid_rowconfigure(4, weight=1)
        detail_frame.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _new_ai_action(self):
        """新建AI操作"""
        # 清空输入框
        self.train_group_var.set("")
        self.train_long_txt_var.set("")
        self.long_txt_location_var.set("")
        self.output_location_var.set("")
        self.show_message("提示", "已清空输入框，请输入新的AI操作信息")
        
    def _modify_ai_action(self):
        """修改AI操作"""
        selected_item = self.ai_list.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要修改的AI操作", "warning")
            return
            
        # 模拟加载选中的AI操作信息
        self.train_group_var.set("示例训练组")
        self.train_long_txt_var.set("示例长文本")
        self.long_txt_location_var.set("D:/HISAuto/LongTxt/示例")
        self.output_location_var.set("D:/HISAuto/outputTxt/示例")
        
        self.show_message("提示", "已加载选中的AI操作信息，可以进行修改")
        
    def _delete_ai_action(self):
        """删除AI操作"""
        selected_item = self.ai_list.selection()
        if not selected_item:
            self.show_message("警告", "请先选择要删除的AI操作", "warning")
            return
            
        if self.show_question("确认", "确定要删除选中的AI操作吗？"):
            self.ai_list.delete(selected_item)
            self._new_ai_action()  # 清空输入框
            self.show_message("提示", "AI操作已删除")
            
    def _save_ai_action(self):
        """保存AI操作"""
        # 验证必填字段
        if not self.train_group_var.get():
            self.show_message("警告", "训练组不能为空", "warning")
            return
            
        # 模拟保存到数据库
        # TODO: 实际保存到数据库的逻辑
        
        self.show_message("成功", "AI操作保存成功") 