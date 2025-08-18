import configparser
from operator import concat
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import traceback

# from config import config_manager  # 注释掉错误的导入
from gui.tabs.base_tab import BaseTab
from config.config_manager import ConfigManager
import globalvariable
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank
import os
import sys
import functools
import time

from models.user import User
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy, ListGroupHierarchy
from utils.hometab_funcdata import hometab_funcData
from utils.screenshot_tool import ScreenshotTool
from utils.home_tab_func import home_tab_action_group_func, ActionManager, ActionGroupManager

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def prevent_double_click(interval=1.0):
    """防误触装饰器，防止按钮被连续点击"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 获取当前时间
            current_time = time.time()
            
            # 检查是否是第一次调用或者已经过了间隔时间
            if not hasattr(self, '_last_click_time'):
                self._last_click_time = {}
            
            func_name = func.__name__
            if func_name not in self._last_click_time:
                self._last_click_time[func_name] = 0
            
            # 如果距离上次点击时间太短，则忽略
            if current_time - self._last_click_time[func_name] < interval:
                print(f"防误触：{func_name} 被忽略，距离上次点击时间过短")
                return
            
            # 更新最后点击时间
            self._last_click_time[func_name] = current_time
            
            # 按钮名称映射
            button_mapping = {
                '_create_action': 'btn_create_action',
                '_record_action': 'btn_record_action',
                '_modify_action': 'btn_modify_action',
                '_delete_action': 'btn_delete_action',
                '_save_action': 'btn_save_action',
                '_use_suit': 'btn_use_suit',
                '_new_action_group_group': 'btn_new_action_group',
                '_new_action_group': 'btn_new_action_group',
                '_edit_action_group': 'btn_edit_action_group',
                '_save_action_group': 'btn_save_action_group',
                '_capture_image': 'btn_capture_image',
                '_delete_action_group': 'btn_delete_action_group',
                '_run_action_group': 'btn_run_action_group',
                '_refresh_action_group': 'btn_refresh_action_group',
                '_add_excel_file': 'btn_add_excel_file',
                '_create_debug_action': 'btn_create_debug_action',
                '_modify_debug_action': 'btn_modify_debug_action',
                '_delete_debug_action': 'btn_delete_debug_action',
                '_save_debug_action': 'btn_save_debug_action',
                '_use_debug_suit': 'btn_use_debug_suit',
                '_sort_action_group_up': None,  # 右键菜单，没有对应按钮
                '_sort_action_group_down': None,  # 右键菜单，没有对应按钮
            }
            
            # 尝试禁用对应的按钮（如果存在）
            try:
                button_attr = button_mapping.get(func_name)
                if button_attr and hasattr(self, button_attr):
                    button = getattr(self, button_attr)
                    if hasattr(button, 'config'):
                        original_state = button.cget('state')
                        button.config(state='disabled')
                        
                        # 执行原函数
                        result = func(self, *args, **kwargs)
                        
                        # 恢复按钮状态
                        button.config(state=original_state)
                        return result
            except Exception as e:
                print(f"按钮状态管理失败: {e}")
            
            # 如果按钮管理失败，直接执行原函数
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class HomeTab(BaseTab):
    def __init__(self, notebook, main_window):
        super().__init__(notebook, main_window, "首页")
        self.my_window = main_window.window
        
        # =============================================================================
        # UI状态变量 - 由UI层管理，反映用户界面当前状态
        # =============================================================================
        
        # 行为组树形视图选中项的iid,格式如：A1B2C3D4
        self.action_group_hierarchy_tree_iid = None
        # show_model_pick中选择的相对位置
        self.relate_location_selected = None
        # show_model_pick中选择与action_list相关的相对位置
        self.relate_location_selected_action_list = None
        # 行为组树形视图选中项的rank 格式如：A1B2C3D4
        self.action_group_selected_rank = None
        # 行为组树形视图选中项的rank中的sort_num的值
        self.hierarchy_sort = None
        # 行为组类型，1:表示新增保存；2.表示修改保存；3.表示删除action_group；4.表示删除action_group_hierarchy；
        self.action_group_action_type = None
        # 选中行为组ID
        self.action_group_id = None
        # 选中行为组层次ID
        self.action_group_hierarchy_id = None
        # 行为组树形视图选中项的rank中的A的值
        self.action_group_selected_Arank = None
        
        # 行为元操作相关全局变量
        # 行为元操作类型，1:表示新增保存；2:表示修改保存；3:表示删除
        self.action_operation_type = None
        #当前选中的行为元列表层级的id
        self.current_action_list_hierarchy_id = None
        # 当前选中的行为元ID
        self.current_action_id = None
        # 选中行为元list的Rank
        self.current_action_list_selected_rank = None
        # =============================================================================
        # 业务逻辑管理器 - 处理具体的业务操作
        # =============================================================================
        
        # 创建行为元管理器
        self.action_manager = ActionManager(self)
        
        # 创建行为组管理器
        self.action_group_manager = ActionGroupManager(self)

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
        
        # 创建右键菜单
        self.tree_context_menu = tk.Menu(self.action_tree, tearoff=0)
        self.tree_context_menu.add_command(label="新建组", command=self._new_action_group_group)
        self.tree_context_menu.add_command(label="排序↑", command=self._sort_action_group_up)
        self.tree_context_menu.add_command(label="排序↓", command=self._sort_action_group_down)
        self.tree_context_menu.add_command(label="删除", command=self._delete_action_group)
        
        # 绑定右键菜单
        self.action_tree.bind("<Button-3>", self._show_tree_context_menu)
        
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

    def _show_tree_context_menu(self, event):
        """显示树形视图的右键菜单"""
        # 获取点击位置的项
        item = self.action_tree.identify_row(event.y)
        if item:
            # 选中该项
            self.action_tree.selection_set(item)
            # 显示菜单
            self.tree_context_menu.post(event.x_root, event.y_root)

    @prevent_double_click(interval=0.5)
    def _sort_action_group_up(self):
        """将选中的行为组向上移动"""
        selected = self.action_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        parent = self.action_tree.parent(item)
        if not parent:  # 如果是根节点，不处理
            return
            
        # 获取同级所有项
        siblings = self.action_tree.get_children(parent)
        current_index = siblings.index(item)
        
        if current_index > 0:  # 如果不是第一个
            # 移动项
            self.action_tree.move(item, parent, current_index - 1)
            # 更新数据库
            from utils.hometab_funcdata import hometab_funcData
            hometab_funcData._sort_action_group_up_data(sheet_type="Action",iid=self.action_tree_selected_iid,hierarchy_id=self.action_group_hierarchy_id,group_id=self.action_group_id,sort_num=self.hierarchy_sort)
            
    @prevent_double_click(interval=0.5)
    def _sort_action_group_down(self):
        """将选中的行为组向下移动"""
        selected = self.action_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        parent = self.action_tree.parent(item)
        if not parent:  # 如果是根节点，不处理
            return
            
        # 获取同级所有项
        siblings = self.action_tree.get_children(parent)
        current_index = siblings.index(item)
        
        if current_index < len(siblings) - 1:  # 如果不是最后一个
            # 移动项
            self.action_tree.move(item, parent, current_index + 1)
            messagebox.showinfo("提示", "数据库功能待实现")
    
    def _create_action_group_buttons(self, parent):
        """创建行为组相关按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)
        
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
                                            values=["list_hierarchy","mouse", "keyboard", "class", "AI", "image", "function","group"],
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
        
        # 强制设置最小高度为250px
        self.action_list_frame.pack_propagate(False)
        self.action_list_frame.grid_propagate(False)  # 防止grid布局影响大小
        self.action_list_frame.configure(height=210)  # 设置固定尺寸
        
        # 配置网格权重
        self.action_list_frame.grid_rowconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        
        # 延迟初始化，确保默认值已设置
        self.frame.after_idle(self._on_action_type_changed)
        
        # 行为列表
        list_frame = ttk.LabelFrame(left1_panel, text="行为列表")
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.action_list = ttk.Treeview(list_frame, name='action_list_tree', 
                                       columns=("name","type", "note"),selectmode='browse',show="tree headings")
        #设置Treeview的id列为隐藏
        self.action_list.heading("#0", text="结构")
        self.action_list.column("#0", width=60)
        self.action_list.heading("name", text="名称")
        self.action_list.column("name", width=200)
        self.action_list.heading("type", text="类型")
        self.action_list.column("type", width=100)
        self.action_list.heading("note", text="备注")
        self.action_list.column("note", width=200)
        # 创建右键菜单
        self.action_list_context_menu = tk.Menu(self.action_list, tearoff=0)
        self.action_list_context_menu.add_command(label="新建", command=self._create_action)
        self.action_list_context_menu.add_command(label="新建组", command=self._create_action_list_group)
        self.action_list_context_menu.add_command(label="删除", command=self._delete_action)
        # 绑定右键菜单
        self.action_list.bind("<Button-3>", self._show_action_list_context_menu)
        # 滚动条
        action_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.action_list.yview)
        self.action_list.configure(yscrollcommand=action_scroll.set)
        # 绑定选择事件
        self.action_list.bind('<<TreeviewSelect>>', self._on_action_list_select)
        # 布局
        self.action_list.grid(row=0, column=0, sticky=tk.NSEW)
        action_scroll.grid(row=0, column=1, sticky=tk.NS)
        # 行为列表按钮
        action_button_frame = ttk.Frame(left1_panel)
        action_button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_create_action_list_group = ttk.Button(action_button_frame, text="新建组", command=self._create_action_list_group)
        self.btn_create_action_list_group.pack(side=tk.LEFT, padx=5)
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
    def _show_action_list_context_menu(self,event):
        """显示行为列表的右键菜单"""
        item = self.action_list.identify_row(event.y)
        if item:
            self.action_list.selection_set(item)
            self.action_list_context_menu.post(event.x_root, event.y_root)

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
                                                   values=["list_hierarchy","mouse", "keyboard", "class", "AI", "image", "function","group"],
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
        self.action_debug_list.bind('<<TreeviewSelect>>', self.action_manager._on_debug_action_list_select)
        
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
    @prevent_double_click(interval=1.0)
    def _add_excel_file(self):
        """添加Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path_var.set(file_path)
    def _on_action_tree_select(self, event=None):
        """行为组树选择事件处理"""
        selected = self.action_tree.selection()
        if not selected:
            return
        iid = selected[0]
        self.action_tree_selected_iid = iid
        self.action_group_hierarchy_tree_iid = iid
        if iid in("A0","A1","A2"):
            self._set_action_group_entry_controls_state('disabled')
            self._set_action_group_button_controls_state('disabled') 
            self.btn_new_action_group.config(state='normal')
            self.btn_run_action_group.config(state='disabled')
        # 先全部禁用
        self._set_home_controls_state('disabled')
        
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
        
        try:
            # 如果treeview中的value的值中group_type的值为group，则表示选中的是组
            if self.action_list.item(iid, "values")[1] == "action_group":
                # 选中的是ActionGroup
                self.action_group_id = self.action_list.item(iid,"values")[2]
                
                # 使用ActionGroupManager获取数据
                data = self.action_group_manager.get_action_group_data("ActionGroup",self.action_group_id )
                if data:
                    group = data['group']
                    user = data['user']
                    actions = data['actions']
                    hierarchy = data['hierarchy']
                    
                    self.action_group_hierarchy_id = group.group_rank_id
                    
                    # 填充详情区
                    self.group_name_var.set(self.action_list.item(iid, "values")[0] or "")
                    self.group_last_circle_local_var.set(group.last_circle_local or "")
                    self.group_last_circle_node_var.set(group.last_circle_node or "")
                    self.group_setup_time_var.set(str(group.created_at or ""))
                    self.group_update_time_var.set(str(group.updated_at or ""))
                    self.group_user_id_var.set(str(group.user_id or ""))
                    self.group_user_name_var.set(user.username if user else "")
                    self.department_id_var.set(str(group.department_id or ""))
                    self.is_auto_var.set(bool(group.is_auto or False))
                    self.auto_time_var.set(str(group.auto_time or ""))
                    self.group_desc_var.set(group.action_list_group_note or "")
                    
                    # 填充action_list_tree
                    self.action_list.delete(*self.action_list.get_children())
                    # 先把list_hierarchy填充到action_list_tree
                    # 调用hometab_funcData._load_action_group_data方法，填充action_list_tree
                    hometab_funcData._load_action_group_data('Action',self.action_list)
                    
                    self.hierarchy_sort = group.sort_num if group else None
                    selected_group_rank = hierarchy.group_rank if hierarchy else None
                    
                    # 启用中间面板按钮 - 使用ActionManager的方法
                    self.action_manager._set_action_button_state('normal')
            else:
                # 选中的是ActionsGroupHierarchy
                selected_group_rank = iid_to_group_rank(iid)
                
                # 使用ActionGroupManager获取层级数据
                hierarchy = self.action_group_manager.get_hierarchy_data(selected_group_rank)
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
                    self.btn_create_action_list_group,self.btn_create_action, self.btn_record_action, self.btn_modify_action,self.btn_create_action_list_group,
                    self.btn_delete_action, self.btn_save_action, self.btn_use_suit,self.btn_add_excel_file
                ]:
                    btn.config(state='disabled')
                
                # 清空action_list_tree
                self.action_list.delete(*self.action_list.get_children())
            
            self.action_group_selected_rank = selected_group_rank
            
        except Exception as e:
            print(f"Error in _on_action_tree_select: {e}")
            print(traceback.format_exc())
        
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
    @prevent_double_click(interval=1.0)
    def _refresh_action_group(self):
        """刷新行为组树，按GroupRank分层显示"""
        hometab_funcData._load_action_group_data('Action',self.action_tree)
        return
    @prevent_double_click(interval=1.0)
    def _new_action_group_group(self):
        """新建行为组组"""
        #先判断是否有Hierarchy tree是否有被选中的项目
        selected_iid = self.action_tree.selection()[0]
        if selected_iid == None: 
            messagebox.showinfo("提示", "请先选择行为组")
            return
        
        #调用show_mode_picker方法,获取用户的新建意图
        self.show_mode_picker(self.my_window,"action_tree")
        if self.relate_location_selected == None:
            return
        from utils.actionGroupHierarchyManager import ActionGroupHierarchy_Manager
        #调用ActionGroupHierarchy_Manager方法，新建行为组组套
        ActionGroupHierarchy_Manager(self.my_window, "ActionsGroupHierarchy", self.action_group_selected_rank, self.relate_location_selected, self.hierarchy_sort,is_action_list=True)

        #刷新行为组树
        self._refresh_action_group()
        
    # 行为组操作方法
    @prevent_double_click(interval=1.0)
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
        self.btn_add_excel_file.config(state='normal')
        self.btn_new_action_group.config(state='disabled')
        self.btn_edit_action_group.config(state='disabled')
        self.btn_delete_action_group.config(state='normal')
        self.btn_capture_image.config(state='normal')
        self.btn_save_action_group.config(state='normal')
        self.btn_refresh_action_group.config(state='normal')
        self.action_group_action_type = 1
    @prevent_double_click(interval=1.0)
    def _edit_action_group(self):
        #先判断Hierarchy tree是否有被选中的项目
        selected_iid = self.action_tree.selection()[0]
        if self.action_group_hierarchy_tree_iid == None: 
            messagebox.showinfo("提示", "请先选择行为组")
            return

        #修改行为组相关按钮
        self.btn_add_excel_file.config(state='normal')
        self.btn_new_action_group.config(state='disabled')
        self.btn_edit_action_group.config(state='disabled')
        self.btn_delete_action_group.config(state='normal')
        self.btn_capture_image.config(state='normal')
        self.btn_save_action_group.config(state='normal')
        self.btn_refresh_action_group.config(state='normal')
        if selected_iid.startswith("group_"):
            self.action_group_action_type = 2
        elif selected_iid.startswith("A"):
            self.action_group_action_type = 3
        else:
            self.action_group_action_type = None

    @prevent_double_click(interval=1.0)
    def _save_action_group(self):
        """保存行为组"""
        try:
            if not self.action_group_action_type :
                messagebox.showwarning("警告", "请先选择行为组类型")
                return
            # 验证必填字段
            if not self.group_name_var.get().strip():
                messagebox.showwarning("警告", "请输入行为组名称")
                return
                
            # 验证自动执行时间
            if self.is_auto_var.get() and not self.auto_time_var.get().strip():
                messagebox.showwarning("警告", "启用自动执行时，必须设置执行时间")
                return
            if self.action_group_action_type == 3 and self.action_group_hierarchy_tree_iid.startswith("A"):
                # 开始保存行为组层级信息
                if not hometab_funcData._save_action_group_hierarchy_data('Action',self.action_group_hierarchy_id,self.group_name_var.get(),self.group_desc_var.get(),self.is_auto_var.get(),self.auto_time_var.get()) :
                    return False
                messagebox.showinfo("成功", "保存行为组层级信息成功")
                return True
            else:
                # 创建home_tab_action_group_func实例
                home_tab_action_group_func_model = home_tab_action_group_func(
                    group_name=self.group_name_var.get().strip(), 
                    group_desc=self.group_desc_var.get().strip(),
                    group_user_id=globalvariable.USER_ID,
                    group_department_id=globalvariable.USER_DEPARTMENT_ID,
                    is_auto=self.is_auto_var.get(),
                    auto_time=self.auto_time_var.get(),
                    action_group_selected_rank=self.action_group_selected_rank,
                    action_tree_selected_iid=self.action_tree_selected_iid,
                    action_group_type=self.action_group_action_type,
                    sort_num=self.hierarchy_sort,
                    action_group_id=self.action_group_id,
                    action_group_hierarchy_id=self.action_group_hierarchy_id
                )
                
                # 保存行为组
                if home_tab_action_group_func_model._save_action_group():
                    messagebox.showinfo("成功", "保存行为组成功")
                    # 刷新行为组列表
                    self._refresh_action_group()
                    # 重置界面状态
                    self._reset_action_group_interface()
                else:
                    messagebox.showerror("错误", "保存行为组失败")
                
        except ValueError as e:
            print(traceback.format_exc())
            messagebox.showerror("验证错误", str(e))
        except Exception as e:
            print(traceback.format_exc())
            messagebox.showerror("错误", f"保存行为组时发生异常: {str(e)}")
        finally:
            # 确保关闭数据库会话
            if 'home_tab_action_group_func_model' in locals():
                home_tab_action_group_func_model._session_close()
    
    def _reset_action_group_interface(self):
        """重置行为组界面状态"""
        # 禁用所有相关控件
        for widget in (self.btn_new_action_group, self.btn_edit_action_group, 
                      self.btn_delete_action_group, self.btn_capture_image, 
                      self.btn_save_action_group, self.group_name_entry, 
                      self.group_desc_entry, self.auto_time_entry, self.is_auto_check):
            widget.config(state='disabled')
        
        # 清空表单
        self.group_name_var.set("")
        self.group_desc_var.set("")
        self.auto_time_var.set("")
        self.is_auto_var.set(False)
        
        # 重置操作类型
        self.action_group_action_type = None
    @prevent_double_click(interval=1.0)
    def _capture_image(self):
        """图像采集"""
        # 检查是否有选中的行为组
        if not self.action_group_id:
            messagebox.showwarning("警告", "请先选择行为组")
            return
            
        try:
            # 使用改进后的独立函数
            from utils.home_tab_func import _home_capture_image
            if not _home_capture_image(self.action_group_id,self.my_window):
                messagebox.showerror("错误", "图像采集失败")
        except Exception as e:
            print(traceback.format_exc())
    
    @prevent_double_click(interval=1.0)
    def _delete_action_group(self):
        """删除行为组"""
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为组")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的行为组吗？\n此操作将同时删除该行为组下的所有行为元，且不可恢复。"):
            try:
                # 创建home_tab_action_group_func实例
                home_tab_action_group_func_model = home_tab_action_group_func(
                    self.group_name_var.get().strip(), 
                    self.group_desc_var.get().strip(),
                    globalvariable.USER_ID,
                    globalvariable.USER_DEPARTMENT_ID,
                    self.is_auto_var.get(),
                    self.auto_time_var.get(),
                    self.action_group_selected_rank,
                    self.action_tree_selected_iid,
                    3,  # 删除操作类型
                    self.hierarchy_sort,
                    self.action_group_id,
                    self.action_group_hierarchy_id
                )
                
                # 删除行为组
                if home_tab_action_group_func_model._delete_action_group(self.action_tree_selected_iid,self.action_group_id,self.action_group_hierarchy_id):
                    messagebox.showinfo("成功", "删除行为组成功")
                    # 刷新行为组列表
                    self._refresh_action_group()
                    # 清空当前选中的行为组信息
                    self._clear_action_group_info()
                else:
                    print(traceback.format_exc())
                    messagebox.showerror("错误", "删除行为组失败")
                    
            except ValueError as e:
                messagebox.showerror("验证错误", str(e))
            except Exception as e:
                print(traceback.format_exc())
                messagebox.showerror("错误", f"删除行为组时发生异常: {str(e)}")
            finally:
                # 确保关闭数据库会话
                if 'home_tab_action_group_func_model' in locals():
                    home_tab_action_group_func_model._session_close()
    
    def _clear_action_group_info(self):
        """清空行为组信息"""
        # 清空表单
        self.group_name_var.set("")
        self.group_desc_var.set("")
        self.auto_time_var.set("")
        self.is_auto_var.set(False)
        self.group_last_circle_local_var.set("")
        self.group_last_circle_node_var.set("")
        self.group_setup_time_var.set("")
        self.group_update_time_var.set("")
        self.group_user_id_var.set("")
        self.group_user_name_var.set("")
        self.department_id_var.set("")
        
        # 重置相关变量
        self.action_group_hierarchy_tree_iid = None
        self.action_group_selected_rank = None
        self.hierarchy_sort = None
        self.action_group_action_type = None
        self.action_group_id = None
        self.action_group_hierarchy_id = None
        
        # 清空行为列表
        self.action_list.delete(*self.action_list.get_children())
        
        # 禁用相关控件
        self._set_action_group_entry_controls_state('disabled')
        self._set_action_group_button_controls_state('disabled')
    @prevent_double_click(interval=1.0)
    def _run_action_group(self):
        """运行行为组"""
        action_group_manager = ActionGroupManager(self)
        if action_group_manager.run_action_group(self.action_group_id):
            messagebox.showinfo("提示", "行为组运行成功")
        else:
            messagebox.showerror("错误", "行为组运行失败")
    
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
        
        if action_type == "list_hierarchy":
            self._create_list_hierarchy_controls()
        elif action_type == "mouse":
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
        elif action_type == "group":
            self._create_group_controls()
        # 强制更新界面
        self.action_list_frame.update_idletasks()
    
    # 动态控件创建方法（按类型顺序：list_hierarchy -> mouse -> keyboard -> class -> AI -> image -> function）
    def _create_list_hierarchy_controls(self):
        """创建列表层级控件"""
        # 列表层级名称
        ttk.Label(self.action_list_frame, text="层级名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_list_hierarchy_name_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_list_hierarchy_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(self.action_list_frame, text="备注:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_list_hierarchy_note_var = tk.StringVar(master=self.frame)
        ttk.Entry(self.action_list_frame, textvariable=self.action_list_hierarchy_note_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
    def _create_group_controls(self):
        """创建组控件"""
        ttk.Label(self.action_list_frame, text="欢迎来到AI世界").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
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
        self.action_group_ai_training_group = self._get_ai_training_group()
        # 训练库名称
        ttk.Label(self.action_list_frame, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_ai_training_group_var = tk.StringVar(master=self.frame)
        self.action_ai_training_group_comb = ttk.Combobox(self.action_list_frame, textvariable=self.action_ai_training_group_var, values=self.action_group_ai_training_group, state="readonly")
        self.action_ai_training_group_comb.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
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
        self.action_ai_training_group_comb.bind('<<ComboboxSelected>>', self._on_ai_training_group_changed)

        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)
    def _get_ai_training_group(self):
        """获取AI训练组字典"""
        try:
            # 模拟几组数据
            return ["AI病历审查", "AI病史汇报", "AI诊疗审查"]
        except Exception as e:
            print(f"获取AI训练组失败: {e}")
            return []
    def _on_ai_training_group_changed(self, event=None):
        # 模拟几组数据到相应的控件中
        if self.action_ai_training_group_var.get() == "AI病历审查":
            self.action_ai_record_name_var.set("病历审查")
            self.action_ai_long_text_name_var.set("病历审查长文本.txt")
            self.action_ai_illustration_var.set("")
            self.action_ai_note_var.set("病历审查备注信息")
            self.action_ai_time_diff_var.set("病历审查时间差")
        elif self.action_ai_training_group_var.get() == "AI病史汇报":
            self.action_ai_record_name_var.set("病史汇报")
            self.action_ai_long_text_name_var.set("病史汇报长文本.txt")
            self.action_ai_illustration_var.set("")
            self.action_ai_note_var.set("病史汇报备注信息")
            self.action_ai_time_diff_var.set("病史汇报时间差")  
        elif self.action_ai_training_group_var.get() == "AI诊疗审查":
            self.action_ai_record_name_var.set("诊疗审查")
            self.action_ai_long_text_name_var.set("诊疗审查长文本.txt")
            self.action_ai_illustration_var.set("")
            self.action_ai_note_var.set("诊疗审查备注信息")
            self.action_ai_time_diff_var.set("诊疗审查时间差")
        
    def _create_image_controls(self):
        """创建图像控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_list_frame)
        right_frame = ttk.Frame(self.action_list_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        self.action_group_image_match_group = self._get_image_match_group()

        # 左列控件
        # 获取左上角坐标
        ttk.Button(left_frame, text="获取区域坐标", command=self._get_region_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
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
        ttk.Combobox(right_frame, textvariable=self.action_image_names_var, values=self.action_group_image_match_group, state="readonly").grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
    

        # 匹配条件
        ttk.Label(right_frame, text="匹配条件:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_image_match_criteria_var = tk.StringVar(master=self.frame)
        ttk.Entry(right_frame, textvariable=self.action_image_match_criteria_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.action_image_match_group_dic = {}
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
    def _get_image_match_group(self):
        """获取图像匹配组字典"""
        try:
            # 先获取到当前的action_group_id对应的文件夹，然后从文件夹中获取到所有文件，然后获取到文件的名称，然后获取到文件的名称的
            # 文件夹路径为：从HISAutoConfiguration.cfg中获取到sysfolder路径，然后拼接上/action_group/,然后拼接上action_group_id，然后拼接上/Picture/
            # 使用ConfigManager中的get_value方法获取到sysfolder路径
            config = ConfigManager()
            sysfolder = config.get_value("System", "sysfolder")
            if not self.action_group_id:
                return []
            
            picture_folder = os.path.join(sysfolder, "ActionsGroup", str(self.action_group_id), "Picture")
            
            # 检查文件夹是否存在
            if not os.path.exists(picture_folder):
                return []
            
            # 获取到picture_folder中的所有文件，然后获取到文件的名称，然后获取到文件的名称的
            image_files = []
            for file in os.listdir(picture_folder):
                if file.endswith((".png", ".jpg", ".jpeg")):
                    image_files.append(file)
            return image_files
        except Exception as e:
            print(f"获取图像匹配组失败: {e}")
            return []

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

    @prevent_double_click(interval=1.0)
    def _get_region_coordinates(self):
        """获取区域坐标"""
        try:
            # 调用独立的区域坐标获取模块
            from utils.region_coordinates import get_region_coordinates
            
            success = get_region_coordinates(
                self.my_window,
                self.action_image_left_top_x_var,
                self.action_image_left_top_y_var,
                self.action_image_right_bottom_x_var,
                self.action_image_right_bottom_y_var
            )
            
            if success:
                print("区域坐标获取成功")
            else:
                print("区域坐标获取失败")
                
        except Exception as e:
            print(f"获取区域坐标时发生异常: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"获取区域坐标失败: {str(e)}")
    
    # 行为列表相关方法
    @prevent_double_click(interval=1.0)
    def _on_action_list_select(self, event):
        """行为列表选择事件处理"""
        selected = self.action_list.selection()
        if not selected:
            # 清空表单
            self._clear_action_form()
            # 更新按钮状态
            self._update_action_buttons_state()
            return
            
        # 获取选中项的数据
        item = selected[0]
        selected_iid = selected[0]
        values = self.action_list.item(item)['values']
        action_name = values[0]  # 名称在values[2]
        action_type = values[1]  # 类型在values[1]
        action_note = values[2]  # 下一步在values[3]
        if action_type == "list_hierarchy":
            self.current_action_list_hierarchy_id = selected_iid.split("_")[1]
            self.current_action_id = None
        else:
            action_id = selected_iid.split("_")[1]
            self.current_action_id = action_id
            parent_selected_iid = self.action_list.parent(item)
            if parent_selected_iid:
                if parent_selected_iid.startswith("hierarchy_"):
                    self.current_action_list_hierarchy_id = parent_selected_iid.split("_")[1]
                    self.current_action_list_hierarchy_rank = self.action_manager._get_action_list_rank(self.current_action_list_hierarchy_id)
                else:
                    self.current_action_list_hierarchy_id = None
            else:
                self.current_action_list_hierarchy_id = None
        # 清空动态区域
        for widget in self.action_list_frame.winfo_children():
            widget.destroy()
            
        # 根据类型创建对应的控件
        if action_type == "list_hierarchy":
            self._create_list_hierarchy_controls()
        elif action_type == "mouse":
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
            
        # 在正常状态下禁用控件
        if not self.action_operation_type:
            for entry in [
                self.action_name_entry, self.next_action_entry, self.action_type_combo,
                self.debug_group_id_entry, self.action_note_entry
            ]:
                entry.config(state='disabled')
            
        # 填充基本信息
        self.action_name_var.set(action_name)
        self.action_type_var.set(action_type)
        
        # 填充详细数据 - 使用ActionManager的方法(因控件填充问题，action_list特有的方法)
        self.action_manager._fill_action_data(action_type, self.current_action_id,self.current_action_list_hierarchy_id)
        
        # 更新按钮状态
        self._update_action_buttons_state()
    def _create_action_list_group(self):
        """创建行为列表组"""
        #先判断是否有Hierarchy tree是否有被选中的项目
        if self.current_action_list_hierarchy_id == None and self.current_action_id == None:
            self.relate_location_selected_action_list = 4
        else:
            #调用show_mode_picker方法,获取用户的新建意图
            self.show_mode_picker(self.my_window,"action_list",is_action_list=True)
            if self.relate_location_selected_action_list == None:
                return
        from utils.actionGroupHierarchyManager import ActionGroupHierarchy_Manager
        #调用ActionGroupHierarchy_Manager方法，新建行为组组套
        ActionGroupHierarchy_Manager(self.my_window, "ActionList",
                                      self.current_action_list_selected_rank, self.relate_location_selected_action_list,
                                      self.hierarchy_sort,is_action_list=True,action_group_id=self.action_group_id)

        #刷新行为组树
        self._refresh_action_list()
    # 行为操作方法  
    @prevent_double_click(interval=1.0)
    def _create_action(self):
        """创建行为元"""
        try:
            if self.action_manager.create_action():
                # 启用相关控件 - 使用ActionManager的方法
                self.action_manager._set_action_controls_state('normal')
                # 修改按钮状态 - 使用ActionManager的方法
                self.action_manager._set_action_button_state()
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("错误", f"创建行为元时发生异常: {str(e)}")
            return False
    def _clear_action_form(self):
        """清空行为表单"""
        # 清空基本信息
        self.action_name_var.set("")
        self.next_action_var.set("")
        self.action_type_var.set("")
        self.debug_group_id.set("")
        self.action_note_var.set("")
        
        # 清空动态详情区域 - 使用ActionManager的方法
        self.action_manager._clear_action_detail_controls()
        
        # 修改按钮状态 - 使用ActionManager的方法
        self.action_manager._set_action_button_state()
        
        # 触发行为类型变更事件以显示默认控件
        self._on_action_type_changed()
    
    @prevent_double_click(interval=1.0)
    def _record_action(self):
        """录制行为"""
        try:
            if self.current_action_list_hierarchy_id == None:
                messagebox.showerror("错误", "请先选择要录制行为的行为列表")
                return
            # 调用修复后的录制模块中的录制功能
            from utils.action_recorder_fixed import record_action
            if record_action(self):
                print("录制功能已启动")
            else:
                print("录制功能启动失败")
        except Exception as e:
            print("错误", f"录制行为时发生异常: {str(e)}")
            print(traceback.format_exc())
    
    @prevent_double_click(interval=1.0)
    def _modify_action(self):
        """修改行为元"""
        try:
            if self.action_manager.modify_action():
                # 启用相关控件 - 使用ActionManager的方法
                self.action_manager._set_action_controls_state('normal')
                # 修改按钮状态 - 使用ActionManager的方法
                self.action_manager._set_action_button_state()
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("错误", f"修改行为元时发生异常: {str(e)}")
            return False
    
    @prevent_double_click(interval=1.0)
    def _delete_action(self):
        """删除行为元"""
        try:
            if self.action_manager.delete_action(self.action_type_var.get(),self.current_action_id,self.current_action_list_hierarchy_id):
                # 刷新行为列表
                self._refresh_action_list()
                # 更新按钮状态
                self._update_action_buttons_state()
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("错误", f"删除行为元时发生异常: {str(e)}")
            return False
    
    @prevent_double_click(interval=1.0)
    def _save_action(self):
        """保存行为元"""
        try:
            # 使用ActionManager的验证方法
            validation_errors = self.action_manager.validate_action_data()
            if validation_errors:
                error_message = "请修正以下错误：\n" + "\n".join(validation_errors)
                messagebox.showwarning("验证错误", error_message)
            
            if self.action_manager.save_action():
                # 刷新行为列表
                self._refresh_action_list()
                # 更新按钮状态
                self._update_action_buttons_state()
                #弹窗提示任务完成
                messagebox.showinfo("提示", "行为元保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存行为元时发生异常: {str(e)}")
            print(traceback.format_exc())
            return False
    
    @prevent_double_click(interval=1.0)
    def _use_suit(self):
        """调用套餐"""
        # 开始调用套餐，创建套餐窗口（suit_view.py)
        from gui.suit_view import SuitView
        # 创建套餐窗口，采用对话框模式
        suit_view = SuitView(self.main_window.window,self.action_group_id,self.current_action_id)
        # 等待窗口关闭
        self.main_window.window.wait_window(suit_view)
    
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
        elif action_type == "group":
            self._create_group_controls_debug()
            
        # 强制更新界面
        self.action_debug_detail.update_idletasks()
    def _create_group_controls_debug(self):
        """创建调试组控件"""
        ttk.Label(self.action_debug_detail, text="欢迎来到组控件调试世界").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
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
        try:
            # 调用独立的区域坐标获取模块
            from utils.region_coordinates import get_debug_region_coordinates
            
            success = get_debug_region_coordinates(
                self.my_window,
                self.debug_image_left_top_x_var,
                self.debug_image_left_top_y_var,
                self.debug_image_right_bottom_x_var,
                self.debug_image_right_bottom_y_var
            )
            
            if success:
                print("调试区域坐标获取成功")
            else:
                print("调试区域坐标获取失败")
                
        except Exception as e:
            print(f"获取调试区域坐标时发生异常: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"获取调试区域坐标失败: {str(e)}")

    def _debug_get_right_bottom_coordinates(self):
        """获取右下角坐标并更新调试输入框变量"""
        try:
            # 调用独立的区域坐标获取模块
            from utils.region_coordinates import get_debug_region_coordinates
            
            success = get_debug_region_coordinates(
                self.my_window,
                self.debug_image_left_top_x_var,
                self.debug_image_left_top_y_var,
                self.debug_image_right_bottom_x_var,
                self.debug_image_right_bottom_y_var
            )
            
            if success:
                print("调试区域坐标获取成功")
            else:
                print("调试区域坐标获取失败")
                
        except Exception as e:
            print(f"获取调试区域坐标时发生异常: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"获取调试区域坐标失败: {str(e)}")
    
    # 调试操作方法
    @prevent_double_click(interval=1.0)
    def _create_debug_action(self):
        """创建调试行为"""
        messagebox.showinfo("提示", "创建调试行为功能待实现")
        
    @prevent_double_click(interval=1.0)
    def _modify_debug_action(self):
        """修改调试行为"""
        messagebox.showinfo("提示", "修改调试行为功能待实现")
        
    @prevent_double_click(interval=1.0)
    def _delete_debug_action(self):
        """删除调试行为"""
        selected = self.action_debug_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的调试行为")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的调试行为吗？"):
            messagebox.showinfo("提示", "删除调试行为功能待实现")
            
    @prevent_double_click(interval=1.0)
    def _save_debug_action(self):
        """保存调试行为"""
        messagebox.showinfo("提示", "保存调试行为功能待实现")
        
    @prevent_double_click(interval=1.0)
    def _use_debug_suit(self):
        """调用调试套餐"""
        messagebox.showinfo("提示", "调用调试套餐功能待实现")
    
    # =============================================================================
    # 辅助方法
    # =============================================================================
    

    def show_mode_picker(self, root,sheet_name,is_action_list=False):
        """显示模式选择器"""
        def confirm_module():
            if is_action_list:
                self.relate_location_selected_action_list = local_mode_var.get()
                select_mode.destroy()
                return
            else:
                self.relate_location_selected = local_mode_var.get()
                select_mode.destroy()
                return    
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
        if sheet_name == "action_list":
            selected = self.action_list.selection()[0]
        elif sheet_name == "action_tree":
            selected = self.action_tree.selection()[0]
        if not selected:
            # 这里解决的是当列表中没有记录的时候，新建第一个List_group
            if is_action_list:
                ttk.Radiobutton(local_mode_frame, text ='插入项', variable=local_mode_var, value=4).pack(pady=5)
            else:
                messagebox.showwarning("警告", "请选择节点")
                local_mode_var.set(5)
                select_mode.destroy()
                return
        elif selected.startswith("group_"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
        elif selected.startswith("A") or selected.startswith("hierarchy_"):
            ttk.Radiobutton(local_mode_frame, text="上方插入", variable=local_mode_var, value=1).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text='下方插入', variable=local_mode_var, value=2).pack(pady=5)
            ttk.Radiobutton(local_mode_frame, text ='插入子项', variable=local_mode_var, value=3).pack(pady=5)
        else:
            messagebox.showwarning("警告", "节点的内容出现错误，请修复")
            local_mode_var.set(5)
            select_mode.destroy()
            return
        self.relate_location_selected = None
        self.relate_location_selected_action_list = None
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
    
    # =============================================================================
    # 行为元操作辅助方法
    def _refresh_action_list(self):
        """刷新行为列表"""
        if not self.action_group_id:
            return
            
        try:
            # 使用ActionManager的方法刷新行为列表
            self.action_manager._refresh_action_list()
        except Exception as e:
            messagebox.showerror("错误", f"刷新行为列表失败: {str(e)}")

    def _update_action_buttons_state(self):
        """更新行为按钮状态"""
        # 根据是否有选中项来设置按钮状态
        selected = self.action_list.selection()
        has_selection = len(selected) > 0
        
        if has_selection and not self.action_operation_type:
            # 有选中项且不在编辑状态
            self.btn_modify_action.config(state='normal')
            self.btn_delete_action.config(state='normal')
        else:
            # 无选中项或在编辑状态
            self.btn_modify_action.config(state='disabled')
            self.btn_delete_action.config(state='disabled')
