#添加对home_tab.py中_save_action_group方法的支持
from datetime import datetime
from tkinter import messagebox
from gui.tabs.Hierarchyutils import iid_to_group_rank
from utils.logger import Logger,logger
from models.actions import ActionGroup, ActionsGroupHierarchy,ActionList,ActionMouse,ActionKeyboard,ActionClass,ActionAI,ActionPrintscreen,ActionFunction
from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager

class home_tab_func:
    """用于支持home_tab.py中相关方法的实现"""
    
    def __init__(self, group_name: str, group_desc: str, group_user_id: str,
                  group_department_id: str,is_auto: bool, auto_time: str, 
                 action_group_selected_rank: str,action_tree_selected_iid: str,
                 action_group_type:int,sort_num:int,action_group_id:int,action_group_hierarchy_id:int):
        """初始化行为组信息,用于新增保存行为组
        
        Args:
            group_name: 行为组名称
            group_desc: 行为组描述
            group_user_id: 用户ID
            group_department_id: 科室ID
            is_auto: 是否自动执行
            auto_time: 自动执行时间
            action_group_selected_rank: 行为组秩序
            action_tree_selected_iid: 行为树选中项的iid
            action_group_type: 行为组类型,1:表示新增保存；2.表示修改保存。
            sort_num: 排序号
        Raises:
            ValueError: 当必要参数为空或无效时
        """
        # 验证必要参数，使用for循环验证，同时提示用户哪个参数为空
        if not all([group_name, group_user_id, group_department_id, action_group_selected_rank,action_tree_selected_iid,action_group_type,sort_num]):
            logger.error("行为组信息无效：必要参数不能为空")
            debugtxt = ""
            for param, value in [("group_name", group_name), ("group_user_id", group_user_id), ("group_department_id", group_department_id), ("action_group_selected_rank", action_group_selected_rank),("action_tree_selected_iid",action_tree_selected_iid),("action_group_type",action_group_type),("sort_num",sort_num)]:
                if not value:
                    debugtxt += f"参数{param}为空\n"
            messagebox.showinfo("提示", debugtxt)
            return False
            
        # 验证自动执行时间
        if is_auto and not auto_time:
            logger.error("行为组信息无效：auto为True时，auto_time不能为空")
            return False
            
        # 初始化属性
        self.group_name = group_name
        self.group_desc = group_desc
        self.group_user_id = group_user_id
        self.group_department_id = group_department_id
        self.is_auto = is_auto
        self.auto_time = auto_time
        self.action_group_selected_rank = action_group_selected_rank
        self.action_tree_selected_iid = action_tree_selected_iid
        self.action_group_type = action_group_type
        self.sort_num = sort_num
        self.action_group_id = action_group_id
        self.action_group_hierarchy_id = action_group_hierarchy_id
        self.session = None
        """1:表示新增保存；2.表示修改保存；"""
    def _get_session(self):
        """获取数据库会话"""
        
        config_manager = ConfigManager()
        db_path = config_manager.get_value('System', 'DataSource')
        encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
        db_manager = DatabaseManager(db_path, encryption_key)
        db_manager.initialize()
        self.session = db_manager.Session()
        return self.session
    
    def _save_action_group(self)->bool:
        """保存行为组"""
        #判断行为组任务类型
        if self.action_group_type == 1:
            #新增保存
            #获取数据库会话
            session = self._get_session()
            if not session:
                return False
            #生成新增行为组记录
            new_action_group = ActionGroup(
                action_list_group_name=self.group_name,
                action_list_group_note=self.group_desc,
                is_auto=self.is_auto,
                auto_time=self.auto_time,
                user_id=self.group_user_id,
                department_id=self.group_department_id,
                setup_time=datetime.now(),
                group_rank_id=self.action_group_selected_rank,
                sort_num=self.sort_num,
            )
            session.add(new_action_group)
            session.commit()
            return True
        elif self.action_group_type == 2:
            #修改保存
            #判断self.action_tree_selected_iid是来源于Action_list_group表还是来源于ActionsGroupHierarchy表
            if self.action_tree_selected_iid.startswith("group_"):
                #来源于Action_list_group表
                group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
                if group:
                    #更新group表的记录
                    group.action_list_group_name = self.group_name
                    group.action_list_group_note = self.group_desc
                    group.is_auto = self.is_auto
                    group.auto_time = self.auto_time
                    group.update_time = datetime.now()
                    session.commit()
                    return True
                else:
                    logger.error(f"无法找到行为组记录: {self.action_tree_selected_iid}")
                    return False
            else:
                #来源于ActionsGroupHierarchy表
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_group_hierarchy_id).first()
                if hierarchy:
                    #更新hierarchy表的记录
                    hierarchy.group_name = self.group_name
                    hierarchy.group_note = self.group_desc
                    hierarchy.doctor_id = self.group_user_id
                    hierarchy.update_time = datetime.now()
                    session.commit()
                    return True
                else:
                    logger.error(f"无法找到行为组记录: {self.action_tree_selected_iid}")
                    return False
        else:
            logger.error(f"无效的行为组类型: {self.action_group_type}")
            return False
    def _delete_action_group(self)->bool:
        """删除行为组"""
        #获取数据库会话
        session = self._get_session()
        if not session:
            return False
        #如果选中的是来源于Action_list_group表
        if self.action_tree_selected_iid.startswith("group_"):
            #删除action_list_group表的记录
            group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
            if group:
                session.delete(group)
                session.commit()
            else:
                logger.error(f"无法找到行为组记录: {self.action_group_id}")
                return False
        elif self.action_tree_selected_iid.startswith("A"):
            #删除ActionsGroupHierarchy表的记录
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_group_hierarchy_id).first()
            if hierarchy:
                session.delete(hierarchy)
                session.commit()
            else:
                logger.error(f"无法找到行为组记录: {self.action_group_hierarchy_id}")
                return False
        else:   
            logger.error(f"无效的行为组类型: {self.action_group_type}")
            return False
        return True

    def _session_close(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
        return True
    def _capture_image(self):
        """图像采集"""
        messagebox.showinfo("提示", "图像采集功能待实现")

def _home_capture_image(action_group_id:int):
    """图像采集"""
    #获取配置文件中的
    messagebox.showinfo("提示", "图像采集功能待实现")

def _home_delete_action_group(action_group_id:int):
    """删除行为组"""
    messagebox.showinfo("提示", "删除行为组功能待实现")

def _home_save_action_group(action_group_id:int):
    """保存行为组"""

class ActionManager:
    """行为元管理器，用于处理middle_panel中行为元相关的按钮功能"""
    
    def __init__(self, home_tab):
        """初始化行为元管理器
        
        Args:
            home_tab: HomeTab实例的引用，用于访问界面控件和变量
        """
        self.home_tab = home_tab
        self.logger = Logger()
    
    def create_action(self):
        """创建行为元"""
        # 检查是否有选中的行为组
        if not self.home_tab.current_action_group_id:
            messagebox.showinfo("提示", "请先选择行为组")
            return False
            
        # 设置行为元操作类型为新增
        self.home_tab.action_operation_type = 1
        
        # 启用相关控件
        self._set_action_controls_state('normal')
        
        # 清空基本信息
        self.home_tab.action_name_var.set("")
        self.home_tab.next_action_var.set("")
        self.home_tab.action_type_var.set("mouse")  # 默认选择鼠标类型
        self.home_tab.debug_group_id.set("")
        self.home_tab.action_note_var.set("")
        
        # 清空动态详情区域
        self._clear_action_detail_controls()
        
        # 修改按钮状态
        self._set_action_button_state()
        
        # 触发行为类型变更事件以显示默认控件
        self._on_action_type_changed()
        return True
    
    def modify_action(self):
        """修改行为元"""
        # 检查是否有选中的行为元
        selected = self.home_tab.action_list.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要修改的行为")
            return False
            
        # 获取选中的行为元ID
        self.home_tab.current_action_id = self.home_tab.action_list.item(selected[0])['values'][0]
        
        # 设置行为元操作类型为修改
        self.home_tab.action_operation_type = 2
        
        # 启用相关控件
        self._set_action_controls_state('normal')
        
        # 修改按钮状态
        self._set_action_button_state()
        
        return True
    
    def delete_action(self):
        """删除行为元"""
        selected = self.home_tab.action_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为")
            return False
            
        if messagebox.askyesno("确认", "确定要删除选中的行为吗？"):
            try:
                # 获取选中的行为元ID
                action_id = self.home_tab.action_list.item(selected[0])['values'][0]
                
                # 从数据库删除行为元
                from models.actions import ActionList
                from database.db_manager import DatabaseManager
                from config.config_manager import ConfigManager
                
                config = ConfigManager()
                db_path = config.get_value('System', 'DataSource')
                dp_encryption_key = config.get_value('System', 'dbencryptionkey')
                db_manager = DatabaseManager(db_path, dp_encryption_key)
                db_manager.initialize()
                session = db_manager.Session()
                
                # 删除行为元记录
                action = session.query(ActionList).filter_by(id=action_id).first()
                if action:
                    session.delete(action)
                    session.commit()
                    messagebox.showinfo("成功", "行为删除成功")
                    # 刷新行为列表
                    self._refresh_action_list()
                else:
                    messagebox.showerror("错误", "未找到要删除的行为")
                
                session.close()
                return True
                
            except Exception as e:
                self.logger.error(f"删除行为失败: {str(e)}")
                messagebox.showerror("错误", f"删除行为失败: {str(e)}")
                return False
        
        return False
    
    def save_action(self):
        """保存行为元"""
        try:
            # 验证必填字段
            if not self.home_tab.action_name_var.get().strip():
                messagebox.showwarning("警告", "请输入行为名称")
                return False
                
            if not self.home_tab.action_type_var.get():
                messagebox.showwarning("警告", "请选择行为类型")
                return False
                
            # 获取数据库连接
            from models.actions import ActionList, ActionMouse, ActionKeyboard, ActionClass, ActionAI, ActionPrintscreen, ActionFunction
            from database.db_manager import DatabaseManager
            from config.config_manager import ConfigManager
            
            config = ConfigManager()
            db_path = config.get_value('System', 'DataSource')
            dp_encryption_key = config.get_value('System', 'dbencryptionkey')
            db_manager = DatabaseManager(db_path, dp_encryption_key)
            db_manager.initialize()
            session = db_manager.Session()
            
            if self.home_tab.action_operation_type == 1:
                # 新增保存
                action_list = ActionList(
                    group_id=self.home_tab.current_action_group_id,
                    action_type=self.home_tab.action_type_var.get(),
                    action_name=self.home_tab.action_name_var.get().strip(),
                    next_id=self.home_tab.next_action_var.get().strip() or None,
                    debug_group_id=self.home_tab.debug_group_id.get().strip() or None,
                    created_at=datetime.now(),
                    action_note=self.home_tab.action_note_var.get().strip()
                )
                session.add(action_list)
                session.flush()  # 获取ID
                
                # 保存详细记录
                self._save_action_detail(session, action_list.id)
                
                messagebox.showinfo("成功", "行为创建成功")
                
            elif self.home_tab.action_operation_type == 2:
                # 修改保存
                action_list = session.query(ActionList).filter_by(id=self.home_tab.current_action_id).first()
                if action_list:
                    action_list.action_name = self.home_tab.action_name_var.get().strip()
                    action_list.next_id = self.home_tab.next_action_var.get().strip() or None
                    action_list.debug_group_id = self.home_tab.debug_group_id.get().strip() or None
                    action_list.updated_at = datetime.now()
                    action_list.created_at = datetime.now()
                    action_list.action_note = self.home_tab.action_note_var.get().strip()
                    # 更新详细记录
                    self._update_action_detail(session, action_list.id)
                    session.commit()
                    session.close()
                    messagebox.showinfo("成功", "行为修改成功")
                else:
                    messagebox.showerror("错误", "未找到要修改的行为")
                    session.close()
                    return False
            # 重置状态
            self.home_tab.action_operation_type = None
            self.home_tab.current_action_id = None
            
            # 禁用控件
            self._set_action_controls_state('disabled')
            
            # 修改按钮状态
            self._set_action_button_state()
            
            # 刷新行为列表
            self._refresh_action_list()
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存行为失败: {str(e)}")
            messagebox.showerror("错误", f"保存行为失败: {str(e)}")
            print(f"保存行为失败: {str(e)}")
            return False
    
    def _set_action_controls_state(self, state):
        """设置行为元控件状态"""
        for ctrl in [
            self.home_tab.action_name_entry, self.home_tab.next_action_entry, 
            self.home_tab.action_type_combo, self.home_tab.debug_group_id_entry, 
            self.home_tab.action_note_entry
        ]:
            ctrl.config(state=state)
    
    def _set_action_button_state(self):
        """设置行为按钮状态"""
        if self.home_tab.action_operation_type:
            # 编辑状态
            self.home_tab.btn_create_action.config(state='disabled')
            self.home_tab.btn_modify_action.config(state='disabled')
            self.home_tab.btn_delete_action.config(state='disabled')
            self.home_tab.btn_save_action.config(state='normal')
        else:
            # 正常状态
            self.home_tab.btn_create_action.config(state='normal')
            self.home_tab.btn_modify_action.config(state='normal')
            self.home_tab.btn_delete_action.config(state='normal')
            self.home_tab.btn_save_action.config(state='disabled')
    
    def _clear_action_detail_controls(self):
        """清空行为详情控件"""
        # 清空动态详情区域
        for widget in self.home_tab.action_list_frame.winfo_children():
            widget.destroy()
        
        # 清空各种类型的变量
        if hasattr(self.home_tab, 'action_mouse_action_type_var'):
            self.home_tab.action_mouse_action_type_var.set("")
        if hasattr(self.home_tab, 'action_mouse_x_var'):
            self.home_tab.action_mouse_x_var.set("")
        if hasattr(self.home_tab, 'action_mouse_y_var'):
            self.home_tab.action_mouse_y_var.set("")
        if hasattr(self.home_tab, 'action_mouse_size_var'):
            self.home_tab.action_mouse_size_var.set("")
        
        if hasattr(self.home_tab, 'keyboard_type_var'):
            self.home_tab.action_keyboard_type_var.set("")
        if hasattr(self.home_tab, 'action_keyboard_value_var'):
            self.home_tab.action_keyboard_value_var.set("")
        if hasattr(self.home_tab, 'keyboard_time_diff_var'):
            self.home_tab.keyboard_time_diff_var.set("")
        
        if hasattr(self.home_tab, 'class_name_var'):
            self.home_tab.class_name_var.set("")
        if hasattr(self.home_tab, 'window_title_var'):
            self.home_tab.window_title_var.set("")
        
        if hasattr(self.home_tab, 'ai_train_group_var'):
            self.home_tab.ai_train_group_var.set("")
        if hasattr(self.home_tab, 'ai_train_long_name_var'):
            self.home_tab.ai_train_long_name_var.set("")
        if hasattr(self.home_tab, 'ai_long_txt_name_var'):
            self.home_tab.ai_long_txt_name_var.set("")
        if hasattr(self.home_tab, 'ai_illustration_var'):
            self.home_tab.ai_illustration_var.set("")
        if hasattr(self.home_tab, 'ai_note_var'):
            self.home_tab.ai_note_var.set("")
        
        if hasattr(self.home_tab, 'print_lux_var'):
            self.home_tab.print_lux_var.set("")
        if hasattr(self.home_tab, 'print_luy_var'):
            self.home_tab.print_luy_var.set("")
        if hasattr(self.home_tab, 'print_rdx_var'):
            self.home_tab.print_rdx_var.set("")
        if hasattr(self.home_tab, 'print_rdy_var'):
            self.home_tab.print_rdy_var.set("")
        if hasattr(self.home_tab, 'print_pic_name_var'):
            self.home_tab.print_pic_name_var.set("")
        if hasattr(self.home_tab, 'print_match_picture_var'):
            self.home_tab.print_match_picture_var.set("")
        if hasattr(self.home_tab, 'print_match_text_var'):
            self.home_tab.print_match_text_var.set("")
        if hasattr(self.home_tab, 'print_mouse_action_var'):
            self.home_tab.print_mouse_action_var.set("")
        
        if hasattr(self.home_tab, 'function_name_var'):
            self.home_tab.function_name_var.set("")
        if hasattr(self.home_tab, 'function_args1_var'):
            self.home_tab.function_args1_var.set("")
        if hasattr(self.home_tab, 'function_args2_var'):
            self.home_tab.function_args2_var.set("")
        if hasattr(self.home_tab, 'function_time_diff_var'):
            self.home_tab.function_time_diff_var.set("")
    
    def _on_action_type_changed(self):
        """行为类型变更事件处理"""
        # 这个方法需要调用home_tab中的_on_action_type_changed方法
        if hasattr(self.home_tab, '_on_action_type_changed'):
            self.home_tab._on_action_type_changed()
    
    def _refresh_action_list(self):
        """刷新行为列表"""
        if hasattr(self.home_tab, '_fill_action_data'):
            self.home_tab._fill_action_data(
                self.home_tab.action_type_var.get(), 
                self.home_tab.current_action_id
            )
    
    def _save_action_detail(self, session, action_list_id):
        """保存行为元详细记录"""
        action_type = self.home_tab.action_type_var.get()
        
        if action_type == "mouse":
            action_detail = ActionMouse(
                mouse_action=self._text_to_mouse_action(self.home_tab.action_mouse_action_type_var.get()),
                mouse_x=int(float(self.home_tab.action_mouse_x_var.get()) or 0),
                mouse_y=int(float(self.home_tab.action_mouse_y_var.get()) or 0),
                mouse_size=int(float(self.home_tab.action_mouse_size_var.get()) or 0),
                action_list_id=action_list_id
            )
            session.add(action_detail)
            
        elif action_type == "keyboard":
            action_detail = ActionKeyboard(
                keyboard_type=self._text_to_keyboard_type(self.home_tab.action_keyboard_type_var.get()),
                keyboard_value=self.home_tab.action_keyboard_value_var.get(),
                action_list_id=action_list_id
            )
            session.add(action_detail)
            
        elif action_type == "class":
            action_detail = ActionClass(
                class_name=self.home_tab.class_name_var.get(),
                windows_title=self.home_tab.window_title_var.get(),
                action_list_id=action_list_id
            )
            session.add(action_detail)
            
        elif action_type == "AI":
            action_detail = ActionAI(
                train_group_name=self.home_tab.ai_train_group_var.get(),
                train_long_name=self.home_tab.ai_train_long_name_var.get(),
                long_txt_name=self.home_tab.ai_long_txt_name_var.get(),
                ai_illustration=self.home_tab.ai_illustration_var.get(),
                ai_note=self.home_tab.ai_note_var.get(),
                action_list_id=action_list_id
            )
            session.add(action_detail)
            
        elif action_type == "image":
            action_detail = ActionPrintscreen(
                lux=int(self.home_tab.action_print_lux_var.get() or 0),
                luy=int(self.home_tab.action_print_luy_var.get() or 0),
                rdx=int(self.home_tab.action_print_rdx_var.get() or 0),
                rdy=int(self.home_tab.action_print_rdy_var.get() or 0),
                pic_name=self.home_tab.action_print_pic_name_var.get(),
                match_picture_name=self.home_tab.action_print_match_picture_var.get(),
                match_text=self.home_tab.action_print_match_text_var.get(),
                mouse_action=int(self.home_tab.action_print_mouse_action_var.get() or 0),
                action_list_id=action_list_id
            )
            session.add(action_detail)
            
        elif action_type == "function":
            action_detail = ActionFunction(
                function_name=self.home_tab.function_name_var.get(),
                args1=self.home_tab.function_args1_var.get(),
                args2=self.home_tab.function_args2_var.get(),
                action_list_id=action_list_id
            )
            session.add(action_detail)
    
    def _update_action_detail(self, session, action_list_id):
        """更新行为元详细记录"""
        action_type = self.home_tab.action_type_var.get()
        
        # 查找并更新现有的详细记录
        if action_type == "mouse":
            action_detail = session.query(ActionMouse).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.mouse_action = self._text_to_mouse_action(self.home_tab.action_mouse_action_type_var.get())
                action_detail.mouse_x = int(float(self.home_tab.action_mouse_x_var.get()) or 0)
                action_detail.mouse_y = int(float(self.home_tab.action_mouse_y_var.get()) or 0)
                action_detail.mouse_size = int(float(self.home_tab.action_mouse_size_var.get()) or 0)
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
                
        elif action_type == "keyboard":
            action_detail = session.query(ActionKeyboard).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.keyboard_type = self._text_to_keyboard_type(self.home_tab.action_keyboard_type_var.get())
                action_detail.keyboard_value = self.home_tab.action_keyboard_value_var.get()
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
                
        elif action_type == "class":
            action_detail = session.query(ActionClass).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.class_name = self.home_tab.class_name_var.get()
                action_detail.windows_title = self.home_tab.window_title_var.get()
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
                
        elif action_type == "AI":
            action_detail = session.query(ActionAI).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.train_group_name = self.home_tab.ai_train_group_var.get()
                action_detail.train_long_name = self.home_tab.ai_train_long_name_var.get()
                action_detail.long_txt_name = self.home_tab.ai_long_txt_name_var.get()
                action_detail.ai_illustration = self.home_tab.ai_illustration_var.get()
                action_detail.ai_note = self.home_tab.ai_note_var.get()
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
                
        elif action_type == "image":
            action_detail = session.query(ActionPrintscreen).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.lux = int(self.home_tab.action_print_lux_var.get() or 0)
                action_detail.luy = int(self.home_tab.action_print_luy_var.get() or 0)
                action_detail.rdx = int(self.home_tab.action_print_rdx_var.get() or 0)
                action_detail.rdy = int(self.home_tab.action_print_rdy_var.get() or 0)
                action_detail.pic_name = self.home_tab.action_print_pic_name_var.get()
                action_detail.match_picture_name = self.home_tab.action_print_match_picture_var.get()
                action_detail.match_text = self.home_tab.action_print_match_text_var.get()
                action_detail.mouse_action = int(self.home_tab.action_print_mouse_action_var.get() or 0)
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
                
        elif action_type == "function":
            action_detail = session.query(ActionFunction).filter_by(id=action_list_id).first()
            if action_detail:
                action_detail.function_name = self.home_tab.function_name_var.get()
                action_detail.args1 = self.home_tab.function_args1_var.get()
                action_detail.args2 = self.home_tab.function_args2_var.get()
            else:
                # 如果不存在则创建新记录
                self._save_action_detail(session, action_list_id)
    
    def _text_to_mouse_action(self, text):
        """将鼠标动作文本转换为数字编码"""
        mouse_action_map = {
            "左键单击": 1, "右键单击": 2, "中键单击": 3,
            "左键按下": 4, "左键释放": 5, "右键按下": 6,
            "右键释放": 7, "中键按下": 8, "中键释放": 9,
            "鼠标移动": 0, "滚轮滚动": 10
        }
        return mouse_action_map.get(text, 1)
    
    def _text_to_keyboard_type(self, text):
        """将键盘类型文本转换为数字编码"""
        keyboard_type_map = {
            "按下": 1, "释放": 2, "单击": 3, "文本": 4
        }
        return keyboard_type_map.get(text, 3)