import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
from tkinter import filedialog
from datetime import datetime
from config.config_manager import ConfigManager
from database import db_manager
from models.department import Department
from models.task import TaskList, TaskListFinished
from models.user import User
from models.actions import ActionGroup, ActionsGroupHierarchy
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from database.db_manager import DatabaseManager
import re
import globalvariable

class MainWindow:
    def show_time_picker(self,root,entry_widget):
        def confirm_time():
            selected_time = f"{hour.get()}:{minute.get()}"
            print("Selected Time:", selected_time)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_time)            
            time_picker.destroy()
            # 获取 Entry 控件在屏幕上的位置
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        time_picker = tk.Toplevel(root)
        time_picker.title("选择时间")
        time_picker.geometry(f"+{x}+{y}")
        time_picker.transient(root)
        time_picker.grab_set()
        time_picker.focus_set()
    
        # 小时选择
        hour_label = ttk.Label(time_picker, text="小时:")
        hour_label.grid(row=0, column=0, padx=5, pady=5)
        hour = ttk.Spinbox(time_picker, from_=0, to=23, width=3)
        hour.grid(row=0, column=1, padx=5, pady=5)
    
        # 分钟选择
        minute_label = ttk.Label(time_picker, text="分钟:")
        minute_label.grid(row=1, column=0, padx=5, pady=5)
        minute = ttk.Spinbox(time_picker, from_=0, to=59, width=3)
        minute.grid(row=1, column=1, padx=5, pady=5)
    
        # 确认按钮
        confirm_btn = ttk.Button(time_picker, text="确定", command=confirm_time)
        confirm_btn.grid(row=2, column=0, columnspan=2, pady=10)
    def show_mode_picker(self,root):
        def confirm_module():
            self.module_select_node=local_mode_var.get()
        select_mode =tk.Toplevel(root)
        select_mode.title="选择模式"
        select_mode.geometry(300*500)
        select_mode.grab_set()
        select_mode.focus_set()

        local_mode_frame = ttk.Frame(select_mode)
        local_mode_frame.pack(side=tk.LEFT,fill="x")
        local_mode_var =ttk.IntVar()
        
        label_local =ttk.Label(local_mode_frame,text='选择位置')
        label_local.pack(side="left",padx=5,pady=5)
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择节点")
            local_mode_var=5
            return
        elif selected[0].startswith("group_"):
            upper_node =ttk.Radiobutton(local_mode_frame,text="上方插入",variable=local_mode_var,value=1).pack(side=tk.LEFT,fill='y')
            lower_node =ttk.Radiobutton(local_mode_frame,text='下方插入',variable=local_mode_var,value=2).pack(side=tk.LEFT,fill='y',padx=5,pady=5)
        elif selected[0].startswith("A"):
            upper_node =ttk.Radiobutton(local_mode_frame,text="上方插入",variable=local_mode_var,value=1).pack(side=tk.LEFT,fill='y')
            lower_node =ttk.Radiobutton(local_mode_frame,text='下方插入',variable=local_mode_var,value=2).pack(side=tk.LEFT,fill='y',padx=5,pady=5)
            child_node = ttk.Radiobutton(local_mode_frame,text ='插入子项',variable=local_mode_var,value=3).pack(side=tk.LEFT,fill='y',padx=5,pady=5)
        else:
            messagebox.showwarning("警告", "节点的内容出现错误，请修复")
            local_mode_var=5
            return
        confirm_btn = ttk.Button(select_mode, text="确定", command=confirm_module)
        confirm_btn.grid(row=2, column=0, columnspan=2, pady=10)
    def __init__(self, username: str, is_super_admin: bool = False,engine=None):
        """
        初始化主窗口
        
        Args:
            username: 当前登录的用户名
            is_super_admin: 是否为超级管理员
        """
        self.window = tk.Tk()
        self.window.title(f"智能自动化办公系统 - {username}")
        self.window.state('zoomed')  # 最大化窗口
        #获取数据库会话
        self.session = None
        # 设置窗口图标
        # self.window.iconbitmap("path/to/icon.ico")  # TODO: 添加图标
        # 设置tree控件的选中的节点内容
        self.module_select_node =None
        self.actiongroup_hierarchy_tree_iid =None
        self.action_list_tree_iid =None
        self.action_debug_list_tree_iid=None
        self.username = username
        self.is_super_admin = is_super_admin
        
        self._create_widgets()
        
    def _create_widgets(self):
        """创建主界面的控件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Notebook控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个子界面
        self._create_home_tab()
        self._create_debug_tab()
        self._create_conduction_manager_tab()
        self._create_workspace_tab()
        self._create_aiset_tab()
        
        # 只有超级管理员才能看到任务控制界面
        if self.is_super_admin:
            self._create_task_control_tab()
            
        self._create_cloud_control_tab()
        self._create_setting_tab()
        
    def _create_home_tab(self):
        """创建首页标签页"""
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="首页")
        
        # 创建左侧面板
        left_panel = ttk.Frame(home_frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建Excel导入区域
        excel_frame = ttk.LabelFrame(left_panel, text="Excel导入")
        excel_frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # Excel路径
        ttk.Label(excel_frame, text="Excel路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.excel_path_var = tk.StringVar()
        ttk.Entry(excel_frame, textvariable=self.excel_path_var, width=50,state='').grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(excel_frame, text="添加", command=self._add_excel_file,state ="disable").grid(row=0, column=3, padx=5, pady=5)
        
        # Sheet编号和监测字段
        ttk.Label(excel_frame, text="Sheet编号:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sheet_num_var = tk.StringVar()
        self.sheet_num_entry = ttk.Entry(excel_frame, textvariable=self.sheet_num_var, width=10)
        self.sheet_num_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(excel_frame, text="监测字段:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.column_var = tk.StringVar()
        self.column_entry = ttk.Entry(excel_frame, textvariable=self.column_var, width=10)
        self.column_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 导入和保存按钮
        button_frame = ttk.Frame(excel_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        self.btn_import_excel=ttk.Button(button_frame, text="导入", command=self._import_excel,state="disabled")
        self.btn_import_excel.pack(side=tk.LEFT, padx=5)
        self.btn_save_excel_setting=ttk.Button(button_frame, text="保存", command=self._save_excel_settings,state="disabled")
        self.btn_save_excel_setting.pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重
        excel_frame.grid_columnconfigure(1, weight=1)
        
        # 创建行为组详情区域
        action_group_frame = ttk.LabelFrame(left_panel, text="行为组详情")
        action_group_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建基本信息区域（第一行）
        basic_info_frame = ttk.Frame(action_group_frame)
        basic_info_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 行为组名称
        ttk.Label(basic_info_frame, text="名称:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_name_var = tk.StringVar()
        self.group_name_var.set('ceshi1')
        self.group_name_entry = ttk.Entry(basic_info_frame, textvariable=self.group_name_var, width=20, state="normal")
        self.group_name_var.set('ceshi2')
        # 添加诊断信息
        print("诊断信息:")
        print(f"1. StringVar 值: {self.group_name_var.get()}")
        print(f"2. Entry 控件值: {self.group_name_entry.get()}")
        print(f"3. Entry 状态: {self.group_name_entry.cget('state')}")
        print(f"4. StringVar ID: {id(self.group_name_var)}")
        print(f"5. Entry 的 textvariable ID: {id(self.group_name_entry.cget('textvariable'))}")

        # 强制刷新
        self.window.update()
        self.window.update_idletasks()

        print("刷新后 Entry 值:", self.group_name_entry.get())
        self.group_name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 上一次循环位置
        ttk.Label(basic_info_frame, text="上一次循环位置:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_last_circle_local_var = tk.StringVar()
        self.group_last_circle_local_entry = ttk.Entry(basic_info_frame, textvariable=self.group_last_circle_local_var, width=20, state="disabled")
        self.group_last_circle_local_entry.pack(side=tk.LEFT)

        # 创建时间信息区域（第二行）
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

        # 创建用户信息区域（第三行）
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

        # 创建部门信息区域（第四行）
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

        # 创建自动执行区域（第五行）
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
        self.auto_time_entry.pack(side=tk.LEFT)
        self.auto_time_entry.bind("<Button-1>", lambda e: self.show_time_picker(self.window, self.auto_time_entry))

        # 创建描述区域（第六行）
        desc_frame = ttk.Frame(action_group_frame)
        desc_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 行为组备注
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_desc_var = tk.StringVar()
        self.group_desc_entry = ttk.Entry(desc_frame, textvariable=self.group_desc_var, width=50, state="disabled")
        self.group_desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 配置grid权重
        action_group_frame.grid_columnconfigure(0, weight=1)
        action_group_frame.grid_columnconfigure(1, weight=1)

        # 创建树形视图区域
        tree_frame = ttk.LabelFrame(left_panel, text="行为组")
        tree_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建树形视图和滚动条
        self.action_tree = ttk.Treeview(tree_frame,name='actiongroup_hierarchy_tree', columns=("name","userid",),selectmode='browse',show="tree headings")
        self.action_tree.heading("#0", text="结构")
        self.action_tree.column("#0", width=60)
        self.action_tree.heading("name", text="名称")
        self.action_tree.column("name", width=150)
        self.action_tree.heading("userid", text="创建者")
        self.action_tree.column("userid", width=50)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=tree_scroll.set)
        self.action_tree.bind('<<TreeviewSelect>>',self._on_action_tree_select)
        # 布局
        self.action_tree.grid(row=0, column=0, sticky=tk.NSEW)
        tree_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建行为组按钮
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_new_action_group=ttk.Button(button_frame, text="新建", command=self._new_action_group, state="disabled")
        self.btn_new_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_edit_action_group=ttk.Button(button_frame, text="编辑", command=self._edit_action_group,state="disabled")
        self.btn_edit_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_capture_image=ttk.Button(button_frame, text="图像采集", command=self._capture_image,state="disabled")
        self.btn_capture_image.pack(side=tk.LEFT, padx=5)
        self.btn_refresh_action_group=ttk.Button(button_frame, text="刷新", command=self._refresh_action_group,state="disabled")
        self.btn_refresh_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_delete_action_group=ttk.Button(button_frame, text="删除", command=self._delete_action_group,state="disabled")
        self.btn_delete_action_group.pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重，使树形视图可以随窗口调整大小
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=4)
        left_panel.grid_rowconfigure(3, weight=0)
        tree_frame.grid_rowconfigure(1, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 创建左侧面板1
        left1_panel = ttk.Frame(home_frame)
        left1_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        #创建行为列表详情
        action_list_frame_main = ttk.Frame(left1_panel)
        action_list_frame_main.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建行为列表主要详情控件
        content_frame = ttk.Frame(action_list_frame_main)
        content_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建行为名称控件
        ttk.Label(content_frame, text="行为名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_name_var = tk.StringVar()
        self.action_name_entry= ttk.Entry(content_frame, textvariable=self.action_name_var,state="disabled")
        self.action_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # 创建下一步行为控件
        ttk.Label(content_frame, text="下一步行为:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.next_action_var = tk.StringVar()
        self.next_action_entry = ttk.Entry(content_frame, textvariable=self.next_action_var,state="disabled")
        self.next_action_entry.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        # 行为类型
        ttk.Label(content_frame, text="行为类型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_type_var = tk.StringVar()
        self.action_type_combo = ttk.Combobox(content_frame, 
                     values=["mouse", "keyboard", "class", "AI","image","function"],
                     state="readonly",
                     textvariable=self.action_type_var)
        self.action_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 绑定选择事件和变量跟踪
        self.action_type_combo.bind('<<ComboboxSelected>>', self._on_action_type_changed)
        self.action_type_var.trace_add('write', lambda *args: self._on_action_type_changed())
        # Debug_group_id
        ttk.Label(content_frame, text="调试组ID:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.debug_group_id = tk.StringVar()
        self.debug_group_id_entry=ttk.Entry(content_frame, textvariable=self.debug_group_id)
        self.debug_group_id_entry.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)

        # 行为备注
        ttk.Label(content_frame, text="行为备注:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_note_var = tk.StringVar()
        self.action_note_entry=ttk.Entry(content_frame, textvariable=self.action_note_var)
        self.action_note_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # 配置grid权重
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(3, weight=1)

        # 创建行为详情子区域,这里用来动态显示
        self.action_list_frame = ttk.Frame(action_list_frame_main)
        self.action_list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        # 设置action_list_frame的默认大小和自动调整
        self.action_list_frame.pack_propagate(False)  # 禁止自动调整子控件大小
        self.action_list_frame.configure(height=100)  # 设置默认高度
        
        # 配置action_list_frame的grid权重,使其可以自动调整大小
        self.action_list_frame.grid_rowconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        # 初始化action_type_combo的值
        self._on_action_type_changed()
        # 创建行为列表
        list_frame = ttk.LabelFrame(left1_panel, text="行为列表")
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建列表视图和滚动条
        self.action_list = ttk.Treeview(list_frame, name='action_list_tree',columns=("type", "name", "next"), show="headings")
        self.action_list.heading("type", text="类型")
        self.action_list.heading("name", text="名称")
        self.action_list.heading("next", text="下一步")
        
        self.action_list.column("type", width=100)
        self.action_list.column("name", width=200)
        self.action_list.column("next", width=100)
        
        # 添加滚动条
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.action_list.yview)
        self.action_list.configure(yscrollcommand=list_scroll.set)
        
        # 布局
        self.action_list.grid(row=0, column=0, sticky=tk.NSEW)
        list_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建行为列表按钮
        button_frame = ttk.Frame(left1_panel)
        button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_new_group=ttk.Button(button_frame, text="创建", command=self._create_action)
        self.btn_new_group.pack(side=tk.LEFT, padx=5)
        self.btn_record_action=ttk.Button(button_frame, text="录制", command=self._record_action)
        self.btn_record_action.pack(side=tk.LEFT, padx=5)
        self.btn_modify_action=ttk.Button(button_frame, text="修改", command=self._modify_action)
        self.btn_modify_action.pack(side=tk.LEFT, padx=5)
        self.btn_delete_action=ttk.Button(button_frame, text="删除", command=self._delete_action)
        self.btn_delete_action.pack(side=tk.LEFT, padx=5)
        self.btn_save_action=ttk.Button(button_frame, text="保存", command=self._save_action)
        self.btn_save_action.pack(side=tk.LEFT, padx=5)
        self.btn_use_suit=ttk.Button(button_frame, text="调用套餐", command=self._use_suit)
        self.btn_use_suit.pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重，使左侧1面板可以随窗口调整大小
        home_frame.grid_columnconfigure(0, weight=1)
        home_frame.grid_columnconfigure(1, weight=1)
        home_frame.grid_columnconfigure(2, weight=1)
        left1_panel.grid_rowconfigure(0, weight=1)
        left1_panel.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        #  创建左侧面板2
        left2_panel = ttk.Frame(home_frame)
        left2_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

         #创建行为列表详情
        action_debug_list_frame = ttk.Frame(left2_panel)
        action_debug_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建行为列表主要详情控件
        content_debug_frame = ttk.Frame(action_debug_list_frame)
        content_debug_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建行为名称控件
        ttk.Label(content_debug_frame, text="行为名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_name_var = tk.StringVar()
        ttk.Entry(content_debug_frame, textvariable=self.action_debug_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # 创建下一步行为控件
        ttk.Label(content_debug_frame, text="下一步行为ID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.next_debug_id_var = tk.StringVar()
        ttk.Entry(content_debug_frame, textvariable=self.next_debug_id_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # 行为类型
        ttk.Label(content_debug_frame, text="行为类型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_type_var = tk.StringVar()
        self.action_debug_type_combo = ttk.Combobox(content_debug_frame, 
                     values=["mouse", "keyboard", "class", "AI","image","function"],
                     state="readonly",
                     textvariable=self.action_debug_type_var)
        self.action_debug_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 绑定选择事件和变量跟踪
        print("Binding debug combo events...")  # 调试信息
        self.action_debug_type_combo.bind('<<ComboboxSelected>>', lambda e: print("Debug combo selected event triggered") or self._on_debug_action_type_changed(e))
        self.action_debug_type_var.trace_add('write', lambda *args: print("Debug var write event triggered") or self._on_debug_action_type_changed())

        # 创建返回id
        ttk.Label(content_debug_frame, text="返回ID:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.back_id_var = tk.StringVar()
        ttk.Entry(content_debug_frame, textvariable=self.back_id_var).grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)

        # 行为备注
        ttk.Label(content_debug_frame, text="行为备注:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_debug_note_var = tk.StringVar()
        ttk.Entry(content_debug_frame, textvariable=self.action_debug_note_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # 配置grid权重
        content_debug_frame.grid_columnconfigure(1, weight=1)
        content_debug_frame.grid_columnconfigure(3, weight=1)

        # 创建行为详情子区域,这里用来动态显示
        self.action_debug_detail = ttk.Frame(action_debug_list_frame)
        self.action_debug_detail.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        # 设置action_list_frame的默认大小和自动调整
        self.action_debug_detail.pack_propagate(False)  # 禁止自动调整到子控件大小
        self.action_debug_detail.configure(height=100)  # 设置默认高度
        
        # 配置action_list_frame的grid权重,使其可以自动调整大小
        self.action_debug_detail.grid_rowconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(0, weight=1)

        # 初始化调试行为类型变更事件
        print("Initializing debug action type...")  # 调试信息
        self._on_debug_action_type_changed()

        # 创建行为列表
        list_debug_frame = ttk.LabelFrame(left2_panel, text="Debug行为列表")
        list_debug_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建列表视图和滚动条
        self.action_debug_list = ttk.Treeview(list_debug_frame, columns=("type", "name", "next"), show="headings")
        self.action_debug_list.heading("type", text="类型")
        self.action_debug_list.heading("name", text="名称")
        self.action_debug_list.heading("next", text="下一步")
        
        self.action_debug_list.column("type", width=100)
        self.action_debug_list.column("name", width=200)
        self.action_debug_list.column("next", width=100)
        
        # 添加滚动条
        list_debug_scroll = ttk.Scrollbar(list_debug_frame, orient="vertical", command=self.action_list.yview)
        self.action_debug_list.configure(yscrollcommand=list_debug_scroll.set)
        
        # 布局
        self.action_debug_list.grid(row=0, column=0, sticky=tk.NSEW)
        list_debug_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建行为列表按钮
        button_frame = ttk.Frame(left2_panel)
        button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_create_debug_action=ttk.Button(button_frame, text="创建", command=self._create_debug_action)
        self.btn_create_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_modify_debug_action=ttk.Button(button_frame, text="修改", command=self._modify_debug_action)
        self.btn_modify_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_delete_debug_action=ttk.Button(button_frame, text="删除", command=self._delete_debug_action)
        self.btn_delete_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_save_debug_action=ttk.Button(button_frame, text="保存", command=self._save_debug_action)
        self.btn_save_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_use_debug_suit=ttk.Button(button_frame, text="调用套餐", command=self._use_debug_suit)
        self.btn_use_debug_suit.pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重，使左侧1面板可以随窗口调整大小
        left2_panel.grid_rowconfigure(0, weight=1)
        left2_panel.grid_columnconfigure(0, weight=1)
        list_debug_frame.grid_rowconfigure(0, weight=1)
        list_debug_frame.grid_columnconfigure(0, weight=1)
       
       #数据更新
        self._refresh_action_group()
        self._refresh_debug_action_group()

    def action_group_item_selected(self, event=None):
        """当行为组树形视图项被选中时触发"
        """
        selected = self.action_tree.selection()
        if selected:
            item = self.action_tree.item(selected[0])
            self.actiongroup_hierarchy_tree_iid = selected[0]
            self._update_action_group_details(item['values'])
            self._refresh_action_list()
            self._refresh_debug_action_list()

    def _on_action_type_changed(self, event=None):
        """当行为类型改变时触发
        
        Args:
            event: 事件对象，由Tkinter自动传入
        """
        # 清除现有的控件
        for widget in self.action_list_frame.winfo_children():
            widget.destroy()
            
        # 直接从Combobox获取当前值
        action_type = self.action_type_combo.get()
        print(f"Action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.action_list_frame, text="欢迎使用自动化服务平台", font=("Arial", 16))
            welcome_label.pack(expand=True)
            return
            
        # 根据行为类型创建对应的控件
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

    def _create_mouse_controls(self):
        """创建鼠标行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_list_frame)
        right_frame = ttk.Frame(self.action_list_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 鼠标动作
        ttk.Label(left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(left_frame, 
                                        textvariable=self.mouse_action_var,
                                        values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mouse_size_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.mouse_x_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mouse_y_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.mouse_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

    def _create_keyboard_controls(self):
        """创建键盘行为控件"""
        # 键盘类型
        ttk.Label(self.action_list_frame, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.keyboard_type_var = tk.StringVar(self.window)  # 使用主窗口作为master
        keyboard_type_combo = ttk.Combobox(self.action_list_frame, 
                                         textvariable=self.keyboard_type_var,
                                         values=["按下", "释放", "单击", "文本"],
                                         state="readonly")
        keyboard_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 按键值或文本内容
        ttk.Label(self.action_list_frame, text="按键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.keyboard_value_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.keyboard_time_diff_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)

    def _create_class_controls(self):
        """创建类行为控件"""
        # 类名
        ttk.Label(self.action_list_frame, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_name_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗体名
        ttk.Label(self.action_list_frame, text="窗体名:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.windows_title_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.windows_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_time_diff_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)

    def _create_ai_controls(self):
        """创建AI行为控件"""
        # 训练库名称
        ttk.Label(self.action_list_frame, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_group_name_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.train_group_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(self.action_list_frame, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_long_name_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.train_long_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(self.action_list_frame, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.long_txt_name_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.long_txt_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # AI网页输入框输入的文本内容
        ttk.Label(self.action_list_frame, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_illustration_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 备注信息
        ttk.Label(self.action_list_frame, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_note_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_list_frame, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_time_diff_var = tk.StringVar(self.window)  # 使用主窗口作为master
        ttk.Entry(self.action_list_frame, textvariable=self.ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(1, weight=1)

    def _create_image_controls(self):
        """创建图像行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_list_frame)
        right_frame = ttk.Frame(self.action_list_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        #获取左上角坐标
        ttk.Button(left_frame, text="获取左上角坐标", command=self._get_left_top_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        #获取右下角坐标
        ttk.Button(left_frame, text="获取右下角坐标", command=self._get_right_bottom_coordinates).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        # 截屏左上角x坐标
        ttk.Label(left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lux_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.lux_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏左上角y坐标
        ttk.Label(left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.luy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.luy_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角x坐标
        ttk.Label(left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.rdx_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.rdx_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角y坐标
        ttk.Label(left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.rdy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.rdy_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 图片名称
        ttk.Label(right_frame, text="图片名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pic_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.pic_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # 匹配的图片文件名
        ttk.Label(right_frame, text="匹配图片:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.match_picture_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.match_picture_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配的文本信息
        ttk.Label(right_frame, text="匹配文本:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.match_text_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.match_text_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(right_frame, 
                                        textvariable=self.image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_list_frame.grid_columnconfigure(0, weight=1)
        self.action_list_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

    def _create_function_controls(self):
        """创建函数行为控件"""
        # 显示自定义函数文本
        function_label = ttk.Label(self.action_list_frame, text="自定义函数", font=("Arial", 16))
        function_label.pack(expand=True)
        
    def _add_excel_file(self):
        """打开文件对话框以选择Excel文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.excel_path_var.set(file_path)
            
    def _import_excel(self):
        """导入Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path_var.set(file_path)
            
    def _save_excel_settings(self):
        """保存Excel设置到配置文件"""
        from config.config_manager import ConfigManager
        config = ConfigManager()
        config.set_value('System', 'WorkExcelFile', self.excel_path_var.get())
        config.set_value('System', 'SheetNum', self.sheet_num_var.get())
        config.set_value('System', 'Column', self.column_var.get())
        from tkinter import messagebox
        messagebox.showinfo("提示", "Excel设置已保存")
    def _on_action_tree_select(self, event=None):
        selected = self.action_tree.selection()
        if not selected:
            return
        iid = selected[0]

        # 1. 先全部禁用
        self._set_controls_state(
            [
                self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
                self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
                self.is_auto_check, self.auto_time_entry, self.group_desc_entry,
                self.btn_new_group, self.btn_edit_group, self.btn_capture_image, self.btn_refresh_group, self.btn_delete_group
            ],
            'disabled'
        )
        self._set_controls_state(
            [
                self.action_name_entry, self.next_action_entry, self.action_type_combo,
                self.debug_group_id_entry, self.action_note_entry,
                self.btn_create_action, self.btn_record_action, self.btn_modify_action,
                self.btn_delete_action, self.btn_save_action, self.btn_use_suit,
                self.action_list
            ],
            'disabled'
        )

        # 2. 判断节点类型
        if iid.startswith("group_"):
            # 选中的是ActionGroup
            group_id = int(iid.split("_")[1])
            # Left_panel和Left1_panel全部可用
            self._set_controls_state(
                [
                    self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
                    self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
                    self.is_auto_check, self.auto_time_entry, self.group_desc_entry,
                    self.btn_new_group, self.btn_edit_group, self.btn_capture_image, self.btn_refresh_group, self.btn_delete_group
                ],
                'normal'
            )
            self.group_user_name_entry.config(state='disabled')
            self.department_id_entry.config(state='disabled')
            self._set_controls_state(
                [
                    self.action_name_entry, self.next_action_entry, self.action_type_combo,
                    self.debug_group_id_entry, self.action_note_entry,
                    self.btn_create_action, self.btn_record_action, self.btn_modify_action,
                    self.btn_delete_action, self.btn_save_action, self.btn_use_suit,
                    self.action_list
                ],
                'normal'
            )
            # 填充Left_panel和Left1_panel内容
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine
            from config.config_manager import ConfigManager
            from models.actions import ActionGroup, ActionsGroupHierarchy, ActionList
            from models.user import User
            config = ConfigManager()
            db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            group = session.query(ActionGroup).filter_by(id=group_id).first()
            if group:
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                # Left_panel
                print("set StringVar", id(self.group_name_var))
                self.group_name_var.set(group.action_list_group_name)
                print("set StringVar", id(self.group_name_var))
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
                # Left1_panel
                self.action_list.delete(*self.action_list.get_children())
                actions = session.query(ActionList).filter_by(group_id=group_id).all()
                for action in actions:
                    self.action_list.insert("", "end", iid=str(action.id), values=(
                        action.action_type, action.action_name, action.next_id
                    ))
            session.close()
        else:
            # 选中的是ActionsGroupHierarchy
            # Left_panel可用，Left1_panel全部禁用
            self._set_controls_state(
                [
                    self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
                    self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
                    self.is_auto_check, self.auto_time_entry, self.group_desc_entry,
                    self.btn_new_group, self.btn_edit_group, self.btn_capture_image, self.btn_refresh_group, self.btn_delete_group
                ],
                'normal'
            )
            self.group_user_name_entry.config(state='disabled')
            self.department_id_entry.config(state='disabled')
            self._set_controls_state(
                [
                    self.action_name_entry, self.next_action_entry, self.action_type_combo,
                    self.debug_group_id_entry, self.action_note_entry,
                    self.btn_create_action, self.btn_record_action, self.btn_modify_action,
                    self.btn_delete_action, self.btn_save_action, self.btn_use_suit,
                    self.action_list
                ],
                'disabled'
            )
            # 填充Left_panel内容
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine
            from config.config_manager import ConfigManager
            from models.actions import ActionsGroupHierarchy
            config = ConfigManager()
            db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=int(iid)).first()
            if hierarchy:
                print("set StringVar", id(self.group_name_var))
                self.group_name_var.set(hierarchy.group_name)
                print("set StringVar", id(self.group_name_var))
                self.group_last_circle_local_var.set("")
                self.group_last_circle_node_var.set("")
                self.group_setup_time_var.set(str(hierarchy.setup_time or ""))
                self.group_update_time_var.set(str(hierarchy.update_time or ""))
                self.group_user_id_var.set(str(hierarchy.doctor_id or ""))
                self.group_user_name_var.set("")  # 可查user表
                self.department_id_var.set(str(hierarchy.department_id or ""))
                self.is_auto_var.set(False)
                self.auto_time_var.set("")
                self.group_desc_var.set(hierarchy.group_note or "")
            session.close()
            # Left1_panel内容清空
            self.action_list.delete(*self.action_list.get_children())
            self.action_name_var.set("")
            self.next_action_var.set("")
            self.action_type_var.set("")
            self.debug_group_id.set("")
            self.action_note_var.set("")

    def _new_action_group(self):
        """新建行为组（弹窗输入，保存到数据库）"""
        import tkinter.simpledialog as simpledialog
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionGroup, ActionsGroupHierarchy
        from sqlalchemy import create_engine
        #获取要新建的组相对于目前选中的项的位置
        self.show_mode_picker()
        if self.module_select_node==5:
            return 
        #获取新建组的名称
        group_name = simpledialog.askstring("新建行为组", "请输入行为组名称：")
        if not group_name:
            return
        
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        # 这里可以根据当前选中的分层节点，决定group_rank_id
        if self.actiongroup_hierarchy_tree_iid.startswith('group_'):
            select_group= session.query(ActionGroup).filter_by(id=self.actiongroup_hierarchy_tree_iid).first()
            select_group_rank_id = select_group.group_rank_id
        hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=select_group_rank_id).first()
        group_rank_id = hierarchy.id if hierarchy else None
        if globalvariable.USER_IS_SUPER_ADMIN:
            department_id_var = simpledialog.askstring("入组的科室代码", "请输入科室代码：")
        else:
            department_id_var = globalvariable.USER_DEPARTMENT_ID
                                                       

        new_group = ActionGroup(
            action_list_group_name=group_name,
            user_id=self.username,
            group_rank_id=group_rank_id,
            setup_time=datetime.now(),
            update_time=datetime.now(),
            excel_name=self.excel_path_var.get() if hasattr(self, 'excel_path_var') else "",
            excel_sheet_num=int(self.sheet_num_var.get()) if hasattr(self, 'sheet_num_var') and self.sheet_num_var.get().isdigit() else 0,
            excel_column=int(self.column_var.get()) if hasattr(self, 'column_var') and self.column_var.get().isdigit() else 0,
            last_circle_local=0,
            last_circle_node=0,
            action_list_group_note=self.group_desc_var.get() if hasattr(self, 'group_desc_var') else "",
            is_auto=self.is_auto_var.get() if hasattr(self, 'is_auto_var') else False,
            auto_time=self.auto_time_var.get() if hasattr(self, 'auto_time_var') else "",
            department_id= department_id_var,
            sort_num=0,
            about_time=""
            # 其他字段可补充
        )
        session.add(new_group)
        session.commit()
        session.close()
        self._refresh_action_group()

    def _edit_action_group(self):
        """编辑行为组名称"""
        import tkinter.simpledialog as simpledialog
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionGroup
        from sqlalchemy import create_engine
        from tkinter import messagebox
        selected = self.action_tree.selection()
        if not selected or not selected[0].startswith("group_"):
            messagebox.showwarning("警告", "请选择要编辑的行为组")
            return
        group_id = int(selected[0].split("_")[1])
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        group = session.query(ActionGroup).filter_by(id=group_id).first()
        if not group:
            messagebox.showerror("错误", "行为组不存在")
            session.close()
            return
        new_name = simpledialog.askstring("编辑行为组", "请输入新的行为组名称：", initialvalue=group.action_list_group_name)
        if new_name:
            group.action_list_group_name = new_name
            session.commit()
        session.close()
        self._refresh_action_group()

    def _capture_image(self):
        """图像采集"""
        # TODO: 实现图像采集的功能
        self.group_name_var.set('ceshi2')

        # 添加诊断信息
        print("诊断信息:")
        print(f"1. StringVar 值: {self.group_name_var.get()}")
        print(f"2. Entry 控件值: {self.group_name_entry.get()}")
        print(f"3. Entry 状态: {self.group_name_entry.cget('state')}")
        print(f"4. StringVar ID: {id(self.group_name_var)}")
        print(f"5. Entry 的 textvariable ID: {id(self.group_name_entry.cget('textvariable'))}")

        # 强制刷新
        self.window.update()
        self.window.update_idletasks()

        print("刷新后 Entry 值:", self.group_name_entry.get()) 
    def _get_left_top_coordinates(self):
        """获取左上角坐标"""
        # TODO: 实现获取左上角坐标的功能
        pass
    def _get_right_bottom_coordinates(self):
        """获取右下角坐标"""
        # TODO: 实现获取右下角坐标的功能
        pass
    def _get_debug_left_top_coordinates(self):
        """获取左上角坐标"""
        # TODO: 实现获取左上角坐标的功能
        pass
    def _get_debug_right_bottom_coordinates(self):
        """获取右下角坐标"""
        # TODO: 实现获取右下角坐标的功能
        pass
    def _refresh_action_group(self):
        """刷新行为组树，按GroupRank分层显示"""
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionGroup, ActionsGroupHierarchy
        from models.user import User
        from sqlalchemy import create_engine
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.action_tree.delete(*self.action_tree.get_children())
        # 添加根节点
        #root_nodes = {
        #    'A0': self.action_tree.insert("", "end", text="个人", values=("A0",), iid="A0"),
        #    'A1': self.action_tree.insert("", "end", text="科室", values=("A1",), iid="A1"),
        #    'A2': self.action_tree.insert("", "end", text="全局", values=("A2",), iid="A2"),
        #}
        # 查询所有行为组层级
        hierarchies = session.query(ActionsGroupHierarchy).order_by(ActionsGroupHierarchy.group_rank).all()
        # 构建分层树结构
        tree_dict = {}
        for h in hierarchies:
            rank_dict = self.parse_group_rank(h.group_rank)
            key = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
            if globalvariable.USER_IS_SUPER_ADMIN:
                tree_dict[key] = {
                    'obj': h,
                    'iid': None,
                    'children': [],
                    'parent': None
                }
            else:
                if rank_dict['A'] == 2 or h.department_id == globalvariable.USER_DEPARTMENT_ID:
                    tree_dict[key] = {
                        'obj': h,
                        'iid': None,
                        'children': [],
                        'parent': None
                    }
        # 建立父子关系
        for key, node in tree_dict.items():
            rank = self.parse_group_rank(key)
            # 找父节点key
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
            if parent_key and parent_key in tree_dict:
                node['parent'] = parent_iid
                tree_dict[parent_key]['children'].append(key)
            else:
                node['parent'] = None
        # 插入到Treeview
        def insert_node(key, parent_iid):
            node = tree_dict[key]
            h = node['obj']
            user = session.query(User).filter_by(user_id=h.doctor_id).first()
            username = user.username if user else "未知"
            if parent_iid == "":
                self.action_tree.insert("", "end", iid=node['iid'], text=h.group_name, values=(h.group_name, username))
            else:
                self.action_tree.insert(parent_iid, "end", iid=node['iid'], text="📁", values=(h.group_name, username))
            #for child_key in node['children']:
            #    insert_node(child_key, iid)
        # 插入顶层节点
        for key, node in tree_dict.items():
            rank = self.parse_group_rank(key)
            if rank['B'] == 0 and rank['C'] == 0 and rank['D'] == 0 and rank['E'] == 0:
                a_code = f"A{rank['A']}"
                parent_iid = ""
                insert_node(key, parent_iid)
            else:
                parent_iid = node['parent']
                insert_node(key, parent_iid)
        # 查询所有行为组，插入到对应层级
        groups = session.query(ActionGroup).all()
        for group in groups:
            rank_id = getattr(group, 'group_rank_id', '')
            rank_record = session.query(ActionsGroupHierarchy).filter_by(id=rank_id).first()
            rank = rank_record.group_rank
            rank_dict = self.parse_group_rank(rank)
            # 找到父层级idd
            if rank_dict['E'] > 0:
                parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
            elif rank_dict['D'] > 0:
                parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
            elif rank_dict['C'] > 0:
                parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
            elif rank_dict['B'] > 0:
                parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}"
            else:
                parent_iid = ""
            user = session.query(User).filter_by(user_id=group.user_id).first()
            username = user.username if user else "未知"
            self.action_tree.insert(parent_iid, "end", text="📄", values=(group.action_list_group_name, username, username), iid=f"group_{group.id}")
        session.close() 

    def _delete_action_group(self):
        """删除行为组"""
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionGroup
        from sqlalchemy import create_engine
        from tkinter import messagebox
        selected = self.action_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为组")
            return
        iid = selected[0]
        if not iid.startswith("group_"):
            messagebox.showwarning("警告", "请选择具体的行为组节点")
            return
        group_id = int(iid.split("_")[1])
        if not messagebox.askyesno("确认", "确定要删除该行为组吗？"):
            return
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        group = session.query(ActionGroup).filter_by(id=group_id).first()
        if group:
            session.delete(group)
            session.commit()
            messagebox.showinfo("成功", "行为组已删除")
        session.close()
        self._refresh_action_group()
        
    def _create_action(self):
        """创建行为元（保存到数据库）"""
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionList
        from sqlalchemy import create_engine
        from tkinter import messagebox
        selected = self.action_tree.selection()
        if not selected or not selected[0].startswith("group_"):
            messagebox.showwarning("警告", "请先选择所属的行为组")
            return
        group_id = int(selected[0].split("_")[1])
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        action = ActionList(
            group_id=group_id,
            action_type=self.action_type_var.get(),
            action_name=self.action_name_var.get(),
            next_id=self.next_action_var.get(),
            debug_group_id=self.debug_group_id.get(),
            action_note=self.action_note_var.get()
        )
        session.add(action)
        session.commit()
        session.close()
        self._refresh_action_group()
    def _record_action(self):
        """录制行为元"""
        # TODO: 实现录制行为元的功能
        from gui.Recordaction import RecordWindow
        self.hide()
        record_window = RecordWindow(self)
        record_window.show()
    def _modify_action(self):
        """修改行为元"""
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionList
        from sqlalchemy import create_engine
        from tkinter import messagebox
        selected = self.action_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的行为元")
            return
        action_id = int(selected[0])
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        action = session.query(ActionList).filter_by(id=action_id).first()
        if not action:
            messagebox.showerror("错误", "行为元不存在")
            session.close()
            return
        # 这里可以弹窗编辑，也可以直接用界面上的输入框
        action.action_type = self.action_type_var.get()
        action.action_name = self.action_name_var.get()
        action.next_id = self.next_action_var.get()
        action.debug_group_id = self.debug_group_id.get()
        action.action_note = self.action_note_var.get()
        session.commit()
        session.close()
        self._refresh_action_group()
        
    def _delete_action(self):
        """删除行为元"""
        from config.config_manager import ConfigManager
        from sqlalchemy.orm import sessionmaker
        from models.actions import ActionList
        from sqlalchemy import create_engine
        from tkinter import messagebox
        selected = self.action_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为元")
            return
        action_id = int(selected[0])
        if not messagebox.askyesno("确认", "确定要删除该行为元吗？"):
            return
        config = ConfigManager()
        db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        action = session.query(ActionList).filter_by(id=action_id).first()
        if action:
            session.delete(action)
            session.commit()
        session.close()
        self._refresh_action_group()
        
    def _save_action(self):
        """保存行为元（与创建/修改合并）"""
        # 这里可以根据当前是否有选中行为元决定是新建还是修改
        if self.action_list.selection():
            self._modify_action()
        else:
            self._create_action()
        
    def _use_suit(self):
        """调用套餐"""
        # TODO: 实现调用套餐的功能
        pass
        
    def _create_debug_action(self):
        """创建行为"""
        # TODO: 实现创建行为的功能
        pass
        
    def _modify_debug_action(self):
        """修改行为"""
        # TODO: 实现修改行为的功能
        pass
        
    def _delete_debug_action(self):
        """删除行为"""
        # TODO: 实现删除行为的功能
        pass
        
    def _save_debug_action(self):
        """保存行为"""
        # TODO: 实现保存行为的功能
        pass
        
    def _use_debug_suit(self):
        """调用套餐"""
        # TODO: 实现调用套餐的功能
        pass
    
    def _create_debug_tab(self):
        """创建调试标签页"""
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text="调试")
        
        # 创建左侧面板（调试行为组）
        left_panel = ttk.Frame(debug_frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建调试行为组详情区域
        action_group_frame = ttk.LabelFrame(left_panel, text="调试行为组详情")
        action_group_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        # 创建基本信息区域（第一行）
        basic_info_frame = ttk.Frame(action_group_frame)
        basic_info_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 调试行为组名称
        ttk.Label(basic_info_frame, text="名称:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_name_var = tk.StringVar()
        self.debug_group_name_entry=ttk.Entry(basic_info_frame, textvariable=self.debug_group_name_var, width=20)
        self.debug_group_name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 创建时间信息区域（第二行）
        time_info_frame = ttk.Frame(action_group_frame)
        time_info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 创建时间
        ttk.Label(time_info_frame, text="创建时间:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_setup_time_var = tk.StringVar()
        self.debug_group_setup_time_entry=ttk.Entry(time_info_frame, textvariable=self.debug_group_setup_time_var, width=20)
        self.debug_group_setup_time_entry.pack(side=tk.LEFT)

        # 创建用户信息区域（第三行）
        user_info_frame = ttk.Frame(action_group_frame)
        user_info_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 更新时间
        ttk.Label(user_info_frame, text="更新时间:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_update_time_var = tk.StringVar()
        self.debug_group_update_time_entry=ttk.Entry(user_info_frame, textvariable=self.debug_group_update_time_var, width=20)
        self.debug_group_update_time_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 创建者ID
        ttk.Label(user_info_frame, text="创建者ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_user_id_var = tk.StringVar()
        self.debug_group_user_id_entry=ttk.Entry(user_info_frame, textvariable=self.debug_group_user_id_var, width=20)
        self.debug_group_user_id_entry.pack(side=tk.LEFT)

        # 创建部门信息区域（第四行）
        dept_info_frame = ttk.Frame(action_group_frame)
        dept_info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 创建者姓名
        ttk.Label(dept_info_frame, text="创建者姓名:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_user_name_var = tk.StringVar()
        self.debug_group_user_name_entry=ttk.Entry(dept_info_frame, textvariable=self.debug_group_user_name_var, width=20)
        self.debug_group_user_name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # 科室ID
        ttk.Label(dept_info_frame, text="科室:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_department_id_var = tk.StringVar()
        self.debug_department_id_entry=ttk.Entry(dept_info_frame, textvariable=self.debug_department_id_var, width=10)
        self.debug_department_id_entry.pack(side=tk.LEFT)

        # 创建描述区域（第六行）
        desc_frame = ttk.Frame(action_group_frame)
        desc_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 调试行为组备注
        ttk.Label(desc_frame, text="描述:").pack(side=tk.LEFT, padx=(0, 5))
        self.debug_group_desc_var = tk.StringVar()
        self.debug_group_desc_entry=ttk.Entry(desc_frame, textvariable=self.debug_group_desc_var, width=50)
        self.debug_group_desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 配置grid权重
        action_group_frame.grid_columnconfigure(0, weight=1)
        action_group_frame.grid_columnconfigure(1, weight=1)

        # 创建树形视图区域
        tree_frame = ttk.LabelFrame(left_panel, text="调试行为组")
        tree_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建树形视图和滚动条
        self.debug_action_tree = ttk.Treeview(tree_frame, columns=("name","userid",), show="tree headings")
        self.debug_action_tree.heading("#0", text="结构")
        self.debug_action_tree.column("#0", width=60)
        self.debug_action_tree.heading("name", text="名称")
        self.debug_action_tree.column("name", width=150)
        self.debug_action_tree.heading("userid", text="创建者")
        self.debug_action_tree.column("userid", width=50)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.debug_action_tree.yview)
        self.debug_action_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 布局
        self.debug_action_tree.grid(row=0, column=0, sticky=tk.NSEW)
        tree_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建调试行为组按钮
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_new_debug_action_group=ttk.Button(button_frame, text="新建", command=self._new_debug_action_group)
        self.btn_new_debug_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_edit_debug_action_group=ttk.Button(button_frame, text="编辑", command=self._edit_debug_action_group)
        self.btn_edit_debug_action_group.pack(side=tk.LEFT, padx=5)
        self.btn_capture_debug_image=ttk.Button(button_frame, text="图像采集", command=self._capture_debug_image)
        self.btn_capture_debug_image.pack(side=tk.LEFT, padx=5)
        self.btn_refresh_debug_action_group=ttk.Button(button_frame, text="刷新", command=self._refresh_debug_action_group)
        self.btn_refresh_debug_action_group.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self._delete_debug_action_group).pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重，使树形视图可以随窗口调整大小
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 创建中间面板（调试行为列表）
        middle_panel = ttk.Frame(debug_frame)
        middle_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建调试行为列表
        list_frame = ttk.LabelFrame(middle_panel, text="调试行为列表")
        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建列表视图和滚动条
        self.debug_action_list = ttk.Treeview(list_frame, columns=("type", "name", "next"), show="headings")
        self.debug_action_list.heading("type", text="类型")
        self.debug_action_list.heading("name", text="名称")
        self.debug_action_list.heading("next", text="下一步")
        
        self.debug_action_list.column("type", width=100)
        self.debug_action_list.column("name", width=200)
        self.debug_action_list.column("next", width=100)
        
        # 添加滚动条
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.debug_action_list.yview)
        self.debug_action_list.configure(yscrollcommand=list_scroll.set)
        
        # 布局
        self.debug_action_list.grid(row=0, column=0, sticky=tk.NSEW)
        list_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建调试行为按钮
        button_frame = ttk.Frame(middle_panel)
        button_frame.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        
        self.btn_create_debug_action=ttk.Button(button_frame, text="创建", command=self._create_debug_action)
        self.btn_create_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_modify_debug_action=ttk.Button(button_frame, text="修改", command=self._modify_debug_action)
        self.btn_modify_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_delete_debug_action=ttk.Button(button_frame, text="删除", command=self._delete_debug_action)
        self.btn_delete_debug_action.pack(side=tk.LEFT, padx=5)
        self.btn_save_debug_action=ttk.Button(button_frame, text="保存", command=self._save_debug_action)
        self.btn_save_debug_action.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="调用套餐", command=self._use_debug_suit).pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重
        middle_panel.grid_rowconfigure(0, weight=1)
        middle_panel.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 创建右侧面板（调试行为详情）
        right_panel = ttk.Frame(debug_frame)
        right_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建调试行为详情区域
        detail_frame = ttk.LabelFrame(right_panel, text="调试行为详情")
        detail_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建基本信息区域
        basic_info_frame = ttk.Frame(detail_frame)
        basic_info_frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # 调试行为名称
        ttk.Label(basic_info_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_name_var = tk.StringVar()
        self.debug_action_name_entry=ttk.Entry(basic_info_frame, textvariable=self.debug_action_name_var)
        self.debug_action_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 下一步调试行为
        ttk.Label(basic_info_frame, text="下一步:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_next_action_var = tk.StringVar()
        self.debug_next_action_entry=ttk.Entry(basic_info_frame, textvariable=self.debug_next_action_var)
        self.debug_next_action_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 调试行为类型
        ttk.Label(basic_info_frame, text="类型:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_action_type_var = tk.StringVar()
        self.debug_tab_action_type_combo = ttk.Combobox(basic_info_frame, 
                     values=["mouse", "keyboard", "class", "AI","image","function"],
                     state="readonly",
                     textvariable=self.debug_tab_action_type_var)
        self.debug_tab_action_type_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 绑定选择事件和变量跟踪
        self.debug_tab_action_type_combo.bind('<<ComboboxSelected>>', self._on_debug_tab_action_type_changed)
        self.debug_tab_action_type_var.trace_add('write', lambda *args: self._on_debug_tab_action_type_changed())
        
        # 调试返回行为
        ttk.Label(basic_info_frame, text="返回:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_return_action_var = tk.StringVar()
        self.debug_return_action_entry=ttk.Entry(basic_info_frame, textvariable=self.debug_return_action_var)
        self.debug_return_action_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 调试行为备注
        ttk.Label(basic_info_frame, text="备注:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_action_note_var = tk.StringVar()
        self.debug_action_note_entry=ttk.Entry(basic_info_frame, textvariable=self.debug_action_note_var)
        self.debug_action_note_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        #调试行为详情
        self.debug_tab_action_detail = ttk.Frame(detail_frame)
        self.debug_tab_action_detail.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 配置grid权重
        basic_info_frame.grid_columnconfigure(1, weight=1)
        
        # 创建调试行为详情子区域
        self.debug_action_detail = ttk.Frame(right_panel)
        self.debug_action_detail.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 配置grid权重
        detail_frame.grid_rowconfigure(1, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # 配置主窗口grid权重
        debug_frame.grid_columnconfigure(0, weight=1)
        debug_frame.grid_columnconfigure(1, weight=1)
        debug_frame.grid_columnconfigure(2, weight=1)
        debug_frame.grid_rowconfigure(0, weight=1)
    
    def _create_conduction_manager_tab(self):
        """创建流程管理器标签页"""
        conduction_frame = ttk.Frame(self.notebook)
        self.notebook.add(conduction_frame, text="流程管理器")
        
        # TODO: 实现流程管理器的具体内容
        
    def _create_workspace_tab(self):
        """创建工作区标签页"""
        workspace_frame = ttk.Frame(self.notebook)
        self.notebook.add(workspace_frame, text="工作区")
        
        # 创建左侧面板（在院患者）
        left_panel = ttk.LabelFrame(workspace_frame, text="在院患者")
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建在院患者树形视图
        self.in_hospital_tree = ttk.Treeview(left_panel, columns=("bed", "name", "id"), show="headings")
        self.in_hospital_tree.heading("bed", text="床号")
        self.in_hospital_tree.heading("name", text="姓名")
        self.in_hospital_tree.heading("id", text="病历号")
        
        self.in_hospital_tree.column("bed", width=100)
        self.in_hospital_tree.column("name", width=100)
        self.in_hospital_tree.column("id", width=150)
        
        # 添加滚动条
        in_hospital_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.in_hospital_tree.yview)
        self.in_hospital_tree.configure(yscrollcommand=in_hospital_scroll.set)
        
        # 布局
        self.in_hospital_tree.grid(row=0, column=0, sticky=tk.NSEW)
        in_hospital_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 创建中间按钮区域
        middle_panel = ttk.Frame(workspace_frame)
        middle_panel.grid(row=0, column=1, sticky=tk.NS, padx=5, pady=5)
        
        # 创建按钮
        self.btn_patient_discharge=ttk.Button(middle_panel, text="患者出院", command=self._patient_discharge)
        self.btn_patient_discharge.grid(row=0, column=0, pady=5)
        self.btn_patient_archive=ttk.Button(middle_panel, text="患者归档", command=self._patient_archive)
        self.btn_patient_archive.grid(row=1, column=0, pady=5)
        self.btn_cancel_discharge=ttk.Button(middle_panel, text="出院撤销", command=self._cancel_discharge)
        self.btn_cancel_discharge.grid(row=2, column=0, pady=5)
        self.btn_cancel_archive=ttk.Button(middle_panel, text="归档撤销", command=self._cancel_archive)
        self.btn_cancel_archive.grid(row=3, column=0, pady=5)
        
        # 创建右侧面板（出院患者）
        left1_panel = ttk.LabelFrame(workspace_frame, text="出院患者")
        left1_panel.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建出院患者树形视图
        self.out_hospital_tree = ttk.Treeview(left1_panel, columns=("bed", "name", "id"), show="headings")
        self.out_hospital_tree.heading("bed", text="床号")
        self.out_hospital_tree.heading("name", text="姓名")
        self.out_hospital_tree.heading("id", text="病历号")
        
        self.out_hospital_tree.column("bed", width=100)
        self.out_hospital_tree.column("name", width=100)
        self.out_hospital_tree.column("id", width=150)
        
        # 添加滚动条
        out_hospital_scroll = ttk.Scrollbar(left1_panel, orient="vertical", command=self.out_hospital_tree.yview)
        self.out_hospital_tree.configure(yscrollcommand=out_hospital_scroll.set)
        
        # 布局
        self.out_hospital_tree.grid(row=0, column=0, sticky=tk.NSEW)
        out_hospital_scroll.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置grid权重，使面板可以随窗口调整大小
        workspace_frame.grid_columnconfigure(0, weight=1)
        workspace_frame.grid_columnconfigure(2, weight=1)
        workspace_frame.grid_rowconfigure(0, weight=1)
        
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        left1_panel.grid_rowconfigure(0, weight=1)
        left1_panel.grid_columnconfigure(0, weight=1)
        
    def _patient_discharge(self):
        """处理患者出院"""
        selected_item = self.in_hospital_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要出院的患者")
            return
            
        # 获取选中的患者信息
        patient_info = self.in_hospital_tree.item(selected_item[0])
        bed_num = patient_info['values'][0]
        patient_name = patient_info['values'][1]
        patient_id = patient_info['values'][2]
        
        try:
            # TODO: 实现患者出院的具体逻辑
            # 1. 将患者文件夹从InHospital移动到OutHospital
            # 2. 重命名为当前日期和时间
            messagebox.showinfo("成功", f"患者 {patient_name} 已成功出院")
            self._refresh_patient_lists()
        except Exception as e:
            messagebox.showerror("错误", f"患者出院失败: {str(e)}")
            
    def _patient_archive(self):
        """处理患者归档"""
        messagebox.showinfo("提示", "归档功能开发中...")
        
    def _cancel_discharge(self):
        """撤销患者出院"""
        selected_item = self.out_hospital_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要撤销出院的患者")
            return
            
        # 获取选中的患者信息
        patient_info = self.out_hospital_tree.item(selected_item[0])
        bed_num = patient_info['values'][0]
        patient_name = patient_info['values'][1]
        patient_id = patient_info['values'][2]
        
        try:
            # TODO: 实现撤销患者出院的具体逻辑
            # 1. 将患者文件夹从OutHospital移动回InHospital
            messagebox.showinfo("成功", f"患者 {patient_name} 已成功撤销出院")
            self._refresh_patient_lists()
        except Exception as e:
            messagebox.showerror("错误", f"撤销出院失败: {str(e)}")
            
    def _cancel_archive(self):
        """撤销患者归档"""
        messagebox.showinfo("提示", "归档撤销功能开发中...")
        
    def _refresh_patient_lists(self):
        """刷新患者列表"""
        # TODO: 实现刷新患者列表的具体逻辑
        # 1. 清空现有列表
        self.in_hospital_tree.delete(*self.in_hospital_tree.get_children())
        self.out_hospital_tree.delete(*self.out_hospital_tree.get_children())
        
        # 2. 重新加载患者数据
        # TODO: 从数据库或文件系统加载患者数据
        
    def _create_aiset_tab(self):
        """创建AI设置标签页"""
        aiset_frame = ttk.Frame(self.notebook)
        self.notebook.add(aiset_frame, text="AI设置")
        
        # 创建左侧列表区域
        left_panel = ttk.Frame(aiset_frame)
        left_panel.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建AI操作列表
        list_frame = ttk.LabelFrame(left_panel, text="AI操作列表")
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
        
        # 创建右侧详情区域
        left1_panel = ttk.Frame(aiset_frame)
        left1_panel.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        
        # 创建详情显示区域
        detail_frame = ttk.LabelFrame(left1_panel, text="AI操作详情")
        detail_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 训练组
        ttk.Label(detail_frame, text="训练组:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_group_var = tk.StringVar()
        self.train_group_entry = ttk.Entry(detail_frame, textvariable=self.train_group_var, width=40)
        self.train_group_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 训练长文本
        ttk.Label(detail_frame, text="训练长文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.train_long_txt_var = tk.StringVar()
        self.train_long_txt_entry = ttk.Entry(detail_frame, textvariable=self.train_long_txt_var, width=40)
        self.train_long_txt_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 长文本位置
        ttk.Label(detail_frame, text="长文本位置:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.long_txt_location_var = tk.StringVar()
        self.long_txt_location_entry = ttk.Entry(detail_frame, textvariable=self.long_txt_location_var, width=40)
        self.long_txt_location_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 输出位置
        ttk.Label(detail_frame, text="输出位置:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_location_var = tk.StringVar()
        self.output_location_entry = ttk.Entry(detail_frame, textvariable=self.output_location_var, width=40)
        self.output_location_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(detail_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="新建", command=self._new_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修改", command=self._modify_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self._delete_ai_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self._save_ai_action).pack(side=tk.LEFT, padx=5)
        
        # 配置grid权重，使面板可以随窗口调整大小
        aiset_frame.grid_columnconfigure(1, weight=1)
        aiset_frame.grid_rowconfigure(0, weight=1)
        
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        left1_panel.grid_rowconfigure(0, weight=1)
        left1_panel.grid_columnconfigure(0, weight=1)
        
        detail_frame.grid_rowconfigure(4, weight=1)
        detail_frame.grid_columnconfigure(1, weight=1)
        
    def _new_ai_action(self):
        """新建AI操作"""
        # 清空输入框
        self.train_group_var.set("")
        self.train_long_txt_var.set("")
        self.long_txt_location_var.set("")
        self.output_location_var.set("")
        
    def _modify_ai_action(self):
        """修改AI操作"""
        selected_item = self.ai_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要修改的AI操作")
            return
            
        # TODO: 从数据库加载选中的AI操作信息
        # 这里暂时使用模拟数据
        self.train_group_var.set("示例训练组")
        self.train_long_txt_var.set("示例长文本")
        self.long_txt_location_var.set("D:/HISAuto/LongTxt/示例")
        self.output_location_var.set("D:/HISAuto/outputTxt/示例")
        
    def _delete_ai_action(self):
        """删除AI操作"""
        selected_item = self.ai_list.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的AI操作")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的AI操作吗？"):
            # TODO: 从数据库删除选中的AI操作
            self.ai_list.delete(selected_item)
            self._new_ai_action()  # 清空输入框
            
    def _save_ai_action(self):
        """保存AI操作"""
        # 验证必填字段
        if not self.train_group_var.get():
            messagebox.showwarning("警告", "训练组不能为空")
            return
            
        # TODO: 保存到数据库
        messagebox.showinfo("成功", "AI操作保存成功")
        
    def _create_task_control_tab(self):
        """创建任务控制标签页"""
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="任务控制")
        
        # 创建左侧面板（待执行任务）
        left_panel = ttk.LabelFrame(task_frame, text="待执行任务")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建待执行任务树形视图
        self.pending_task_tree = ttk.Treeview(left_panel, columns=("id", "time", "user", "priority", "auto", "group"), show="headings")
        self.pending_task_tree.heading("id", text="ID")
        self.pending_task_tree.heading("time", text="发起时间")
        self.pending_task_tree.heading("user", text="发起用户")
        self.pending_task_tree.heading("priority", text="优先级")
        self.pending_task_tree.heading("auto", text="自动执行")
        self.pending_task_tree.heading("group", text="行为组")
        
        self.pending_task_tree.column("id", width=50)
        self.pending_task_tree.column("time", width=150)
        self.pending_task_tree.column("user", width=100)
        self.pending_task_tree.column("priority", width=50)
        self.pending_task_tree.column("auto", width=50)
        self.pending_task_tree.column("group", width=100)
        
        # 添加滚动条
        pending_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.pending_task_tree.yview)
        self.pending_task_tree.configure(yscrollcommand=pending_scroll.set)
        
        # 布局
        self.pending_task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pending_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建中间按钮区域
        middle_panel = ttk.Frame(task_frame)
        middle_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 创建按钮
        ttk.Button(middle_panel, text="执行任务", command=self._execute_task).pack(pady=5)
        ttk.Button(middle_panel, text="暂停任务", command=self._pause_task).pack(pady=5)
        ttk.Button(middle_panel, text="删除任务", command=self._delete_task).pack(pady=5)
        ttk.Button(middle_panel, text="刷新列表", command=self._refresh_task_lists).pack(pady=5)
        
        # 创建右侧面板（已完成任务）
        left1_panel = ttk.LabelFrame(task_frame, text="已完成任务")
        left1_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建已完成任务树形视图
        self.finished_task_tree = ttk.Treeview(left1_panel, columns=("id", "time", "user", "priority", "auto", "group", "finish_time"), show="headings")
        self.finished_task_tree.heading("id", text="ID")
        self.finished_task_tree.heading("time", text="发起时间")
        self.finished_task_tree.heading("user", text="发起用户")
        self.finished_task_tree.heading("priority", text="优先级")
        self.finished_task_tree.heading("auto", text="自动执行")
        self.finished_task_tree.heading("group", text="行为组")
        self.finished_task_tree.heading("finish_time", text="完成时间")
        
        self.finished_task_tree.column("id", width=50)
        self.finished_task_tree.column("time", width=150)
        self.finished_task_tree.column("user", width=100)
        self.finished_task_tree.column("priority", width=50)
        self.finished_task_tree.column("auto", width=50)
        self.finished_task_tree.column("group", width=100)
        self.finished_task_tree.column("finish_time", width=150)
        
        # 添加滚动条
        finished_scroll = ttk.Scrollbar(left1_panel, orient="vertical", command=self.finished_task_tree.yview)
        self.finished_task_tree.configure(yscrollcommand=finished_scroll.set)
        
        # 布局
        self.finished_task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        finished_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化任务列表
        self._refresh_task_lists()
        
    def _execute_task(self):
        """执行选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要执行的任务")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        try:
            # 获取任务对象
            task = self.session.query(TaskList).filter_by(id=task_id).first()
            if not task:
                raise Exception("任务不存在")
            
            # 更新任务状态
            task.task_status = "running"
            self.session.commit()
            
            # TODO: 实现任务执行的具体逻辑
            messagebox.showinfo("成功", f"任务 {task_id} 已开始执行")
            self._refresh_task_lists()
        except Exception as e:
            messagebox.showerror("错误", f"任务执行失败: {str(e)}")
        
    def _pause_task(self):
        """暂停选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要暂停的任务")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        try:
            # 获取任务对象
            task = self.session.query(TaskList).filter_by(id=task_id).first()
            if not task:
                raise Exception("任务不存在")
            
            # 更新任务状态
            task.task_status = "paused"
            self.session.commit()
            
            messagebox.showinfo("成功", f"任务 {task_id} 已暂停")
            self._refresh_task_lists()
        except Exception as e:
            messagebox.showerror("错误", f"任务暂停失败: {str(e)}")
        
    def _delete_task(self):
        """删除选中的任务"""
        selected_item = self.pending_task_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return
        
        # 获取选中的任务信息
        task_info = self.pending_task_tree.item(selected_item[0])
        task_id = task_info['values'][0]
        
        if messagebox.askyesno("确认", f"确定要删除任务 {task_id} 吗？"):
            try:
                # 获取任务对象
                task = self.session.query(TaskList).filter_by(id=task_id).first()
                if not task:
                    raise Exception("任务不存在")
                
                # 删除任务
                self.session.delete(task)
                self.session.commit()
                
                messagebox.showinfo("成功", f"任务 {task_id} 已删除")
                self._refresh_task_lists()
            except Exception as e:
                messagebox.showerror("错误", f"任务删除失败: {str(e)}")
        
    def _refresh_task_lists(self):
        """刷新任务列表"""
        try:
            # 清空现有列表
            self.pending_task_tree.delete(*self.pending_task_tree.get_children())
            self.finished_task_tree.delete(*self.finished_task_tree.get_children())
            
            # 获取配置管理器实例
            config_manager = ConfigManager()
            db_path = config_manager.get_value('System', 'DataSource')
            encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
            db_manager = DatabaseManager(
            db_path=db_path,
            encryption_key=encryption_key
            )
            db_manager.initialize()
            self.session = db_manager.get_session()            

            pending_tasks = self.session.query(TaskList).all()
            for task in pending_tasks:
                # 获取行为组名称
                group = self.session.query(ActionGroup).filter_by(id=task.actions_group_id).first()
                group_name = group.action_list_group_name if group else "未知"
                
                self.pending_task_tree.insert("", "end", values=(
                    task.id,
                    task.task_start_time,
                    task.task_user_name,
                    task.task_priority,
                    "是" if task.task_is_auto else "否",
                    group_name
                ))
            
            # 从数据库加载已完成任务
            finished_tasks = self.session.query(TaskListFinished).all()
            for task in finished_tasks:
                # 获取行为组名称
                group = self.session.query(ActionGroup).filter_by(id=task.action_list_group_id).first()
                group_name = group.action_list_group_name if group else "未知"
                
                self.finished_task_tree.insert("", "end", values=(
                    task.id,
                    task.task_start_time,
                    task.task_user_name,
                    task.task_priority,
                    "是" if task.task_is_auto else "否",
                    group_name,
                    task.finished_time
                ))
        except Exception as e:
            print(f"刷新任务列表失败: {str(e)}")
            messagebox.showerror("错误", f"刷新任务列表失败: {str(e)}")
        
    def _create_cloud_control_tab(self):
        """创建云控制标签页"""
        cloud_frame = ttk.Frame(self.notebook)
        self.notebook.add(cloud_frame, text="云控制")
        
        # 创建左侧状态面板
        status_frame = ttk.LabelFrame(cloud_frame, text="云服务状态")
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建状态显示区域
        self.cpu_label = ttk.Label(status_frame, text="CPU使用率: --")
        self.cpu_label.pack(pady=5)
        
        self.memory_label = ttk.Label(status_frame, text="内存使用率: --")
        self.memory_label.pack(pady=5)
        
        self.disk_label = ttk.Label(status_frame, text="磁盘使用率: --")
        self.disk_label.pack(pady=5)
        
        self.network_label = ttk.Label(status_frame, text="网络状态: --")
        self.network_label.pack(pady=5)
        
        # 创建右侧控制面板
        control_frame = ttk.LabelFrame(cloud_frame, text="云服务控制")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 创建控制按钮
    def show(self):
        """显示主窗口"""
        self.window.mainloop()
        
    def hide(self):
        """隐藏主窗口"""
        self.window.withdraw()
        
    def destroy(self):
        """销毁主窗口"""
        self.window.destroy()

    def _create_setting_tab(self):
        """创建设置标签页，动态展示和编辑所有配置项"""
        setting_frame = ttk.Frame(self.notebook)
        self.notebook.add(setting_frame, text="设置")

        self.config_manager = ConfigManager()
        self.setting_entries = {}  # {(section, key): entry}

        row = 0
        for section in self.config_manager.config.sections():
            section_frame = ttk.LabelFrame(setting_frame, text=section)
            section_frame.grid(row=row, column=0, sticky=tk.W+tk.E, padx=10, pady=5, ipadx=5, ipady=5)
            row += 1
            inner_row = 0
            for key, value in self.config_manager.config[section].items():
                ttk.Label(section_frame, text=key+":").grid(row=inner_row, column=0, sticky=tk.W, padx=5, pady=2)
                entry = ttk.Entry(section_frame, width=40)
                entry.insert(0, value)
                entry.grid(row=inner_row, column=1, sticky=tk.W, padx=5, pady=2)
                self.setting_entries[(section, key)] = entry
                inner_row += 1

        # 保存按钮
        save_btn = ttk.Button(setting_frame, text="保存所有设置", command=self._save_all_settings)
        save_btn.grid(row=row, column=0, sticky=tk.E, padx=10, pady=10)

    def _save_all_settings(self):
        """保存所有设置到配置文件"""
        for (section, key), entry in self.setting_entries.items():
            value = entry.get()
            self.config_manager.set_value(section, key, value)
        messagebox.showinfo("提示", "所有设置已保存！") 

    def _on_debug_action_type_changed(self, event=None):
        """当调试行为类型改变时触发
        
        Args:
            event: 事件对象，由Tkinter自动传入
        """
        print("Debug action type changed method called")  # 调试信息
        # 清除现有的控件
        for widget in self.action_debug_detail.winfo_children():
            widget.destroy()
            
        # 直接从Combobox获取当前值
        action_type = self.action_debug_type_combo.get()
        print(f"Debug action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.action_debug_detail, text="欢迎使用调试功能", font=("Arial", 16))
            welcome_label.pack(expand=True)
            return
            
        # 根据行为类型创建对应的控件
        if action_type == "mouse":
            self._create_debug_mouse_controls()
        elif action_type == "keyboard":
            self._create_debug_keyboard_controls()
        elif action_type == "class":
            self._create_debug_class_controls()
        elif action_type == "AI":
            self._create_debug_ai_controls()
        elif action_type == "image":
            self._create_debug_image_controls()
        elif action_type == "function":
            self._create_debug_function_controls()

    def _on_debug_tab_action_type_changed(self, event=None):
        """当调试行为类型改变时触发
        
        Args:
            event: 事件对象，由Tkinter自动传入
        """
        print("Debug action type changed method called")  # 调试信息
        # 清除现有的控件
        for widget in self.debug_tab_action_detail.winfo_children():
            widget.destroy()
        # 直接从Combobox获取当前值
        action_type = self.debug_tab_action_type_combo.get()
        print(f"Debug action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.debug_tab_action_detail, text="欢迎使用调试功能", font=("Arial", 16))
            welcome_label.pack(expand=True)
            return
            
        # 根据行为类型创建对应的控件
        if action_type == "mouse":
            self._create_debug_tab_mouse_controls()
        elif action_type == "keyboard":
            self._create_debug_tab_keyboard_controls()
        elif action_type == "class":
            self._create_debug_tab_class_controls()
        elif action_type == "AI":
            self._create_debug_tab_ai_controls()
        elif action_type == "image":
            self._create_debug_tab_image_controls()
        elif action_type == "function":
            self._create_debug_tab_function_controls()

            

    def _create_debug_mouse_controls(self):
        """创建调试鼠标行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_debug_detail)
        right_frame = ttk.Frame(self.action_debug_detail)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 鼠标动作
        ttk.Label(left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(left_frame, 
                                        textvariable=self.debug_mouse_action_var,
                                        values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_size_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_x_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_y_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

    def _create_debug_keyboard_controls(self):
        """创建调试键盘行为控件"""
        # 键盘类型
        ttk.Label(self.action_debug_detail, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_type_var = tk.StringVar(self.window)
        keyboard_type_combo = ttk.Combobox(self.action_debug_detail, 
                                         textvariable=self.debug_keyboard_type_var,
                                         values=["按下", "释放", "单击", "文本"],
                                         state="readonly")
        keyboard_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 按键值或文本内容
        ttk.Label(self.action_debug_detail, text="按键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_value_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_debug_detail, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_keyboard_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_class_controls(self):
        """创建调试类行为控件"""
        # 类名
        ttk.Label(self.action_debug_detail, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_class_name_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗体名
        ttk.Label(self.action_debug_detail, text="窗体名:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_windows_title_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_windows_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_debug_detail, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_class_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_ai_controls(self):
        """创建调试AI行为控件"""
        # 训练库名称
        ttk.Label(self.action_debug_detail, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_train_group_name_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_train_group_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(self.action_debug_detail, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_train_long_name_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_train_long_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(self.action_debug_detail, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_long_txt_name_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_long_txt_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # AI网页输入框输入的文本内容
        ttk.Label(self.action_debug_detail, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_illustration_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        
        # 备注信息
        ttk.Label(self.action_debug_detail, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_note_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.action_debug_detail, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_ai_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.action_debug_detail, textvariable=self.debug_ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_image_controls(self):
        """创建调试图像行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.action_debug_detail)
        right_frame = ttk.Frame(self.action_debug_detail)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 获取左上角坐标
        ttk.Button(left_frame, text="获取左上角坐标", command=self._get_debug_left_top_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        # 获取右下角坐标
        ttk.Button(left_frame, text="获取右下角坐标", command=self._get_debug_right_bottom_coordinates).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        # 截屏左上角x坐标
        ttk.Label(left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_lux_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_lux_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏左上角y坐标
        ttk.Label(left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_luy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_luy_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角x坐标
        ttk.Label(left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_rdx_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_rdx_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角y坐标
        ttk.Label(left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_rdy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_rdy_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        # 右列控件
        # 图片名称
        ttk.Label(right_frame, text="图片名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_pic_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_pic_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配的图片文件名
        ttk.Label(right_frame, text="匹配图片:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_match_picture_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_match_picture_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配的文本信息
        ttk.Label(right_frame, text="匹配文本:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_match_text_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_match_text_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(right_frame, 
                                        textvariable=self.debug_image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

    def _create_debug_tab_mouse_controls(self):
        """创建调试鼠标行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.debug_tab_action_detail)
        right_frame = ttk.Frame(self.debug_tab_action_detail)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 鼠标动作
        ttk.Label(left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(left_frame, 
                                        textvariable=self.debug_tab_mouse_action_var,
                                        values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_size_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_x_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_y_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_mouse_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.action_debug_detail.grid_columnconfigure(0, weight=1)
        self.action_debug_detail.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

    def _create_debug_tab_keyboard_controls(self):
        """创建调试键盘行为控件"""
        # 键盘类型
        ttk.Label(self.debug_tab_action_detail, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_keyboard_type_var = tk.StringVar(self.window)
        keyboard_type_combo = ttk.Combobox(self.debug_tab_action_detail, 
                                         textvariable=self.debug_tab_keyboard_type_var,
                                         values=["按下", "释放", "单击", "文本"],
                                         state="readonly")
        keyboard_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 按键值或文本内容
        ttk.Label(self.debug_tab_action_detail, text="按键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_keyboard_value_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.debug_tab_action_detail, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_keyboard_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.debug_tab_action_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_tab_class_controls(self):
        """创建调试类行为控件"""
        # 类名
        ttk.Label(self.debug_tab_action_detail, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_class_name_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗体名
        ttk.Label(self.debug_tab_action_detail, text="窗体名:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_windows_title_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_windows_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.debug_tab_action_detail, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_class_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.debug_tab_action_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_tab_ai_controls(self):
        """创建调试AI行为控件"""
        # 训练库名称
        ttk.Label(self.debug_tab_action_detail, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_train_group_name_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_train_group_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(self.debug_tab_action_detail, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_train_long_name_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_train_long_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(self.debug_tab_action_detail, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
       
        
        # AI网页输入框输入的文本内容
        ttk.Label(self.debug_tab_action_detail, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_ai_illustration_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 备注信息
        ttk.Label(self.debug_tab_action_detail, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_ai_note_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.debug_tab_action_detail, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_tab_ai_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(self.debug_tab_action_detail, textvariable=self.debug_tab_ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.debug_tab_action_detail.grid_columnconfigure(1, weight=1)

    def _create_debug_tab_image_controls(self):
        """创建调试图像行为控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.debug_tab_action_detail)
        right_frame = ttk.Frame(self.debug_tab_action_detail)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 获取左上角坐标
        ttk.Button(left_frame, text="获取左上角坐标", command=self._get_debug_left_top_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        # 获取右下角坐标
        ttk.Button(left_frame, text="获取右下角坐标", command=self._get_debug_right_bottom_coordinates).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        # 截屏左上角x坐标
        ttk.Label(left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_lux_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_lux_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏左上角y坐标
        ttk.Label(left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_luy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_luy_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角x坐标
        ttk.Label(left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_rdx_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_rdx_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角y坐标
        ttk.Label(left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_rdy_var = tk.StringVar(self.window)
        ttk.Entry(left_frame, textvariable=self.debug_rdy_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        # 右列控件
        # 图片名称
        ttk.Label(right_frame, text="图片名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_pic_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_pic_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配的图片文件名
        ttk.Label(right_frame, text="匹配图片:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_match_picture_name_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_match_picture_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配的文本信息
        ttk.Label(right_frame, text="匹配文本:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_match_text_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_match_text_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_mouse_action_var = tk.StringVar(self.window)
        mouse_action_combo = ttk.Combobox(right_frame, 
                                        textvariable=self.debug_image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.debug_image_time_diff_var = tk.StringVar(self.window)
        ttk.Entry(right_frame, textvariable=self.debug_image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.debug_tab_action_detail.grid_columnconfigure(0, weight=1)
        self.debug_tab_action_detail.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)


    def _create_debug_tab_function_controls(self):
        """创建调试函数行为控件"""
        # 显示自定义函数文本
        function_label = ttk.Label(self.debug_tab_action_detail, text="调试自定义函数", font=("Arial", 16))
        function_label.pack(expand=True) 

    def _new_debug_action_group(self):
        """创建新的调试行为组"""
        pass
        
    def _edit_debug_action_group(self):
        """编辑选中的调试行为组"""
        pass
        
    def _capture_debug_image(self):
        """为调试行为组采集图像"""
        pass
        
    def _refresh_debug_action_group(self):
        """刷新调试行为组列表"""
        pass
        
    def _delete_debug_action_group(self):
        """删除选中的调试行为组"""
        pass
        
    def _create_debug_action(self):
        """创建新的调试行为"""
        pass
        
    def _modify_debug_action(self):
        """修改选中的调试行为"""
        pass
        
    def _delete_debug_action(self):
        """删除选中的调试行为"""
        pass
        
    def _save_debug_action(self):
        """保存调试行为的修改"""
        pass
        
    def _use_debug_suit(self):
        """调用调试行为套餐"""
        pass

    def parse_group_rank(self, rank: str):
        """
        解析GroupRank字符串，返回分层级字典。
        例如：A2B1C1D1E1 -> {'A': 2, 'B': 1, 'C': 1, 'D': 1, 'E': 1}
        """
        import re
        result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        if not rank:
            return result
        matches = re.findall(r'([ABCDE])(\d+)', rank)
        for k, v in matches:
            result[k] = int(v)
        return result

        
    def _delete_debug_action(self):
        """删除选中的调试行为"""
        pass
        
    def _save_debug_action(self):
        """保存调试行为的修改"""
        pass
        
    def _use_debug_suit(self):
        """调用调试行为套餐"""
        pass

    def parse_group_rank(self, rank: str):
        """
        解析GroupRank字符串，返回分层级字典。
        例如：A2B1C1D1E1 -> {'A': 2, 'B': 1, 'C': 1, 'D': 1, 'E': 1}
        """
        import re
        result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        if not rank:
            return result
        matches = re.findall(r'([ABCDE])(\d+)', rank)
        for k, v in matches:
            result[k] = int(v)
        return result
    def iid_to_group_rank(self,iid: str) -> str:
        """
        根据树节点iid（如A2B1C1D1E1、A1B1、A2等）复原标准group_rank字符串（A2B1C0D0E0等）。
        """
        import re
        # 先解析已有的级别
        result = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        matches = re.findall(r'([ABCDE])(\d+)', iid)
        for k, v in matches:
            result[k] = int(v)
        # 拼接成标准格式
        return f"A{result['A']}B{result['B']}C{result['C']}D{result['D']}E{result['E']}" 
    
    def _on_action_tree_select(self, event=None):        
        selected = self.action_tree.selection()
        if not selected:
            return
        iid = selected[0]
        # 先全部禁用
        self._set_home_controls_state('disabled')
        # 只让"创建者姓名"、"科室"不可用，其他可用
        for entry in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            entry.config(state='normal')
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
        try:
            # 判断节点类型
            if iid.startswith("group_"):
                # 选中的是ActionGroup
                group_id = int(iid.split("_")[1])
                # 查询ActionGroup和其关联的ActionsGroupHierarchy
                from sqlalchemy.orm import sessionmaker
                from sqlalchemy import create_engine
                from config.config_manager import ConfigManager
                from models.actions import ActionGroup, ActionsGroupHierarchy, ActionList
                from models.user import User
                config = ConfigManager()
                db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
                engine = create_engine(db_url)
                Session = sessionmaker(bind=engine)
                session = Session()
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                if group:
                    # Left1_panel按钮可用
                    for btn in [
                        self.btn_new_group, self.btn_record_action, self.btn_modify_action,
                        self.btn_delete_action, self.btn_save_action, self.btn_use_suit
                    ]:
                        btn.config(state='normal')

                    hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                    # 填充详情区
                    self.group_last_circle_local_entry.config(state= 'normal')
                    self.group_last_circle_local_var.set(group.last_circle_local or "")
                    self.group_name_entry.config(state = 'normal')
                    print("set StringVar", id(self.group_name_var))
                    self.group_name_var.set(group.action_list_group_name)
                    print("set StringVar", id(self.group_name_var))
                    print('group_name_var' + self.group_name_var.get())
                    print('group_name_var' + group.action_list_group_name)
                    print('group_name_entry state:', self.group_name_entry.cget("state"))
                    print('group_name_entry value:', self.group_name_entry.get())
                    print("StringVar id:", id(self.group_name_var))
                    print("Entry textvariable id:", id(self.group_name_entry.cget('textvariable')))
                    self.window.update()
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
                    # 检查变量是否绑定到控件（假设有一个 Entry）
                    if hasattr(self, 'group_name_entry'):
                        print("绑定的控件值:", self.group_name_entry.get())
                    else:
                        print("警告：变量未绑定到控件！")
                    self.group_name_entry.update_idletasks
                    # 填充action_list_tree
                    self.action_list.delete(*self.action_list.get_children())
                    actions = session.query(ActionList).filter_by(group_id=group_id).all()
                    for action in actions:
                        self.action_list.insert("", "end", iid=str(action.id), values=(
                            action.action_type, action.action_name, action.next_id
                        ))
                session.close()
            else:
                # 选中的是ActionsGroupHierarchy
                # 通过idd复原node的group_rank。
                
                from sqlalchemy.orm import sessionmaker
                from sqlalchemy import create_engine
                from config.config_manager import ConfigManager
                from models.actions import ActionsGroupHierarchy
                config = ConfigManager()
                db_url = f"sqlite:///{config.get_value('System', 'DataSource')}"
                engine = create_engine(db_url)
                Session = sessionmaker(bind=engine)
                session = Session()
                selected_group_rank = self.iid_to_group_rank(iid)
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=selected_group_rank).first()
                if hierarchy:
                    print("set StringVar", id(self.group_name_var))
                    self.group_name_var.set(hierarchy.group_name)
                    print("set StringVar", id(self.group_name_var))
                    # 其他字段根据实际表结构补充
                    self.group_last_circle_local_var.set("")
                    self.group_last_circle_node_var.set("")
                    self.group_setup_time_var.set(str(hierarchy.created_at or ""))
                    self.group_update_time_var.set(str(hierarchy.updated_at or ""))
                    self.group_user_id_var.set(str(hierarchy.doctor_id or ""))
                    self.group_user_name_var.set("")  # 可查user表
                    self.department_id_var.set(str(hierarchy.department_id or ""))
                    self.is_auto_var.set(False)
                    self.auto_time_var.set("")
                    self.group_desc_var.set(hierarchy.group_note or "")
                session.close()
                # Left_panel按钮可用
                for btn in [
                    self.btn_new_action_group, self.btn_edit_action_group, self.btn_capture_image,
                    self.btn_refresh_action_group, self.btn_delete_action_group
                ]:
                    btn.config(state='normal')
                # Left1_panel按钮不可用
                for btn in [
                    self.btn_new_group, self.btn_record_action, self.btn_modify_action,
                    self.btn_delete_action, self.btn_save_action, self.btn_use_suit
                ]:
                    btn.config(state='disabled')
                # 清空action_list_tree
                self.action_list.delete(*self.action_list.get_children())
        except Exception as e:
            print(e)

    def _set_home_controls_state(self, state):
        for ctrl in [
            self.group_name_entry, self.group_last_circle_local_entry, self.group_last_circle_node_entry,
            self.group_setup_time_entry, self.group_update_time_entry, self.group_user_id_entry,
            self.is_auto_check, self.auto_time_entry, self.group_desc_entry
        ]:
            ctrl.config(state=state)
        self.group_user_name_entry.config(state='disabled')
        self.department_id_entry.config(state='disabled')
