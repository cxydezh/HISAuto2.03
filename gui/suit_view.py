import tkinter as tk
from tkinter import ttk, messagebox
from core.action_manager import ActionManager
from core.suit_manager import SuitManager
from core.debug_manager import DebugManager
from core.ai_manager import AIManager
from core.function_manager import FunctionManager
from core.config_manager import ConfigManager
from core.database import Database
from core.logger import Logger

class SuitView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("行为组套管理")
        self.geometry("1200x800")
        
        # 初始化管理器
        self.action_manager = ActionManager()
        self.suit_manager = SuitManager()
        self.debug_manager = DebugManager()
        self.ai_manager = AIManager()
        self.function_manager = FunctionManager()
        self.config_manager = ConfigManager()
        self.db = Database()
        self.logger = Logger()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Excel导入区域
        self.create_excel_import_area()
        
        # 创建树形视图区域
        self.create_treeview_area()
        
        # 创建操作按钮区域
        self.create_button_area()
        
        # 创建详细信息显示区域
        self.create_detail_area()
        
        # 绑定事件
        self.bind_events()
        
        # 加载数据
        self.load_data()
        
    def create_excel_import_area(self):
        """创建Excel导入区域"""
        excel_frame = ttk.LabelFrame(self.main_frame, text="Excel导入")
        excel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Excel路径
        ttk.Label(excel_frame, text="Excel路径:").grid(row=0, column=0, padx=5, pady=5)
        self.excel_path = ttk.Entry(excel_frame, width=50)
        self.excel_path.grid(row=0, column=1, padx=5, pady=5)
        self.excel_path.insert(0, self.config_manager.get_excel_path())
        
        # Sheet编号
        ttk.Label(excel_frame, text="Sheet编号:").grid(row=0, column=2, padx=5, pady=5)
        self.sheet_num = ttk.Entry(excel_frame, width=10)
        self.sheet_num.grid(row=0, column=3, padx=5, pady=5)
        self.sheet_num.insert(0, self.config_manager.get_sheet_num())
        
        # 监测字段
        ttk.Label(excel_frame, text="监测字段:").grid(row=0, column=4, padx=5, pady=5)
        self.monitor_column = ttk.Entry(excel_frame, width=10)
        self.monitor_column.grid(row=0, column=5, padx=5, pady=5)
        self.monitor_column.insert(0, self.config_manager.get_monitor_column())
        
        # 导入按钮
        self.import_btn = ttk.Button(excel_frame, text="导入", command=self.import_excel)
        self.import_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # 保存按钮
        self.save_btn = ttk.Button(excel_frame, text="保存", command=self.save_excel_config)
        self.save_btn.grid(row=0, column=7, padx=5, pady=5)
        
    def create_treeview_area(self):
        """创建树形视图区域"""
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧树形视图
        self.suit_tree = ttk.Treeview(tree_frame, show="tree")
        self.suit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.suit_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.suit_tree.configure(yscrollcommand=scrollbar.set)
        
        # 创建右侧列表视图
        self.action_list = ttk.Treeview(tree_frame, columns=("type", "name", "next_id"), show="headings")
        self.action_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置列标题
        self.action_list.heading("type", text="类型")
        self.action_list.heading("name", text="名称")
        self.action_list.heading("next_id", text="下一步ID")
        
        # 添加滚动条
        scrollbar2 = ttk.Scrollbar(tree_frame, orient="vertical", command=self.action_list.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_list.configure(yscrollcommand=scrollbar2.set)
        
    def create_button_area(self):
        """创建操作按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建按钮
        self.new_btn = ttk.Button(button_frame, text="新建", command=self.new_suit)
        self.new_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(button_frame, text="编辑", command=self.edit_suit)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="删除", command=self.delete_suit)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(button_frame, text="刷新", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存", command=self.save_suit)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.use_suit_btn = ttk.Button(button_frame, text="使用组套", command=self.use_suit)
        self.use_suit_btn.pack(side=tk.LEFT, padx=5)
        
    def create_detail_area(self):
        """创建详细信息显示区域"""
        detail_frame = ttk.LabelFrame(self.main_frame, text="详细信息")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧详细信息
        left_frame = ttk.Frame(detail_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 基本信息
        ttk.Label(left_frame, text="组套名称:").grid(row=0, column=0, padx=5, pady=5)
        self.suit_name = ttk.Entry(left_frame, width=30)
        self.suit_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="组套备注:").grid(row=1, column=0, padx=5, pady=5)
        self.suit_note = tk.Text(left_frame, width=30, height=5)
        self.suit_note.grid(row=1, column=1, padx=5, pady=5)
        
        # 创建右侧详细信息
        right_frame = ttk.Frame(detail_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 行为元信息
        ttk.Label(right_frame, text="行为元类型:").grid(row=0, column=0, padx=5, pady=5)
        self.action_type_var = tk.StringVar()
        action_type_combo = ttk.Combobox(right_frame, 
                     values=["mouse", "keyboard", "class", "AI","image","function"],
                     state="readonly",
                     textvariable=self.action_type_var)
        action_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        # Bind the event to trigger on change
        action_type_combo.bind("<<ComboboxSelected>>", self._on_action_type_changed)
        
        ttk.Label(right_frame, text="行为元名称:").grid(row=1, column=0, padx=5, pady=5)
        self.action_name = ttk.Entry(right_frame, width=30)
        self.action_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(right_frame, text="下一步ID:").grid(row=2, column=0, padx=5, pady=5)
        self.next_id = ttk.Entry(right_frame, width=30)
        self.next_id.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(right_frame, text="调试组ID:").grid(row=3, column=0, padx=5, pady=5)
        self.debug_id = ttk.Entry(right_frame, width=30)
        self.debug_id.grid(row=3, column=1, padx=5, pady=5)
        
        # 创建函数选择区域
        function_frame = ttk.LabelFrame(right_frame, text="函数选择")
        function_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.function_tree = ttk.Treeview(function_frame, columns=("name",), show="headings", height=5)
        self.function_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.function_tree.heading("name", text="函数名称")
        
        ttk.Button(function_frame, text="导入函数", command=self.import_function).pack(side=tk.RIGHT, padx=5)
        
        # 创建AI选择区域
        ai_frame = ttk.LabelFrame(right_frame, text="AI选择")
        ai_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.ai_tree = ttk.Treeview(ai_frame, columns=("id", "name"), show="headings", height=5)
        self.ai_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ai_tree.heading("id", text="ID")
        self.ai_tree.heading("name", text="名称")
        
        ttk.Button(ai_frame, text="导入AI", command=self.import_ai).pack(side=tk.RIGHT, padx=5)
        
    def bind_events(self):
        """绑定事件"""
        self.suit_tree.bind("<<TreeviewSelect>>", self.on_suit_select)
        self.action_list.bind("<<TreeviewSelect>>", self.on_action_select)
        self.function_tree.bind("<<TreeviewSelect>>", self.on_function_select)
        self.ai_tree.bind("<<TreeviewSelect>>", self.on_ai_select)
        
    def load_data(self):
        """加载数据"""
        # 加载组套树形数据
        self.load_suit_tree()
        
        # 加载函数列表
        self.load_function_list()
        
        # 加载AI列表
        self.load_ai_list()
        
    def load_suit_tree(self):
        """加载组套树形数据"""
        # 清空现有数据
        for item in self.suit_tree.get_children():
            self.suit_tree.delete(item)
            
        # 添加根节点
        personal = self.suit_tree.insert("", "end", text="个人", values=("A0",))
        department = self.suit_tree.insert("", "end", text="科室", values=("A1",))
        global_node = self.suit_tree.insert("", "end", text="全局", values=("A2",))
        
        # 加载组套数据
        suits = self.suit_manager.get_all_suits()
        for suit in suits:
            parent = personal if suit.group_rank.startswith("A0") else (
                department if suit.group_rank.startswith("A1") else global_node
            )
            self.suit_tree.insert(parent, "end", text=suit.name, values=(suit.group_rank,))
            
    def load_function_list(self):
        """加载函数列表"""
        # 清空现有数据
        for item in self.function_tree.get_children():
            self.function_tree.delete(item)
            
        # 加载函数数据
        functions = self.function_manager.get_all_functions()
        for func in functions:
            self.function_tree.insert("", "end", values=(func.name,))
            
    def load_ai_list(self):
        """加载AI列表"""
        # 清空现有数据
        for item in self.ai_tree.get_children():
            self.ai_tree.delete(item)
            
        # 加载AI数据
        ai_list = self.ai_manager.get_all_ai()
        for ai in ai_list:
            self.ai_tree.insert("", "end", values=(ai.id, ai.name))
            
    def import_excel(self):
        """导入Excel文件"""
        # TODO: 实现Excel导入功能
        pass
        
    def save_excel_config(self):
        """保存Excel配置"""
        # TODO: 实现Excel配置保存功能
        pass
        
    def new_suit(self):
        """新建组套"""
        # TODO: 实现新建组套功能
        pass
        
    def edit_suit(self):
        """编辑组套"""
        # TODO: 实现编辑组套功能
        pass
        
    def delete_suit(self):
        """删除组套"""
        # TODO: 实现删除组套功能
        pass
        
    def refresh_data(self):
        """刷新数据"""
        self.load_data()
        
    def save_suit(self):
        """保存组套"""
        # TODO: 实现保存组套功能
        pass
        
    def use_suit(self):
        """使用组套"""
        # TODO: 实现使用组套功能
        pass
        
    def import_function(self):
        """导入函数"""
        # TODO: 实现导入函数功能
        pass
        
    def import_ai(self):
        """导入AI"""
        # TODO: 实现导入AI功能
        pass
        
    def on_suit_select(self, event):
        """组套选择事件处理"""
        # TODO: 实现组套选择事件处理
        pass
        
    def on_action_select(self, event):
        """行为元选择事件处理"""
        # TODO: 实现行为元选择事件处理
        pass
        
    def on_function_select(self, event):
        """函数选择事件处理"""
        # TODO: 实现函数选择事件处理
        pass
        
    def on_ai_select(self, event):
        """AI选择事件处理"""
        # TODO: 实现AI选择事件处理
        pass 
        
    def _on_action_type_changed(self, event):
        """处理行为元类型改变事件"""
        selected_type = self.action_type_var.get()
        print(f"Selected action type: {selected_type}")
        # TODO: 根据选择的行为元类型更新界面
