import tkinter as tk
from tkinter import ttk, messagebox
from gui.tabs.base_tab import BaseTab

class DebugTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "调试")
        
        # 创建界面
        self._create_widgets()
        
    def _create_widgets(self):
        """创建调试标签页的所有控件"""
        # 创建三列布局
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧面板（调试行为组）
        left_panel = ttk.Frame(self.frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建中间面板（调试行为列表）
        middle_panel = ttk.Frame(self.frame)
        middle_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建右侧面板（调试行为详情）
        right_panel = ttk.Frame(self.frame)
        right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建各个面板内容
        self._create_left_panel(left_panel)
        self._create_middle_panel(middle_panel)
        self._create_right_panel(right_panel)
        
    def _create_left_panel(self, parent):
        """创建左侧面板 - 调试行为组"""
        # 调试行为组详情
        group_frame = ttk.LabelFrame(parent, text="调试行为组详情")
        group_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        ttk.Label(group_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_group_name_entry = ttk.Entry(group_frame)
        self.debug_group_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(group_frame, text="创建时间:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_group_time_entry = ttk.Entry(group_frame)
        self.debug_group_time_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        group_frame.grid_columnconfigure(1, weight=1)
        
        # 调试行为组树形视图
        tree_frame = ttk.LabelFrame(parent, text="调试行为组")
        tree_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.debug_action_tree = ttk.Treeview(tree_frame, columns=("name", "userid"), show="tree headings")
        self.debug_action_tree.heading("#0", text="结构")
        self.debug_action_tree.heading("name", text="名称")
        self.debug_action_tree.heading("userid", text="创建者")
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.debug_action_tree.yview)
        self.debug_action_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.debug_action_tree.grid(row=0, column=0, sticky=tk.NSEW)
        tree_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="新建", command=self._new_debug_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑", command=self._edit_debug_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self._refresh_debug_groups).pack(side=tk.LEFT, padx=5)
        
        # 配置左侧面板权重
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _create_middle_panel(self, parent):
        """创建中间面板 - 调试行为列表"""
        # 调试行为列表
        list_frame = ttk.LabelFrame(parent, text="调试行为列表")
        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.debug_action_list = ttk.Treeview(list_frame, columns=("type", "name", "next"), show="headings")
        self.debug_action_list.heading("type", text="类型")
        self.debug_action_list.heading("name", text="名称")
        self.debug_action_list.heading("next", text="下一步")
        
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.debug_action_list.yview)
        self.debug_action_list.configure(yscrollcommand=list_scroll.set)
        
        self.debug_action_list.grid(row=0, column=0, sticky=tk.NSEW)
        list_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="创建", command=self._create_debug_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="修改", command=self._modify_debug_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self._delete_debug_action).pack(side=tk.LEFT, padx=5)
        
        # 配置中间面板权重
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _create_right_panel(self, parent):
        """创建右侧面板 - 调试行为详情"""
        # 调试行为详情
        detail_frame = ttk.LabelFrame(parent, text="调试行为详情")
        detail_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_name_entry = ttk.Entry(detail_frame)
        self.debug_action_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_type_combo = ttk.Combobox(detail_frame, 
                                                   values=["mouse", "keyboard", "class", "AI", "image", "function"],
                                                   state="readonly")
        self.debug_action_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="下一步:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_next_action_entry = ttk.Entry(detail_frame)
        self.debug_next_action_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="备注:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_note_entry = ttk.Entry(detail_frame)
        self.debug_action_note_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        detail_frame.grid_columnconfigure(1, weight=1)
        
        # 调试行为详细配置区域
        config_frame = ttk.LabelFrame(parent, text="详细配置")
        config_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 这里可以根据行为类型动态显示不同的配置选项
        self.debug_config_area = ttk.Frame(config_frame)
        self.debug_config_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置右侧面板权重
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
    def _new_debug_group(self):
        """新建调试行为组"""
        self.show_message("提示", "新建调试行为组功能")
        
    def _edit_debug_group(self):
        """编辑调试行为组"""
        self.show_message("提示", "编辑调试行为组功能")
        
    def _refresh_debug_groups(self):
        """刷新调试行为组列表"""
        self.debug_action_tree.delete(*self.debug_action_tree.get_children())
        # 添加示例数据
        self.debug_action_tree.insert("", "end", text="调试组1", values=("调试行为组1", "admin"))
        self.show_message("提示", "调试行为组列表已刷新")
        
    def _create_debug_action(self):
        """创建调试行为"""
        self.show_message("提示", "创建调试行为功能")
        
    def _modify_debug_action(self):
        """修改调试行为"""
        self.show_message("提示", "修改调试行为功能")
        
    def _delete_debug_action(self):
        """删除调试行为"""
        if self.show_question("确认", "确定要删除选中的调试行为吗？"):
            self.show_message("提示", "调试行为已删除") 