import tkinter as tk
from tkinter import ttk, messagebox
from utils.suit_view_func import SuitViewFunc

class SuitView(tk.Toplevel):
    def __init__(self, parent,action_group_id,current_action_id):
        super().__init__(parent)
        self.action_group_id = action_group_id
        self.current_action_id = current_action_id
        self.title("行为组套管理")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.transient(parent)  # 设为父窗口的临时窗口
        self.grab_set()  # 模态行为：阻止与其他窗口交互
        
        # 设置关闭窗口时的行为
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 初始化功能管理器
        self.suit_func = SuitViewFunc(self, action_group_id, current_action_id)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        #创建树形视图区域
        self.create_treeview_area()
        
        # 创建操作按钮区域
        self.create_button_area()
        
        # 创建详细信息显示区域
        self.create_detail_area()
        # 动态显示区域
        self.create_suit_list_dynamic_area()
        # 绑定事件
        self.bind_events()
        
        # 加载数据
        self.suit_func.load_suit_tree()
        self.suit_func.load_action_list()
        
        # 延迟初始化，确保默认值已设置
        self.after_idle(self._on_action_type_changed)
        
    def create_treeview_area(self):
        """创建树形视图区域，与home_tab.py中的self.action_tree类似，但这里只显示组套树形视图
        其数据来源自action_suit.py中相关的表"""
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        tree_frame.configure(height=250)
        
        # 创建左侧树形视图 - 参考home_tab.py中的action_tree
        self.suit_tree = ttk.Treeview(tree_frame, name='suit_hierarchy_tree', 
                                     columns=("name", "userid"), selectmode='browse', show="tree headings")
        self.suit_tree.heading("#0", text="结构")
        self.suit_tree.column("#0", width=60)
        self.suit_tree.heading("name", text="名称")
        self.suit_tree.column("name", width=150)
        self.suit_tree.heading("userid", text="创建者")
        self.suit_tree.column("userid", width=50)
        
        # 绑定右键菜单
        self.suit_tree.bind("<Button-3>", self._show_tree_context_menu)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.suit_tree.yview)
        self.suit_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.suit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # 创建右侧列表视图 - 参考home_tab.py中的action_list
        self.action_list = ttk.Treeview(tree_frame, name='suit_action_list_tree', 
                                       columns=("id", "type", "name", "next"), show="headings")
        # 设置Treeview的id列为隐藏
        self.action_list.heading("id", text="ID")
        self.action_list.heading("type", text="类型")
        self.action_list.heading("name", text="名称")
        self.action_list.heading("next", text="下一步")
        self.action_list.column("id", width=0, stretch=tk.NO)
        self.action_list.column("type", width=100)
        self.action_list.column("name", width=200)
        self.action_list.column("next", width=100)
        
        # 添加滚动条
        scrollbar2 = ttk.Scrollbar(tree_frame, orient="vertical", command=self.action_list.yview)
        self.action_list.configure(yscrollcommand=scrollbar2.set)
        
        # 布局
        self.action_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_suit_list_dynamic_area(self):
        """创建动态显示区域"""
        self.suit_list_dynamic_area = ttk.Frame(self.main_frame)
        self.suit_list_dynamic_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_button_area(self):
        """创建操作按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        #这里参考了home_tab.py中的self.action_tree的右键菜单
        self.tree_context_menu = tk.Menu(self.suit_tree, tearoff=0)
        self.tree_context_menu.add_command(label="新建组", command=self.suit_func.new_suit_group)
        self.tree_context_menu.add_command(label="排序↑", command=self.suit_func.sort_up_suit)
        self.tree_context_menu.add_command(label="排序↓", command=self.suit_func.sort_down_suit)
        self.tree_context_menu.add_command(label="刷新", command=self.suit_func.refresh_data)
        self.tree_context_menu.add_command(label="保存", command=self.suit_func.save_suit)
        # 创建按钮，参考home_tab.py中的self.action_tree的右键菜单
        self.new_btn = ttk.Button(button_frame, text="新建", command=self.suit_func.new_suit,state="disabled")
        self.new_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(button_frame, text="编辑", command=self.suit_func.edit_suit,state="disabled")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="删除", command=self.suit_func.delete_suit,state="disabled")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(button_frame, text="刷新", command=self.suit_func.refresh_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存", command=self.suit_func.save_suit,state="disabled" )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.import_btn = ttk.Button(button_frame, text="导入", command=self.suit_func.import_suit,state="disabled")
        self.import_btn.pack(side=tk.LEFT, padx=5)

    def create_detail_area(self):
        """创建详细信息显示区域"""
        detail_frame = ttk.LabelFrame(self.main_frame, text="详细信息")
        # 设置detail_frame的高度限制
        detail_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        # 通过配置来限制高度
        detail_frame.configure(height=150)
        
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
                     values=["mouse", "keyboard", "class", "AI","image","function","group"],
                     state="readonly",
                     textvariable=self.action_type_var)
        action_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        # Bind the event to trigger on change
        action_type_combo.bind("<<ComboboxSelected>>", self._on_action_type_changed)
        
        # 设置默认值并触发事件
        self.action_type_var.set("mouse")
        
        ttk.Label(right_frame, text="行为元名称:").grid(row=1, column=0, padx=5, pady=5)
        self.action_name = ttk.Entry(right_frame, width=30)
        self.action_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(right_frame, text="下一步ID:").grid(row=2, column=0, padx=5, pady=5)
        self.next_id = ttk.Entry(right_frame, width=30)
        self.next_id.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(right_frame, text="调试组ID:").grid(row=3, column=0, padx=5, pady=5)
        self.debug_id = ttk.Entry(right_frame, width=30)
        self.debug_id.grid(row=3, column=1, padx=5, pady=5)
        
        
    def bind_events(self):
        """绑定事件"""
        self.suit_tree.bind("<<TreeviewSelect>>", self.suit_func.on_suit_select)
        self.action_list.bind("<<TreeviewSelect>>", self.suit_func.on_action_select)
    
    def _show_tree_context_menu(self, event):
        """显示树形视图的右键菜单"""
        # 获取点击位置的项
        item = self.suit_tree.identify_row(event.y)
        if item:
            # 选中该项
            self.suit_tree.selection_set(item)
            # 显示菜单
            self.tree_context_menu.post(event.x_root, event.y_root)

        
 
        
    def _on_action_type_changed(self, event=None):
        """行为类型改变时的处理"""
        # 检查容器是否已创建
        if not hasattr(self, 'suit_list_dynamic_area') or not self.suit_list_dynamic_area.winfo_exists():
            return
        
        # 清空动态区域
        for widget in self.suit_list_dynamic_area.winfo_children():
            widget.destroy()
            
        # 直接从Combobox获取当前值
        action_type = self.action_type_var.get()
        print(f"Suit action type changed to: {action_type}")  # 调试信息
        
        if not action_type:
            # 如果行为类型为空，显示欢迎文本
            welcome_label = ttk.Label(self.suit_list_dynamic_area, text="请选择行为类型", font=("Arial", 12))
            welcome_label.pack(expand=True)
            return
        
        if action_type == "mouse":
            self._create_suit_mouse_controls()
        elif action_type == "keyboard":
            self._create_suit_keyboard_controls()
        elif action_type == "class":
            self._create_suit_class_controls()
        elif action_type == "AI":
            self._create_suit_ai_controls()
        elif action_type == "image":
            self._create_suit_image_controls()
        elif action_type == "function":
            self._create_suit_function_controls()
            
        # 强制更新界面
        self.suit_list_dynamic_area.update_idletasks()
    
    # 动态控件创建方法（按类型顺序：mouse -> keyboard -> class -> AI -> image -> function）
    def _create_suit_mouse_controls(self):
        """创建套餐鼠标控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.suit_list_dynamic_area)
        right_frame = ttk.Frame(self.suit_list_dynamic_area)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        
        # 左列控件
        # 鼠标动作
        ttk.Label(left_frame, text="鼠标动作:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_mouse_action_type_var = tk.StringVar()
        mouse_action_combo = ttk.Combobox(left_frame, 
                                       values=["左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                       textvariable=self.suit_mouse_action_type_var, state="readonly")
        mouse_action_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作大小
        ttk.Label(left_frame, text="动作大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_mouse_size_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.suit_mouse_size_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # X坐标
        ttk.Label(right_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_mouse_x_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_mouse_x_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(right_frame, text="Y坐标:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_mouse_y_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_mouse_y_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_mouse_time_diff_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_mouse_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(0, weight=1)
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)
        
    def _create_suit_keyboard_controls(self):
        """创建套餐键盘控件"""
        # 键盘类型
        ttk.Label(self.suit_list_dynamic_area, text="键盘类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_keyboard_type_var = tk.StringVar()
        keyboard_type_combo = ttk.Combobox(self.suit_list_dynamic_area, 
                                        values=["按下", "释放", "单击", "文本"],
                                        textvariable=self.suit_keyboard_type_var, state="readonly")
        keyboard_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 按键值或文本内容
        ttk.Label(self.suit_list_dynamic_area, text="按键值/文本:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_keyboard_value_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_keyboard_value_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.suit_list_dynamic_area, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_keyboard_time_diff_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_keyboard_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        
    def _create_suit_class_controls(self):
        """创建套餐类控件"""
        # 类名
        ttk.Label(self.suit_list_dynamic_area, text="类名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_class_name_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_class_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 窗体名
        ttk.Label(self.suit_list_dynamic_area, text="窗体名:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_window_title_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_window_title_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.suit_list_dynamic_area, text="时间差:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_class_time_diff_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_class_time_diff_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        
    def _create_suit_ai_controls(self):
        """创建套餐AI控件"""
        # 训练库名称
        ttk.Label(self.suit_list_dynamic_area, text="训练库名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_training_group_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_training_group_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 记录名称
        ttk.Label(self.suit_list_dynamic_area, text="记录名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_record_name_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_record_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 长文本名称
        ttk.Label(self.suit_list_dynamic_area, text="长文本名称:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_long_text_name_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_long_text_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # AI网页输入框输入的文本内容
        ttk.Label(self.suit_list_dynamic_area, text="AI输入文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_illustration_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_illustration_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 备注信息
        ttk.Label(self.suit_list_dynamic_area, text="备注信息:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_note_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_note_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.suit_list_dynamic_area, text="时间差:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_ai_time_diff_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_ai_time_diff_var).grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        
    def _create_suit_image_controls(self):
        """创建套餐图像控件"""
        # 创建左右两列Frame容器
        left_frame = ttk.Frame(self.suit_list_dynamic_area)
        right_frame = ttk.Frame(self.suit_list_dynamic_area)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)

        # 左列控件
        # 获取左上角坐标
        ttk.Button(left_frame, text="获取区域坐标", command=self._get_suit_region_coordinates).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)  
        # 截屏左上角x坐标
        ttk.Label(left_frame, text="左上角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_left_top_x_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.suit_image_left_top_x_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏左上角y坐标
        ttk.Label(left_frame, text="左上角Y:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_left_top_y_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.suit_image_left_top_y_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角x坐标
        ttk.Label(left_frame, text="右下角X:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_right_bottom_x_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.suit_image_right_bottom_x_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 截屏右下角y坐标
        ttk.Label(left_frame, text="右下角Y:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_right_bottom_y_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.suit_image_right_bottom_y_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 右列控件
        # 图像名称
        ttk.Label(right_frame, text="图像名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_names_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_image_names_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 匹配条件
        ttk.Label(right_frame, text="匹配条件:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_match_criteria_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_image_match_criteria_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 鼠标动作
        ttk.Label(right_frame, text="鼠标动作:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_mouse_action_var = tk.StringVar()
        mouse_action_combo = ttk.Combobox(right_frame, 
                                        textvariable=self.suit_image_mouse_action_var,
                                        values=["无", "左击", "右击", "左键按下", "右键按下", "左键释放", "右键释放", "滚轮动作"],
                                        state="readonly")
        mouse_action_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(right_frame, text="时间差:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_image_time_diff_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.suit_image_time_diff_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(0, weight=1)
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        
    def _create_suit_function_controls(self):
        """创建套餐函数控件"""
        # 函数名称
        ttk.Label(self.suit_list_dynamic_area, text="函数名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_function_name_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_function_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数
        ttk.Label(self.suit_list_dynamic_area, text="参数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_function_parameters_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_function_parameters_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 参数列表
        ttk.Label(self.suit_list_dynamic_area, text="参数列表:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_function_arguments_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_function_arguments_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 时间差
        ttk.Label(self.suit_list_dynamic_area, text="时间差:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.suit_function_time_diff_var = tk.StringVar()
        ttk.Entry(self.suit_list_dynamic_area, textvariable=self.suit_function_time_diff_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 配置grid权重
        self.suit_list_dynamic_area.grid_columnconfigure(1, weight=1)
        
    def _get_suit_region_coordinates(self):
        """获取套餐区域坐标"""
        try:
            # 调用独立的区域坐标获取模块
            from utils.region_coordinates import get_region_coordinates
            
            success = get_region_coordinates(
                self,
                self.suit_image_left_top_x_var,
                self.suit_image_left_top_y_var,
                self.suit_image_right_bottom_x_var,
                self.suit_image_right_bottom_y_var
            )
            
            if success:
                print("套餐区域坐标获取成功")
            else:
                print("套餐区域坐标获取失败")
                
        except Exception as e:
            print(f"获取套餐区域坐标时发生异常: {str(e)}")
            messagebox.showerror("错误", f"获取套餐区域坐标失败: {str(e)}")
    
    def on_cancel(self):
        """取消按钮处理"""
        self.result = None
        self.destroy()
