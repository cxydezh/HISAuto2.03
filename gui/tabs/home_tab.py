import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from database.db_manager import DatabaseManager
from gui.tabs.base_tab import BaseTab
from models.actions import ActionGroup, ActionsGroupHierarchy, ActionList, ActionMouse, ActionKeyboard, ActionAI, ActionFunction, ActionClass, ActionPrintscreen
from models.user import User
from config.config_manager import ConfigManager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import globalvariable
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank

class HomeTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "首页")
        self.my_window = main_window.window
        # 初始化实例变量
        self.action_group_hierarchy_tree_iid = None
        """行为组树形视图选中项的iid,格式如：group_11或A1B2C3D4"""
        self.action_debug_list_tree_iid = None
        #show_model_pick中选择的相对位置
        self.relate_location_selected = None
        #行为组树形视图选中项的rank
        self.action_group_selected_rank = None
        #行为组树形视图选中项的rank中的sort_num的值
        self.hierarchy_sort = None
        #行为组类型，1:表示新增保存；2.表示修改保存；3.表示删除action_group；4.表示删除action_group_hierarchy；
        self.action_group_action_type = None
        #选中行为组ID
        self.action_group_id = None
        #选中行为组层次ID
        self.action_group_hierarchy_id = None
        #选中行为组树形视图选中项的iid
        # 行为组树形视图选中项的rank中的A的值
        self.action_group_selected_Arank = None
        # 创建界面
        self._create_widgets()
        
        # 数据更新
        self._refresh_action_group()
        
    def _create_widgets(self):
        """创建首页标签页的所有控件"""
        # 配置主框架的grid权重
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1) 
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # 创建三列面板
        self._create_left_panel()
        self._create_middle_panel()
        self._create_right_panel()
        
    def _create_left_panel(self):
        """创建左侧面板"""
        left_panel = ttk.Frame(self.frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # Excel导入区域
        self._create_excel_section(left_panel)
        
        # 行为组详情区域
        self._create_action_group_details(left_panel)
        
        # 行为组树形视图
        self._create_action_tree(left_panel)
        
        # 行为组按钮
        self._create_action_group_buttons(left_panel)
        
        # 配置权重
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_rowconfigure(2, weight=4)
        left_panel.grid_columnconfigure(0, weight=1)
        
    def _create_excel_section(self, parent):
        """创建Excel导入区域"""
        excel_frame = ttk.LabelFrame(parent, text="Excel导入")
        excel_frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # Excel路径
        ttk.Label(excel_frame, text="Excel路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.excel_path_var = tk.StringVar()
        ttk.Entry(excel_frame, textvariable=self.excel_path_var, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.btn_add_excel_file = ttk.Button(excel_frame, text="添加", command=self._add_excel_file, state="disabled")
        self.btn_add_excel_file.grid(row=0, column=3, padx=5, pady=5)
        
        # Sheet编号和监测字段
        ttk.Label(excel_frame, text="Sheet编号:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sheet_num_var = tk.StringVar()
        self.sheet_num_entry = ttk.Entry(excel_frame, textvariable=self.sheet_num_var, width=10)
        self.sheet_num_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(excel_frame, text="监测字段:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.column_var = tk.StringVar()
        self.column_entry = ttk.Entry(excel_frame, textvariable=self.column_var, width=10)
        self.column_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(excel_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        self.btn_import_excel = ttk.Button(button_frame, text="导入", command=self._import_excel, state="disabled")
        self.btn_import_excel.pack(side=tk.LEFT, padx=5)
        self.btn_save_excel_setting = ttk.Button(button_frame, text="保存", command=self._save_excel_settings, state="disabled")
        self.btn_save_excel_setting.pack(side=tk.LEFT, padx=5)
        
        excel_frame.grid_columnconfigure(1, weight=1)
        
    def _create_action_group_details(self, parent):
        """创建行为组详情区域"""
        action_group_frame = ttk.LabelFrame(parent, text="行为组详情")
        action_group_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 基本信息区域（第一行）
        basic_info_frame = ttk.Frame(action_group_frame)
        basic_info_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 行为组名称
        ttk.Label(basic_info_frame, text="名称:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_name_var = tk.StringVar()
        self.group_name_entry = ttk.Entry(basic_info_frame, textvariable=self.group_name_var, width=20, state="disabled")
        self.group_name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 上一次循环位置
        ttk.Label(basic_info_frame, text="上一次循环位置:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_last_circle_local_var = tk.StringVar()
        self.group_last_circle_local_entry = ttk.Entry(basic_info_frame, textvariable=self.group_last_circle_local_var, width=20, state="disabled")
        self.group_last_circle_local_entry.pack(side=tk.LEFT)
        
        # 时间信息区域（第二行）
        time_info_frame = ttk.Frame(action_group_frame)
        time_info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 上一次循环节点
        ttk.Label(time_info_frame, text="上一次循环节点:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_last_circle_node_var = tk.StringVar()
        self.group_last_circle_node_entry = ttk.Entry(time_info_frame, textvariable=self.group_last_circle_node_var, width=20, state="disabled")
        self.group_last_circle_node_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 创建时间
        ttk.Label(time_info_frame, text="创建时间:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_setup_time_var = tk.StringVar()
        self.group_setup_time_entry = ttk.Entry(time_info_frame, textvariable=self.group_setup_time_var, width=20, state="disabled")
        self.group_setup_time_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 用户信息区域（第三行）
        user_info_frame = ttk.Frame(action_group_frame)
        user_info_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 更新时间
        ttk.Label(user_info_frame, text="更新时间:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_update_time_var = tk.StringVar()
        self.group_update_time_entry = ttk.Entry(user_info_frame, textvariable=self.group_update_time_var, width=20, state="disabled")
        self.group_update_time_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 创建者ID
        ttk.Label(user_info_frame, text="创建者ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_user_id_var = tk.StringVar()
        self.group_user_id_entry = ttk.Entry(user_info_frame, textvariable=self.group_user_id_var, width=20, state="disabled")
        self.group_user_id_entry.pack(side=tk.LEFT)
        
        # 部门信息区域（第四行）
        dept_info_frame = ttk.Frame(action_group_frame)
        dept_info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 创建者姓名
        ttk.Label(dept_info_frame, text="创建者姓名:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_user_name_var = tk.StringVar()
        self.group_user_name_entry = ttk.Entry(dept_info_frame, textvariable=self.group_user_name_var, width=20, state="disabled")
        self.group_user_name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 科室ID
        ttk.Label(dept_info_frame, text="科室:").pack(side=tk.LEFT, padx=(0, 5))
        self.department_id_var = tk.StringVar()
        self.department_id_entry = ttk.Entry(dept_info_frame, textvariable=self.department_id_var, width=10, state="disabled")
        self.department_id_entry.pack(side=tk.LEFT)
        
        # 自动执行区域（第五行）
        auto_exec_frame = ttk.Frame(action_group_frame)
        auto_exec_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 是否自动执行
        self.is_auto_var = tk.BooleanVar()
        self.is_auto_check = ttk.Checkbutton(auto_exec_frame, text="自动执行", variable=self.is_auto_var, state="disabled")
        self.is_auto_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 自动执行时间
        ttk.Label(auto_exec_frame, text="自动执行时间:").pack(side=tk.LEFT, padx=(0, 5))
        self.auto_time_var = tk.StringVar()
        self.auto_time_entry = ttk.Entry(auto_exec_frame, textvariable=self.auto_time_var, width=20, state="disabled")
        self.auto_time_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.auto_time_entry.bind("<Button-1>", lambda e: self.main_window.show_time_picker(self.main_window.window, self.auto_time_entry))
        
        # 描述区域（第六行）
        desc_frame = ttk.Frame(action_group_frame)
        desc_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 行为组备注
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_desc_var = tk.StringVar()
        self.group_desc_entry = ttk.Entry(desc_frame, textvariable=self.group_desc_var, width=50, state="disabled")
        self.group_desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 配置权重
        action_group_frame.grid_columnconfigure(0, weight=1)
        action_group_frame.grid_columnconfigure(1, weight=1)
        
    def _create_action_tree(self, parent):
        """创建行为组树形视图"""
        tree_frame = ttk.LabelFrame(parent, text="行为组")
        tree_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建树形视图
        self.action_tree = ttk.Treeview(tree_frame, name='actiongroup_hierarchy_tree', 
                                       columns=("name", "userid"), selectmode='browse', show="tree headings")
        self.action_tree.heading("#0", text="结构")
        self.action_tree.column("#0", width=60)
        self.action_tree.heading("name", text="名称")
        self.action_tree.column("name", width=150)
        self.action_tree.heading("userid", text="创建者")
        self.action_tree.column("userid", width=50)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=tree_scroll.set)
        self.action_tree.bind('<<TreeviewSelect>>', self._on_action_tree_select)
        
        # 布局
        self.action_tree.grid(row=0, column=0, sticky=tk.NSEW)
        tree_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def _create_action_group_buttons(self, parent):
        """创建行为组相关按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_new_action_group_group = ttk.Button(button_frame, text="新建组", command=self._new_action_group_group, state="disabled")
        self.btn_new_action_group_group.pack(side=tk.LEFT, padx=5)
        self.btn_new_action_group = ttk.Button(button_frame, text="新建", command=self._new_action_group, state="disabled")
        self.btn_new_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_edit_action_group = ttk.Button(button_frame, text="编辑", command=self._edit_action_group, state="disabled")
        self.btn_edit_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_save_action_group = ttk.Button(button_frame, text="保存", command=self._save_action_group, state="disabled")
        self.btn_save_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_capture_image = ttk.Button(button_frame, text="图像采集", command=self._capture_image, state="disabled")
        self.btn_capture_image.pack(side=tk.LEFT, padx=5)
        self.btn_refresh_action_group = ttk.Button(button_frame, text="刷新", command=self._refresh_action_group, state="disabled")
        self.btn_refresh_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_delete_action_group = ttk.Button(button_frame, text="删除", command=self._delete_action_group, state="disabled")
        self.btn_delete_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_run_action_group = ttk.Button(button_frame, text="运行", command=self._run_action_group, state="disabled")
        self.btn_run_action_group.pack(side=tk.LEFT, padx=5)
        
    def _create_middle_panel(self):
        """创建中间面板（行为列表）"""
        left1_panel = ttk.Frame(self.frame)
        left1_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 行为列表详情
        action_list_frame_main = ttk.Frame(left1_panel)
        action_list_frame_main.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 主要详情控件
        content_frame = ttk.Frame(action_list_frame_main)
        content_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 行为名称
        ttk.Label(content_frame, text="行为名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_name_var = tk.StringVar()
        self.action_name_entry = ttk.Entry(content_frame, textvariable=self.action_name_var, state="disabled")
        self.action_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 下一步行为
        ttk.Label(content_frame, text="下一步行为:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.next_action_var = tk.StringVar()
        self.next_action_entry = ttk.Entry(content_frame, textvariable=self.next_action_var, state="disabled")
        self.next_action_entry.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        
        # 行为类型
        ttk.Label(content_frame, text="行为类型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_type_var = tk.StringVar()
        self.action_type_combo = ttk.Combobox(content_frame, 
                                            values=["mouse", "keyboard", "class", "AI", "image", "function"],
                                            state="readonly", textvariable=self.action_type_var)
        self.action_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 绑定事件 - 简化事件绑定方式
        self.action_type_combo.bind('<<ComboboxSelected>>', self._on_action_type_changed)
        
        # 设置默认值
        self.action_type_var.set("mouse")
        
        # 调试组ID
        ttk.Label(content_frame, text="调试组ID:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.debug_group_id = tk.StringVar()
        self.debug_group_id_entry = ttk.Entry(content_frame, textvariable=self.debug_group_id)
        self.debug_group_id_entry.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)
        
        # 行为备注
        ttk.Label(content_frame, text="行为备注:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_note_var = tk.StringVar()
        self.action_note_entry = ttk.Entry(content_frame, textvariable=self.action_note_var)
        self.action_note_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置权重
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)
        
        # 动态显示区域
        self.action_list_frame = ttk.Frame(action_list_frame_main)
        self.action_list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        self.action_list_frame.pack_propagate(False)
        self.action_list_frame.configure(height=100)
        self.action_list_frame.grid_rowconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        
        # 延迟初始化，确保默认值已设置
        self.frame.after_idle(self._on_action_type_changed)
        
        # 行为列表
        list_frame = ttk.LabelFrame(left1_panel, text="行为列表")
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.action_list = ttk.Treeview(list_frame, name='action_list_tree', 
                                       columns=("type", "name", "next"), show="headings")
        self.action_list.heading("type", text="类型")
        self.action_list.heading("name", text="名称")
        self.action_list.heading("next", text="下一步")
        self.action_list.column("type", width=100)
        self.action_list.column("name", width=200)
        self.action_list.column("next", width=100)
        
        # 滚动条
        action_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.action_list.yview)
        self.action_list.configure(yscrollcommand=action_scroll.set)
        
        # 布局
        self.action_list.grid(row=0, column=0, sticky=tk.NSEW)
        action_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 绑定选择事件
        self.action_list.bind('<<TreeviewSelect>>', self._on_action_list_select)
        
        # 行为列表按钮
        action_button_frame = ttk.Frame(left1_panel)
        action_button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_create_action = ttk.Button(action_button_frame, text="创建", command=self._create_action)
        self.btn_create_action.pack(side=tk.LEFT, padx=5)
        self.btn_record_action = ttk.Button(action_button_frame, text="录制", command=self._record_action)
        self.btn_record_action.pack(side=tk.LEFT, padx=5)
        self.btn_modify_action = ttk.Button(action_button_frame, text="修改", command=self._modify_action)
        self.btn_modify_action.pack(side=tk.LEFT, padx=5)
        self.btn_delete_action = ttk.Button(action_button_frame, text="删除", command=self._delete_action)
        self.btn_delete_action.pack(side=tk.LEFT, padx=5)
        self.btn_save_action = ttk.Button(action_button_frame, text="保存", command=self._save_action)
        self.btn_save_action.pack(side=tk.LEFT, padx=5)
        self.btn_use_suit = ttk.Button(action_button_frame, text="调用套餐", command=self._use_suit)
        self.btn_use_suit.pack(side=tk.LEFT, padx=5)
        
        # 配置权重
        left1_panel.grid_rowconfigure(0, weight=1)
        left1_panel.grid_rowconfigure(1, weight=1)
        left1_panel.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
    def _create_right_panel(self):
        """创建右侧面板（调试列表）"""
        right_panel = ttk.Frame(self.frame)
        right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 调试行为详情区域
        debug_detail_frame = ttk.LabelFrame(right_panel, text="调试行为详情")
        debug_detail_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建基本信息区域
        content_debug_frame = ttk.Frame(debug_detail_frame)
        content_debug_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 调试行为名称
        ttk.Label(content_debug_frame, text="行为名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_name_var = tk.StringVar()
        self.action_debug_name_entry = ttk.Entry(content_debug_frame, textvariable=self.action_debug_name_var, state="disabled")
        self.action_debug_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 下一步行为ID
        ttk.Label(content_debug_frame, text="下一步行为ID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.next_debug_id_var = tk.StringVar()
        self.next_debug_id_entry = ttk.Entry(content_debug_frame, textvariable=self.next_debug_id_var, state="disabled")
        self.next_debug_id_entry.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        
        # 行为类型
        ttk.Label(content_debug_frame, text="行为类型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_type_var = tk.StringVar()
        self.action_debug_type_combo = ttk.Combobox(content_debug_frame, 
                                                   values=["mouse", "keyboard", "class", "AI", "image", "function"],
                                                   state="readonly", textvariable=self.action_debug_type_var)
        self.action_debug_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 绑定选择事件 - 简化事件绑定方式
        self.action_debug_type_combo.bind('<<ComboboxSelected>>', self._on_debug_action_type_changed)
        
        # 设置默认值
        self.action_debug_type_var.set("mouse")
        
        # 返回ID
        ttk.Label(content_debug_frame, text="返回ID:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.back_id_var = tk.StringVar()
        self.back_id_entry = ttk.Entry(content_debug_frame, textvariable=self.back_id_var, state="disabled")
        self.back_id_entry.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)
        
        # 行为备注
        ttk.Label(content_debug_frame, text="行为备注:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_note_var = tk.StringVar()
        self.action_debug_note_entry = ttk.Entry(content_debug_frame, textvariable=self.action_debug_note_var, state="disabled")
        self.action_debug_note_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        content_debug_frame.grid_columnconfigure(1, weight=1)
        content_debug_frame.grid_columnconfigure(3, weight=1)
        
        # 创建调试行为详情子区域（动态显示）
        self.action_debug_detail = ttk.Frame(debug_detail_frame)
        self.action_debug_detail.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        self.action_debug_detail.pack_propagate(False)
        self.action_debug_detail.configure(height=100)
        self.action_debug_detail.grid_rowconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        
        # 延迟初始化调试行为类型变更事件，确保默认值已设置
        self.frame.after_idle(self._on_debug_action_type_changed)
        
        # 调试列表
        debug_frame = ttk.LabelFrame(right_panel, text="调试行为列表")
        debug_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.action_debug_list = ttk.Treeview(debug_frame, name='action_debug_list_tree',
                                            columns=("type", "name", "next"), show="headings")
        self.action_debug_list.heading("type", text="类型")
        self.action_debug_list.heading("name", text="名称")
        self.action_debug_list.heading("next", text="下一步")
        self.action_debug_list.column("type", width=100)
        self.action_debug_list.column("name", width=200)
        self.action_debug_list.column("next", width=100)
        
        # 绑定选择事件
        self.action_debug_list.bind('<<TreeviewSelect>>', self._on_debug_action_list_select)
        
        # 滚动条
        debug_scroll = ttk.Scrollbar(debug_frame, orient="vertical", command=self.action_debug_list.yview)
        self.action_debug_list.configure(yscrollcommand=debug_scroll.set)
        
        # 布局
        self.action_debug_list.grid(row=0, column=0, sticky=tk.NSEW)
        debug_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 调试按钮
        debug_button_frame = ttk.Frame(right_panel)
        debug_button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_create_debug_action = ttk.Button(debug_button_frame, text="创建", command=self._create_debug_action)
        self.btn_create_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_modify_debug_action = ttk.Button(debug_button_frame, text="修改", command=self._modify_debug_action)
        self.btn_modify_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_delete_debug_action = ttk.Button(debug_button_frame, text="删除", command=self._delete_debug_action)
        self.btn_delete_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_save_debug_action = ttk.Button(debug_button_frame, text="保存", command=self._save_debug_action)
        self.btn_save_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_use_debug_suit = ttk.Button(debug_button_frame, text="调用套餐", command=self._use_debug_suit)
        self.btn_use_debug_suit.pack(side=tk.LEFT, padx=5)
        
        # 配置权重
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        debug_detail_frame.grid_rowconfigure(1, weight=1)
        debug_detail_frame.grid_columnconfigure(0, weight=1)
        debug_frame.grid_rowconfigure(0, weight=1)
        debug_frame.grid_columnconfigure(0, weight=1)

    '''逻辑代码区域'''
    
    # =============================================================================
    # 左侧面板相关方法（Excel导入 -> 行为组树 -> 行为组操作）
    # =============================================================================
    
    # Excel操作方法
    def _add_excel_file(self):
        """添加Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path_var.set(file_path)
            
    def _import_excel(self):
        """导入Excel"""
        messagebox.showinfo("提示", "Excel导入功能待实现")
        
    def _save_excel_settings(self):
        """保存Excel设置"""
        messagebox.showinfo("提示", "Excel设置保存功能待实现")
    
    def _on_action_tree_select(self, event=None):
        """行为组树选择事件处理"""
        selected = self.action_tree.selection()
        if not selected:
            return
        iid = selected[0]
        if iid in("A0","A1","A2"):
            self._set_action_group_entry_controls_state('disabled')
            self._set_action_group_button_controls_state('disabled') 
            self.btn_run_action_group.config(state='disabled')
            return
        self.action_tree_selected_iid = iid
        # 先全部禁用
        self._set_home_controls_state('disabled')
        
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
        
        try:
            config = ConfigManager()
            db_url = config.get_value('System', 'DataSource')
            encryption_key = config.get_value('Security', 'DBEncryptionKey')
            db_manager = DatabaseManager(db_url, encryption_key)
            db_manager.initialize()
            session = db_manager.Session()
            
            if iid.startswith("group_"):
                # 选中的是ActionGroup
                group_id = int(iid.split("_")[1])
                self.action_group_id = group_id
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                if group:
                    self.action_group_hierarchy_tree_iid = group.group_rank_id
                    selected_group_hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                    self.action_group_hierarchy_id = group.group_rank_id
                    # 填充详情区
                    self.group_name_var.set(group.action_list_group_name or "")
                    self.group_last_circle_local_var.set(group.last_circle_local or "")
                    self.group_last_circle_node_var.set(group.last_circle_node or "")
                    self.group_setup_time_var.set(str(group.setup_time or ""))
                    self.group_update_time_var.set(str(group.update_time or ""))
                    self.group_user_id_var.set(str(group.user_id or ""))
                    
                    user = session.query(User).filter_by(user_id=group.user_id).first()
                    self.group_user_name_var.set(user.username if user else "")
                    self.department_id_var.set(str(group.department_id or ""))
                    self.is_auto_var.set(bool(group.is_auto or False))
                    self.auto_time_var.set(str(group.auto_time or ""))
                    self.group_desc_var.set(group.action_list_group_note or "")
                    #获取行为组的group_rank_id
                    self.action_group_hierarchy_id = group.group_rank_id
                    
                    # 填充action_list_tree
                    self.action_list.delete(*self.action_list.get_children())
                    actions = session.query(ActionList).filter_by(group_id=group_id).all()
                    for action in actions:
                        self.action_list.insert("", "end", iid=str(action.id), values=(
                            action.action_type, action.action_name, action.next_id
                        ))
                    self.hierarchy_sort = selected_group_hierarchy.sort_num
                    selected_group_rank = selected_group_hierarchy.group_rank
            else:
                # 选中的是ActionsGroupHierarchy
                selected_group_rank = iid_to_group_rank(iid)
                self.action_group_hierarchy_tree_iid = selected_group_rank
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=self.action_group_hierarchy_tree_iid).first()
                if hierarchy:
                    self.group_name_var.set(hierarchy.group_name or "")
                    self.group_last_circle_local_var.set("")
                    self.group_last_circle_node_var.set("")
                    self.group_setup_time_var.set(str(hierarchy.created_at or ""))
                    self.group_update_time_var.set(str(hierarchy.updated_at or ""))
                    self.group_user_id_var.set(str(hierarchy.doctor_id or ""))
                    self.group_user_name_var.set("")
                    self.department_id_var.set(str(hierarchy.department_id or ""))
                    self.is_auto_var.set(False)
                    self.auto_time_var.set("")
                    self.group_desc_var.set(hierarchy.group_note or "")

                    self.action_group_hierarchy_id = hierarchy.id   
                    self.hierarchy_sort = hierarchy.sort_num
                    self.action_group_id = None
                
                # 禁用中间按钮
                for btn in [
                    self.btn_create_action, self.btn_record_action, self.btn_modify_action,
                    self.btn_delete_action, self.btn_save_action, self.btn_use_suit
                ]:
                    btn.config(state='disabled')
                
                # 清空action_list_tree
                self.action_list.delete(*self.action_list.get_children())
            self.action_group_selected_rank = selected_group_rank
            session.close()
        except Exception as e:
            print(f"Error in _on_action_tree_select: {e}")
        #根据当前用户的权限，设置部分控件的可用状态
        if globalvariable.USER_IS_SUPER_ADMIN:
            #超级管理员
            self._set_action_group_entry_controls_state('normal')
            self._set_action_group_button_controls_state('normal')
        else:
            #管理员
            #判断当前选中项的rank中的A的值
            rank_dict = parse_group_rank(self.action_group_selected_rank)
            if globalvariable.USER_IS_ADMIN:
                if (rank_dict['A'] == 1 and globalvariable.USER_DEPARTMENT_ID == self.department_id_var.get()) or (rank_dict['A'] == 0):
                    self._set_action_group_entry_controls_state('normal')
                    self._set_action_group_button_controls_state('normal')
                else:
                    self._set_action_group_entry_controls_state('disabled')
                    self._set_action_group_button_controls_state('disabled')
        if iid.startswith("group_"):
            self.btn_run_action_group.config(state='normal')
        else:
            self.btn_run_action_group.config(state='disabled')
        
    def _refresh_action_group(self):
        """刷新行为组树，按GroupRank分层显示"""
        try:
            config = ConfigManager()
            db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # 清空树
            self.action_tree.delete(*self.action_tree.get_children())
            
            # 查询所有行为组层级，按group_rank排序
            hierarchies = session.query(ActionsGroupHierarchy).order_by(ActionsGroupHierarchy.sort_num,ActionsGroupHierarchy.group_rank).all()
            
            # 构建分层树结构
            tree_dict = {}
            for h in hierarchies:
                rank_dict = parse_group_rank(h.group_rank)
                key = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
                
                # 根据用户权限过滤
                if globalvariable.USER_IS_SUPER_ADMIN:
                    tree_dict[key] = {
                        'obj': h,
                        'iid': None,
                        'children': [],
                        'parent': None
                    }
                else:
                    # 普通用户只能看到全局(A=2)或自己科室的层级
                    if rank_dict['A'] == 2 or h.department_id == globalvariable.USER_DEPARTMENT_ID:
                        tree_dict[key] = {
                            'obj': h,
                            'iid': None,
                            'children': [],
                            'parent': None
                        }
            
            # 建立父子关系
            for key, node in tree_dict.items():
                rank = parse_group_rank(key)
                
                # 确定父节点key和当前节点iid
                if rank['E'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E0"
                    parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
                elif rank['D'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}D0E0"
                    parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                elif rank['C'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}C0D0E0"
                    parent_iid = f"A{rank['A']}B{rank['B']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                elif rank['B'] > 0:
                    parent_key = f"A{rank['A']}B0C0D0E0"
                    parent_iid = f"A{rank['A']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}"
                else:
                    parent_key = None
                    parent_iid = None
                    node['iid'] = f"A{rank['A']}"
                
                # 设置父子关系
                if parent_key and parent_key in tree_dict:
                    node['parent'] = parent_iid
                    tree_dict[parent_key]['children'].append(key)
                else:
                    node['parent'] = None
            
            # 递归插入节点到Treeview
            def insert_node(key, parent_iid):
                if key not in tree_dict:
                    return
                    
                node = tree_dict[key]
                h = node['obj']
                user = session.query(User).filter_by(user_id=h.doctor_id).first()
                username = user.username if user else "未知"
                
                # 插入当前节点
                if parent_iid == "":
                    self.action_tree.insert("", "end", iid=node['iid'], text=h.group_name, 
                                          values=(h.group_name, username))
                else:
                    self.action_tree.insert(parent_iid, "end", iid=node['iid'], text="📁", 
                                          values=(h.group_name, username))
                
                # 递归插入子节点
                for child_key in node['children']:
                    insert_node(child_key, node['iid'])
            
            # 插入顶层节点（A级节点，B=C=D=E=0）
            inserted_nodes = set()  # 记录已插入的节点，避免重复
            for key, node in tree_dict.items():
                rank = parse_group_rank(key)
                if (rank['B'] == 0 and rank['C'] == 0 and 
                    rank['D'] == 0 and rank['E'] == 0):
                    if key not in inserted_nodes:
                        insert_node(key, "")
                        inserted_nodes.add(key)
            
            # 查询所有行为组，插入到对应层级下
            groups = session.query(ActionGroup).all()
            for group in groups:
                if not hasattr(group, 'group_rank_id') or not group.group_rank_id:
                    continue
                    
                # 获取行为组对应的层级
                rank_record = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                if not rank_record:
                    continue
                    
                rank_dict = parse_group_rank(rank_record.group_rank)
                
                # 确定行为组应该插入到哪个层级节点下
                if rank_dict['E'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
                elif rank_dict['D'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
                elif rank_dict['C'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
                elif rank_dict['B'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}"
                else:
                    parent_iid = f"A{rank_dict['A']}"
                
                # 检查父节点是否存在
                try:
                    if self.action_tree.exists(parent_iid):
                        user = session.query(User).filter_by(user_id=group.user_id).first()
                        username = user.username if user else "未知"
                        
                        # 插入行为组节点
                        self.action_tree.insert(parent_iid, "end", text="📄", 
                                              values=(group.action_list_group_name, username), 
                                              iid=f"group_{group.id}")
                except tk.TclError:
                    # 父节点不存在，跳过这个行为组
                    print(f"Warning: Parent node {parent_iid} not found for group {group.id}")
                    continue
            
            session.close()
            
            # 启用刷新按钮
            self.btn_refresh_action_group.config(state='normal')
            
        except Exception as e:
            print(f"Error in _refresh_action_group: {e}")
            messagebox.showerror("错误", f"刷新行为组失败: {e}")
    def _new_action_group_group(self):
        """新建行为组组"""
        #先判断是否有Hierarchy tree是否有被选中的项目
        selected_iid = self.action_tree.selection()[0]
        if self.actiongroup_hierarchy_tree_iid == None: 
            messagebox.showinfo("提示", "请先选择行为组")
            return
        
        #调用show_mode_picker方法,获取用户的新建意图
        self.show_mode_picker(self.my_window)
        if self.relate_location_selected == None:
            return
        from utils.actionGroupHierarchyManager import ActionGroupHierarchy_Manager
        ActionGroupHierarchy_Manager(self.my_window, self.actiongroup_hierarchy_tree_iid, self.relate_location_selected, self.hierarchy_sort)
        #关闭窗口

        #刷新行为组树
        self._refresh_action_group()
        
    # 行为组操作方法
    def _new_action_group(self):
        """新建行为组"""
        #先判断是否有Hierarchy tree是否有被选中的项目
        if self.action_group_hierarchy_tree_iid == None: 
            messagebox.showinfo("提示", "请先选择行为组")
            return
        self.group_name_entry.config(state='normal')
        self.group_last_circle_local_entry.config(state='disabled')
        self.group_last_circle_node_entry.config(state='disabled')
        self.group_setup_time_entry.config(state='disabled')
        self.group_update_time_entry.config(state='disabled')
        self.is_auto_check.config(state='normal')
        self.auto_time_entry.config(state='normal')
        self.group_desc_entry.config(state='normal')

        #初始化行为组信息
        self.group_name_var.set("")
        self.group_last_circle_local_var.set("")
        self.group_last_circle_node_var.set("")
        self.group_setup_time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.group_update_time_var.set("")
        self.group_user_id_var.set(globalvariable.USER_ID)
        self.is_auto_var.set(False)
        self.auto_time_var.set("")
        self.group_desc_var.set("")
        
        #修改行为组相关按钮
        self.btn_new_action_group.config(state='disabled')
        self.btn_edit_action_group.config(state='disabled')
        self.btn_delete_action_group.config(state='normal')
        self.btn_capture_image.config(state='normal')
        self.btn_save_action_group.config(state='normal')
        self.btn_refresh_action_group.config(state='normal')
        self.action_group_action_type = 1
    def _edit_action_group(self):
        #先判断是否有Hierarchy tree是否有被选中的项目
        selected_iid = self.action_tree.selection()[0]
        if self.actiongroup_hierarchy_tree_iid == None: 
            messagebox.showinfo("提示", "请先选择行为组")
            return
        #调用show_mode_picker方法,获取用户的新建意图
        self.show_mode_picker(self.my_window)
        if self.relate_location_selected == None:
            return

        #修改行为组相关按钮
        self.btn_new_action_group.config(state='disabled')
        self.btn_edit_action_group.config(state='disabled')
        self.btn_delete_action_group.config(state='normal')
        self.btn_capture_image.config(state='normal')
        self.btn_save_action_group.config(state='normal')
        self.btn_refresh_action_group.config(state='normal')
        self.action_group_action_type = 2
    def _save_action_group(self):
        """保存行为组"""
        from utils.home_tab_func import home_tab_func
        home_tab_func_model = home_tab_func(self.group_name_var.get(), self.group_desc_var.get(),
                                            globalvariable.USER_ID,globalvariable.USER_DEPARTMENT_ID,
                                            self.is_auto_var.get(),self.auto_time_var.get(),
                                            self.action_group_selected_rank,self.action_tree_selected_iid,
                                            self.action_group_action_type,self.hierarchy_sort,
                                            self.action_group_id,self.action_group_hierarchy_id)
        if home_tab_func_model._save_action_group():
            messagebox.showinfo("提示", "保存行为组成功")
        else:
            messagebox.showerror("错误", "保存行为组失败")
        home_tab_func_model._session_close()
        self._refresh_action_group()
        for widget in (self.btn_new_action_group,self.btn_edit_action_group,self.btn_delete_action_group,self.btn_capture_image,self.btn_save_action_group, \
                    self.group_name_entry,self.group_desc_entry,self.auto_time_entry,self.is_auto_check):
            widget.config(state='disabled')
        self.btn_save_action_group.config(state='disabled')
    def _capture_image(self):
        """图像采集"""
        messagebox.showinfo("提示", "图像采集功能待实现")
    def _delete_action_group(self):
        """删除行为组"""
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为组")
            return
        if messagebox.askyesno("确认", "确定要删除选中的行为组吗？"):
            from utils.home_tab_func import home_tab_func
            home_tab_func_model = home_tab_func(self.group_name_var.get(), self.group_desc_var.get(),
                                            globalvariable.USER_ID,globalvariable.USER_DEPARTMENT_ID,
                                            self.is_auto_var.get(),self.auto_time_var.get(),
                                            self.action_group_selected_rank,self.action_tree_selected_iid,
                                            3,self.hierarchy_sort,
                                            self.action_group_id,self.action_group_hierarchy_id)
            home_tab_func_model._get_session()
            if home_tab_func_model._delete_action_group():
                messagebox.showinfo("提示", "删除行为组成功")
            else:
                messagebox.showerror("错误", "删除行为组失败")
            home_tab_func_model._session_close()
            self._refresh_action_group()
    def _run_action_group(self):
        """运行行为组"""
        messagebox.showinfo("提示", "运行行为组功能待实现")
    # =============================================================================
    # 中间面板相关方法（行为类型切换 -> 控件创建 -> 行为列表 -> 行为操作）
    # =============================================================================
    
    # 行为类型切换相关方法
    def _on_action_type_changed(self, event=None):
        """行为类型改变时的处理"""
        # 检查容器是否已创建
        if not hasattr(self, 'action_list_frame') or not self.action_list_frame.winfo_exists():
            return
        
        # 清空动态区域
        for widget in self.action_list_frame.winfo_children():
            widget.destroy()
            
        # 直接从Combobox获取当前值
        action_type = self.action_type_var.get()
        print(f"Action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.action_list_frame, text="请选择行为类型", font=("Arial", 12))
            welcome_label.pack(expand=True)
            return
        
        if action_type == "mouse":
            self._create_mouse_controls()
        elif action_type == "keyboard":
            self._create_keyboard_controls()
        elif action_type == "class":
            self._create_class_controls()
        elif action_type == "AI":
            self._create_ai_controls()
        elif action_type == "image":
            self._create_image_controls()
        elif action_type == "function":
            self._create_function_controls()
            
        # 强制更新界面
        self.action_list_frame.update_idletasks()
    
    # 动态控件创建方法（按类型顺序：mouse -> keyboard -> class -> AI -> image -> function）
    def _create_mouse_controls(self):
        """创建鼠标控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_list_frame)
        right_frame = ttk.Frame(self.action_list_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 鼠标动作
        ttk.Label(left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_mouse_action_type_var = tk.StringVar(master=self.frame)
        mouse_action_combo = ttk.Combobox(left_frame, 
                                       values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                       textvariable=self.action_mouse_action_type_var, state="readonly")
        mouse_action_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_mouse_size_var = tk.StringVar(master=self.frame)
        ttk.Entry(left_frame, textvariable=self.action_mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_mouse_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_mouse_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_mouse_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)
        
    def _create_keyboard_controls(self):
        """创建键盘控件"""
        # 键盘类型
        ttk.Label(self.action_list_frame, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_keyboard_type_var = tk.StringVar(master=self.frame)
        keyboard_type_combo = ttk.Combobox(self.action_list_frame, 
                                        values=["按下", "释放", "单击", "文本"],
                                        textvariable=self.action_keyboard_type_var, state="readonly")
        keyboard_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 按键值或文本内容
        ttk.Label(self.action_list_frame, text="按键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_keyboard_value_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_keyboard_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        
    def _create_class_controls(self):
        """创建类控件"""
        # 类名
        ttk.Label(self.action_list_frame, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_class_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗体名
        ttk.Label(self.action_list_frame, text="窗体名:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_window_title_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_window_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_class_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        
    def _create_ai_controls(self):
        """创建AI控件"""
        # 训练库名称
        ttk.Label(self.action_list_frame, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_training_group_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_training_group_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(self.action_list_frame, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_record_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_record_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(self.action_list_frame, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_long_text_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_long_text_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # AI网页输入框输入的文本内容
        ttk.Label(self.action_list_frame, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_illustration_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 备注信息
        ttk.Label(self.action_list_frame, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_note_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        
        
    def _create_image_controls(self):
        """创建图像控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_list_frame)
        right_frame = ttk.Frame(self.action_list_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 获取左上角坐标
        ttk.Button(left_frame, text="获取左上角坐标", command=self._get_left_top_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        # 获取右下角坐标
        ttk.Button(left_frame, text="获取右下角坐标", command=self._get_right_bottom_coordinates).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        # 截屏左上角x坐标
        ttk.Label(left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_left_top_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(left_frame, textvariable=self.action_image_left_top_x_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏左上角y坐标
        ttk.Label(left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_left_top_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(left_frame, textvariable=self.action_image_left_top_y_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角x坐标
        ttk.Label(left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_right_bottom_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(left_frame, textvariable=self.action_image_right_bottom_x_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角y坐标
        ttk.Label(left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_right_bottom_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(left_frame, textvariable=self.action_image_right_bottom_y_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # 图像名称
        ttk.Label(right_frame, text="图像名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_names_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_image_names_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
    

        # 匹配条件
        ttk.Label(right_frame, text="匹配条件:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_match_criteria_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_image_match_criteria_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_mouse_action_var = tk.StringVar(master=self.frame)
        mouse_action_combo = ttk.Combobox(right_frame, 
                                        textvariable=self.image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        
    def _create_function_controls(self):
        """创建函数控件"""
        # 函数名称
        ttk.Label(self.action_list_frame, text="函数名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_function_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_function_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数
        ttk.Label(self.action_list_frame, text="参数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_function_parameters_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_function_parameters_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数列表
        ttk.Label(self.action_list_frame, text="参数列表:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_function_arguments_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_function_arguments_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.function_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.function_time_diff_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

    def _get_left_top_coordinates(self):
        """获取左上角坐标"""
        x, y = self.main_window.get_mouse_position()
        self.action_image_left_top_x_var.set(str(x))
        self.action_image_left_top_y_var.set(str(y))

    def _get_right_bottom_coordinates(self):
        """获取右下角坐标"""
        x, y = self.main_window.get_mouse_position()
        self.action_image_right_bottom_x_var.set(str(x))
        self.action_image_right_bottom_y_var.set(str(y))
    
    # 行为列表相关方法
    def _on_action_list_select(self, event):
        """行为列表选择事件处理"""
        selected = self.action_list.selection()
        if not selected:
            return
            
        action_id = int(selected[0])
        
        # 启用相关控件
        for entry in [
            self.action_name_entry, self.next_action_entry, self.action_type_combo,
            self.debug_group_id_entry, self.action_note_entry
        ]:
            entry.config(state='normal')
    
    # 行为操作方法  
    def _create_action(self):
        """创建行为"""
        messagebox.showinfo("提示", "创建行为功能待实现")
        
    def _record_action(self):
        """录制行为"""
        messagebox.showinfo("提示", "录制行为功能待实现")
        
    def _modify_action(self):
        """修改行为"""
        messagebox.showinfo("提示", "修改行为功能待实现")
        
    def _delete_action(self):
        """删除行为"""
        selected = self.action_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的行为吗？"):
            messagebox.showinfo("提示", "删除行为功能待实现")
            
    def _save_action(self):
        """保存行为"""
        messagebox.showinfo("提示", "保存行为功能待实现")
        
    def _use_suit(self):
        """调用套餐"""
        messagebox.showinfo("提示", "调用套餐功能待实现")
    
    # =============================================================================
    # 右侧面板相关方法（调试行为类型切换 -> 调试控件创建 -> 调试列表 -> 调试操作）
    # =============================================================================
    
    # 调试行为类型切换相关方法
    def _on_debug_action_type_changed(self, event=None):
        """调试行为类型改变时的处理"""
        # 检查容器是否已创建
        if not hasattr(self, 'action_debug_detail') or not self.action_debug_detail.winfo_exists():
            return
        
        # 清空动态区域
        for widget in self.action_debug_detail.winfo_children():
            widget.destroy()
            
        # 直接从Combobox获取当前值
        action_type = self.action_debug_type_var.get()
        print(f"Debug action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.action_debug_detail, text="请选择行为类型", font=("Arial", 12))
            welcome_label.pack(expand=True)
            return
        
        if action_type == "mouse":
            self._create_mouse_controls_debug()
        elif action_type == "keyboard":
            self._create_keyboard_controls_debug()
        elif action_type == "class":
            self._create_class_controls_debug()
        elif action_type == "AI":
            self._create_ai_controls_debug()
        elif action_type == "image":
            self._create_image_controls_debug()
        elif action_type == "function":
            self._create_function_controls_debug()
            
        # 强制更新界面
        self.action_debug_detail.update_idletasks()
    
    # 调试动态控件创建方法（按类型顺序：mouse -> keyboard -> class -> AI -> image -> function）
    def _create_mouse_controls_debug(self):
        """创建调试鼠标控件"""
        debug_left_frame = ttk.Frame(self.action_debug_detail)
        debug_right_frame = ttk.Frame(self.action_debug_detail)
        debug_left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        debug_right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)

        # 左列控件
        # 鼠标动作
        ttk.Label(debug_left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_action_type_var = tk.StringVar(master=self.frame)
        debug_mouse_combo = ttk.Combobox(debug_left_frame, values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"], 
                                  textvariable=self.debug_mouse_action_type_var, state="readonly")
        debug_mouse_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(debug_left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_mouse_size_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_left_frame, textvariable=self.debug_action_mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(debug_right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(debug_right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(debug_right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(1, weight=1)
        debug_left_frame.grid_columnconfigure(1, weight=1)
        debug_right_frame.grid_columnconfigure(1, weight=1)
    
    def _create_keyboard_controls_debug(self):
        """创建调试键盘控件"""
        frame = ttk.Frame(self.action_debug_detail)
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 键盘类型
        ttk.Label(frame, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_type_var = tk.StringVar(master=self.frame)
        keyboard_combo = ttk.Combobox(frame, values=["按下", "释放", "单击", "文本"], 
                                     textvariable=self.debug_keyboard_type_var, state="readonly")
        keyboard_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 键值/文本
        ttk.Label(frame, text="键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_value_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        frame.grid_columnconfigure(1, weight=1)
        
    def _create_class_controls_debug(self):
        """创建调试类控件"""
        frame = ttk.Frame(self.action_debug_detail)
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 类名
        ttk.Label(frame, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_class_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗口标题
        ttk.Label(frame, text="窗口标题:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_window_title_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_window_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_class_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        frame.grid_columnconfigure(1, weight=1)
        
    def _create_ai_controls_debug(self):
        """创建调试AI控件"""
        frame = ttk.Frame(self.action_debug_detail)
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 训练库组
        ttk.Label(frame, text="训练库组:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_training_group_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_training_group_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(frame, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_record_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_record_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(frame, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_long_text_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_long_text_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # AI描述
        ttk.Label(frame, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_illustration_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 备注信息
        ttk.Label(frame, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_note_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(frame, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        frame.grid_columnconfigure(1, weight=1)
    
    def _create_image_controls_debug(self):
        """创建调试图像控件"""
        debug_left_frame = ttk.Frame(self.action_debug_detail)
        debug_right_frame = ttk.Frame(self.action_debug_detail)
        debug_left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        debug_right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)

        # 左列控件
        # 获取坐标按钮
        ttk.Button(debug_left_frame, text="获取左上角坐标", command=self._debug_get_left_top_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        ttk.Button(debug_left_frame, text="获取右下角坐标", command=self._debug_get_right_bottom_coordinates).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 左上角坐标
        ttk.Label(debug_left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_left_top_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_left_frame, textvariable=self.debug_image_left_top_x_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(debug_left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_left_top_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_left_frame, textvariable=self.debug_image_left_top_y_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # 右下角坐标
        ttk.Label(debug_left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_right_bottom_x_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_left_frame, textvariable=self.debug_image_right_bottom_x_var, width=10).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(debug_left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_right_bottom_y_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_left_frame, textvariable=self.debug_image_right_bottom_y_var, width=10).grid(row=4, column=1, padx=5, pady=5)
        
        # 右列控件
        # 图像名称
        ttk.Label(debug_right_frame, text="图像名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_names_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_image_names_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配条件
        ttk.Label(debug_right_frame, text="匹配条件:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_match_criteria_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_image_match_criteria_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(debug_right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_mouse_action_var = tk.StringVar(master=self.frame)
        mouse_action_combo = ttk.Combobox(debug_right_frame, 
                                        textvariable=self.debug_image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(debug_right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(debug_right_frame, textvariable=self.debug_image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(1, weight=1)
        
    def _create_function_controls_debug(self):
        """创建调试函数控件"""
        frame = ttk.Frame(self.action_debug_detail)
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 函数名称
        ttk.Label(frame, text="函数名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_function_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_function_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数
        ttk.Label(frame, text="参数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_function_parameters_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_function_parameters_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数列表
        ttk.Label(frame, text="参数列表:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_function_arguments_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_function_arguments_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(frame, text="时间差:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_function_time_diff_var = tk.StringVar(master=self.frame)
        ttk.Entry(frame, textvariable=self.debug_function_time_diff_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        frame.grid_columnconfigure(1, weight=1)
    
    def _debug_get_left_top_coordinates(self):
        """获取左上角坐标并更新调试输入框变量"""
        x, y = self.main_window.get_mouse_position()
        self.debug_image_left_top_x_var.set(str(x))
        self.debug_image_left_top_y_var.set(str(y))

    def _debug_get_right_bottom_coordinates(self):
        """获取右下角坐标并更新调试输入框变量"""
        x, y = self.main_window.get_mouse_position()
        self.debug_image_right_bottom_x_var.set(str(x))
        self.debug_image_right_bottom_y_var.set(str(y))
    
    # 调试行为列表相关方法
    def _on_debug_action_list_select(self, event):
        """调试行为列表选择事件处理"""
        selected = self.action_debug_list.selection()
        if not selected:
            return
        iid = selected[0]
        
        # 先全部禁用
        self._set_home_controls_state('disabled')
        
        # 只让部分控件可用
        for entry in [
            self.action_debug_name_entry, self.next_debug_id_entry, self.action_debug_type_combo,
            self.back_id_entry, self.action_debug_note_entry
        ]:
            entry.config(state='normal')
        
        try:
            config = ConfigManager()
            db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            if iid.startswith("group_"):
                # 选中的是ActionGroup
                group_id = int(iid.split("_")[1])
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                if group:
                    # 启用按钮
                    for btn in [
                        self.btn_create_debug_action, self.btn_modify_debug_action, self.btn_delete_debug_action,
                        self.btn_save_debug_action, self.btn_use_debug_suit
                    ]:
                        btn.config(state='normal')

                    # 填充详情区
                    self.action_debug_name_var.set(group.action_list_group_name or "")
                    self.next_debug_id_var.set(group.next_id or "")
                    self.action_debug_type_var.set(group.action_type or "")
                    self.back_id_var.set(group.next_id or "")
                    self.action_debug_note_var.set(group.action_list_group_note or "")
                    
                    # 填充action_debug_list
                    self.action_debug_list.delete(*self.action_debug_list.get_children())
                    actions = session.query(ActionList).filter_by(group_id=group_id).all()
                    for action in actions:
                        self.action_debug_list.insert("", "end", iid=str(action.id), values=(
                            action.action_type, action.action_name, action.next_id
                        ))
            else:
                # 选中的是ActionsGroupHierarchy
                selected_group_rank = iid_to_group_rank(iid)
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=selected_group_rank).first()
                if hierarchy:
                    self.action_debug_name_var.set(hierarchy.group_name or "")
                    self.next_debug_id_var.set("")
                    self.action_debug_type_var.set("")
                    self.back_id_var.set("")
                    self.action_debug_note_var.set(hierarchy.group_note or "")
                
                # 启用左侧按钮
                for btn in [
                    self.btn_create_debug_action, self.btn_modify_debug_action, self.btn_delete_debug_action,
                    self.btn_save_debug_action, self.btn_use_debug_suit
                ]:
                    btn.config(state='normal')
                
                # 禁用中间按钮
                for btn in [
                    self.btn_create_debug_action, self.btn_modify_debug_action, self.btn_delete_debug_action,
                    self.btn_save_debug_action, self.btn_use_debug_suit
                ]:
                    btn.config(state='disabled')
                
                # 清空action_debug_list
                self.action_debug_list.delete(*self.action_debug_list.get_children())
                
            session.close()
        except Exception as e:
            print(f"Error in _on_debug_action_list_select: {e}")
    
    # 调试操作方法
    def _create_debug_action(self):
        """创建调试行为"""
        messagebox.showinfo("提示", "创建调试行为功能待实现")
        
    def _modify_debug_action(self):
        """修改调试行为"""
        messagebox.showinfo("提示", "修改调试行为功能待实现")
        
    def _delete_debug_action(self):
        """删除调试行为"""
        selected = self.action_debug_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的调试行为")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的调试行为吗？"):
            messagebox.showinfo("提示", "删除调试行为功能待实现")
            
    def _save_debug_action(self):
        """保存调试行为"""
        messagebox.showinfo("提示", "保存调试行为功能待实现")
        
    def _use_debug_suit(self):
        """调用调试套餐"""
        messagebox.showinfo("提示", "调用调试套餐功能待实现")
    
    # =============================================================================
    # 辅助方法
    # =============================================================================
    
    def _fill_action_data(self, action):
        """根据action数据填充具体控件"""
        # 这里需要根据action.action_type的不同类型，填充对应的控件数据
        # 具体实现根据数据库字段结构而定
        pass
    def show_mode_picker(self, root):
        """显示模式选择器"""
        def confirm_module():
            self.relate_location_selected = local_mode_var.get()
            select_mode.destroy()
            return self.relate_location_selected
            
        select_mode = tk.Toplevel(root)
        select_mode.title("选择模式")
        select_mode.geometry("400x300")
        select_mode.resizable(False, False)

        select_mode.transient(root)
        select_mode.grab_set()
        select_mode.focus_set()

        local_mode_frame = ttk.Frame(select_mode)
        local_mode_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        local_mode_var = tk.IntVar()
        
        label_local = ttk.Label(local_mode_frame, text='选择插入位置:', font=("Arial", 12))
        label_local.pack(pady=10)
        
        # 根据当前选中的节点类型显示不同的选项
        selected = self.action_tree.selection()[0]
        if not selected:
            messagebox.showwarning("警告", "请选择节点")
            local_mode_var.set(5)
            select_mode.destroy()
            return
        elif selected.startswith("group_"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
        elif selected.startswith("A") and not selected.endswith("E"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text ='插入子项', variable=local_mode_var, value=3).pack(pady=5)
        else:
            messagebox.showwarning("警告", "节点的内容出现错误，请修复")
            local_mode_var.set(5)
            select_mode.destroy()
            return
            
        confirm_btn = ttk.Button(local_mode_frame, text="确定", command=confirm_module)
        confirm_btn.pack(pady=10)
        root.wait_window(select_mode)

    def _set_home_controls_state(self, state):
        """设置首页控件状态"""
        for ctrl in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            ctrl.config(state=state)
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
    def _set_action_group_entry_controls_state(self, state): 
        """设置行为组输入框控件状态"""
        for ctrl in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            ctrl.config(state=state) 
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
    def _set_action_group_button_controls_state(self, state):
        """设置行为组按钮控件状态"""
        for ctrl in [
            self.btn_new_action_group, self.btn_edit_action_group, self.btn_delete_action_group,
            self.btn_capture_image, self.btn_save_action_group, self.btn_refresh_action_group
        ]:
            ctrl.config(state=state)